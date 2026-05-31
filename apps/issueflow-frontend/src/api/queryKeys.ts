import type { IssueFilters } from "@/api/types";

export const queryKeys = {
  users: {
    all: ["users"] as const,
  },
  issues: {
    all: ["issues"] as const,
    lists: () => [...queryKeys.issues.all, "list"] as const,
    list: (filters: IssueFilters) => [...queryKeys.issues.lists(), filters] as const,
    details: () => [...queryKeys.issues.all, "detail"] as const,
    detail: (id: number) => [...queryKeys.issues.details(), id] as const,
  },
};
