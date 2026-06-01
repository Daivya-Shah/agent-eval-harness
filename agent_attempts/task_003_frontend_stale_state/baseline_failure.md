# Task 003 — Baseline failure

## Task summary

Fix stale UI after mutations: status updates and comments from the issue detail panel must reflect in the dashboard list and active filters without full page reload. Target React Query hooks and cache keys.

Key files: `src/hooks/useIssues.ts`, `src/api/queryKeys.ts`, `src/components/IssueDetail.tsx`, `src/pages/DashboardPage.tsx`.

## What a broken baseline might do

- Detail panel fetches issue; list fetches separately — **no cache coordination**
- After status change, only local component state updates in the modal
- Dashboard list shows stale status until manual browser refresh
- Filter `status=open` still shows issue after moving to `in_progress`

## Visible test pattern

| Result | Likely reason |
|--------|----------------|
| **May pass** | Visible tests mock hooks and assert mutation **called** — not real cache |
| **Fail** | If detail component does not wire status select to mutation |

Visible eval tests (`detail_visible.test.tsx`) verify mutation invocation, not live list sync.

## Hidden-style test pattern

| Result | Likely reason |
|--------|----------------|
| **Fail** | Cache not updated/invalidated |

Hidden tests (`cache_hidden.test.tsx`):

- List cache + invalidation after status mutation
- Detail/list status alignment
- Comment mutation invalidates detail query
- No `window.location.reload`
- Rapid sequential mutations

## Why this matters

Users trust the dashboard as source of truth. Stale rows after an action look like data loss and erode confidence — common real-world bug in React SPAs with naive data fetching.

## Capability gap revealed

- Treating React Query as **fetch-on-mount** only
- No **query key discipline**
- No model of **filter-dependent list queries**
- Confusing **component state** with **server state**

Harness: low `hidden_tests`, failure mode *"frontend UI/cache consistency issue"*.
