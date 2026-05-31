# Eval design

How IssueFlow eval tasks are structured, scored, and intended to be used. This repo ships four tasks as a **demonstration benchmark** — hidden-style tests are included in-repo for transparency; production eval systems would typically keep them private.

## What is a task?

A task is a bounded SWE assignment an coding agent (or human) would receive:

| Artifact | Purpose |
|----------|---------|
| `prompt.md` | Natural-language instructions |
| `task.yaml` | Machine-readable config for the harness |
| `visible_tests/` | Smaller test suite (agent-facing in real deployments) |
| `hidden_tests/` | Deeper invariant tests (hidden-style in real deployments) |
| `expected_failures.md` | Grader intent — common weak patches and what hidden tests catch |

Agents modify files listed in `target_files`. The harness runs test commands and produces a score — it does not apply patches automatically today.

## Visible vs hidden-style tests

| | Visible | Hidden-style |
|---|---------|--------------|
| **Size** | Small (2–4 tests per task here) | Larger (5–10 tests) |
| **Focus** | Basic wiring, happy paths | Boundaries, invariants, idempotency, cache coherence |
| **Agent exposure** | Would be shown to agent in production | Would be withheld in production |
| **This repo** | Both included for demo and review |

**Design intent:** visible tests verify the agent understood the prompt at a surface level. Hidden-style tests verify the patch preserves domain invariants an agent often skips when optimizing for visible pass rate.

## Scoring

### Suite level

Each suite command produces:

- `passed` / `failed` boolean (all tests green)
- `passed_count` / `failed_count` / `total_count` when parseable
- Partial credit: `passed_count / total_count` when some tests fail

### Overall score

`score.py` maps `task.yaml` `scoring_weights` onto harness categories, normalizes to sum 1.0, then computes a weighted average of category scores.

Example mapping:

- `correctness` in YAML → `visible_tests` category
- `hidden_tests`, `regression_safety`, `interface_contract`, `determinism`, `code_quality` map directly or use defaults

When both suites pass with no timeouts, golden reference tasks score **1.00**.

### Failure modes

When tests fail, the harness adds heuristic tags from stdout (e.g. `likely overfit to visible tests or missed edge cases`, `issue lifecycle / state transition regression`, `SLA deterministic time/boundary issue`, `frontend UI/cache consistency issue`, `webhook normalization/idempotency issue`).

Task-level `common_failure_modes` in YAML document expected weak patterns for humans; the harness uses keyword heuristics on test output.

## `task.yaml` structure

```yaml
id: task_001_backend_state_transition
title: Backend Issue Status Transition Robustness
description: >
  ...
difficulty: medium
target_files:
  - apps/issueflow-backend/app/services/state_machine.py
  - ...
setup_command: pip install -e ".[dev]"
visible_test_command: pytest evals/tasks/.../visible_tests -q -c evals/pytest.ini --rootdir=evals
hidden_test_command: pytest evals/tasks/.../hidden_tests -q -c evals/pytest.ini --rootdir=evals
scoring_weights:
  correctness: 0.35
  hidden_tests: 0.30
  ...
timeout_seconds: 900
expected_capabilities:
  - state_machine_modeling
common_failure_modes:
  - allows invalid lifecycle jumps
```

Commands run from **repo root** with the caller's environment (venv activated, frontend deps installed for task 003).

## Golden reference runs

The checked-in implementation passes all visible and hidden-style suites. Reports under `evals/results/` with `run_type: golden_reference` establish:

- Harness and tests are wired correctly
- A known-good baseline score (1.00) for comparison
- Example report shape for reviewers

Re-run after changes:

```powershell
python scripts/run_all_evals.py --output-dir=evals/results
```

## Grading future candidate patches

Intended workflow (manual today):

1. Check out or apply agent patch on top of IssueFlow
2. Run setup (`pip install -e ".[dev]"`, `npm install` if frontend touched)
3. Run harness with `--run-type agent_attempt`:
   ```powershell
   python -m evals.harness.run_task --task evals/tasks/task_001_backend_state_transition --run-type agent_attempt --output-dir=evals/results
   ```
4. Compare JSON report to golden reference and read `failure_modes`
5. Cross-check `agent_attempts/` for illustrative weak vs strong patterns

Future automation (not implemented): git worktree sandbox, CI matrix, patch application hook.

---

## Task 1 — Backend state transition robustness

**ID:** `task_001_backend_state_transition`  
**Difficulty:** medium  
**Capability:** State machine modeling, audit logging, datetime invariants, API validation

### Why it exists

Issue lifecycle rules are easy to patch superficially. Agents often hardcode the transitions visible tests exercise while breaking blocked paths, reopen semantics, and audit trails.

