# Eval Report: Frontend Cache Consistency After Mutations

- **Task ID:** `task_003_frontend_stale_state`
- **Difficulty:** hard
- **Run type:** `golden_reference`
- **Run timestamp:** 2026-05-31T21:08:56.941228+00:00
- **Overall score:** **1.00**

## Scoring breakdown (weighted contributions)

| Category | Category score | Weight | Contribution |
|----------|----------------|--------|--------------|
| visible_tests | 1.00 | 0.29 | 0.29 |
| hidden_tests | 1.00 | 0.33 | 0.33 |
| regression_safety | 1.00 | 0.10 | 0.10 |
| interface_contract | 1.00 | 0.10 | 0.10 |
| determinism | 1.00 | 0.14 | 0.14 |
| code_quality | 1.00 | 0.05 | 0.05 |

## Test suites

### Visible — PASS (2/2 tests)

- **Command:** `cd apps/issueflow-frontend && npx vitest run --config vitest.eval-task003.config.ts ../../evals/tasks/task_003_frontend_stale_state/visible_tests`
- **Suite score:** 1.00
- **Timed out:** False

**Stdout excerpt**
```
Duration  3.14s (transform 169ms, setup 292ms, collect 658ms, tests 517ms, environment 1.05s, prepare 273ms)
```

### Hidden-style — PASS (5/5 tests)

- **Command:** `cd apps/issueflow-frontend && npx vitest run --config vitest.eval-task003.config.ts ../../evals/tasks/task_003_frontend_stale_state/hidden_tests`
- **Suite score:** 1.00
- **Timed out:** False

**Stdout excerpt**
```
Duration  1.96s (transform 85ms, setup 253ms, collect 233ms, tests 37ms, environment 825ms, prepare 142ms)
```

## Grader notes

Golden reference passed visible and hidden-style tests.

## Expected capabilities

- react_query_cache_management
- optimistic_updates
- ui_state_consistency
- mutation_error_handling

## Common failure modes (from task.yaml)

- detail_updates_but_list_stale
- filter_shows_wrong_status_after_transition
- only_invalidates_detail_not_lists
- uses_window_location_reload
- optimistic_update_without_rollback
