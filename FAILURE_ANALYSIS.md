# Failure analysis

Summary of the `agent_attempts/` folder and how to use harness reports when reviewing coding-agent patches.

## Why failure analysis exists

Pass/fail scores alone do not explain *why* a patch is weak. Eval engineering needs narratives that connect:

- what the agent changed
- which tests passed and which failed
- which invariants were violated
- what capability gap that implies

The harness produces structured grades; `agent_attempts/` provides illustrative weak vs strong patterns aligned with each task's `expected_failures.md`.

## Common coding-agent failure patterns

| Pattern | Symptom | Example in this repo |
|---------|---------|----------------------|
| **Visible-test overfitting** | Visible green, hidden red | Task 001: only `open→in_progress→resolved→closed` implemented |
| **Symptom patching vs invariants** | Route-layer hacks, no shared service | Task 002: SLA math inline in `routes/issues.py` |
| **Missing lifecycle edge cases** | Happy path works, reopen/blocked broken | Task 001: `resolved_at` not cleared on reopen |
| **Flaky / non-deterministic time** | Boundary tests fail intermittently | Task 002: `datetime.now()` instead of injectable `now` |
| **Stale frontend caches** | Detail correct, list wrong | Task 003: detail-only invalidation |
| **Idempotency failures** | Retries create duplicates or audit spam | Task 004: second POST creates new issue or extra activity |
| **Weak validation of messy inputs** | Silent defaults on bad data | Task 004: ambiguous priority → `medium` without log |

## Task-by-task examples

Detailed notes live in each task folder under `agent_attempts/`:

| Task | Folder | Weak pattern highlight |
|------|--------|--------------------------|
| 001 State transitions | [task_001_backend_state_transition/](agent_attempts/task_001_backend_state_transition/) | Inline `ALLOWED` dict in routes; no audit; no blocked transitions |
| 002 SLA | [task_002_sla_feature/](agent_attempts/task_002_sla_feature/) | `datetime.now()` in handler; no `at_risk`; resolved marked overdue |
| 003 Frontend cache | [task_003_frontend_stale_state/](agent_attempts/task_003_frontend_stale_state/) | Local state in detail; visible mock tests pass; hidden cache tests fail |
| 004 Webhooks | [task_004_webhook_normalization/](agent_attempts/task_004_webhook_normalization/) | Partial aliases; idempotency for visible test only; no ingest log |

Each folder contains:

- `baseline_failure.md` — broken starting point
- `weak_agent_attempt.md` — plausible overfit patch
- `strong_agent_attempt.md` — invariant-preserving approach (matches golden impl)
- `diff_summary.md` — files touched, reviewer checklist, grader catch

Start with [agent_attempts/README.md](agent_attempts/README.md) for methodology.

## How harness reports make failures inspectable

After running:

```powershell
python -m evals.harness.run_task --task evals/tasks/task_001_backend_state_transition --output-dir=evals/results --run-type agent_attempt
```

Inspect `evals/results/task_001_backend_state_transition_agent_attempt.json`:

| Field | Use |
|-------|-----|
| `overall_score` | Weighted 0–1 grade |
| `visible` / `hidden` | Per-suite pass, counts, stdout excerpts |
| `scoring_breakdown` | Category weights applied |
| `category_scores` | visible_tests, hidden_tests, determinism, … |
| `failure_modes` | Heuristic tags from test output |
| `common_failure_modes` | Copied from task.yaml for context |

Markdown sibling (`.md`) gives a quick human summary.

Aggregate runs (`scripts/run_all_evals.py`) write `evals/results/aggregate_summary.json` — compare `average_overall_score` and `failed_tasks` to golden reference (**1.00**, none failed).

### Reading a suspicious pass

If `visible.passed == true` and `hidden.passed == false`:

1. Read `failure_modes` — often includes *"likely overfit to visible tests or missed edge cases"*
2. Open hidden test stdout excerpt in the JSON report
3. Match failing assertion to `expected_failures.md` and `agent_attempts/*/weak_agent_attempt.md`
4. Check whether patch touched `target_files` in the service layer or only routes/UI

### Reading environment failures

If failure modes mention **Vite/Vitest path issues**, the repo path may contain apostrophes (common on Windows). Work from `C:\dev\agent-eval-harness` or use `subst` — documented in README.

## Reviewer workflow

1. Read task `prompt.md` and `expected_failures.md`
2. Skim agent diff (or notes in `agent_attempts/`)
3. Run harness with `--run-type agent_attempt`
4. Compare JSON to golden reference report for same task
5. Use `diff_summary.md` checklist before approving a patch

## Future work

- **Run real agent patches** — apply transcripts/diffs and store actual stdout as artifacts (clearly labeled)
- **Git worktree sandboxing** — isolate each attempt without polluting working tree
- **CI** — matrix of backend tests, frontend tests, and eval harness on push
- **Linter / static-analysis score** — extend `code_quality` category beyond placeholder weight
- **Docker isolation** — reproducible env for agents and graders
- **More tasks across unfamiliar repos** — generalize harness beyond IssueFlow

---

## Related docs

- [EVAL_DESIGN.md](EVAL_DESIGN.md) — task and scoring design
- [ARCHITECTURE.md](ARCHITECTURE.md) — harness implementation
- [evals/results/aggregate_summary.md](evals/results/aggregate_summary.md) — golden reference summary
