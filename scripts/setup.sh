#!/usr/bin/env bash
# IssueFlow / SWE-Agent Eval Harness — macOS/Linux setup
# Run from repo root: ./scripts/setup.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo "SWE-Agent Eval Harness setup"
echo "Repo root: $REPO_ROOT"

# Python venv
if [[ ! -f .venv/bin/activate ]]; then
  echo "Creating Python venv..."
  python3 -m venv .venv
else
  echo "Python venv already exists."
fi

echo "Installing Python dependencies (editable + dev)..."
.venv/bin/python -m pip install -q --upgrade pip
.venv/bin/python -m pip install -q -e ".[dev]"

# Frontend
echo "Installing frontend dependencies..."
(cd apps/issueflow-frontend && npm install)

echo ""
echo "Setup complete."
echo ""
echo "Next steps:"
echo "  source .venv/bin/activate"
echo "  uvicorn app.main:app --reload --app-dir apps/issueflow-backend"
echo "  cd apps/issueflow-frontend && npm run dev"
echo ""
echo "Tests:"
echo "  pytest apps/issueflow-backend/tests -q"
echo "  cd apps/issueflow-frontend && npm test"
echo ""
echo "Evals:"
echo "  python scripts/run_all_evals.py --output-dir=evals/results"
