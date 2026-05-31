export type IssueStatus = "open" | "in_progress" | "blocked" | "resolved" | "closed";
export type IssuePriority = "low" | "medium" | "high" | "urgent";
export type SlaStatus = "healthy" | "at_risk" | "overdue" | "closed";

export type ActivityEventType =
  | "status_change"
  | "priority_change"
  | "assignee_change"
  | "comment_added"
  | "issue_created"
  | "issue_updated"
  | "webhook_ingested";

export interface User {
  id: number;
  email: string;
  name: string;
  created_at: string;
}

export interface Comment {
  id: number;
  issue_id: number;
  author_id: number;
  body: string;
  created_at: string;
  author: User | null;
}

export interface ActivityEvent {
  id: number;
  issue_id: number;
  event_type: ActivityEventType;
  old_value: string | null;
  new_value: string | null;
  created_at: string;
}

export interface Issue {
  id: number;
  title: string;
  description: string | null;
  status: IssueStatus;
  priority: IssuePriority;
  assignee_id: number | null;
  created_at: string;
  updated_at: string;
  due_at: string | null;
  resolved_at: string | null;
  sla_status: SlaStatus | null;
  assignee: User | null;
}

export interface IssueDetail extends Issue {
  comments: Comment[];
  activity_events: ActivityEvent[];
}

export interface IssueListResponse {
  items: Issue[];
  total: number;
}

export interface IssueFilters {
  status?: IssueStatus;
  priority?: IssuePriority;
  assignee_id?: number;
  q?: string;
}

export interface IssueCreatePayload {
  title: string;
  description?: string | null;
  priority?: IssuePriority;
  assignee_id?: number | null;
  due_at?: string | null;
}

export interface IssueUpdatePayload {
  title?: string;
  description?: string | null;
  priority?: IssuePriority;
  assignee_id?: number | null;
  due_at?: string | null;
}

export const ISSUE_STATUSES: IssueStatus[] = [
  "open",
  "in_progress",
  "blocked",
  "resolved",
  "closed",
];

export const ISSUE_PRIORITIES: IssuePriority[] = ["low", "medium", "high", "urgent"];

/** Allowed transitions matching backend state machine. */
export const ALLOWED_TRANSITIONS: Record<IssueStatus, IssueStatus[]> = {
  open: ["in_progress", "blocked"],
  in_progress: ["resolved", "blocked", "open"],
  blocked: ["open", "in_progress"],
  resolved: ["closed", "open"],
  closed: ["open"],
};

export function getAllowedNextStatuses(current: IssueStatus): IssueStatus[] {
  return ALLOWED_TRANSITIONS[current] ?? [];
}
