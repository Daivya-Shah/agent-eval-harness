# Task 003 — Weak agent attempt (sample)

> **Sample/simulated attempt for demonstration.**

## Sample weak approach

Agent edits `IssueDetail.tsx` only:

```typescript
// Simulated weak patch
const onStatusChange = async (status) => {
  await api.updateIssueStatus(issueId, status);
  setLocalStatus(status); // local useState only
};
```

List continues using stale React Query data. Optional hack:

```typescript
window.location.reload(); // removed after visible test complains
```

Or agent adds:

```typescript
queryClient.invalidateQueries({ queryKey: ["issue", issueId] });
```

…using wrong key shape (not `queryKeys.issues.detail(id)`).

## What the agent likely changed

- `IssueDetail.tsx` — local state or single-query invalidation
- Maybe one `useEffect` refetch in detail only
- **Not** `useIssues.ts` mutation `onSuccess` handlers

## Why visible tests might pass

Visible eval tests **mock** `useUpdateIssueStatus` and assert:

- Status select calls `mutateAsync({ id, status })`
- Comment form calls `addComment` with author/body

They do **not** integration-test list cache. A weak patch that only wires the form passes visible suite.

## Why hidden-style tests fail

| Hidden test | Failure |
|-------------|---------|
| `updates list cache and invalidates` | List query never patched/invalidated |
| `keeps detail and list caches aligned` | Detail updated, list stale |
| `invalidates detail query after comment` | Comment success doesn't invalidate |
| `does not use full page reload` | Reload hack detected |
| `rapid sequential status updates` | Race/stale closure if no proper mutation handling |

## Missed edge cases

- **Active filter** `status=open` — issue should disappear after → `in_progress`
- **`queryKeys.issues.list(filters)`** — each filter combo is separate cache entry
- **Optimistic rollback** on 400 from invalid transition
- **Comment thread** refresh via detail invalidation

## What this reveals about coding agents

Frontend agents often **fix what they see** (detail panel) without tracing **data flow** through React Query. Visible tests that mock hooks reinforce this gap. Hidden tests import real hooks + `QueryClient` and assert cache shape.

Simulated harness: **visible ~1.0, hidden ~0.0–0.2**.

Note: Run eval Vitest from a clean repo path; see `apps/issueflow-frontend/vitest.eval-task003.config.ts`.
