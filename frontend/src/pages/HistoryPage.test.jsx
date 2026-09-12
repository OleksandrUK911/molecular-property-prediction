import { describe, expect, it, vi } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import { HistoryPage } from "./HistoryPage";
import { getHistory } from "../api";
import { renderWithProviders } from "../testUtils";
import { TREND_MAX_POINTS, getTrendChartData } from "../historyTrend";

vi.mock("../api", async () => {
  const actual = await vi.importActual("../api");
  return {
    ...actual,
    getHistory: vi.fn(),
  };
});

function makeRow(overrides = {}) {
  return {
    id: 1,
    smiles: "CCO",
    predicted_target: -1.23,
    model_version: "v1",
    created_at: "2024-01-01T10:00:00Z",
    ...overrides,
  };
}

describe("HistoryPage trend chart gating", () => {
  it("does not render the trend chart when there is only one history row", async () => {
    getHistory.mockResolvedValueOnce([makeRow({ id: 1 })]);
    renderWithProviders(<HistoryPage />);

    await waitFor(() => {
      expect(screen.getByText("CCO")).toBeInTheDocument();
    });
    expect(screen.queryByText("Prediction trend")).not.toBeInTheDocument();
    expect(screen.queryByRole("img", { name: "Line chart of predicted solubility over time" })).not.toBeInTheDocument();
  });

  it("renders the trend chart when there are two or more history rows", async () => {
    getHistory.mockResolvedValueOnce([
      makeRow({ id: 1, smiles: "CCO", created_at: "2024-01-02T10:00:00Z" }),
      makeRow({ id: 2, smiles: "CCN", created_at: "2024-01-01T10:00:00Z" }),
    ]);
    renderWithProviders(<HistoryPage />);

    await waitFor(() => {
      expect(screen.getByText("Prediction trend")).toBeInTheDocument();
    });
    expect(screen.getByRole("img", { name: "Line chart of predicted solubility over time" })).toBeInTheDocument();
  });

  it("keeps the table showing all rows (newest-first) even when the chart is capped", async () => {
    const rows = Array.from({ length: 25 }, (_, i) =>
      makeRow({ id: i, smiles: "CCO", created_at: new Date(2024, 0, i + 1).toISOString() }),
    );
    getHistory.mockResolvedValueOnce(rows);
    renderWithProviders(<HistoryPage />);

    await waitFor(() => {
      expect(screen.getByText("Prediction trend")).toBeInTheDocument();
    });
    expect(screen.getAllByRole("row")).toHaveLength(26); // 25 data rows + header
  });
});

describe("getTrendChartData", () => {
  const rows = Array.from({ length: 25 }, (_, i) =>
    makeRow({ id: i, predicted_target: i, created_at: new Date(2024, 0, i + 1).toISOString() }),
  );

  it("caps the result at TREND_MAX_POINTS entries", () => {
    expect(TREND_MAX_POINTS).toBe(20);
    const result = getTrendChartData(rows, "en");
    expect(result).toHaveLength(20);
  });

  it("reverses newest-first input into chronological order", () => {
    // rows[0] is the newest (Jan 25); after capping to the most recent 20
    // (rows[0..19]) and reversing, the oldest of those (rows[19], Jan 6)
    // should come first and the newest (rows[0], Jan 25) should come last.
    const result = getTrendChartData(rows, "en");
    expect(result[0].predicted_target).toBe(19);
    expect(result[result.length - 1].predicted_target).toBe(0);
  });
});
