# Expected agent failures — Task 004 (webhook normalization)

## What weak agents typically do

### Support only canonical field names
Agents read `title` and `description` but ignore `summary`, `issueTitle`, `body`, and `details`. Visible alias tests may pass if agents got lucky with one alias pair, but hidden tests fail on alternate vendor payloads.

### Create duplicate issues on retry
Without `external_id` uniqueness checks, webhook retries create multiple issues and duplicate audit noise—common in real integrations.

### Silent priority default
Agents default missing priority to `medium` without logging low confidence, hiding data quality problems from operators.

### Weak date parsing
Agents use `datetime.fromisoformat` only, rejecting common date strings external systems send (`2025/12/01`, date-only ISO).

### Spam activity on duplicate ingest
Even when duplicates are detected, naive code re-logs `webhook_ingested` events on every POST.

## Why visible tests are not enough

Visible tests cover:

- straightforward title/description/P1 payload
- summary/body aliases once
- duplicate external_id returning same id

They do not require rejection paths, multi-format dates, assignee-by-id, ingest logs, or activity idempotency.

## What hidden-style tests catch

| Hidden check | Exposes |
|--------------|---------|
| missing title → 400 | required field validation |
| critical/P9 priority → 400 | ambiguous enum handling |
| unknown assignee → 400 | referential integrity |
| invalid date → 400 | parser error messages |
| assignee numeric id | multi-shape assignee logic |
| multiple date formats | brittle parsing |
| WebhookIngestLog row | missing low-confidence ops trail |
| single webhook activity on retry | idempotency + audit coupling |
| all title aliases in unit test | incomplete alias map |

## What a robust solution preserves

1. Normalizer pure-ish function returning `NormalizedIssuePayload` + confidence notes.
2. Route maps normalization errors → HTTP 400 with message text.
3. CRUD ingest checks `external_id` before insert; returns `(issue, created=False)` on retry.
4. Low-confidence rows persisted to `webhook_ingest_logs`.
5. Activity logged once per created issue, not per duplicate delivery.

## What this reveals about coding agents

Webhook tasks test **integration realism**: messy input, idempotency, and operator observability. Weak agents write happy-path mappers; strong agents separate normalize → validate → persist and think about retries.
