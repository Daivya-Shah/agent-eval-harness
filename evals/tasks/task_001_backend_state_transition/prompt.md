# Task: Backend issue status transitions

You are working in **IssueFlow**, an issue-tracking codebase used by an engineering team. The backend enforces a lifecycle for issues and records audit activity when status changes.

Your task is to **implement or repair** status transition behavior in the backend so that lifecycle rules and audit invariants hold under edge cases—not only on the happy path.

## Context

Relevant modules:

- `apps/issueflow-backend/app/services/state_machine.py` — allowed transitions and edit guards
- `apps/issueflow-backend/app/crud.py` — transition logic, `resolved_at`, activity logging
- `apps/issueflow-backend/app/routes/issues.py` — HTTP endpoints (`PATCH /api/issues/{id}`, `POST /api/issues/{id}/status`)

Issues have statuses: `open`, `in_progress`, `blocked`, `resolved`, `closed`.

## Required behavior

### Allowed transitions

| From | Allowed next statuses |
|------|------------------------|
| `open` | `in_progress`, `blocked` |
| `in_progress` | `resolved`, `blocked`, `open` |
| `blocked` | `open`, `in_progress` |
| `resolved` | `closed`, `open` (reopen) |
| `closed` | `open` (reopen) |

Any other transition must return **HTTP 400** with a clear error message naming the invalid `from → to` pair.

### Closed issue editing

- Issues in `closed` status **must not** be editable via `PATCH /api/issues/{id}` (title, description, priority, assignee, etc.).
- A closed issue **may** be reopened via `POST /api/issues/{id}/status` with `{ "status": "open" }`.
- After reopening, normal edits should work again.

### `resolved_at` invariant

- When status becomes `resolved`, set `resolved_at` to the transition timestamp (UTC).
- When reopening from `resolved` or `closed` to `open`, clear `resolved_at` (`null`).
- Transitioning `resolved → closed` should **keep** `resolved_at` set.

Use the existing clock abstraction (`app/services/clock.py`) rather than scattering raw `datetime.now()` calls.

### Activity / audit events

Every **successful** status change must create an `activity_events` row:

- `event_type`: `status_change`
- `old_value`: previous status string
- `new_value`: new status string

Posting the **same** status again should be idempotent: do not create duplicate misleading audit entries or corrupt state.

### API contract

- `POST /api/issues/{id}/status` body: `{ "status": "<status>" }`
- Invalid transitions: **400** with JSON `{ "detail": "<human-readable message>" }`
- Successful transitions: **200** with updated issue JSON including `resolved_at` when applicable

## What reviewers check

Visible tests cover basic transitions. **Hidden-style tests** (included in-repo for this benchmark demo) cover reopen flows, closed-edit blocking, `resolved_at` correctness, audit integrity, and error message quality.

Do not hardcode one transition path. Preserve existing architecture (routes → crud → state machine → audit service).

## Out of scope

- Frontend changes
- Authentication
- Changing database schema unless strictly necessary
