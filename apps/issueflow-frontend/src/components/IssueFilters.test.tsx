import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { IssueFiltersBar } from "@/components/IssueFilters";

describe("IssueFiltersBar", () => {
  it("calls onChange when search and filters are updated", async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();

    render(
      <IssueFiltersBar
        filters={{}}
        users={[{ id: 1, email: "a@test.dev", name: "Alice", created_at: "2025-01-01T00:00:00Z" }]}
        onChange={onChange}
      />,
    );

    fireEvent.change(screen.getByTestId("filter-search"), {
      target: { value: "timeout" },
    });
    expect(onChange).toHaveBeenCalledWith({ q: "timeout" });

    await user.selectOptions(screen.getByTestId("filter-status"), "blocked");
    expect(onChange).toHaveBeenLastCalledWith(
      expect.objectContaining({ status: "blocked" }),
    );

    await user.selectOptions(screen.getByTestId("filter-priority"), "urgent");
    expect(onChange).toHaveBeenLastCalledWith(
      expect.objectContaining({ priority: "urgent" }),
    );

    await user.selectOptions(screen.getByTestId("filter-assignee"), "1");
    expect(onChange).toHaveBeenLastCalledWith(
      expect.objectContaining({ assignee_id: 1 }),
    );
  });
});
