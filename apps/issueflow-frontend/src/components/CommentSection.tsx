import type { Comment, User } from "@/api/types";
import { formatDateTime } from "@/utils/format";

interface CommentSectionProps {
  comments: Comment[];
  users: User[];
  authorId: number | "";
  body: string;
  isSubmitting: boolean;
  onAuthorChange: (authorId: number | "") => void;
  onBodyChange: (body: string) => void;
  onSubmit: () => void;
}

export function CommentSection({
  comments,
  users,
  authorId,
  body,
  isSubmitting,
  onAuthorChange,
  onBodyChange,
  onSubmit,
}: CommentSectionProps) {
  return (
    <section data-testid="comment-section" className="space-y-4">
      <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-400">Comments</h3>

      <div className="space-y-3">
        {comments.length === 0 ? (
          <p className="text-sm text-slate-500">No comments yet.</p>
        ) : (
          comments.map((comment) => (
            <article
              key={comment.id}
              data-testid={`comment-${comment.id}`}
              className="rounded-lg border border-slate-800 bg-slate-950/60 p-3"
            >
              <div className="mb-1 flex items-center justify-between gap-2 text-xs text-slate-500">
                <span>{comment.author?.name ?? `User #${comment.author_id}`}</span>
                <time>{formatDateTime(comment.created_at)}</time>
              </div>
              <p className="text-sm text-slate-200">{comment.body}</p>
            </article>
          ))
        )}
      </div>

      <form
        className="space-y-3 rounded-lg border border-slate-800 bg-slate-900/50 p-4"
        onSubmit={(e) => {
          e.preventDefault();
          onSubmit();
        }}
      >
        <label className="flex flex-col gap-1 text-sm">
          <span className="text-slate-400">Author</span>
          <select
            data-testid="comment-author"
            value={authorId}
            onChange={(e) =>
              onAuthorChange(e.target.value ? Number(e.target.value) : "")
            }
            className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100"
          >
            <option value="">Select author…</option>
            {users.map((user) => (
              <option key={user.id} value={user.id}>
                {user.name}
              </option>
            ))}
          </select>
        </label>

        <label className="flex flex-col gap-1 text-sm">
          <span className="text-slate-400">Comment</span>
          <textarea
            data-testid="comment-body"
            rows={3}
            value={body}
            onChange={(e) => onBodyChange(e.target.value)}
            placeholder="Add a comment…"
            className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-slate-100 placeholder:text-slate-500"
          />
        </label>

        <button
          type="submit"
          data-testid="comment-submit"
          disabled={isSubmitting || !authorId || !body.trim()}
          className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isSubmitting ? "Posting…" : "Post comment"}
        </button>
      </form>
    </section>
  );
}
