# Task 003 — Strong agent attempt

## What a robust solution does

1. **Structured query keys** in `src/api/queryKeys.ts`:
   - `issues.list(filters)`, `issues.detail(id)`, `issues.lists()` prefix
2. **Mutations in `useIssues.ts`**:
   - `onSuccess`: patch list cache via `setQueriesData` for matching issues
   - Update detail cache slice
   - `invalidateQueries` on `issues.lists()` and `issues.detail(id)` for server reconciliation
3. **Same pattern** for assignee + comment mutations
4. **No reload hacks** — all UX via cache
5. Optional: optimistic update with `onError` rollback (not required for golden pass but stronger)

## Invariants preserved

| Invariant | Mechanism |
|-----------|-----------|
| List reflects status change | Patch + invalidate list queries |
| Detail reflects change | `setQueryData` on detail |
| Filters stay honest | Refetch after invalidation drops non-matching rows |
| Comments appear | Detail invalidation after `addComment` |
| Predictable keys | Central `queryKeys` module |

## Edge case handling

- Multiple filter caches updated via `setQueriesData` on `issues.lists()` prefix
- Rapid mutations — await `mutateAsync`, React Query serializes per hook instance
- Failed backend transition — mutation error surfaces in UI; cache not left permanently wrong if no optimistic layer

## Tests that should pass

- Eval visible (2) + hidden (5) via `vitest.eval-task003.config.ts`
- App Vitest: `IssueFilters.test.tsx`, etc.
- Playwright e2e: `e2e/issue-flow.spec.ts` (status + comment workflow)

Golden report: `evals/results/task_003_frontend_stale_state_golden_reference.json` — **1.0**, visible **2/2**, hidden **5/5**.

## Why this is stronger engineering

The agent models **Issue** as shared server state observed by multiple queries. Mutations are **cache transactions**, not isolated API calls. This matches how senior frontend engineers reason about React Query in production dashboards.
