# IssueFlow Backend — Setup

## Prerequisites

- Python 3.11+
- pip

## Recommended repo path

Clone or work from a simple path without special characters, e.g. `C:\dev\swe-agent-eval-harness`. Some Windows tooling (Vite/Vitest) can break when paths contain apostrophes.

## Install (Windows PowerShell)

```powershell
cd C:\dev\swe-agent-eval-harness
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## Install (macOS/Linux)

```bash
cd swe-agent-eval-harness
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Run backend

```powershell
# From repo root with venv activated
uvicorn app.main:app --reload --app-dir apps/issueflow-backend
```

If PowerShell has trouble with your path, map a drive letter:

```powershell
subst Z: "C:\dev\swe-agent-eval-harness"
Z:
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --app-dir apps/issueflow-backend
```

API: http://127.0.0.1:8000  
Docs: http://127.0.0.1:8000/docs  
Health: http://127.0.0.1:8000/health

## Run tests

```powershell
pytest apps/issueflow-backend/tests -q
```

## Reset database

Delete `apps/issueflow-backend/issueflow.db` and restart the server to re-seed.
