# IssueFlow / SWE-Agent Eval Harness — Windows setup
# Run from repo root: .\scripts\setup.ps1

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

Write-Host "SWE-Agent Eval Harness setup" -ForegroundColor Cyan
Write-Host "Repo root: $RepoRoot"

if ($RepoRoot -match "'") {
    Write-Host ""
    Write-Host "WARNING: This path contains an apostrophe." -ForegroundColor Yellow
    Write-Host "Vitest/Vite eval tasks may fail here. Prefer C:\dev\swe-agent-eval-harness" -ForegroundColor Yellow
    Write-Host "  subst Z: `"$RepoRoot`"" -ForegroundColor Yellow
    Write-Host ""
}

# Python venv
if (-not (Test-Path ".venv\Scripts\Activate.ps1")) {
    Write-Host "Creating Python venv..."
    python -m venv .venv
} else {
    Write-Host "Python venv already exists."
}

Write-Host "Installing Python dependencies (editable + dev)..."
.\.venv\Scripts\python.exe -m pip install -q --upgrade pip
.\.venv\Scripts\python.exe -m pip install -q -e ".[dev]"

# Frontend
Write-Host "Installing frontend dependencies..."
Push-Location apps\issueflow-frontend
npm install
Pop-Location

Write-Host ""
Write-Host "Setup complete." -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host "  uvicorn app.main:app --reload --app-dir apps/issueflow-backend"
Write-Host "  cd apps\issueflow-frontend; npm run dev"
Write-Host ""
Write-Host "Tests:"
Write-Host "  pytest apps/issueflow-backend/tests -q"
Write-Host "  cd apps\issueflow-frontend; npm test"
Write-Host ""
Write-Host "Evals:"
Write-Host "  python scripts/run_all_evals.py --output-dir=evals/results"
