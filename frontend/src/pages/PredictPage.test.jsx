import { describe, expect, it, vi, beforeEach } from "vitest";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { PredictPage } from "./PredictPage";
import { ApiError } from "../api";
import { predict } from "../api";
import { renderWithProviders } from "../testUtils";

vi.mock("../api", async () => {
  const actual = await vi.importActual("../api");
  return {
    ...actual,
    predict: vi.fn(),
  };
});

function renderPage() {
  return renderWithProviders(<PredictPage />);
}

const sampleResult = {
  smiles: "CC(=O)Oc1ccccc1C(=O)O",
  predicted_target: -2.1,
  target_name: "ESOL",
  confidence: null,
  structure_svg: "<svg><title>aspirin</title></svg>",
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

beforeEach(() => {
  predict.mockReset();
});

describe("PredictPage", () => {
  it("goes idle -> loading -> success and shows the results card and structure", async () => {
    const user = userEvent.setup();
    let resolvePredict;
    predict.mockImplementation(
      () =>
        new Promise((resolve) => {
          resolvePredict = resolve;
        }),
    );

    renderPage();

    await user.type(screen.getByLabelText("SMILES string"), "CC(=O)Oc1ccccc1C(=O)O");
    await user.click(screen.getByRole("button", { name: "Predict" }));

    // loading state
    expect(screen.getByRole("status")).toHaveTextContent("Predicting…");
    expect(screen.getByLabelText("SMILES string")).toBeDisabled();

    resolvePredict(sampleResult);

    // success state
    await waitFor(() => {
      expect(screen.getByText(/Predicted solubility: -2\.10 log\(mol\/L\)/)).toBeInTheDocument();
    });
    expect(
      screen.getByRole("button", { name: "2D structure of the input molecule. Click to enlarge." }),
    ).toBeInTheDocument();
    expect(screen.queryByRole("status")).not.toBeInTheDocument();
    expect(screen.queryByRole("alert")).not.toBeInTheDocument();
  });

  it("goes idle -> loading -> error and shows the error banner with the right message", async () => {
    const user = userEvent.setup();
    let rejectPredict;
    predict.mockImplementation(
      () =>
        new Promise((_, reject) => {
          rejectPredict = reject;
        }),
    );

    renderPage();

    await user.type(screen.getByLabelText("SMILES string"), "not-a-smiles");
    await user.click(screen.getByRole("button", { name: "Predict" }));

    expect(screen.getByRole("status")).toHaveTextContent("Predicting…");

    rejectPredict(new ApiError("Invalid SMILES string", 422));

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent("Invalid SMILES string");
    });
    expect(screen.queryByRole("status")).not.toBeInTheDocument();
    expect(screen.queryByText(/Predicted solubility/)).not.toBeInTheDocument();

    // Retry re-invokes predict
    predict.mockResolvedValueOnce(sampleResult);
    await user.click(screen.getByRole("button", { name: "Retry" }));
    await waitFor(() => {
      expect(screen.getByText(/Predicted solubility/)).toBeInTheDocument();
    });
  });
});
