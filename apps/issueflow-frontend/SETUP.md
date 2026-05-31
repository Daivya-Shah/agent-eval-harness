# IssueFlow Frontend — Setup

## Prerequisites

- Node.js 20+
- Backend running on http://127.0.0.1:8000 (see `apps/issueflow-backend/SETUP.md`)

## Install

```powershell
cd apps/issueflow-frontend
npm install
```

## Dev server

Terminal 1 — backend:
```powershell
uvicorn app.main:app --reload --app-dir apps/issueflow-backend
```

Terminal 2 — frontend:
```powershell
cd apps/issueflow-frontend
npm run dev
```

Open http://localhost:5173 (Vite proxies `/api` to the backend).

Tip: use a simple repo path (e.g. `C:\dev\swe-agent-eval-harness`) for reliable Vitest/Playwright runs on Windows.

## Tests

```powershell
npm test
npm run build
npx playwright install chromium
npm run e2e
```

Playwright starts backend + frontend automatically if they are not already running.
