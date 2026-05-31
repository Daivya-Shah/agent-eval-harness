# Expected agent failures — Task 002 (SLA)

## What weak agents typically do

### Hardcode visible priorities only
Agents implement overdue logic for `urgent` because a visible test mentions 24 hours, but leave `low` (14 days) or `medium` windows wrong.

### Use wall-clock time directly
```python
now = datetime.now()  # inside compute_sla_status
```
This makes tests flaky and hides boundary bugs. Reviewers expect injectable `now` and/or `clock.utc_now()` at the edges.

### Treat resolved issues as overdue
Agents compare `created_at` against SLA deadline without checking terminal statuses. Resolved issues should always return `closed` SLA status.

### Wrong at_risk math
Common mistakes: using 20% remaining time instead of elapsed ≥ 80%, or comparing against `due_at` instead of SLA window from `created_at`.

### Ignore timezone normalization
SQLite and Python often produce naive datetimes. Weak solutions compare mixed naive/aware values or assume local timezone.

## Why visible tests are not enough

Visible tests check:

- urgent overdue (service-level, fixed `now`)
- high healthy (young issue)
- resolved → closed SLA via API

They do **not** enforce exact boundary timestamps, timezone normalization, low-priority windows, or closed-status invariants under aged issues.

## What hidden-style tests catch

| Hidden check | Exposes |
|--------------|---------|
| exact deadline instant | off-by-one at boundary |
| one second before deadline | premature overdue |
| 80% elapsed mark | incorrect at_risk band |
| naive UTC datetime | timezone bugs |
| EST → UTC conversion | localization mistakes |
| 14-day low priority | incomplete priority table |
| closed + old created_at | terminal status not handled |

## What a robust solution preserves

1. Pure function `compute_sla_status(issue, now=None)` with UTC normalization helper.
2. Priority → hours map as single constant.
3. Terminal statuses short-circuit to `closed` before age math.
4. API layers call SLA attach on list/detail/create responses.
5. No nondeterministic behavior in unit tests.

## What this reveals about coding agents

SLA tasks expose whether agents can implement **deterministic temporal logic** vs copy-paste threshold checks. Strong agents centralize time; weak agents scatter `datetime.now()` and fail hidden boundary cases.
