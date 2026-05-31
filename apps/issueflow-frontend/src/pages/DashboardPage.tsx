import { useMemo, useState } from "react";

import type { Issue, IssueFilters } from "@/api/types";
import { IssueDetailPanel } from "@/components/IssueDetail";
import { IssueFiltersBar } from "@/components/IssueFilters";
import { IssueList } from "@/components/IssueList";
import { useCreateIssue, useIssues, useUsers } from "@/hooks/useIssues";

export function DashboardPage() {
  const [filters, setFilters] = useState<IssueFilters>({});
  const [selectedIssueId, setSelectedIssueId] = useState<number | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newTitle, setNewTitle] = useState("");

  const usersQuery = useUsers();
  const issuesQuery = useIssues(filters);
  const createIssue = useCreateIssue();

  const issues = useMemo(() => issuesQuery.data?.items ?? [], [issuesQuery.data]);
  const total = issuesQuery.data?.total ?? 0;

  const handleSelectIssue = (issue: Issue) => {
    setSelectedIssueId(issue.id);
  };

  const handleCreateIssue = async () => {
    if (!newTitle.trim()) return;
    await createIssue.mutateAsync({ title: newTitle.trim() });
    setNewTitle("");
    setShowCreateForm(false);
  };

  return (
    <div className="min-h-screen">
      <header className="border-b border-slate-800 bg-slate-950/80">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-6 py-5">
          <div>
            <p className="text-xs uppercase tracking-[0.2em] text-indigo-400">IssueFlow</p>
            <h1 className="text-2xl font-semibold text-slate-100">Engineering issue dashboard</h1>
          </div>
          <button
            type="button"
            data-testid="create-issue-toggle"
            onClick={() => setShowCreateForm((v) => !v)}
            className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500"
          >
            New issue
          </button>
        </div>
      </header>

      <main className="mx-auto max-w-6xl space-y-6 px-6 py-6">
        {showCreateForm ? (
          <form
            data-testid="create-issue-form"
            className="flex flex-col gap-3 rounded-xl border border-slate-800 bg-slate-900/50 p-4 md:flex-row"
            onSubmit={(e) => {
              e.preventDefault();
              void handleCreateIssue();
            }}
          >
            <input
              data-testid="create-issue-title"
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
              placeholder="Issue title"
              className="flex-1 rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100"
            />
            <button
              type="submit"
              disabled={createIssue.isPending || !newTitle.trim()}
              className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-500 disabled:opacity-50"
            >
              Create
            </button>
          </form>
        ) : null}

        <IssueFiltersBar
          filters={filters}
          users={usersQuery.data ?? []}
          onChange={setFilters}
        />

        <div className="flex items-center justify-between text-sm text-slate-400">
          <span data-testid="issue-count">
            {issuesQuery.isLoading ? "Loading…" : `${total} issue${total === 1 ? "" : "s"}`}
          </span>
        </div>

        <IssueList
          issues={issues}
          isLoading={issuesQuery.isLoading}
          isError={issuesQuery.isError}
          errorMessage={
            issuesQuery.error instanceof Error ? issuesQuery.error.message : undefined
          }
          onSelect={handleSelectIssue}
        />
      </main>

      {selectedIssueId != null ? (
        <IssueDetailPanel
          issueId={selectedIssueId}
          users={usersQuery.data ?? []}
          onClose={() => setSelectedIssueId(null)}
        />
      ) : null}
    </div>
  );
}
