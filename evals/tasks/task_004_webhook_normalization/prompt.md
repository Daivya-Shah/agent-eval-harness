# Task: Webhook issue ingestion normalization

External systems send issue webhooks to IssueFlow with **inconsistent field names**. Your job is to implement or repair normalization so messy payloads map to the canonical internal issue schema safely.

## Context

- `app/services/webhook_normalizer.py` — field aliasing, validation, confidence notes
- `app/routes/webhooks.py` — `POST /api/webhooks/issues`
- `app/crud.py` — `ingest_webhook_issue` persistence + idempotency
- `app/models.py` — `WebhookIngestLog` for manual review

## Incoming payload aliases

**Title** (required — at least one):

- `title`, `issueTitle`, `summary`

**Description** (optional):

- `description`, `body`, `details`

**Priority** (optional but validated when present):

- `P0`, `P1`, `P2`, `P3` → `urgent`, `high`, `medium`, `low`
- or direct strings `urgent`, `high`, `medium`, `low` (case-insensitive)

If priority is **missing**, default to `medium` and mark mapping as **low confidence**.

If priority is **ambiguous/unknown** (e.g. `critical`, `P4`), reject with HTTP 400.

**Assignee** (optional):

- `assignee_email` or email-shaped `assignee` string
- numeric `assignee` or `assignee_id`

Unknown assignees must be rejected with a clear 400 error.

**Due date** (optional):

- `due_at`, `due_date`, or `dueDate`
- support ISO timestamps and common date strings (deterministic parsing)

Invalid dates → HTTP 400 with clear message.

**External id** (required for idempotency):

- `external_id` or `id`

## Idempotency

Duplicate `external_id` must **not** create a second issue. Return the existing issue with `created: false` in the webhook response.

Do not spam duplicate `webhook_ingested` activity events on retries.

## Low-confidence logging

When normalization fills defaults or cannot resolve optional fields confidently, record a row in `webhook_ingest_logs` for manual review and return `confidence: "low"` plus explanatory `notes` in the API response.

## Response shape

```json
{
  "issue": { ... IssueRead ... },
  "created": true,
  "confidence": "high",
  "notes": []
}
```

## Out of scope

- Authentication/signatures for webhooks
- Non-issue webhook types
