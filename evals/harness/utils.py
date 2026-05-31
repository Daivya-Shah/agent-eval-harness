from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT_MARKER = "pyproject.toml"


def find_repo_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / REPO_ROOT_MARKER).exists():
            return candidate
    raise FileNotFoundError(
        f"Could not locate repo root (missing {REPO_ROOT_MARKER}) from {current}"
    )


def resolve_repo_path(repo_root: Path, path_str: str) -> Path:
    path = Path(path_str)
    if path.is_absolute():
        return path
    return (repo_root / path).resolve()


def excerpt(text: str, *, max_lines: int = 12, max_chars: int = 2000) -> str:
    if not text.strip():
        return ""
    lines = text.strip().splitlines()
    tail = lines[-max_lines:]
    joined = "\n".join(tail)
    if len(joined) > max_chars:
        return joined[-max_chars:]
    return joined


def path_has_apostrophe(path: Path) -> bool:
    return "'" in str(path)


def detect_vite_path_issue(stdout: str, stderr: str) -> bool:
    combined = f"{stdout}\n{stderr}".lower()
    needles = [
        "failed to load url",
        "does the file exist?",
        "repo's",
        "unexpected token",
    ]
    return any(n in combined for n in needles)
