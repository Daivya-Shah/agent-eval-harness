# Task 001 — Diff summary

## Likely files — weak solution

| File | Risky change |
|------|----------------|
| `app/routes/issues.py` | Inline transition dict; HTTP-layer business logic |
| `app/crud.py` | Partial `transition_status`; missing audit / `resolved_at` clear |

**Usually untouched by weak agents:** `app/services/state_machine.py`, `app/services/audit.py`

## Likely files — strong solution

| File | Change |
|------|--------|
| `app/services/state_machine.py` | Transition matrix + edit guard |
| `app/crud.py` | `transition_status`, `update_issue` guards, audit hooks |
| `app/routes/issues.py` | Thin error mapping only |
| `app/services/clock.py` | Used for testable timestamps |

## Risk areas

- **Duplicated transition rules** in route + crud (weak) → diverge over time
- **Forgotten PATCH guard** on comments/assignee endpoints
- **Audit event schema** — missing `old_value`/`new_value` breaks activity UI
- **Regression** to webhook ingest or list filters if crud raises new exceptions

## Reviewer checklist

- [ ] Single transition source of truth in `state_machine.py`
- [ ] `resolved_at` set on resolve, cleared on reopen to `open`
- [ ] Closed issue: PATCH fails, status reopen succeeds
- [ ] Same-status POST is idempotent (no extra audit rows)
- [ ] 400 messages name both statuses
- [ ] Visible + hidden eval suites pass via harness

## How the grader catches regressions

```powershell
python -m evals.harness.run_task --task evals/tasks/task_001_backend_state_transition --output-dir=evals/results
```

Hidden failures drop `hidden_tests` score; classifier adds *"issue lifecycle / state transition regression"* when assertion output mentions transitions. Compare against golden JSON in `evals/results/`.
