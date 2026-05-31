# Task 004 — Weak agent attempt (sample)

> **Sample/simulated attempt for demonstration.**

## Sample weak approach

Agent patches `webhook_normalizer.py` with minimal mapping:

```python
# Simulated weak patch
def normalize(payload):
    return {
        "title": payload.get("title") or "",
        "description": payload.get("description") or "",
        "priority": payload.get("priority", "medium"),
    }
```

Route always `INSERT` new issue. Priority accepts any string and stores raw value. `external_id` ignored.

## What the agent likely changed

- `app/services/webhook_normalizer.py` — title/description only
- `app/routes/webhooks.py` — direct create, no idempotency lookup
- Skips `WebhookIngestLog` model usage

## Why visible tests might pass

1. **Standard payload** — `P1` → `high`, assignee by email — **pass** if enum map includes P-level codes
2. **`summary` + `body`** — agent adds two aliases — **pass** (visible test covers exactly this pair)
3. **Duplicate `external_id`** — agent adds lookup before insert — **pass**

All three visible tests can pass while hidden validation remains broken.

## Why hidden-style tests fail

| Hidden test | Failure |
|-------------|---------|
| `test_missing_title_rejected` | Empty title after aliases → 201 with blank title |
| `test_ambiguous_priority_rejected` | `critical`/`P9` silently → `medium` |
| `test_unknown_assignee_rejected` | Unknown email → 201 with null assignee |
| `test_invalid_date_rejected` | Strict `fromisoformat` only |
| `test_assignee_by_numeric_id` | Only email assignee supported |
| `test_multiple_date_formats` | Rejects `2025/12/01` or date-only strings |
| `test_low_confidence_missing_priority_logged` | No ingest log row |
| `test_idempotent_duplicate_does_not_spam_activity` | Re-logs activity on retry |
| `test_normalizer_accepts_all_title_aliases` | Missing `issueTitle` and other aliases |

## Missed edge cases

- **Title alias completeness** — visible only checks `summary`; hidden unit test covers full alias map
- **Priority confidence** — `P1` works but `critical`/`P9` must 400, not default
- **Assignee by id** — not just email string
- **Date parsing** — multiple external formats, not ISO-only
- **Activity idempotency** — duplicate webhook must not re-emit `webhook_ingested`

## What this reveals about coding agents

Agents optimize for **first visible JSON example** in the prompt. They add one alias (`summary`) but miss the **combinatorics of real vendor payloads**. Hidden tests simulate Jira/Linear-style field variance and retry semantics.

Simulated harness: **visible ~1.0, hidden ~0.1–0.4**.
