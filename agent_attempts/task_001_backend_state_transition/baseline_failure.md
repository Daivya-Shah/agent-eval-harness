# Task 001 — Baseline failure

## Task summary

Agents must implement issue status transitions in IssueFlow: allowed moves among `open`, `in_progress`, `blocked`, `resolved`, and `closed`; guard edits on closed issues; maintain `resolved_at`; log audit events.

Target modules: `app/services/state_machine.py`, `app/crud.py`, `app/routes/issues.py`.

## What a broken baseline might do

A minimal baseline ships with:

- Every status allowed to transition to any other status (or no validation at all)
- `PATCH /api/issues/{id}` still updates closed issues
- No `resolved_at` field updates
- No `activity_events` on status change

Alternatively, a **partial** baseline hardcodes only:

```text
open → in_progress → resolved → closed
```

and ignores `blocked` entirely.

## Visible test pattern

| Result | Likely reason |
|--------|----------------|
| **Some pass** | Happy-path transitions work if hardcoded |
| **Some fail** | `open → closed` shortcut or missing `resolved_at` on resolve |

Example: `test_invalid_open_to_closed_returns_400` fails because the route accepts the transition.

## Hidden-style test pattern

| Result | Likely reason |
|--------|----------------|
| **Most fail** | No blocked paths, no closed-edit guard, no audit idempotency |

Examples from `evals/tasks/task_001_backend_state_transition/hidden_tests/`:

- `test_blocked_to_open_and_in_progress` — blocked state never handled
- `test_closed_issue_patch_blocked` — PATCH still succeeds on closed issues
- `test_resolved_at_set_and_cleared` — timestamp never cleared on reopen
- `test_repeated_same_status_is_idempotent_for_audit` — duplicate activity rows

## Why this matters

Issue tracking systems depend on **lifecycle invariants** for reporting, SLA, and compliance. A baseline that treats status as a free-form string field will look fine in a demo UI but breaks audit trails and reopen workflows.

## Capability gap revealed

- No **state machine modeling** — agent sees HTTP, not domain rules
- No **timestamp invariants** — `resolved_at` treated as decorative
- No **audit design** — activity history omitted or duplicated

The harness would score hidden_tests near **0** while visible might be **partial**, producing failure mode: *"likely overfit to visible tests or missed edge cases"* once an agent patches only the visible path.
