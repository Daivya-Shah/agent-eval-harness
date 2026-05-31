import type { IssuePriority } from "@/api/types";

const PRIORITY_CONFIG: Record<IssuePriority, string> = {
  low: "bg-slate-500/15 text-slate-300 ring-slate-500/30",
  medium: "bg-blue-500/15 text-blue-300 ring-blue-500/30",
  high: "bg-amber-500/15 text-amber-300 ring-amber-500/30",
  urgent: "bg-rose-500/15 text-rose-300 ring-rose-500/30",
};

interface PriorityBadgeProps {
  priority: IssuePriority;
}

export function PriorityBadge({ priority }: PriorityBadgeProps) {
  return (
    <span
      data-testid="priority-badge"
      data-priority={priority}
      className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium capitalize ring-1 ring-inset ${PRIORITY_CONFIG[priority]}`}
    >
      {priority}
    </span>
  );
}
