import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { StatusBadge } from "@/components/StatusBadge";

describe("StatusBadge", () => {
  it("maps issue statuses to readable labels", () => {
    render(<StatusBadge status="in_progress" />);
    const badge = screen.getByTestId("status-badge");
    expect(badge).toHaveAttribute("data-status", "in_progress");
    expect(badge).toHaveTextContent("in progress");
  });
});
