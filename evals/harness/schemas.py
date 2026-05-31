from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal

RunType = Literal["golden_reference", "agent_attempt", "baseline"]
SuiteName = Literal["visible", "hidden", "all"]


@dataclass
class TaskConfig:
    id: str
    title: str
    description: str
    difficulty: str
    target_files: list[str]
    setup_command: str | None
    visible_test_command: str
    hidden_test_command: str
    scoring_weights: dict[str, float]
    timeout_seconds: int
    expected_capabilities: list[str]
    common_failure_modes: list[str]
    task_dir: str


@dataclass
class TestRunResult:
    suite: Literal["visible", "hidden"]
    command: str
    exit_code: int
    stdout: str
    stderr: str
    runtime_seconds: float
    timed_out: bool
    passed: bool
    passed_count: int | None = None
    failed_count: int | None = None
    total_count: int | None = None
    parse_notes: str | None = None

    @property
    def stdout_excerpt(self) -> str:
        lines = [ln.strip() for ln in self.stdout.strip().splitlines() if ln.strip()]
        return lines[-1] if lines else ""


@dataclass
class SuiteScore:
    command: str
    passed: bool
    score: float
    passed_count: int | None
    failed_count: int | None
    total_count: int | None
    timed_out: bool
    stdout_excerpt: str
    stderr_excerpt: str


@dataclass
class TaskGradeResult:
    task_id: str
    task_title: str
    difficulty: str
    run_type: RunType
    run_timestamp: datetime
    overall_score: float
    visible: SuiteScore | None
    hidden: SuiteScore | None
    scoring_breakdown: dict[str, float]
    category_scores: dict[str, float]
    scoring_weights: dict[str, float]
    failure_modes: list[str]
    grader_notes: str
    expected_capabilities: list[str]
    common_failure_modes: list[str]
    harness_errors: list[str] = field(default_factory=list)
    environment_notes: list[str] = field(default_factory=list)
    raw_results: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        def suite_dict(s: SuiteScore | None) -> dict[str, Any] | None:
            if s is None:
                return None
            return {
                "command": s.command,
                "passed": s.passed,
                "score": round(s.score, 4),
                "passed_count": s.passed_count,
                "failed_count": s.failed_count,
                "total_count": s.total_count,
                "timed_out": s.timed_out,
                "stdout_excerpt": s.stdout_excerpt,
                "stderr_excerpt": s.stderr_excerpt,
            }

        return {
            "task_id": self.task_id,
            "task_title": self.task_title,
            "difficulty": self.difficulty,
            "run_type": self.run_type,
            "run_timestamp": self.run_timestamp.isoformat(),
            "overall_score": round(self.overall_score, 4),
            "visible": suite_dict(self.visible),
            "hidden": suite_dict(self.hidden),
            "scoring_breakdown": {k: round(v, 4) for k, v in self.scoring_breakdown.items()},
            "category_scores": {k: round(v, 4) for k, v in self.category_scores.items()},
            "scoring_weights": self.scoring_weights,
            "failure_modes": self.failure_modes,
            "grader_notes": self.grader_notes,
            "expected_capabilities": self.expected_capabilities,
            "common_failure_modes": self.common_failure_modes,
            "harness_errors": self.harness_errors,
            "environment_notes": self.environment_notes,
        }


@dataclass
class AggregateSummary:
    run_type: RunType
    run_timestamp: datetime
    tasks_run: int
    average_overall_score: float
    total_runtime_seconds: float
    task_results: list[TaskGradeResult]
    failed_tasks: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_type": self.run_type,
            "run_timestamp": self.run_timestamp.isoformat(),
            "tasks_run": self.tasks_run,
            "average_overall_score": round(self.average_overall_score, 4),
            "total_runtime_seconds": round(self.total_runtime_seconds, 2),
            "failed_tasks": self.failed_tasks,
            "tasks": [
                {
                    "task_id": r.task_id,
                    "task_title": r.task_title,
                    "overall_score": round(r.overall_score, 4),
                    "visible_passed": r.visible.passed if r.visible else None,
                    "hidden_passed": r.hidden.passed if r.hidden else None,
                }
                for r in self.task_results
            ],
        }
