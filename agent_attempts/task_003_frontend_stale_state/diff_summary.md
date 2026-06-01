# Task 003 — Diff summary

## Likely files — weak solution

| File | Change |
|------|--------|
| `src/components/IssueDetail.tsx` | Local state / detail-only refetch |
| Maybe `src/pages/DashboardPage.tsx` | `key={refresh}` hack |

**Often untouched:** `src/hooks/useIssues.ts`, `src/api/queryKeys.ts`

## Likely files — strong solution

| File | Change |
|------|--------|
| `src/hooks/useIssues.ts` | Mutation `onSuccess` cache logic |
| `src/api/queryKeys.ts` | Consistent key factory |
| `src/components/IssueDetail.tsx` | Uses hooks only; no local status source of truth |
| `src/components/IssueList.tsx` | Consumes list query (unchanged if cache correct) |

## Risk areas

- Wrong invalidation scope (too narrow or too broad)
- Forgetting `issues.lists()` prefix invalidation
- Optimistic patch without rollback on 400
- Breaking Playwright e2e while unit tests pass

## Reviewer checklist

- [ ] Status mutation updates list + detail caches
- [ ] Comment mutation invalidates detail
- [ ] No `window.location.reload`
- [ ] `queryKeys` used everywhere (no ad-hoc strings)
- [ ] Filtered dashboard drops issue after status leaves filter
- [ ] Eval task_003 hidden Vitest green from clean path

## Grader regression catch

Vitest hidden suite imports real `@/hooks/useIssues` with test `QueryClient`. Harness runs:

```powershell
cd apps/issueflow-frontend
npx vitest run --config vitest.eval-task003.config.ts ../evals/tasks/task_003_frontend_stale_state/hidden_tests
```

Failure drops `hidden_tests` weight; visible may still pass if mocks-only tests unchanged.
