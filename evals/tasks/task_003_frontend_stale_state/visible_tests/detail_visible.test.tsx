import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import type { IssueDetail, IssueStatus } from "@/api/types";
import { IssueDetailPanel } from "@/components/IssueDetail";
import * as useIssuesModule from "@/hooks/useIssues";

const baseIssue: IssueDetail = {
  id: 42,
  title: "Stale state eval issue",
  description: "Testing detail updates",
  status: "open",
  priority: "medium",
  assignee_id: null,
  created_at: "2025-06-01T00:00:00Z",
  updated_at: "2025-06-01T00:00:00Z",
  due_at: null,
  resolved_at: null,
  sla_status: "healthy",
  assignee: null,
  comments: [],
  activity_events: [],
};

function renderDetail(issue: IssueDetail) {
  vi.spyOn(useIssuesModule, "useIssue").mockReturnValue({
    data: issue,
    isLoading: false,
    isError: false,
    error: null,
  } as never);

  const mutateAsync = vi.fn().mockImplementation(async ({ status }: { status: IssueStatus }) => ({
    ...issue,
    status,
  }));

  vi.spyOn(useIssuesModule, "useUpdateIssueStatus").mockReturnValue({
    mutateAsync,
    isPending: false,
  } as never);

  vi.spyOn(useIssuesModule, "useUpdateAssignee").mockReturnValue({
    mutateAsync: vi.fn(),
    isPending: false,
  } as never);

  vi.spyOn(useIssuesModule, "useAddComment").mockReturnValue({
    mutateAsync: vi.fn(),
    isPending: false,
  } as never);

  render(
    <QueryClientProvider client={new QueryClient()}>
      <IssueDetailPanel issueId={issue.id} users={[]} onClose={() => undefined} />
    </QueryClientProvider>,
  );

  return { mutateAsync };
}

describe("Issue detail visible eval behavior", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("status update changes visible badge in detail panel", async () => {
    const user = userEvent.setup();
    const issue = { ...baseIssue };
    const { mutateAsync } = renderDetail(issue);

    const select = screen.getByTestId("detail-status-select");
    await user.selectOptions(select, "in_progress");

    await waitFor(() => {
      expect(mutateAsync).toHaveBeenCalledWith({ id: 42, status: "in_progress" });
    });
  });

  it("adding comment invokes mutation with author and body", async () => {
    vi.spyOn(useIssuesModule, "useIssue").mockReturnValue({
      data: baseIssue,
      isLoading: false,
      isError: false,
      error: null,
    } as never);

    vi.spyOn(useIssuesModule, "useUpdateIssueStatus").mockReturnValue({
      mutateAsync: vi.fn(),
      isPending: false,
    } as never);

    vi.spyOn(useIssuesModule, "useUpdateAssignee").mockReturnValue({
      mutateAsync: vi.fn(),
      isPending: false,
    } as never);

    const addComment = vi.fn().mockResolvedValue({
      id: 1,
      issue_id: 42,
      author_id: 7,
      body: "New eval comment",
      created_at: "2025-06-02T00:00:00Z",
      author: null,
    });

    vi.spyOn(useIssuesModule, "useAddComment").mockReturnValue({
      mutateAsync: addComment,
      isPending: false,
    } as never);

    const user = userEvent.setup();
    render(
      <QueryClientProvider client={new QueryClient()}>
        <IssueDetailPanel
          issueId={42}
          users={[{ id: 7, email: "a@test.dev", name: "Alice", created_at: "2025-01-01T00:00:00Z" }]}
          onClose={() => undefined}
        />
      </QueryClientProvider>,
    );

    await user.selectOptions(screen.getByTestId("comment-author"), "7");
    await user.type(screen.getByTestId("comment-body"), "New eval comment");
    await user.click(screen.getByTestId("comment-submit"));

    await waitFor(() => {
      expect(addComment).toHaveBeenCalledWith({
        issueId: 42,
        authorId: 7,
        body: "New eval comment",
      });
    });
  });
});
