# Eval Report: SLA Status Calculation and API Exposure

- **Task ID:** `task_002_sla_feature`
- **Difficulty:** medium
- **Run type:** `golden_reference`
- **Run timestamp:** 2026-05-31T21:08:48.813075+00:00
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

- **Command:** `pytest evals/tasks/task_002_sla_feature/visible_tests -q -c evals/pytest.ini --rootdir=evals`
- **Suite score:** 1.00
- **Timed out:** False

**Stdout excerpt**
```
3 passed, 1 warning in 0.11s
```

### Hidden-style — PASS (7/7 tests)

- **Command:** `pytest evals/tasks/task_002_sla_feature/hidden_tests -q -c evals/pytest.ini --rootdir=evals`
- **Suite score:** 1.00
- **Timed out:** False

**Stdout excerpt**
```
7 passed, 1 warning in 0.10s
```

## Grader notes

Golden reference passed visible and hidden-style tests.

## Expected capabilities

- time_based_business_logic
- timezone_safe_datetime
- api_field_exposure
- boundary_condition_reasoning

## Common failure modes (from task.yaml)

- uses wall_clock directly in sla.py
- off_by_one_at_sla_boundary
- marks resolved_issues overdue
- wrong_at_risk_percentage
- ignores_naive_datetime_normalization
