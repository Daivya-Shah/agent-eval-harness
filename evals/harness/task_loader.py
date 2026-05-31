from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import yaml

from evals.harness.report import report_basename, write_json_report, write_markdown_report
from evals.harness.schemas import RunType, SuiteName, TaskConfig, TaskGradeResult
from evals.harness.score import grade_task
from evals.harness.test_runner import run_test_command
from evals.harness.utils import find_repo_root, path_has_apostrophe, resolve_repo_path

REQUIRED_FIELDS = (
    "id",
    "title",
    "description",
    "difficulty",
    "target_files",
    "visible_test_command",
    "hidden_test_command",
    "scoring_weights",
    "timeout_seconds",
    "expected_capabilities",
    "common_failure_modes",
)


class TaskLoadError(ValueError):
    pass


def load_task(task_path: str | Path, repo_root: Path | None = None) -> TaskConfig:
    root = repo_root or find_repo_root()
    task_dir = resolve_repo_path(root, str(task_path))
    if task_dir.is_file():
        task_dir = task_dir.parent

    yaml_path = task_dir / "task.yaml"
    if not yaml_path.exists():
        raise TaskLoadError(f"Missing task.yaml at {yaml_path}")

    with yaml_path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    if not isinstance(data, dict):
        raise TaskLoadError(f"task.yaml must be a mapping: {yaml_path}")

    missing = [field for field in REQUIRED_FIELDS if field not in data]
    if missing:
        raise TaskLoadError(f"task.yaml missing required fields {missing}: {yaml_path}")

    scoring_weights = data["scoring_weights"]
    if not isinstance(scoring_weights, dict):
        raise TaskLoadError("scoring_weights must be a mapping")

    return TaskConfig(
        id=str(data["id"]),
        title=str(data["title"]),
        description=str(data["description"]).strip(),
        difficulty=str(data["difficulty"]),
        target_files=[str(p) for p in data["target_files"]],
        setup_command=str(data["setup_command"]) if data.get("setup_command") else None,
        visible_test_command=str(data["visible_test_command"]),
        hidden_test_command=str(data["hidden_test_command"]),
        scoring_weights={str(k): float(v) for k, v in scoring_weights.items()},
        timeout_seconds=int(data["timeout_seconds"]),
        expected_capabilities=[str(c) for c in data["expected_capabilities"]],
        common_failure_modes=[str(m) for m in data["common_failure_modes"]],
        task_dir=str(task_dir),
    )


def run_task_grading(
    task_path: str | Path,
    *,
    suite: SuiteName = "all",
    run_type: RunType = "golden_reference",
    output_dir: str | Path | None = None,
    repo_root: Path | None = None,
    run_setup: bool = False,
) -> TaskGradeResult:
    root = repo_root or find_repo_root()
    task = load_task(task_path, root)
    environment_notes: list[str] = []

    if path_has_apostrophe(root) and "vitest" in (
        task.visible_test_command + task.hidden_test_command
    ).lower():
        environment_notes.append(
            "Repo path contains an apostrophe; Vite/Vitest may fail to load frontend tests. "
            "Use a clean path such as C:\\dev\\swe-agent-eval-harness for task_003."
        )

    if run_setup and task.setup_command:
        setup_result = run_test_command(
            task.setup_command,
            suite="visible",
            cwd=str(root),
            timeout_seconds=task.timeout_seconds,
        )
        if not setup_result.passed:
            environment_notes.append(f"Setup command failed: {task.setup_command}")

    visible_result = None
    hidden_result = None

    if suite in ("all", "visible"):
        visible_result = run_test_command(
            task.visible_test_command,
            suite="visible",
            cwd=str(root),
            timeout_seconds=task.timeout_seconds,
        )

    if suite in ("all", "hidden"):
        hidden_result = run_test_command(
            task.hidden_test_command,
            suite="hidden",
            cwd=str(root),
            timeout_seconds=task.timeout_seconds,
        )

    grade = grade_task(
        task,
        visible_result,
        hidden_result,
        run_type=run_type,
        run_timestamp=datetime.now(UTC),
        environment_notes=environment_notes,
    )

    if output_dir is not None:
        out = resolve_repo_path(root, str(output_dir))
        base = report_basename(task.id, run_type)
        write_json_report(grade, out / f"{base}.json")
        write_markdown_report(grade, out / f"{base}.md")

    return grade


def discover_task_dirs(tasks_root: Path) -> list[Path]:
    if not tasks_root.exists():
        return []
    dirs = []
    for child in sorted(tasks_root.iterdir()):
        if child.is_dir() and (child / "task.yaml").exists():
            dirs.append(child)
    return dirs
