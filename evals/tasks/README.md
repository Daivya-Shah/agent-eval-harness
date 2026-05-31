# Eval tasks

This directory contains **coding-agent evaluation tasks** for IssueFlow. Each task includes:

- `prompt.md` — agent-facing instructions
- `task.yaml` — metadata and test commands for the eval harness
- `visible_tests/` — smaller checks agents may overfit to
- `hidden_tests/` — deeper hidden-style checks (included in-repo for demo purposes)
- `expected_failures.md` — analysis of weak agent behavior

## Run backend task tests (from repo root)

```powershell
pytest evals/tasks/task_001_backend_state_transition/visible_tests -q -c evals/pytest.ini --rootdir=evals
pytest evals/tasks/task_001_backend_state_transition/hidden_tests -q -c evals/pytest.ini --rootdir=evals
```

Replace `task_001_...` with any backend task id (`task_002`, `task_004`).

## Run frontend task tests (task 003)

From repo root (requires `apps/issueflow-frontend/node_modules`):

```powershell
cd apps/issueflow-frontend
npx vitest run --config vitest.eval-task003.config.ts ../../evals/tasks/task_003_frontend_stale_state/visible_tests
npx vitest run --config vitest.eval-task003.config.ts ../../evals/tasks/task_003_frontend_stale_state/hidden_tests
```

**Note:** Main app tests remain under `apps/issueflow-backend/tests` and `apps/issueflow-frontend` — they are separate from eval task tests.
