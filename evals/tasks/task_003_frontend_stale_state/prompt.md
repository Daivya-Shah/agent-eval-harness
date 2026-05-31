# Task: Fix stale frontend state after issue mutations

You are working on **IssueFlow** frontend (`apps/issueflow-frontend`). Users report that after updating an issue from the detail panel, the dashboard sometimes shows **stale data** until they manually refresh the page.

Fix React Query cache behavior so list, filter, and detail views remain consistent after mutations.

## Context

Key files:

- `src/hooks/useIssues.ts` — queries and mutations
- `src/api/queryKeys.ts` — query key structure
- `src/components/IssueDetail.tsx` — detail panel with status/assignee/comment actions
- `src/components/IssueList.tsx` — dashboard list rows
- `src/pages/DashboardPage.tsx` — filters + list + detail orchestration

The app uses **React Query** (`@tanstack/react-query`) and talks to the real backend under `/api`.

## Required behavior

### Status updates

When a user changes issue status from the detail panel:

1. Detail view reflects the new status immediately (badge + fields).
2. Dashboard issue list updates **without** `window.location.reload()`.
3. If the user has an active **status filter**, issues that no longer match should disappear from the list after the mutation succeeds.
4. Query keys must stay structured and predictable (`queryKeys.issues.list(filters)`, `queryKeys.issues.detail(id)`).

### Comments

Adding a comment must append to the detail view comment list after success (via refetch or cache update).

### Error handling

If you use optimistic updates, failed mutations must **roll back** UI state to the last known good server state.

### Non-goals

- Do not fix this by forcing full page reloads.
- Do not bypass React Query with ad-hoc global variables.

## Verification

Visible tests cover detail badge updates and comment appearance. Hidden-style tests check filter consistency, list/detail alignment, rollback, and rapid sequential updates.

## API reference (existing)

- `POST /api/issues/{id}/status` — `{ status }`
- `POST /api/issues/{id}/comments` — `{ author_id, body }`
- `GET /api/issues?status=...` — filtered list
