# Task 002 — Weak agent attempt

## Weak approach

Agent edits `app/routes/issues.py`:

```python
def _sla(issue):
    age = datetime.now() - issue.created_at
    if issue.priority == IssuePriority.URGENT and age > timedelta(hours=24):
        return "overdue"
    return "healthy"
```

Attaches `_sla(issue)` in list/detail handlers only. Ignores `app/services/sla.py`. Does not handle `at_risk`, `low`, or `medium`. Never checks if issue is resolved.

## What the agent likely changed

- `routes/issues.py` — inline SLA helper with `datetime.now()`
- Maybe adds `sla_status` to response manually
- Leaves `app/services/sla.py` unused or deletes its logic

## Why visible tests might pass

1. **Urgent overdue** — hidden test uses `compute_sla_status` directly; visible test checks urgent model with fixed `now` — **passes** if agent's 24h check aligns  
2. **High healthy** — young high issue returns `healthy` — **passes**  
3. **Resolved → closed SLA** — if agent adds `if status in (resolved, closed): return "closed"` in route helper — **passes**

All three visible tests can pass with ~15 lines in routes.

## Why hidden-style tests fail

| Hidden test | Failure |
|-------------|---------|
| `test_exact_overdue_boundary` | Uses `>= deadline` incorrectly (`>` only) |
| `test_one_second_before_overdue_not_overdue` | Off-by-one at 24h mark |
| `test_at_risk_boundary_exactly_80_percent` | No at_risk band |
| `test_naive_created_at_treated_as_utc` | Mixes naive/aware |
| `test_timezone_aware_created_at_normalized` | Local offset math wrong |
| `test_low_priority_14_day_window` | Only urgent implemented |
| `test_closed_issue_never_overdue` | Missing terminal check in service path |

## Missed edge cases

- **80% elapsed** at_risk window (not 20% remaining)
- **SLA from `created_at`**, not `due_at`
- **Injectable `now`** for tests and harness determinism
- **`UTCDateTime`** ORM type for SQLite consistency

## What this reveals about coding agents

Agents often **implement the first visible assertion** (urgent 24h) and **scatter time logic in HTTP layer**. Hidden tests target exact boundaries and timezone normalization — classic deterministic eval failure mode.

Estimated harness score: **visible ~1.0, hidden ~0.1–0.3**, failure modes include *"SLA deterministic time/boundary issue"*.
