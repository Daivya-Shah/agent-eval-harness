# Task 001 — Weak agent attempt (sample)

> **Sample/simulated attempt for demonstration.** Describes a plausible weak patch, not an actual model transcript.

## Sample weak approach

The agent reads `prompt.md` and visible tests, then edits `app/routes/issues.py`:

```python
# Simulated weak patch
if new_status == "resolved":
    issue.resolved_at = datetime.utcnow()
issue.status = new_status
db.commit()
```

It adds a small dict for transitions the visible tests exercise:

```python
ALLOWED = {
    ("open", "in_progress"),
    ("in_progress", "resolved"),
    ("resolved", "closed"),
}
```

No changes to `state_machine.py`. No audit calls. No check on `PATCH` for closed issues.

## What the agent likely changed

- Inline validation in the status route (not shared with crud)
- Sets `resolved_at` on resolve only — never clears on reopen
- Returns generic `400` with `"Invalid transition"` (no from/to in message)

## Why visible tests might pass

Visible suite (`visible_tests/test_visible_transitions.py`) only checks:

1. open → in_progress  
2. in_progress → resolved (+ `resolved_at` present)  
3. resolved → closed  
4. open → closed returns 400  

If the agent blocks `open → closed` explicitly and implements those three hops, **all four visible tests pass**.

## Why hidden-style tests fail

| Hidden test | Failure |
|-------------|---------|
| `test_blocked_to_open_and_in_progress` | No blocked transitions in `ALLOWED` |
| `test_closed_issue_patch_blocked` | `update_issue` never calls edit guard |
| `test_closed_issue_reopens_via_status_endpoint` | May work by accident, but PATCH still broken |
| `test_resolved_at_set_and_cleared` | Reopen leaves old `resolved_at` |
| `test_repeated_same_status_is_idempotent_for_audit` | No early return; logs duplicate events |
| `test_invalid_transition_message_is_specific` | Message lacks `closed` / `resolved` |
| `test_status_change_activity_contains_old_and_new` | No `log_activity` call |

## Missed edge cases

- **Blocked** as a first-class state (return path to open/in_progress)
- **Closed vs reopen** — edit guard only on PATCH, not on status POST
- **Idempotent status POST** — same status should not append audit noise
- **Clock injection** — uses raw `utcnow()` instead of `app/services/clock.py`

## What this reveals about coding agents

Classic **visible-test overfitting**: the agent optimized for four assertions without reading `expected_failures.md` or existing `state_machine.py`. It patches symptoms in the route layer instead of preserving invariants in crud + audit.

Estimated harness score (simulated): **visible ~1.0, hidden ~0.0–0.3**, overall **~0.35–0.45** depending on weights in `task.yaml`.
