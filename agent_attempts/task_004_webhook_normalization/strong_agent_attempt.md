# Task 004 — Strong agent attempt

## What a robust solution does

1. **`normalize_webhook_payload(raw)`** returns structured dict + confidence metadata:
   - Title from full alias set (`title`, `summary`, `issueTitle`, …)
   - Description from `description`, `body`, `details`
   - Priority via explicit map: `P0`–`P3` and string enums; reject ambiguous values
2. **Flexible date parsing** — multiple string formats normalized to UTC
3. **Route idempotency** — lookup by `external_id`; return existing issue with `created: false`
4. **Assignee** — resolve by email or numeric user id; 400 if provided but not found
5. **`WebhookIngestLog`** — persist low-confidence mappings (e.g. missing priority)
6. **Audit** — `webhook_ingested` activity once per created issue, not on duplicate delivery

## Invariants preserved

| Invariant | Enforcement |
|-----------|-------------|
| No duplicate external issues | Upsert/lookup by `external_id` |
| Priority always valid enum | Normalization table + validation |
| Observable ambiguity | Ingest log + structured errors |
| Safe defaults | Reject empty title, don't invent data |
| Deterministic grading | Same payload → same issue id on retry |

## Edge case handling

- Empty title after alias resolution → 400
- `critical` / `P9` priority → 400 with message
- Assignee id vs email both supported
- `2025/12/01` and date-only ISO accepted
- Retry storm: same issue id, no duplicate activity rows

## Tests that should pass

- Visible (3) + hidden (10) under `evals/tasks/task_004_webhook_normalization/`
- `apps/issueflow-backend/tests/test_webhook_normalizer.py`

Golden report: `evals/results/task_004_webhook_normalization_golden_reference.json` — **1.0**.

## Why this is stronger engineering

Treats webhooks as **untrusted, variable input** with **idempotent side effects**. Normalization is explicit and testable; logging makes production debugging possible without re-running the agent.
