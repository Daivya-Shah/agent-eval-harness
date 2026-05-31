import type { SlaStatus } from "@/api/types";

const SLA_CONFIG: Record<SlaStatus, { label: string; className: string }> = {
  healthy: {
    label: "Healthy",
    className: "bg-emerald-500/15 text-emerald-300 ring-emerald-500/30",
  },
  at_risk: {
    label: "At risk",
    className: "bg-amber-500/15 text-amber-300 ring-amber-500/30",
  },
  overdue: {
    label: "Overdue",
    className: "bg-rose-500/15 text-rose-300 ring-rose-500/30",
  },
  closed: {
    label: "Closed SLA",
    className: "bg-slate-500/15 text-slate-300 ring-slate-500/30",
  },
};

interface SlaBadgeProps {
  status: SlaStatus | null | undefined;
}

export function SlaBadge({ status }: SlaBadgeProps) {
  if (!status) {
    return (
      <span
        data-testid="sla-badge"
        className="inline-flex rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset bg-slate-500/15 text-slate-400 ring-slate-500/30"
      >
        Unknown
      </span>
    );
  }

  const config = SLA_CONFIG[status];
  return (
    <span
      data-testid="sla-badge"
      data-sla={status}
      className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ring-1 ring-inset ${config.className}`}
    >
      {config.label}
    </span>
  );
}
