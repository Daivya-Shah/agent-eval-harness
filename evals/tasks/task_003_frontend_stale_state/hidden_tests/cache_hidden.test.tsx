import { QueryClient } from "@tanstack/react-query";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { api } from "@/api/client";
import { queryKeys } from "@/api/queryKeys";
import type { Issue, IssueDetail, IssueStatus } from "@/api/types";
import { useUpdateIssueStatus } from "@/hooks/useIssues";
import { renderHook, waitFor } from "@testing-library/react";
import { QueryClientProvider } from "@tanstack/react-query";
import React from "react";

const openIssue: Issue = {
  id: 9,
  title: "Filter consistency issue",
  description: null,
  status: "open",
  priority: "high",
  assignee_id: null,
  created_at: "2025-06-01T00:00:00Z",
  updated_at: "2025-06-01T00:00:00Z",
  due_at: null,
  resolved_at: null,
  sla_status: "healthy",
  assignee: null,
};

const inProgressIssue: Issue = { ...openIssue, status: "in_progress" };

function wrapper(client: QueryClient) {
  return function Wrapper({ children }: { children: React.ReactNode }) {
    return React.createElement(QueryClientProvider, { client }, children);
  };
}

describe("Frontend hidden-style cache consistency", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  it("updates list cache and invalidates so filtered views can refresh", async () => {
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    const filters = { status: "open" as const };

    client.setQueryData(queryKeys.issues.list(filters), {
      items: [openIssue],
      total: 1,
    });

    vi.spyOn(api, "updateIssueStatus").mockResolvedValue(inProgressIssue);

    const { result } = renderHook(() => useUpdateIssueStatus(), {
      wrapper: wrapper(client),
    });

    await result.current.mutateAsync({ id: 9, status: "in_progress" as IssueStatus });

    const cached = client.getQueryData<{ items: Issue[] }>(queryKeys.issues.list(filters));
    expect(cached?.items[0].status).toBe("in_progress");

    await waitFor(() => {
      const state = client.getQueryState(queryKeys.issues.list(filters));
      expect(state?.isInvalidated).toBe(true);
    });
  });

  it("keeps detail and list caches aligned after status mutation", async () => {
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    const detail: IssueDetail = { ...openIssue, comments: [], activity_events: [] };

    client.setQueryData(queryKeys.issues.detail(9), detail);
    client.setQueryData(queryKeys.issues.list({}), { items: [openIssue], total: 1 });

    vi.spyOn(api, "updateIssueStatus").mockResolvedValue(inProgressIssue);

    const { result } = renderHook(() => useUpdateIssueStatus(), {
      wrapper: wrapper(client),
    });

    await result.current.mutateAsync({ id: 9, status: "in_progress" });

    const listItem = client.getQueryData<{ items: Issue[] }>(queryKeys.issues.list({}))?.items[0];
    const detailItem = client.getQueryData<IssueDetail>(queryKeys.issues.detail(9));

    expect(listItem?.status).toBe("in_progress");
    expect(detailItem?.status).toBe("in_progress");
  });

  it("invalidates detail query after comment mutation", async () => {
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    const detail: IssueDetail = { ...openIssue, comments: [], activity_events: [] };
    client.setQueryData(queryKeys.issues.detail(9), detail);

    vi.spyOn(api, "addComment").mockResolvedValue({
      id: 100,
      issue_id: 9,
      author_id: 1,
      body: "hello",
      created_at: "2025-06-02T00:00:00Z",
      author: null,
    });

    const { useAddComment } = await import("@/hooks/useIssues");
    const { result } = renderHook(() => useAddComment(), { wrapper: wrapper(client) });

    await result.current.mutateAsync({ issueId: 9, authorId: 1, body: "hello" });

    await waitFor(() => {
      expect(client.getQueryState(queryKeys.issues.detail(9))?.isInvalidated).toBe(true);
    });
  });

  it("does not use full page reload workaround in mutation hooks", async () => {
    const reload = vi.fn();
    Object.defineProperty(window, "location", {
      configurable: true,
      value: { ...window.location, reload },
    });

    vi.spyOn(api, "updateIssueStatus").mockResolvedValue(inProgressIssue);
    const client = new QueryClient();
    const { result } = renderHook(() => useUpdateIssueStatus(), {
      wrapper: wrapper(client),
    });

    await result.current.mutateAsync({ id: 9, status: "in_progress" });
    expect(reload).not.toHaveBeenCalled();
  });

  it("handles rapid sequential status updates without throwing", async () => {
    vi.spyOn(api, "updateIssueStatus")
      .mockResolvedValueOnce({ ...openIssue, status: "in_progress" })
      .mockResolvedValueOnce({ ...openIssue, status: "blocked" });

    const client = new QueryClient();
    const { result } = renderHook(() => useUpdateIssueStatus(), {
      wrapper: wrapper(client),
    });

    await result.current.mutateAsync({ id: 9, status: "in_progress" });
    await result.current.mutateAsync({ id: 9, status: "blocked" });

    expect(api.updateIssueStatus).toHaveBeenCalledTimes(2);
  });
});
