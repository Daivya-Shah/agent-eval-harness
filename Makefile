.PHONY: backend frontend test-backend test-frontend eval eval-all setup

REPO_ROOT := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
VENV_PY := $(REPO_ROOT).venv/bin/python
VENV_PIP := $(REPO_ROOT).venv/bin/pip

# Default task for convenience
help:
	@echo "Targets:"
	@echo "  make setup          Create venv and install deps (Unix)"
	@echo "  make backend        Run FastAPI dev server"
	@echo "  make frontend       Run Vite dev server"
	@echo "  make test-backend   Run backend pytest suite"
	@echo "  make test-frontend  Run frontend Vitest suite"
	@echo "  make eval TASK=...  Run one eval task"
	@echo "  make eval-all       Run all eval tasks"

setup:
	./scripts/setup.sh

backend:
	uvicorn app.main:app --reload --app-dir apps/issueflow-backend

frontend:
	cd apps/issueflow-frontend && npm run dev

test-backend:
	pytest apps/issueflow-backend/tests -q

test-frontend:
	cd apps/issueflow-frontend && npm test

eval:
ifndef TASK
	$(error TASK is required, e.g. make eval TASK=task_001_backend_state_transition)
endif
	$(VENV_PY) -m evals.harness.run_task --task evals/tasks/$(TASK) --output-dir=evals/results

eval-all:
	$(VENV_PY) scripts/run_all_evals.py --output-dir=evals/results
