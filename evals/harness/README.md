# Eval harness

Run one task from repo root:

```powershell
python -m evals.harness.run_task --task evals/tasks/task_001_backend_state_transition --output-dir=evals/results
python -m evals.harness.run_task --task evals/tasks/task_001_backend_state_transition --suite visible
python scripts/run_all_evals.py --output-dir=evals/results
```

On PowerShell, prefer `--output-dir=evals/results` (equals form) to avoid argument parsing issues.

Reports are written to `evals/results/` as JSON + Markdown (`*_golden_reference.*` by default).

Use `--fail-on-test-failure` to exit 1 when suites fail. Harness errors (bad task.yaml) exit 2.
