# Eval Report: Webhook Payload Normalization and Idempotency

- **Task ID:** `task_004_webhook_normalization`
- **Difficulty:** hard
- **Run type:** `golden_reference`
- **Run timestamp:** 2026-05-31T21:09:00.789452+00:00
- **Overall score:** **1.00**

## Scoring breakdown (weighted contributions)

| Category | Category score | Weight | Contribution |
|----------|----------------|--------|--------------|
| visible_tests | 1.00 | 0.33 | 0.33 |
| hidden_tests | 1.00 | 0.29 | 0.29 |
| regression_safety | 1.00 | 0.10 | 0.10 |
| interface_contract | 1.00 | 0.14 | 0.14 |
| determinism | 1.00 | 0.10 | 0.10 |
| code_quality | 1.00 | 0.05 | 0.05 |

## Test suites

### Visible — PASS (3/3 tests)

- **Command:** `pytest evals/tasks/task_004_webhook_normalization/visible_tests -q -c evals/pytest.ini --rootdir=evals`
- **Suite score:** 1.00
- **Timed out:** False

**Stdout excerpt**
```
3 passed, 1 warning in 0.10s
```

### Hidden-style — PASS (10/10 tests)

- **Command:** `pytest evals/tasks/task_004_webhook_normalization/hidden_tests -q -c evals/pytest.ini --rootdir=evals`
- **Suite score:** 1.00
- **Timed out:** False

**Stdout excerpt**
```
10 passed, 1 warning in 0.20s
```

## Grader notes

Golden reference passed visible and hidden-style tests.

## Expected capabilities

- schema_normalization
- validation_and_error_messages
- idempotency
- external_integration_hardening

## Common failure modes (from task.yaml)

- accepts_only_one_field_alias
- creates_duplicate_issues
- silent_priority_default_without_log
- weak_date_parsing
- spams_activity_on_duplicate
