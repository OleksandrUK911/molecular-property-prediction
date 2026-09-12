import { describe, it, expect } from "vitest";
import { screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { renderWithProviders } from "../testUtils";
import { DescriptorBarChart } from "./DescriptorBarChart";

const DESCRIPTORS = {
  MolWt: 180.16,
  LogP: 1.19,
  TPSA: 63.6,
  NumHDonors: 1,
  NumHAcceptors: 4,
  NumRotatableBonds: 3,
  RingCount: 1,
};

describe("DescriptorBarChart", () => {
  it("hides the table by default and reveals it via the toggle button", async () => {
    const user = userEvent.setup();
    renderWithProviders(<DescriptorBarChart descriptors={DESCRIPTORS} />);

    expect(screen.queryByRole("table")).not.toBeInTheDocument();

    const toggle = screen.getByRole("button", { name: "View as table" });
    await user.click(toggle);

    const table = screen.getByRole("table");
    expect(table).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Hide table" })).toBeInTheDocument();

    // All 7 descriptors present, each with a raw and a normalized value.
    const rows = within(table).getAllByRole("row").slice(1); // skip header row
    expect(rows).toHaveLength(7);

    const molWtRow = rows.find((r) => within(r).queryByText("Molecular weight"));
    expect(molWtRow).toBeTruthy();
    const cells = within(molWtRow).getAllByRole("cell");
    expect(cells[1].textContent).toBe("180.16");
    expect(cells[2].textContent).toBe("0.36");
  });
});
