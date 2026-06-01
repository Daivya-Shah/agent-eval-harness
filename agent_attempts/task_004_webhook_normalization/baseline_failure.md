# Task 004 — Baseline failure

## Task summary

Normalize inbound webhook payloads from external systems into IssueFlow issues. Map aliases (`title`/`summary`, `description`/`body`/`details`), normalize priority (`P0`–`P3`, strings), resolve assignees, enforce idempotency on `external_id`, and log low-confidence mappings to `WebhookIngestLog`.

Core logic: `app/services/webhook_normalizer.py`, route: `app/routes/webhooks.py`.

## What a broken baseline might do

- Accept only `{ "title", "description", "priority" }` happy-path keys
- Create a new issue on every POST (no dedup by `external_id`)
- Map priority with a brittle `if priority == "high"` chain
- Silently default unknown assignee to `null` with no log entry
- Return 200 even when payload is mostly empty

## Visible test pattern

| Result | Likely reason |
|--------|----------------|
| **Partial pass** | Standard `title`/`description`/`P1` payload works |
| **Fail** | No `summary`/`body` aliases; duplicate `external_id` creates second row |

Visible tests (`test_visible_webhooks.py`):

- Standard payload with `P1` → `high`
- `summary` + `body` aliases
- Duplicate `external_id` returns same issue with `created: false`

## Hidden-style test pattern

| Result | Likely reason |
|--------|----------------|
| **Most fail** | Validation, date parsing, assignee shapes, audit spam, alias completeness |

Hidden tests in `hidden_tests/test_hidden_webhooks.py`:

- Missing title → 400
- Ambiguous priority (`critical`, `P9`) → 400
- Unknown assignee email → 400
- Invalid/unparseable dates → 400
- Assignee by numeric user id
- Multiple date string formats (`2025/12/01`, date-only ISO)
- Low-confidence missing priority writes `WebhookIngestLog`
- Idempotent retry does not duplicate `webhook_ingested` activity
- Unit test: all title aliases (`issueTitle`, etc.) accepted

## Why this matters

Webhooks are the messiest integration surface. Real payloads use vendor-specific keys, mixed priority schemes, and retries. A happy-path-only normalizer **silently corrupts data** or **duplicates issues** under production load.

## Capability gap revealed

- No **schema tolerance** (aliases)
- No **idempotency key** handling
- No **observability** for ambiguous mappings
- **Fail-open** behavior instead of explicit errors

Harness: low `hidden_tests`, failure modes like *"webhook normalization/idempotency issue"*.
