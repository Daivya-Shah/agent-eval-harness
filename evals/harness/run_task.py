from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from evals.harness.report import write_aggregate_reports
from evals.harness.schemas import AggregateSummary, RunType, SuiteName
from evals.harness.task_loader import TaskLoadError, discover_task_dirs, run_task_grading
from evals.harness.utils import find_repo_root, resolve_repo_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run IssueFlow eval task grading (deterministic test harness)",
    )
    parser.add_argument(
        "--task",
        required=True,
        help="Path to task folder (e.g. evals/tasks/task_001_backend_state_transition)",
    )
    parser.add_argument(
        "--output-dir",
        default="evals/results",
        help="Directory for JSON/Markdown reports (default: evals/results)",
    )
    parser.add_argument(
        "--suite",
        choices=["visible", "hidden", "all"],
        default="all",
        help="Which test suite(s) to run",
    )
    parser.add_argument(
        "--run-type",
        default="golden_reference",
        choices=["golden_reference", "agent_attempt", "baseline"],
        help="Label for this grading run",
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Run task setup_command before tests",
    )
    parser.add_argument(
        "--fail-on-test-failure",
        action="store_true",
        help="Exit with code 1 if any executed test suite fails",
    )
    parser.add_argument(
        "--json-stdout",
        action="store_true",
        help="Print JSON report to stdout",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        repo_root = find_repo_root()
        result = run_task_grading(
            args.task,
            suite=args.suite,  # type: ignore[arg-type]
            run_type=args.run_type,  # type: ignore[arg-type]
            output_dir=args.output_dir,
            repo_root=repo_root,
            run_setup=args.setup,
        )
    except TaskLoadError as exc:
        print(f"HARNESS ERROR: {exc}", file=sys.stderr)
        return 2
    except FileNotFoundError as exc:
        print(f"HARNESS ERROR: {exc}", file=sys.stderr)
        return 2

    out_dir = resolve_repo_path(find_repo_root(), args.output_dir)
    print(f"Task: {result.task_id}")
    print(f"Overall score: {result.overall_score:.2f}")
    print(f"Reports: {out_dir}")

    if args.json_stdout:
        print(json.dumps(result.to_dict(), indent=2))

    if args.fail_on_test_failure:
        failed = False
        if result.visible and not result.visible.passed:
            failed = True
        if result.hidden and not result.hidden.passed:
            failed = True
        if failed:
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
