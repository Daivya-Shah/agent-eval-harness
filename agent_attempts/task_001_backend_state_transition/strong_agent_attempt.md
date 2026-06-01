# Task 001 — Strong agent attempt

## What a robust solution does

1. **Centralizes transitions** in `app/services/state_machine.py` with `ALLOWED_TRANSITIONS` and `validate_transition()`.
2. **Applies changes in crud** via `transition_status()`:
   - Sets `resolved_at` when entering `resolved` (via `utc_now()`)
   - Clears `resolved_at` when reopening from `resolved` or `closed` to `open`
   - Returns early on same-status (no audit spam)
3. **Guards edits** with `assert_issue_editable()` — closed issues reject PATCH, not status reopen.
4. **Logs audit** once per real change through `app/services/audit.py`.
5. **Maps errors** in routes: `StateTransitionError` → HTTP 400 with state machine message.

## Invariants preserved

| Invariant | Mechanism |
|-----------|-----------|
| Valid transition graph | `state_machine.py` |
| Closed issue immutability | `assert_issue_editable` on PATCH/comments/assignee |
| Reopen path | `closed → open` allowed via status endpoint |
| `resolved_at` lifecycle | Set on resolve, clear on reopen |
| Audit integrity | One event per status change, old/new values populated |

## Edge case handling

- **Blocked ↔ open/in_progress** — full matrix, not just forward path
- **Invalid transitions** — message includes `'from' → 'to'` for debugging
- **Idempotent POST** — no duplicate `status_change` events
- **Deterministic timestamps** — `utc_now()` monkeypatchable in tests

## Tests that should pass

- All **visible** tests (4) in `evals/tasks/task_001_backend_state_transition/visible_tests/`
- All **hidden-style** tests (7) in `hidden_tests/`
- Main app suite `apps/issueflow-backend/tests/test_state_transitions.py`

## Why this is stronger engineering

The agent **reads existing architecture** (audit service, clock, state machine extraction) instead of bolting logic into routes. Changes are testable at crud/service layer and survive new endpoints (webhooks, bulk actions) because invariants live in one place.

Golden reference report: `evals/results/task_001_backend_state_transition_golden_reference.json` — **overall_score: 1.0**.
