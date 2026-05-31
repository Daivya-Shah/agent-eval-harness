# Task 002 — Strong agent attempt (sample)

> **Sample/simulated reference.** Aligns with golden `app/services/sla.py` in this repo.

## What a robust solution does

1. **`compute_sla_status(issue, now=None)`** in `app/services/sla.py`:
   - Short-circuit `resolved`/`closed` → `SLAStatus.CLOSED`
   - Normalize datetimes to UTC via `_ensure_utc`
   - Compare elapsed vs priority window from `SLA_HOURS`
   - Mark `at_risk` when elapsed ≥ 80% of window
   - Mark `overdue` when `now >= deadline`
2. **`attach_sla_status`** used from crud/routes on list, detail, create
3. **Clock abstraction** — integration uses `utc_now()`; pure function accepts `now` param for tests
4. **Frontend** — `SlaBadge.tsx` displays four states (optional but consistent)

## Invariants preserved

| Invariant | Enforcement |
|-----------|-------------|
| Terminal issues never overdue | Early return `CLOSED` |
| Priority → hours single map | `SLA_HOURS` constant |
| Boundary inclusive overdue | `reference >= deadline` |
| Deterministic tests | Fixed `now` in eval + backend tests |
| API contract | `sla_status` on every `IssueRead` |

## Edge case handling

- Naive SQLite datetimes treated as UTC
- EST (or any offset) normalized before compare
- One second before deadline ≠ overdue
- Low priority 14-day window same logic as urgent 24h

## Tests that should pass

- Visible (3) + hidden (7) under `evals/tasks/task_002_sla_feature/`
- `apps/issueflow-backend/tests/test_sla.py`

Golden report: `evals/results/task_002_sla_feature_golden_reference.json` — **1.0**.

## Why this is stronger engineering

Time logic is **pure, testable, and centralized**. Routes stay thin. The same function powers eval hidden tests and production API — no duplicate SLA math in list vs detail handlers.
