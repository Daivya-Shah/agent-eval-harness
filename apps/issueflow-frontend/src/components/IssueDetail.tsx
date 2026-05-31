import { useEffect, useState } from "react";

import type { IssueDetail as IssueDetailType, IssueStatus, User } from "@/api/types";
import { getAllowedNextStatuses } from "@/api/types";
import { ActivityTimeline } from "@/components/ActivityTimeline";
import { CommentSection } from "@/components/CommentSection";
import { PriorityBadge } from "@/components/PriorityBadge";
import { SlaBadge } from "@/components/SlaBadge";
import { StatusBadge } from "@/components/StatusBadge";
import {
  useAddComment,
  useIssue,
  useUpdateAssignee,
  useUpdateIssueStatus,
} from "@/hooks/useIssues";
import { formatDate, formatDateTime } from "@/utils/format";

interface IssueDetailProps {
  issueId: number;
  users: User[];
  onClose: () => void;
}

export function IssueDetailPanel({ issueId, users, onClose }: IssueDetailProps) {
  const { data: issue, isLoading, isError, error } = useIssue(issueId);
  const statusMutation = useUpdateIssueStatus();
  const assigneeMutation = useUpdateAssignee();
  const commentMutation = useAddComment();

  const [commentAuthorId, setCommentAuthorId] = useState<number | "">("");
  const [commentBody, setCommentBody] = useState("");
  const [mutationError, setMutationError] = useState<string | null>(null);

  useEffect(() => {
    setCommentAuthorId("");
    setCommentBody("");
    setMutationError(null);
  }, [issueId]);

  const handleStatusChange = async (status: IssueStatus) => {
    setMutationError(null);
    try {
      await statusMutation.mutateAsync({ id: issueId, status });
    } catch (err) {
      setMutationError(err instanceof Error ? err.message : "Status update failed");
    }
  };

  const handleAssigneeChange = async (assigneeId: number | null) => {
    setMutationError(null);
    try {
      await assigneeMutation.mutateAsync({ id: issueId, assigneeId });
    } catch (err) {
      setMutationError(err instanceof Error ? err.message : "Assignee update failed");
    }
  };

  const handleAddComment = async () => {
    if (!commentAuthorId || !commentBody.trim()) return;
    setMutationError(null);
    try {
      await commentMutation.mutateAsync({
        issueId,
        authorId: commentAuthorId,
        body: commentBody.trim(),
      });
      setCommentBody("");
    } catch (err) {
      setMutationError(err instanceof Error ? err.message : "Failed to add comment");
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-stretch justify-end bg-slate-950/70 backdrop-blur-sm"
      data-testid="issue-detail-overlay"
      onClick={onClose}
    >
      <aside
        data-testid="issue-detail-panel"
        className="flex h-full w-full max-w-2xl flex-col border-l border-slate-800 bg-slate-950 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <header className="flex items-start justify-between gap-4 border-b border-slate-800 px-6 py-4">
          <div>
            <p className="text-xs font-mono text-slate-500">Issue #{issueId}</p>
            {isLoading ? (
              <h2 className="mt-1 text-xl font-semibold text-slate-300">Loading…</h2>
            ) : isError ? (
              <h2 className="mt-1 text-xl font-semibold text-rose-300">Failed to load issue</h2>
            ) : issue ? (
              <h2 className="mt-1 text-xl font-semibold text-slate-100">{issue.title}</h2>
            ) : null}
          </div>
          <button
            type="button"
            data-testid="issue-detail-close"
            onClick={onClose}
            className="rounded-lg border border-slate-700 px-3 py-1.5 text-sm text-slate-300 hover:bg-slate-900"
          >
            Close
          </button>
        </header>

        <div className="flex-1 overflow-y-auto px-6 py-5">
          {isLoading ? (
            <p className="text-slate-400">Loading issue details…</p>
          ) : isError ? (
            <p className="text-rose-300">{error instanceof Error ? error.message : "Error"}</p>
          ) : issue ? (
            <IssueDetailContent
              issue={issue}
              users={users}
              mutationError={mutationError}
              isStatusPending={statusMutation.isPending}
              isAssigneePending={assigneeMutation.isPending}
              commentAuthorId={commentAuthorId}
              commentBody={commentBody}
              isCommentPending={commentMutation.isPending}
              onStatusChange={handleStatusChange}
              onAssigneeChange={handleAssigneeChange}
              onCommentAuthorChange={setCommentAuthorId}
              onCommentBodyChange={setCommentBody}
              onAddComment={handleAddComment}
            />
          ) : null}
        </div>
      </aside>
    </div>
  );
}

interface IssueDetailContentProps {
  issue: IssueDetailType;
  users: User[];
  mutationError: string | null;
  isStatusPending: boolean;
  isAssigneePending: boolean;
  commentAuthorId: number | "";
  commentBody: string;
  isCommentPending: boolean;
  onStatusChange: (status: IssueStatus) => void;
  onAssigneeChange: (assigneeId: number | null) => void;
  onCommentAuthorChange: (id: number | "") => void;
  onCommentBodyChange: (body: string) => void;
  onAddComment: () => void;
}

function IssueDetailContent({
  issue,
  users,
  mutationError,
  isStatusPending,
  isAssigneePending,
  commentAuthorId,
  commentBody,
  isCommentPending,
  onStatusChange,
  onAssigneeChange,
  onCommentAuthorChange,
  onCommentBodyChange,
  onAddComment,
}: IssueDetailContentProps) {
  const nextStatuses = getAllowedNextStatuses(issue.status);

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap gap-2">
        <StatusBadge status={issue.status} />
        <PriorityBadge priority={issue.priority} />
        <SlaBadge status={issue.sla_status} />
      </div>

      {issue.description ? (
        <p className="text-sm leading-relaxed text-slate-300">{issue.description}</p>
      ) : (
        <p className="text-sm text-slate-500">No description provided.</p>
      )}

      <dl className="grid grid-cols-2 gap-3 text-sm">
        <div>
          <dt className="text-slate-500">Assignee</dt>
          <dd className="text-slate-200">{issue.assignee?.name ?? "Unassigned"}</dd>
        </div>
        <div>
          <dt className="text-slate-500">Due date</dt>
          <dd className="text-slate-200">{formatDate(issue.due_at)}</dd>
        </div>
        <div>
          <dt className="text-slate-500">Created</dt>
          <dd className="text-slate-200">{formatDateTime(issue.created_at)}</dd>
        </div>
        <div>
          <dt className="text-slate-500">Updated</dt>
          <dd className="text-slate-200">{formatDateTime(issue.updated_at)}</dd>
        </div>
      </dl>

      <div className="grid gap-4 rounded-xl border border-slate-800 bg-slate-900/40 p-4 md:grid-cols-2">
        <label className="flex flex-col gap-1 text-sm">
          <span className="text-slate-400">Update status</span>
          <select
            data-testid="detail-status-select"
            value=""
            disabled={isStatusPending || nextStatuses.length === 0}
            onChange={(e) => {
              const value = e.target.value as IssueStatus;
              if (value) onStatusChange(value);
              e.target.value = "";
            }}
            className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100"
          >
            <option value="">Move to…</option>
            {nextStatuses.map((status) => (
              <option key={status} value={status}>
                {status.replace(/_/g, " ")}
              </option>
            ))}
          </select>
        </label>

        <label className="flex flex-col gap-1 text-sm">
          <span className="text-slate-400">Update assignee</span>
          <select
            data-testid="detail-assignee-select"
            value={issue.assignee_id ?? ""}
            disabled={isAssigneePending}
            onChange={(e) =>
              onAssigneeChange(e.target.value ? Number(e.target.value) : null)
            }
            className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100"
          >
            <option value="">Unassigned</option>
            {users.map((user) => (
              <option key={user.id} value={user.id}>
                {user.name}
              </option>
            ))}
          </select>
        </label>
      </div>

      {mutationError ? (
        <p data-testid="detail-mutation-error" className="text-sm text-rose-300">
          {mutationError}
        </p>
      ) : null}

      <CommentSection
        comments={issue.comments}
        users={users}
        authorId={commentAuthorId}
        body={commentBody}
        isSubmitting={isCommentPending}
        onAuthorChange={onCommentAuthorChange}
        onBodyChange={onCommentBodyChange}
        onSubmit={onAddComment}
      />

      <ActivityTimeline events={issue.activity_events} />
    </div>
  );
}
