# Task 002 — Diff summary

## Likely files — weak solution

| File | Change |
|------|--------|
| `app/routes/issues.py` | Inline age math, `datetime.now()` |
| `app/schemas.py` | Field present but inconsistently populated |

**Often skipped:** `app/services/sla.py`, `app/services/clock.py`, `app/types.py` (UTCDateTime)

## Likely files — strong solution

| File | Change |
|------|--------|
| `app/services/sla.py` | Full SLA computation |
| `app/services/clock.py` | Wall-clock boundary |
| `app/crud.py` / `app/routes/issues.py` | Call `attach_sla_status` |
| `apps/issueflow-frontend/src/components/SlaBadge.tsx` | Display (if task spans UI) |

## Risk areas

- Duplicating SLA in list vs detail handlers
- Using `due_at` instead of SLA window
- Forgetting SLA on webhook-created issues
- Breaking resolved issues by marking them overdue

## Reviewer checklist

- [ ] `compute_sla_status(issue, now=...)` accepts injectable time
- [ ] Resolved/closed always return `closed`
- [ ] at_risk at exactly 80% elapsed
- [ ] Overdue at exact deadline instant
- [ ] All four priority windows in `SLA_HOURS`
- [ ] Harness task_002 hidden suite green

## Grader regression catch

Harness parses pytest summary lines; hidden boundary failures reduce `hidden_tests` and `determinism` weighted scores. Compare agent JSON to golden reference in `evals/results/`.
