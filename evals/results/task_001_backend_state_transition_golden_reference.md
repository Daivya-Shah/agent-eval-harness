# Eval Report: Backend Issue Status Transition Robustness

- **Task ID:** `task_001_backend_state_transition`
- **Difficulty:** medium
- **Run type:** `golden_reference`
- **Run timestamp:** 2026-05-31T21:08:44.816893+00:00
- **Overall score:** **1.00**

## Scoring breakdown (weighted contributions)

| Category | Category score | Weight | Contribution |
|----------|----------------|--------|--------------|
| visible_tests | 1.00 | 0.33 | 0.33 |
| hidden_tests | 1.00 | 0.29 | 0.29 |
| regression_safety | 1.00 | 0.14 | 0.14 |
| interface_contract | 1.00 | 0.10 | 0.10 |
| determinism | 1.00 | 0.10 | 0.10 |
| code_quality | 1.00 | 0.05 | 0.05 |

## Test suites

### Visible — PASS (4/4 tests)

- **Command:** `pytest evals/tasks/task_001_backend_state_transition/visible_tests -q -c evals/pytest.ini --rootdir=evals`
- **Suite score:** 1.00
- **Timed out:** False

**Stdout excerpt**
```
4 passed, 1 warning in 0.33s
```

### Hidden-style — PASS (7/7 tests)

- **Command:** `pytest evals/tasks/task_001_backend_state_transition/hidden_tests -q -c evals/pytest.ini --rootdir=evals`
- **Suite score:** 1.00
- **Timed out:** False

**Stdout excerpt**
```
7 passed, 1 warning in 0.44s
```

## Grader notes

Golden reference passed visible and hidden-style tests.

## Expected capabilities

- state_machine_modeling
- backend_api_validation
- audit_logging
- datetime_invariants
- error_message_quality

## Common failure modes (from task.yaml)

- allows invalid lifecycle jumps
- forgets resolved_at clearing on reopen
- allows PATCH edits on closed issues
- skips activity events on status change
- duplicates activity on idempotent status posts
- hardcodes transitions only for visible test paths
