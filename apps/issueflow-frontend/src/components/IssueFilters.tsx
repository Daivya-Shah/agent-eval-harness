import type { IssueFilters, IssuePriority, IssueStatus, User } from "@/api/types";
import { ISSUE_PRIORITIES, ISSUE_STATUSES } from "@/api/types";

interface IssueFiltersProps {
  filters: IssueFilters;
  users: User[];
  onChange: (filters: IssueFilters) => void;
}

export function IssueFiltersBar({ filters, users, onChange }: IssueFiltersProps) {
  return (
    <div
      data-testid="issue-filters"
      className="grid gap-3 rounded-xl border border-slate-800 bg-slate-900/60 p-4 md:grid-cols-2 xl:grid-cols-4"
    >
      <label className="flex flex-col gap-1 text-sm">
        <span className="text-slate-400">Search</span>
        <input
          data-testid="filter-search"
          type="search"
          placeholder="Search title or description…"
          value={filters.q ?? ""}
          onChange={(e) => onChange({ ...filters, q: e.target.value || undefined })}
          className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100 placeholder:text-slate-500 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
      </label>

      <label className="flex flex-col gap-1 text-sm">
        <span className="text-slate-400">Status</span>
        <select
          data-testid="filter-status"
          value={filters.status ?? ""}
          onChange={(e) =>
            onChange({
              ...filters,
              status: (e.target.value as IssueStatus) || undefined,
            })
          }
          className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        >
          <option value="">All statuses</option>
          {ISSUE_STATUSES.map((status) => (
            <option key={status} value={status}>
              {status.replace(/_/g, " ")}
            </option>
          ))}
        </select>
      </label>

      <label className="flex flex-col gap-1 text-sm">
        <span className="text-slate-400">Priority</span>
        <select
          data-testid="filter-priority"
          value={filters.priority ?? ""}
          onChange={(e) =>
            onChange({
              ...filters,
              priority: (e.target.value as IssuePriority) || undefined,
            })
          }
          className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        >
          <option value="">All priorities</option>
          {ISSUE_PRIORITIES.map((priority) => (
            <option key={priority} value={priority}>
              {priority}
            </option>
          ))}
        </select>
      </label>

      <label className="flex flex-col gap-1 text-sm">
        <span className="text-slate-400">Assignee</span>
        <select
          data-testid="filter-assignee"
          value={filters.assignee_id ?? ""}
          onChange={(e) =>
            onChange({
              ...filters,
              assignee_id: e.target.value ? Number(e.target.value) : undefined,
            })
          }
          className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100 focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        >
          <option value="">All assignees</option>
          {users.map((user) => (
            <option key={user.id} value={user.id}>
              {user.name}
            </option>
          ))}
        </select>
      </label>
    </div>
  );
}
