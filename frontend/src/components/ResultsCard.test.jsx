import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { ResultsCard } from "./ResultsCard";

const baseResult = {
  predicted_target: -2.3456,
  target_name: "ESOL",
  confidence: 0.87,
  descriptors: {
    MolWt: 180.16,
    LogP: 1.19,
    TPSA: 63.6,
    NumHDonors: 1,
    NumHAcceptors: 4,
    NumRotatableBonds: 2,
    RingCount: 1,
  },
};

describe("ResultsCard", () => {
  it("renders the predicted value", () => {
    render(<ResultsCard result={baseResult} />);
    expect(screen.getByText(/Predicted solubility: -2\.35 log\(mol\/L\)/)).toBeInTheDocument();
  });

  it("renders all 7 descriptors", () => {
    render(<ResultsCard result={baseResult} />);
    expect(screen.getByText("Molecular weight")).toBeInTheDocument();
    expect(screen.getByText("180.16")).toBeInTheDocument();
    expect(screen.getByText("LogP")).toBeInTheDocument();
    expect(screen.getByText("1.19")).toBeInTheDocument();
    expect(screen.getByText("TPSA")).toBeInTheDocument();
    expect(screen.getByText("63.60")).toBeInTheDocument();
    expect(screen.getByText("H-Bond Donors")).toBeInTheDocument();
    expect(screen.getByText("H-Bond Acceptors")).toBeInTheDocument();
    expect(screen.getByText("Rotatable Bonds")).toBeInTheDocument();
    expect(screen.getByText("Num Rings")).toBeInTheDocument();
  });

  it("does not render the no-confidence note when confidence is provided", () => {
    render(<ResultsCard result={baseResult} />);
    expect(screen.queryByText(/does not provide a calibrated confidence/)).not.toBeInTheDocument();
  });

  it("renders the no-calibrated-confidence note when confidence is null", () => {
    render(<ResultsCard result={{ ...baseResult, confidence: null }} />);
    expect(screen.getByText(/does not provide a calibrated confidence/)).toBeInTheDocument();
  });
});
