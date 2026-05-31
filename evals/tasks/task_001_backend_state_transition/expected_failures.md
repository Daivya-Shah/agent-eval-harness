# Expected agent failures — Task 001 (status transitions)

## What weak agents typically do

### Patch only the visible transition path
Many agents implement `open → in_progress → resolved → closed` because those cases appear in basic tests, but leave `blocked` transitions broken or unimplemented. They may allow `open → closed` shortcuts that violate the state machine.

### Forget `resolved_at` clearing
A common partial fix sets `resolved_at` when entering `resolved` but never clears it when reopening to `open`. The issue looks resolved in reporting even after reopen.

### Block all edits on closed issues globally
Agents sometimes reject **status** updates on closed issues instead of only blocking `PATCH`. The correct behavior is: block generic edits, allow reopen via the status endpoint.

### Skip audit logging
Agents focused on HTTP status codes update `issues.status` but forget `activity_events`. Visible tests may still pass if they do not fetch issue detail.

### Duplicate audit rows on idempotent requests
Naive implementations log activity even when status does not change, polluting the timeline and breaking audit trust.

## Why visible tests are not enough

Visible tests cover four transitions. They do **not** require:

- blocked ↔ open/in_progress paths
- closed edit guard vs reopen distinction
- exact `resolved_at` timestamp semantics
- audit idempotency
- specific 400 error message content

An agent can hardcode transition tables for the visible paths only.

## What hidden-style tests catch

| Hidden check | Exposes |
|--------------|---------|
| blocked → open / in_progress | Incomplete transition matrix |
| PATCH on closed issue | Missing edit guard in crud/routes |
| reopen via status endpoint | Over-broad closed locking |
| resolved_at set/clear | Lifecycle timestamp bugs |
| repeated same status | Audit spam / non-idempotent updates |
| invalid message content | Generic 400s without actionable detail |
| activity old/new values | Missing or incorrect audit payload |

## What a robust solution preserves

1. **Single source of truth** for transitions in `state_machine.py`.
2. **crud** applies transitions, sets/clears `resolved_at` via injectable clock, logs audit once per real change.
3. **routes** map `StateTransitionError` → HTTP 400 with the state machine message.
4. **No regression** to unrelated issue fields or webhook/search behavior.

## What this reveals about coding agents

This task measures whether an agent understands **domain invariants** vs **endpoint patching**. Strong agents read existing services and extend them; weak agents chase test output and leave edge-case lifecycle rules brittle.
