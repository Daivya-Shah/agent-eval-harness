from __future__ import annotations

from evals.harness.schemas import TaskConfig, TaskGradeResult, TestRunResult
from evals.harness.utils import detect_vite_path_issue, excerpt

DEFAULT_WEIGHTS: dict[str, float] = {
    "visible_tests": 0.25,
    "hidden_tests": 0.35,
    "regression_safety": 0.15,
    "interface_contract": 0.10,
    "determinism": 0.10,
    "code_quality": 0.05,
}


def normalize_scoring_weights(raw: dict[str, float]) -> dict[str, float]:
    """Map task.yaml weights onto harness score categories and normalize to sum=1."""
    mapped = {
        "visible_tests": raw.get("visible_tests", raw.get("correctness", DEFAULT_WEIGHTS["visible_tests"])),
        "hidden_tests": raw.get("hidden_tests", DEFAULT_WEIGHTS["hidden_tests"]),
        "regression_safety": raw.get("regression_safety", DEFAULT_WEIGHTS["regression_safety"]),
        "interface_contract": raw.get("interface_contract", DEFAULT_WEIGHTS["interface_contract"]),
        "determinism": raw.get("determinism", DEFAULT_WEIGHTS["determinism"]),
        "code_quality": raw.get("code_quality", DEFAULT_WEIGHTS["code_quality"]),
    }
    total = sum(mapped.values())
    if total <= 0:
        return DEFAULT_WEIGHTS.copy()
    return {k: v / total for k, v in mapped.items()}


def suite_score(result: TestRunResult) -> float:
    if result.timed_out:
        return 0.0
    if result.total_count and result.total_count > 0 and result.passed_count is not None:
        failed = result.failed_count or 0
        if failed > 0:
            return max(0.0, result.passed_count / result.total_count)
        return 1.0 if result.passed else 0.0
    return 1.0 if result.passed else 0.0


def classify_failure_modes(
    task: TaskConfig,
    visible: TestRunResult | None,
    hidden: TestRunResult | None,
) -> list[str]:
    modes: list[str] = []
    combined = ""
    if visible:
        combined += visible.stdout + visible.stderr
    if hidden:
        combined += hidden.stdout + hidden.stderr
    lower = combined.lower()

    if visible and visible.timed_out:
        modes.append("visible test command timed out")
    if hidden and hidden.timed_out:
        modes.append("hidden-style test command timed out")

    if visible and not visible.passed and not visible.timed_out:
        modes.append("basic functionality broken (visible tests failed)")

    if hidden and not hidden.passed and not hidden.timed_out:
        if visible and visible.passed:
            modes.append("likely overfit to visible tests or missed edge cases")
        else:
            modes.append("hidden-style tests failed")

    any_failed = (
        (visible is not None and not visible.passed)
        or (hidden is not None and not hidden.passed)
    )

    if any_failed and detect_vite_path_issue(combined, ""):
        modes.append("frontend runner path issue (Vite/Vitest cannot load files from apostrophe path)")

    if any_failed:
        if "invalid status transition" in lower or "state_transition" in lower:
            modes.append("issue lifecycle / state transition regression")
        if "sla" in lower or "overdue" in lower or "at_risk" in lower:
            modes.append("SLA deterministic time/boundary issue")
        if "webhook" in lower or "normaliz" in lower or "external_id" in lower:
            modes.append("webhook normalization or idempotency issue")
        if "cache" in lower or "stale" in lower or "react query" in lower:
            modes.append("frontend UI/cache consistency issue")

        for known in task.common_failure_modes:
            if known.lower() in lower:
                modes.append(f"matches task failure mode: {known}")

    # dedupe preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for item in modes:
        if item not in seen:
            seen.add(item)
            unique.append(item)
    return unique


def build_grader_notes(
    visible: TestRunResult | None,
    hidden: TestRunResult | None,
    failure_modes: list[str],
    run_type: str,
) -> str:
    if failure_modes:
        if any("path issue" in m for m in failure_modes):
            return (
                "Harness executed commands but environment blocked frontend test loading. "
                "Use a clean repo path (e.g. C:\\dev\\swe-agent-eval-harness) and re-run."
            )
        return "Solution failed one or more grading suites. See failure_modes and test excerpts."

    prefix = "Golden reference" if run_type == "golden_reference" else "Run"
    parts = []
    if visible:
        parts.append("visible")
    if hidden:
        parts.append("hidden-style")
    joined = " and ".join(parts) if parts else "requested"
    return f"{prefix} passed {joined} tests."


def grade_task(
    task: TaskConfig,
    visible: TestRunResult | None,
    hidden: TestRunResult | None,
    *,
    run_type: str = "golden_reference",
    run_timestamp,
    environment_notes: list[str] | None = None,
) -> TaskGradeResult:
    weights = normalize_scoring_weights(task.scoring_weights)

    visible_score = suite_score(visible) if visible else 0.0
    hidden_score = suite_score(hidden) if hidden else 0.0

    both_pass = (visible.passed if visible else False) and (hidden.passed if hidden else False)
    visible_only = visible is not None and hidden is None
    hidden_only = hidden is not None and visible is None

    regression_score = 1.0 if both_pass else (0.5 if (visible and visible.passed) else 0.0)
    interface_score = visible_score
    determinism_score = hidden_score if hidden else visible_score
    code_quality_score = 1.0 if both_pass else (0.5 if (visible and visible.passed) else 0.0)

    category_scores = {
        "visible_tests": visible_score,
        "hidden_tests": hidden_score,
        "regression_safety": regression_score,
        "interface_contract": interface_score,
        "determinism": determinism_score,
        "code_quality": code_quality_score,
    }

    if visible_only:
        category_scores["hidden_tests"] = 0.0
    if hidden_only:
        category_scores["visible_tests"] = 0.0

    scoring_breakdown = {
        key: category_scores[key] * weights[key] for key in weights
    }
    overall = sum(scoring_breakdown.values())
    overall = max(0.0, min(1.0, overall))

    failure_modes = classify_failure_modes(task, visible, hidden)

    def to_suite_score(result: TestRunResult | None):
        if result is None:
            return None
        from evals.harness.schemas import SuiteScore

        return SuiteScore(
            command=result.command,
            passed=result.passed,
            score=suite_score(result),
            passed_count=result.passed_count,
            failed_count=result.failed_count,
            total_count=result.total_count,
            timed_out=result.timed_out,
            stdout_excerpt=result.stdout_excerpt or excerpt(result.stdout),
            stderr_excerpt=excerpt(result.stderr),
        )

    return TaskGradeResult(
        task_id=task.id,
        task_title=task.title,
        difficulty=task.difficulty,
        run_type=run_type,  # type: ignore[arg-type]
        run_timestamp=run_timestamp,
        overall_score=overall,
        visible=to_suite_score(visible),
        hidden=to_suite_score(hidden),
        scoring_breakdown=scoring_breakdown,
        category_scores=category_scores,
        scoring_weights=weights,
        failure_modes=failure_modes,
        grader_notes=build_grader_notes(visible, hidden, failure_modes, run_type),
        expected_capabilities=task.expected_capabilities,
        common_failure_modes=task.common_failure_modes,
        environment_notes=environment_notes or [],
        raw_results={
            "visible": visible.__dict__ if visible else None,
            "hidden": hidden.__dict__ if hidden else None,
        },
    )
