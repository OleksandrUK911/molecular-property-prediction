import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ErrorBanner } from "./ErrorBanner";

describe("ErrorBanner", () => {
  it("renders the message with role alert", () => {
    render(<ErrorBanner message="Something went wrong" />);
    const alert = screen.getByRole("alert");
    expect(alert).toHaveTextContent("Something went wrong");
  });

  it("calls onRetry when the Retry button is clicked", async () => {
    const user = userEvent.setup();
    const onRetry = vi.fn();
    render(<ErrorBanner message="Server unavailable" onRetry={onRetry} />);
    await user.click(screen.getByRole("button", { name: "Retry" }));
    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it("does not render a Retry button when onRetry is not passed", () => {
    render(<ErrorBanner message="Server unavailable" />);
    expect(screen.queryByRole("button", { name: "Retry" })).not.toBeInTheDocument();
  });
});
