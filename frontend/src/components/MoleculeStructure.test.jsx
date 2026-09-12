import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MoleculeStructure } from "./MoleculeStructure";

const SVG = "<svg><title>aspirin</title></svg>";

describe("MoleculeStructure zoom modal", () => {
  it("opens the enlarged view on click and closes it via the close button", async () => {
    const user = userEvent.setup();
    render(<MoleculeStructure svg={SVG} />);

    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /click to enlarge/i }));
    expect(screen.getByRole("dialog")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Close enlarged structure" }));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("closes the enlarged view when clicking the backdrop", async () => {
    const user = userEvent.setup();
    render(<MoleculeStructure svg={SVG} />);

    await user.click(screen.getByRole("button", { name: /click to enlarge/i }));
    expect(screen.getByRole("dialog")).toBeInTheDocument();

    await user.click(screen.getByRole("presentation"));
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("closes the enlarged view when pressing Escape", async () => {
    const user = userEvent.setup();
    render(<MoleculeStructure svg={SVG} />);

    await user.click(screen.getByRole("button", { name: /click to enlarge/i }));
    expect(screen.getByRole("dialog")).toBeInTheDocument();

    await user.keyboard("{Escape}");
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("does not render a trigger button when no svg is available", () => {
    render(<MoleculeStructure svg={null} />);
    expect(screen.queryByRole("button")).not.toBeInTheDocument();
    expect(screen.getByRole("img", { name: "2D structure of the input molecule" })).toBeInTheDocument();
  });
});