### Visible tests (4)

- `open` → `in_progress`
- `in_progress` → `resolved` (+ `resolved_at` set)
- `resolved` → `closed`
- `open` → `closed` returns 400

### Hidden-style tests (7)

- `blocked` → `open` / `in_progress`
- PATCH blocked on closed issues
- Reopen closed via status endpoint
- `resolved_at` set on resolve, cleared on reopen
- Idempotent same-status POST (no audit spam)
- Specific 400 message content
- Activity events include old/new status

### Common weak solution

Inline transition dict in `routes/issues.py` covering only visible paths; sets `resolved_at` but never clears; no audit calls; generic error messages.

### Robust solution must preserve

- Single transition matrix in `state_machine.py`
- crud applies transitions, `resolved_at` via injectable clock, audit once per real change
- PATCH guard vs status reopen distinction
- `StateTransitionError` → HTTP 400 with actionable message

---

## Task 2 — SLA feature correctness

**ID:** `task_002_sla_feature`  
**Difficulty:** medium  
**Capability:** Time-based business logic, timezone-safe datetime, API field exposure

### Why it exists

SLA logic looks like simple thresholds but fails on boundaries, timezones, and terminal statuses. Agents often use `datetime.now()` in routes and mark resolved issues overdue.

### Visible tests (3)

- Urgent issue overdue after 24h (fixed `now`)
- Young high-priority issue healthy
- Resolved issue → SLA `closed` via API

### Hidden-style tests (7)

- Exact overdue boundary instant
- One second before deadline not overdue
- `at_risk` at exactly 80% elapsed
- Naive `created_at` treated as UTC
- Timezone-aware datetime normalized
- Low priority 14-day window
- Closed issue never overdue regardless of age

### Common weak solution

Inline SLA in `routes/issues.py` with `datetime.now()`; urgent-only thresholds; no `at_risk` band.

### Robust solution must preserve

- Pure `compute_sla_status(issue, now=None)` in `sla.py`
- UTC normalization, priority → hours map, terminal status short-circuit
- `sla_status` on list/detail/create responses

---

## Task 3 — Frontend stale state and optimistic updates

**ID:** `task_003_frontend_stale_state`  
**Difficulty:** hard  
**Capability:** React Query cache management, UI consistency, mutation error handling

### Why it exists

Detail panels update easily; dashboard lists and active filters do not. Agents patch one component or use `window.location.reload()` instead of modeling shared server state.

### Visible tests (2)

- Status select triggers status mutation (mocked hook)
- Comment form calls add-comment mutation

Visible tests **do not** assert list cache coherence — by design.

### Hidden-style tests (5)

- List cache updated + lists invalidated after status change
- Detail and list caches aligned
- Comment mutation invalidates detail query
- No `window.location.reload` in mutation hooks
- Rapid sequential status updates without errors

### Common weak solution

Local `useState` in `IssueDetail.tsx`; invalidate only detail query; wrong query key strings.

### Robust solution must preserve

- Central `queryKeys` module
- Mutations patch list prefix + detail, then invalidate for refetch
- Filter views correct after invalidation (issues leave `status=open` filter when moved)

---

## Task 4 — Webhook normalization and idempotency

**ID:** `task_004_webhook_normalization`  
**Difficulty:** hard  
**Capability:** Schema normalization, validation, idempotency, integration hardening

### Why it exists

Real webhook payloads use inconsistent field names, priority codes, and retries. Happy-path mappers duplicate issues and hide data quality problems.

### Visible tests (3)

- Standard payload with `P1` → `high`
- `summary` + `body` aliases
- Duplicate `external_id` returns existing issue (`created: false`)

### Hidden-style tests (10)

- Missing title → 400
- Ambiguous priority (`critical`, `P9`) → 400
- Unknown assignee → 400
- Invalid date → 400
- Assignee by numeric user id
- Multiple date formats
- Low-confidence missing priority → `WebhookIngestLog` row
- Idempotent retry does not spam webhook activity
- Unit: all title aliases accepted
- Unit: ambiguous priority rejected in normalizer

### Common weak solution

Map only `title`/`description`; idempotency lookup added for visible test but validation/logging missing; strict ISO date parsing only.

### Robust solution must preserve

- Normalizer with full alias and priority maps
- Route: lookup by `external_id`, validate assignees, parse flexible dates
- Ingest log for low-confidence cases
- Single audit event per created issue, not per retry

---

## Related docs

- [ARCHITECTURE.md](ARCHITECTURE.md) — implementation map
- [FAILURE_ANALYSIS.md](FAILURE_ANALYSIS.md) — sample failure narratives
- [evals/tasks/README.md](evals/tasks/README.md) — task folder layout
