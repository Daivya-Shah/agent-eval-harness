import type {
  Comment,
  Issue,
  IssueCreatePayload,
  IssueDetail,
  IssueFilters,
  IssueListResponse,
  IssueStatus,
  IssueUpdatePayload,
  User,
} from "./types";

const API_BASE = import.meta.env.VITE_API_BASE ?? "";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    ...init,
  });

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const body = (await response.json()) as { detail?: string | { msg: string }[] };
      if (typeof body.detail === "string") {
        detail = body.detail;
      } else if (Array.isArray(body.detail)) {
        detail = body.detail.map((d) => d.msg).join(", ");
      }
    } catch {
      // ignore parse errors
    }
    throw new ApiError(detail, response.status);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

function buildQuery(filters: IssueFilters): string {
  const params = new URLSearchParams();
  if (filters.status) params.set("status", filters.status);
  if (filters.priority) params.set("priority", filters.priority);
  if (filters.assignee_id != null) params.set("assignee_id", String(filters.assignee_id));
  if (filters.q?.trim()) params.set("q", filters.q.trim());
  const query = params.toString();
  return query ? `?${query}` : "";
}

export const api = {
  listIssues(filters: IssueFilters = {}): Promise<IssueListResponse> {
    return request(`/api/issues${buildQuery(filters)}`);
  },

  getIssue(id: number): Promise<IssueDetail> {
    return request(`/api/issues/${id}`);
  },

  createIssue(payload: IssueCreatePayload): Promise<Issue> {
    return request("/api/issues", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  updateIssue(id: number, payload: IssueUpdatePayload): Promise<Issue> {
    return request(`/api/issues/${id}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
  },

  updateIssueStatus(id: number, status: IssueStatus): Promise<Issue> {
    return request(`/api/issues/${id}/status`, {
      method: "POST",
      body: JSON.stringify({ status }),
    });
  },

  updateAssignee(id: number, assigneeId: number | null): Promise<Issue> {
    return request(`/api/issues/${id}/assignee`, {
      method: "POST",
      body: JSON.stringify({ assignee_id: assigneeId }),
    });
  },

  addComment(id: number, authorId: number, body: string): Promise<Comment> {
    return request(`/api/issues/${id}/comments`, {
      method: "POST",
      body: JSON.stringify({ author_id: authorId, body }),
    });
  },

  listUsers(): Promise<User[]> {
    return request("/api/users");
  },
};
