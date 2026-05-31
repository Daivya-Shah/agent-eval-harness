from __future__ import annotations

import os
import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from evals.harness.schemas import TestRunResult


@dataclass
class ParsedTestCounts:
    passed: int | None
    failed: int | None
    total: int | None
    notes: str | None = None


PYTEST_SUMMARY = re.compile(
    r"(?:(\d+) failed,\s*)?(?:(\d+) passed)(?:,\s*(\d+) skipped)?(?:,\s*(\d+) error)?",
    re.IGNORECASE,
)
PYTEST_FAILED_ONLY = re.compile(r"(\d+) failed", re.IGNORECASE)
PYTEST_PASSED_ONLY = re.compile(r"(\d+) passed", re.IGNORECASE)

VITEST_SUMMARY = re.compile(
    r"Tests\s+(?:(\d+) failed\s*\|\s*)?(\d+) passed(?:\s*\|\s*(\d+) failed)?(?:\s*\((\d+)\))?",
    re.IGNORECASE,
)
VITEST_FILES = re.compile(
    r"Test Files\s+(?:(\d+) failed\s*\|\s*)?(\d+) passed(?:\s*\((\d+)\))?",
    re.IGNORECASE,
)


def parse_test_output(stdout: str, stderr: str, command: str) -> ParsedTestCounts:
    text = f"{stdout}\n{stderr}"
    lower_cmd = command.lower()

    if "vitest" in lower_cmd or "jest" in lower_cmd:
        return _parse_vitest(text)
    return _parse_pytest(text)


def _parse_pytest(text: str) -> ParsedTestCounts:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    for line in reversed(lines):
        lower = line.lower()
        if "passed" in lower or "failed" in lower or "error" in lower:
            match = PYTEST_SUMMARY.search(line)
            if match:
                failed = int(match.group(1) or 0)
                passed = int(match.group(2) or 0)
                errors = int(match.group(4) or 0)
                total = passed + failed + errors
                return ParsedTestCounts(
                    passed=passed,
                    failed=failed + errors,
                    total=total,
                    notes=f"parsed pytest summary: {line}",
                )
            failed_match = PYTEST_FAILED_ONLY.search(line)
            passed_match = PYTEST_PASSED_ONLY.search(line)
            if failed_match or passed_match:
                failed = int(failed_match.group(1)) if failed_match else 0
                passed = int(passed_match.group(1)) if passed_match else 0
                return ParsedTestCounts(
                    passed=passed,
                    failed=failed,
                    total=passed + failed,
                    notes=f"parsed pytest partial: {line}",
                )
    return ParsedTestCounts(passed=None, failed=None, total=None, notes="could not parse pytest output")


def _parse_vitest(text: str) -> ParsedTestCounts:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    for line in reversed(lines):
        lower = line.lower()
        if lower.startswith("tests"):
            match = VITEST_SUMMARY.search(line)
            if match:
                failed_a = int(match.group(1) or 0)
                passed = int(match.group(2) or 0)
                failed_b = int(match.group(3) or 0)
                total = int(match.group(4) or (passed + failed_a + failed_b))
                failed = failed_a + failed_b
                return ParsedTestCounts(
                    passed=passed,
                    failed=failed,
                    total=total,
                    notes=f"parsed vitest summary: {line}",
                )
        if lower.startswith("test files"):
            match = VITEST_FILES.search(line)
            if match:
                failed = int(match.group(1) or 0)
                passed = int(match.group(2) or 0)
                total = int(match.group(3) or (passed + failed))
                return ParsedTestCounts(
                    passed=passed,
                    failed=failed,
                    total=total,
                    notes=f"parsed vitest files summary: {line}",
                )
    return ParsedTestCounts(passed=None, failed=None, total=None, notes="could not parse vitest output")


def run_test_command(
    command: str,
    *,
    suite: str,
    cwd: str,
    timeout_seconds: int,
) -> TestRunResult:
    start = time.perf_counter()
    timed_out = False
    stdout = ""
    stderr = ""
    exit_code = 1

    env = os.environ.copy()
    repo_root = Path(cwd)
    venv_scripts = repo_root / ".venv" / "Scripts"
    venv_bin = repo_root / ".venv" / "bin"
    if venv_scripts.exists():
        env["PATH"] = str(venv_scripts) + os.pathsep + env.get("PATH", "")
    elif venv_bin.exists():
        env["PATH"] = str(venv_bin) + os.pathsep + env.get("PATH", "")

    try:
        completed = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            env=env,
        )
        stdout = completed.stdout or ""
        stderr = completed.stderr or ""
        exit_code = completed.returncode
    except subprocess.TimeoutExpired as exc:
        timed_out = True
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        stderr = (stderr + "\nHARNESS: command timed out").strip()
        exit_code = 124
    except OSError as exc:
        stderr = f"HARNESS: failed to execute command: {exc}"
        exit_code = 127

    runtime = time.perf_counter() - start
    parsed = parse_test_output(stdout, stderr, command)

    if timed_out:
        passed = False
    elif parsed.total is not None and parsed.total > 0:
        passed = exit_code == 0 and (parsed.failed or 0) == 0
    else:
        passed = exit_code == 0

    return TestRunResult(
        suite=suite,  # type: ignore[arg-type]
        command=command,
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
        runtime_seconds=runtime,
        timed_out=timed_out,
        passed=passed,
        passed_count=parsed.passed,
        failed_count=parsed.failed,
        total_count=parsed.total,
        parse_notes=parsed.notes,
    )
