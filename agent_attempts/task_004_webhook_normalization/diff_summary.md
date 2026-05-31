# Task 004 — Diff summary (sample)

## Likely files — weak solution

| File | Change |
|------|--------|
| `app/services/webhook_normalizer.py` | Minimal key mapping |
| `app/routes/webhooks.py` | Always insert; no idempotency |
| `app/schemas.py` | Maybe widen priority to `str` |

**Often skipped:** `WebhookIngestLog` usage, assignee lookup in crud, audit on create-only

## Likely files — strong solution

| File | Change |
|------|--------|
| `app/services/webhook_normalizer.py` | Full alias + priority maps, confidence |
| `app/routes/webhooks.py` | Idempotent create, assignee validation |
| `app/crud.py` | Lookup by `external_id`, ingest log writes |
| `app/models.py` | `WebhookIngestLog` (already exists) |
| `app/services/audit.py` | Event on new issue only |

## Risk areas

- Breaking existing webhook clients with stricter validation
- Idempotency vs audit (replay should not duplicate events)
- Priority map drift from SLA/priority enums elsewhere
- SQLite unique constraint on `external_id` if added

## Reviewer checklist

- [ ] Full title alias map (unit test covers all keys)
- [ ] P0–P3 mapping; ambiguous values rejected
- [ ] Duplicate `external_id` returns same issue without new activity
- [ ] Unknown assignee → 400; assignee-by-id supported
- [ ] Multiple date formats parse correctly
- [ ] Low-confidence row in `WebhookIngestLog`
- [ ] Harness task_004 hidden pytest green

## Grader regression catch

Backend pytest hidden suite runs via harness `test_runner.py`. Failures on idempotency or alias tests reduce weighted `hidden_tests` score. Compare agent run JSON to `evals/results/task_004_webhook_normalization_golden_reference.json`.
