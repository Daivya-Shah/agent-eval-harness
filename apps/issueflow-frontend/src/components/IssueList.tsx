import type { Issue } from "@/api/types";
import { PriorityBadge } from "@/components/PriorityBadge";
import { SlaBadge } from "@/components/SlaBadge";
import { StatusBadge } from "@/components/StatusBadge";
import { formatDate } from "@/utils/format";

interface IssueRowProps {
  issue: Issue;
  onSelect: (issue: Issue) => void;
}

export function IssueRow({ issue, onSelect }: IssueRowProps) {
  return (
    <button
      type="button"
      data-testid={`issue-row-${issue.id}`}
      onClick={() => onSelect(issue)}
      className="grid w-full grid-cols-1 gap-3 rounded-xl border border-slate-800 bg-slate-900/50 p-4 text-left transition hover:border-indigo-500/40 hover:bg-slate-900 md:grid-cols-[1fr_auto] md:items-center"
    >
      <div className="space-y-2">
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-xs font-mono text-slate-500">#{issue.id}</span>
          <StatusBadge status={issue.status} />
          <PriorityBadge priority={issue.priority} />
          <SlaBadge status={issue.sla_status} />
        </div>
        <h3 className="text-base font-semibold text-slate-100">{issue.title}</h3>
        {issue.description ? (
          <p className="line-clamp-2 text-sm text-slate-400">{issue.description}</p>
        ) : null}
      </div>

      <div className="flex flex-col gap-1 text-sm text-slate-400 md:items-end md:text-right">
        <span data-testid={`issue-assignee-${issue.id}`}>
          {issue.assignee?.name ?? "Unassigned"}
        </span>
        <span>Due {formatDate(issue.due_at)}</span>
        <span className="text-xs text-slate-500">Updated {formatDate(issue.updated_at)}</span>
      </div>
    </button>
  );
}

interface IssueListProps {
  issues: Issue[];
  isLoading: boolean;
  isError: boolean;
  errorMessage?: string;
  onSelect: (issue: Issue) => void;
}

export function IssueList({ issues, isLoading, isError, errorMessage, onSelect }: IssueListProps) {
  if (isLoading) {
    return (
      <div
        data-testid="issue-list-loading"
        className="rounded-xl border border-slate-800 bg-slate-900/40 p-8 text-center text-slate-400"
      >
        Loading issues…
      </div>
    );
  }

  if (isError) {
    return (
      <div
        data-testid="issue-list-error"
        className="rounded-xl border border-rose-500/30 bg-rose-500/10 p-8 text-center text-rose-200"
      >
        Failed to load issues{errorMessage ? `: ${errorMessage}` : "."}
      </div>
    );
  }

  if (issues.length === 0) {
    return (
      <div
        data-testid="issue-list-empty"
        className="rounded-xl border border-dashed border-slate-700 bg-slate-900/30 p-10 text-center"
      >
        <p className="text-lg font-medium text-slate-200">No issues found</p>
        <p className="mt-1 text-sm text-slate-400">Try adjusting your filters or search query.</p>
      </div>
    );
  }

  return (
    <div data-testid="issue-list" className="space-y-3">
      {issues.map((issue) => (
        <IssueRow key={issue.id} issue={issue} onSelect={onSelect} />
      ))}
    </div>
  );
}
