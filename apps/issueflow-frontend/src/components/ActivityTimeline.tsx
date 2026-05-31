import type { ActivityEvent } from "@/api/types";
import { formatDateTime, formatEventType } from "@/utils/format";

interface ActivityTimelineProps {
  events: ActivityEvent[];
}

export function ActivityTimeline({ events }: ActivityTimelineProps) {
  return (
    <section data-testid="activity-timeline" className="space-y-4">
      <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-400">
        Activity
      </h3>

      {events.length === 0 ? (
        <p className="text-sm text-slate-500">No activity recorded.</p>
      ) : (
        <ol className="space-y-3">
          {[...events].reverse().map((event) => (
            <li
              key={event.id}
              data-testid={`activity-${event.id}`}
              className="rounded-lg border border-slate-800 bg-slate-950/40 px-3 py-2 text-sm"
            >
              <div className="flex items-center justify-between gap-2 text-xs text-slate-500">
                <span className="capitalize">{formatEventType(event.event_type)}</span>
                <time>{formatDateTime(event.created_at)}</time>
              </div>
              {(event.old_value || event.new_value) && (
                <p className="mt-1 text-slate-300">
                  {event.old_value ? (
                    <>
                      <span className="text-slate-500">{event.old_value}</span>
                      {" → "}
                    </>
                  ) : null}
                  <span>{event.new_value}</span>
                </p>
              )}
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}
