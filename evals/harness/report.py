from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from evals.harness.schemas import AggregateSummary, TaskGradeResult


def write_json_report(result: TaskGradeResult, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result.to_dict(), indent=2), encoding="utf-8")


def write_markdown_report(result: TaskGradeResult, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = [
        f"# Eval Report: {result.task_title}",
        "",
        f"- **Task ID:** `{result.task_id}`",
        f"- **Difficulty:** {result.difficulty}",
        f"- **Run type:** `{result.run_type}`",
        f"- **Run timestamp:** {result.run_timestamp.isoformat()}",
        f"- **Overall score:** **{result.overall_score:.2f}**",
        "",
        "## Scoring breakdown (weighted contributions)",
        "",
        "| Category | Category score | Weight | Contribution |",
        "|----------|----------------|--------|--------------|",
    ]

    for category, contribution in result.scoring_breakdown.items():
        cat_score = result.category_scores.get(category, 0.0)
        weight = result.scoring_weights.get(category, 0.0)
        lines.append(
            f"| {category} | {cat_score:.2f} | {weight:.2f} | {contribution:.2f} |"
        )

    lines.extend(["", "## Test suites", ""])

    for label, suite in [("Visible", result.visible), ("Hidden-style", result.hidden)]:
        if suite is None:
            lines.append(f"### {label}\n\n_Not run._\n")
            continue
        status = "PASS" if suite.passed else "FAIL"
        counts = ""
        if suite.total_count is not None:
            counts = f" ({suite.passed_count or 0}/{suite.total_count} tests)"
        lines.extend(
            [
                f"### {label} — {status}{counts}",
                "",
                f"- **Command:** `{suite.command}`",
                f"- **Suite score:** {suite.score:.2f}",
                f"- **Timed out:** {suite.timed_out}",
                "",
                "**Stdout excerpt**",
                "```",
                suite.stdout_excerpt or "(empty)",
                "```",
                "",
            ]
        )
        if suite.stderr_excerpt:
            lines.extend(
                [
                    "**Stderr excerpt**",
                    "```",
                    suite.stderr_excerpt,
                    "```",
                    "",
                ]
            )

    if result.failure_modes:
        lines.append("## Detected failure modes")
        lines.append("")
        for mode in result.failure_modes:
            lines.append(f"- {mode}")
        lines.append("")

    lines.extend(["## Grader notes", "", result.grader_notes, ""])

    if result.environment_notes:
        lines.extend(["## Environment notes", ""])
        for note in result.environment_notes:
            lines.append(f"- {note}")
        lines.append("")

    lines.extend(["## Expected capabilities", ""])
    for cap in result.expected_capabilities:
        lines.append(f"- {cap}")
    lines.append("")

    lines.extend(["## Common failure modes (from task.yaml)", ""])
    for mode in result.common_failure_modes:
        lines.append(f"- {mode}")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def report_basename(task_id: str, run_type: str) -> str:
    return f"{task_id}_{run_type}"


def write_aggregate_reports(summary: AggregateSummary, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "aggregate_summary.json"
    md_path = output_dir / "aggregate_summary.md"

    json_path.write_text(json.dumps(summary.to_dict(), indent=2), encoding="utf-8")

    lines = [
        "# IssueFlow Eval Aggregate Summary",
        "",
        f"- **Run type:** `{summary.run_type}`",
        f"- **Run timestamp:** {summary.run_timestamp.isoformat()}",
        f"- **Tasks run:** {summary.tasks_run}",
        f"- **Average overall score:** **{summary.average_overall_score:.2f}**",
        f"- **Total runtime:** {summary.total_runtime_seconds:.1f}s",
        "",
        "## Per-task results",
        "",
        "| Task | Score | Visible | Hidden |",
        "|------|-------|---------|--------|",
    ]

    for result in summary.task_results:
        vis = "pass" if result.visible and result.visible.passed else "fail"
        hid = "pass" if result.hidden and result.hidden.passed else "fail"
        if result.visible is None:
            vis = "—"
        if result.hidden is None:
            hid = "—"
        lines.append(
            f"| `{result.task_id}` | {result.overall_score:.2f} | {vis} | {hid} |"
        )

    if summary.failed_tasks:
        lines.extend(["", "## Failed tasks", ""])
        for task_id in summary.failed_tasks:
            lines.append(f"- `{task_id}`")

    lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")
