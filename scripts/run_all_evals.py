#!/usr/bin/env python3
"""Run all IssueFlow eval tasks and write aggregate summary reports."""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

# Allow running as `python scripts/run_all_evals.py` from repo root
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from evals.harness.report import write_aggregate_reports
from evals.harness.schemas import AggregateSummary
from evals.harness.task_loader import TaskLoadError, discover_task_dirs, run_task_grading
from evals.harness.utils import find_repo_root, resolve_repo_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Run all IssueFlow eval tasks")
    parser.add_argument(
        "--output-dir",
        default="evals/results",
        help="Directory for per-task and aggregate reports",
    )
    parser.add_argument(
        "--run-type",
        default="golden_reference",
        choices=["golden_reference", "agent_attempt", "baseline"],
    )
    parser.add_argument(
        "--fail-on-test-failure",
        action="store_true",
        help="Exit 1 if any task suite fails",
    )
    args = parser.parse_args()

    repo_root = find_repo_root(REPO_ROOT)
    tasks_root = repo_root / "evals" / "tasks"
    output_dir = resolve_repo_path(repo_root, args.output_dir)

    task_dirs = discover_task_dirs(tasks_root)
    if not task_dirs:
        print("HARNESS ERROR: no tasks found under evals/tasks/", file=sys.stderr)
        return 2

    results = []
    total_runtime = 0.0
    failed_tasks: list[str] = []
    harness_error = False

    for task_dir in task_dirs:
        rel = task_dir.relative_to(repo_root)
        print(f"Running {rel}...")
        try:
            grade = run_task_grading(
                task_dir,
                suite="all",
                run_type=args.run_type,
                output_dir=output_dir,
                repo_root=repo_root,
            )
        except TaskLoadError as exc:
            print(f"HARNESS ERROR for {rel}: {exc}", file=sys.stderr)
            harness_error = True
            continue

        results.append(grade)
        if grade.raw_results.get("visible"):
            total_runtime += grade.raw_results["visible"]["runtime_seconds"]
        if grade.raw_results.get("hidden"):
            total_runtime += grade.raw_results["hidden"]["runtime_seconds"]

        task_failed = (grade.visible and not grade.visible.passed) or (
            grade.hidden and not grade.hidden.passed
        )
        if task_failed:
            failed_tasks.append(grade.task_id)

        print(f"  score={grade.overall_score:.2f} visible={'pass' if grade.visible and grade.visible.passed else 'fail'} hidden={'pass' if grade.hidden and grade.hidden.passed else 'fail'}")

    if not results:
        return 2 if harness_error else 1

    avg = sum(r.overall_score for r in results) / len(results)
    summary = AggregateSummary(
        run_type=args.run_type,
        run_timestamp=datetime.now(UTC),
        tasks_run=len(results),
        average_overall_score=avg,
        total_runtime_seconds=total_runtime,
        task_results=results,
        failed_tasks=failed_tasks,
    )
    write_aggregate_reports(summary, output_dir)
    print(f"\nAggregate summary written to {output_dir}")
    print(f"Average score: {avg:.2f} ({len(results)} tasks)")

    if harness_error:
        return 2
    if args.fail_on_test_failure and failed_tasks:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
