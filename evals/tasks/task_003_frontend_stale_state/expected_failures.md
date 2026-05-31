# Expected agent failures — Task 003 (frontend stale state)

## What weak agents typically do

### Invalidate only the detail query
After `updateIssueStatus`, agents call `invalidateQueries(detail(id))` but forget list queries. The detail panel looks correct while the dashboard row still shows the old status.

### Patch list items without invalidating filters
Agents optimistically map over cached list items updating status in place. When a status filter is active (`status=open`), the issue should **leave** the filtered list after transitioning to `in_progress`. In-place patch leaves a stale row until manual refresh.

### Full page reload workaround
```typescript
window.location.reload();
```
This passes superficial manual testing but fails eval requirements and breaks SPA UX.

### Optimistic update without rollback
Agents set cache data before the mutation resolves but never revert on 400 errors from invalid transitions.

### Unstructured query keys
Random string keys (`['issue', id]`) make partial invalidation unreliable across list/filter/detail.

## Why visible tests are not enough

Visible tests verify that:

- status select triggers a mutation
- comment form calls add-comment mutation

They do **not** require list/detail cache alignment, filter-aware invalidation, rollback, or absence of reload hacks.

## What hidden-style tests catch

| Hidden check | Exposes |
|--------------|---------|
| list cache updated + lists invalidated | partial cache updates |
| detail/list status match after mutation | split-brain UI state |
| comment invalidates detail | stale comment threads |
| no `location.reload` | reload workaround |
| rapid sequential mutations | race/stale closure bugs |

## What a robust solution preserves

1. Central `queryKeys` module used everywhere.
2. Mutations update relevant cache slices **and** invalidate list/detail queries for server reconciliation.
3. Filter-aware behavior: rely on refetch after invalidation so filtered views drop non-matching issues.
4. Optional optimistic updates with rollback in `onError`.
5. No navigation hacks.

## What this reveals about coding agents

Frontend eval tasks expose **cache coherence** reasoning. Weak agents treat React Query as a fetch wrapper; strong agents model list/filter/detail as coupled observers of the same domain entity.
