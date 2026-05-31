import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "@/api/client";
import { queryKeys } from "@/api/queryKeys";
import type { Issue, IssueDetail, IssueFilters, IssueStatus } from "@/api/types";

export function useUsers() {
  return useQuery({
    queryKey: queryKeys.users.all,
    queryFn: () => api.listUsers(),
  });
}

export function useIssues(filters: IssueFilters) {
  return useQuery({
    queryKey: queryKeys.issues.list(filters),
    queryFn: () => api.listIssues(filters),
  });
}

export function useIssue(id: number | null) {
  return useQuery({
    queryKey: queryKeys.issues.detail(id ?? 0),
    queryFn: () => api.getIssue(id!),
    enabled: id != null,
  });
}

function patchIssueInLists(queryClient: ReturnType<typeof useQueryClient>, updated: Issue) {
  queryClient.setQueriesData<{ items: Issue[]; total: number }>(
    { queryKey: queryKeys.issues.lists() },
    (old) => {
      if (!old) return old;
      return {
        ...old,
        items: old.items.map((item) => (item.id === updated.id ? { ...item, ...updated } : item)),
      };
    },
  );
}

export function useUpdateIssueStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, status }: { id: number; status: IssueStatus }) =>
      api.updateIssueStatus(id, status),
    onSuccess: (updated) => {
      patchIssueInLists(queryClient, updated);
      queryClient.setQueryData<IssueDetail>(queryKeys.issues.detail(updated.id), (old) =>
        old ? { ...old, ...updated } : old,
      );
      void queryClient.invalidateQueries({ queryKey: queryKeys.issues.detail(updated.id) });
      void queryClient.invalidateQueries({ queryKey: queryKeys.issues.lists() });
    },
  });
}

export function useUpdateAssignee() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, assigneeId }: { id: number; assigneeId: number | null }) =>
      api.updateAssignee(id, assigneeId),
    onSuccess: (updated) => {
      patchIssueInLists(queryClient, updated);
      queryClient.setQueryData<IssueDetail>(queryKeys.issues.detail(updated.id), (old) =>
        old ? { ...old, ...updated } : old,
      );
      void queryClient.invalidateQueries({ queryKey: queryKeys.issues.detail(updated.id) });
      void queryClient.invalidateQueries({ queryKey: queryKeys.issues.lists() });
    },
  });
}

export function useAddComment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      issueId,
      authorId,
      body,
    }: {
      issueId: number;
      authorId: number;
      body: string;
    }) => api.addComment(issueId, authorId, body),
    onSuccess: (_comment, { issueId }) => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.issues.detail(issueId) });
      void queryClient.invalidateQueries({ queryKey: queryKeys.issues.lists() });
    },
  });
}

export function useCreateIssue() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: api.createIssue,
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: queryKeys.issues.lists() });
    },
  });
}
