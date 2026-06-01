# Task 002 — Baseline failure

## Task summary

Implement SLA status (`healthy`, `at_risk`, `overdue`, `closed`) from issue priority and age since `created_at`. Expose `sla_status` on API responses. Logic lives in `app/services/sla.py`.

Priority windows (from creation):

- urgent: 24h, high: 72h, medium: 7d, low: 14d  
- at_risk: final 20% of window  
- resolved/closed → `closed` SLA (never overdue)

## What a broken baseline might do

- No `sla_status` field on responses (always `null`)
- Or a stub: everything `healthy` except manual `due_at` checks
- Or copy-paste: `if priority == urgent and age > 1 day: overdue` with no timezone handling

## Visible test pattern

| Result | Likely reason |
|--------|----------------|
| **Partial pass** | Urgent overdue check accidentally correct |
| **Fail** | Resolved issues still marked overdue; high never healthy |

Visible tests include urgent overdue with fixed `now`, young high priority healthy, and resolved → `closed` SLA via API.

## Hidden-style test pattern

| Result | Likely reason |
|--------|----------------|
| **Most fail** | Boundaries, timezones, low priority window, closed invariants |

Hidden tests in `hidden_tests/test_hidden_sla.py`:

- Exact deadline instant vs one second before
- 80% at_risk boundary for medium priority
- Naive vs EST `created_at` normalization
- 14-day low priority window
- Closed urgent issue aged 30 days must still be SLA `closed`

## Why this matters

SLA labels drive prioritization dashboards. Off-by-one boundaries and timezone bugs cause **flaky production alerts** and **wrong rankings** — especially bad for eval reproducibility.

## Capability gap revealed

- No **deterministic time** abstraction
- No **terminal status short-circuit**
- **Priority table incomplete** (only urgent implemented)
- Confusing **`due_at`** (user deadline) with **SLA window** (priority-based age)

Harness would show low `determinism` and `hidden_tests` scores.
