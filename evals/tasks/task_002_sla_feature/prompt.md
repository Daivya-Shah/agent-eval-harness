# Task: SLA status calculation

You are working in **IssueFlow**. The product tracks service-level agreement (SLA) risk for open issues based on priority and age.

Implement or repair SLA calculation so API responses include a deterministic `sla_status` field on issues.

## Context

- `apps/issueflow-backend/app/services/sla.py` — core SLA logic
- `apps/issueflow-backend/app/services/clock.py` — UTC time abstraction (use this for testability)
- `apps/issueflow-backend/app/schemas.py` — `SLAStatus` enum exposed on `IssueRead`
- List/detail routes attach `sla_status` when returning issues

## SLA rules

SLA windows start at `issue.created_at` (UTC-normalized):

| Priority | Overdue after |
|----------|----------------|
| `urgent` | 24 hours |
| `high` | 72 hours |
| `medium` | 7 days |
| `low` | 14 days |

Status values:

- **`healthy`** — before the final 20% of the SLA window
- **`at_risk`** — within the final 20% of the window but not yet overdue
- **`overdue`** — at or after the SLA deadline
- **`closed`** — issue status is `resolved` or `closed` (never overdue/at_risk)

## Determinism requirements

- Normalize naive datetimes as UTC.
- Convert timezone-aware datetimes to UTC before comparison.
- Do not call `datetime.now()` directly inside SLA logic; use injectable `now` parameter and/or `clock.utc_now()` at integration boundaries.
- Boundary behavior must be exact: at the deadline instant → `overdue`; one second before → not overdue.

## API contract

Issue JSON must include:

```json
"sla_status": "healthy" | "at_risk" | "overdue" | "closed"
```

## Optional frontend

If `sla_status` is already returned correctly, ensure `SlaBadge` displays the four states. Backend correctness is primary for grading.

## Out of scope

- Changing SLA windows
- User-specific timezones
- Notifications or background jobs
