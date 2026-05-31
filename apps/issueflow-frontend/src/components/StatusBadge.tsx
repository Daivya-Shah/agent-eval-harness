import type { IssueStatus } from "@/api/types";
import { formatStatusLabel } from "@/utils/format";

const STATUS_CONFIG: Record<IssueStatus, string> = {
  open: "bg-sky-500/15 text-sky-300 ring-sky-500/30",
  in_progress: "bg-indigo-500/15 text-indigo-300 ring-indigo-500/30",
  blocked: "bg-orange-500/15 text-orange-300 ring-orange-500/30",
  resolved: "bg-violet-500/15 text-violet-300 ring-violet-500/30",
  closed: "bg-slate-500/15 text-slate-300 ring-slate-500/30",
};

interface StatusBadgeProps {
  status: IssueStatus;
}

export function StatusBadge({ status }: StatusBadgeProps) {
  return (
    <span
      data-testid="status-badge"
      data-status={status}
      className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium capitalize ring-1 ring-inset ${STATUS_CONFIG[status]}`}
    >
      {formatStatusLabel(status)}
    </span>
  );
}
