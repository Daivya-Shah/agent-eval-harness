# Agent attempt analysis (sample / simulated)

This folder contains **sample, simulated coding-agent attempt analysis** for the IssueFlow eval tasks. These are **not** logs from real frontier model runs unless explicitly noted elsewhere with actual artifacts.

## Why this exists

Eval engineering is not just writing tests — it is understanding **how agents fail** and **why shallow grading misleads**. These notes document:

- what a broken baseline might look like
- how a weak agent patch can pass visible tests but fail hidden-style checks
- what a robust solution preserves
- how reviewers and the harness catch regressions

The golden reference implementation in this repo **passes all four tasks** (average score **1.00** in `evals/results/aggregate_summary.json`). The scenarios here describe **hypothetical or intentionally incomplete solutions** for demonstration and interview discussion.

## Visible vs hidden-style tests

| Layer | Purpose |
|-------|---------|
| **Visible tests** | Smaller, agent-facing checks — easy to overfit |
| **Hidden-style tests** | Deeper invariants, boundaries, idempotency, cache coherence — included in-repo for this demo benchmark |

An agent that only reads visible tests may implement the happy path in `routes/issues.py` or patch one React Query hook while missing lifecycle rules, SLA boundaries, or webhook idempotency.

## How the harness helps

The eval harness (`evals/harness/`) runs both suites, parses pytest/Vitest output, scores deterministically, and writes JSON/Markdown reports under `evals/results/`. When a simulated weak solution fails, you would see:

- lower `hidden_tests` category score
- `failure_modes` like *"likely overfit to visible tests or missed edge cases"*
- stdout excerpts pointing to specific failing assertions

## How to use this folder

When reviewing this project (e.g. for Mechanize-style eval work):

1. Read the task prompt in `evals/tasks/<task>/prompt.md`
2. Skim `expected_failures.md` for grader intent
3. Read **weak** vs **strong** attempt notes here
4. Run the harness against your own patch:  
   `python -m evals.harness.run_task --task evals/tasks/task_001_backend_state_transition --output-dir=evals/results`

## Task index

| Folder | Focus |
|--------|--------|
| `task_001_backend_state_transition/` | Issue lifecycle, `resolved_at`, audit events |
| `task_002_sla_feature/` | Deterministic SLA windows, time boundaries |
| `task_003_frontend_stale_state/` | React Query cache, filters, mutations |
| `task_004_webhook_normalization/` | Messy payloads, idempotency, ingest logs |

All folder names match eval tasks under `evals/tasks/`.
