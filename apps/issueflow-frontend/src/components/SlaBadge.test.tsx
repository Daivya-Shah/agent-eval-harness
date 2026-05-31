import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { SlaBadge } from "@/components/SlaBadge";

describe("SlaBadge", () => {
  it("displays the correct label for each SLA status", () => {
    const { rerender } = render(<SlaBadge status="healthy" />);
    expect(screen.getByTestId("sla-badge")).toHaveTextContent("Healthy");
    expect(screen.getByTestId("sla-badge")).toHaveAttribute("data-sla", "healthy");

    rerender(<SlaBadge status="at_risk" />);
    expect(screen.getByTestId("sla-badge")).toHaveTextContent("At risk");

    rerender(<SlaBadge status="overdue" />);
    expect(screen.getByTestId("sla-badge")).toHaveTextContent("Overdue");

    rerender(<SlaBadge status="closed" />);
    expect(screen.getByTestId("sla-badge")).toHaveTextContent("Closed SLA");
  });

  it("shows Unknown when status is missing", () => {
    render(<SlaBadge status={null} />);
    expect(screen.getByTestId("sla-badge")).toHaveTextContent("Unknown");
  });
});
