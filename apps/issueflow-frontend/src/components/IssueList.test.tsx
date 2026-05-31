import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { IssueList } from "@/components/IssueList";

describe("IssueList", () => {
  it("renders empty state when there are no issues", () => {
    render(
      <IssueList
        issues={[]}
        isLoading={false}
        isError={false}
        onSelect={() => undefined}
      />,
    );

    expect(screen.getByTestId("issue-list-empty")).toBeInTheDocument();
    expect(screen.getByText("No issues found")).toBeInTheDocument();
  });

  it("renders loading state", () => {
    render(
      <IssueList
        issues={[]}
        isLoading
        isError={false}
        onSelect={() => undefined}
      />,
    );

    expect(screen.getByTestId("issue-list-loading")).toHaveTextContent("Loading issues");
  });
});
