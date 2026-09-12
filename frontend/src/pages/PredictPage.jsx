import { useState } from "react";
import { useLocation } from "react-router-dom";
import { ApiError, predict } from "../api";
import { SmilesInput } from "../components/SmilesInput";
import { ExampleChips } from "../components/ExampleChips";
import { MoleculeStructure } from "../components/MoleculeStructure";
import { ResultsCard } from "../components/ResultsCard";
import { ErrorBanner } from "../components/ErrorBanner";
import { DescriptorBarChart } from "../components/DescriptorBarChart";

export function PredictPage() {
  const location = useLocation();
  // Came from History page's "View" action - pre-fill, let the user
  // re-submit (we don't cache full prediction detail in history rows).
  const [smiles, setSmiles] = useState(location.state?.smiles || "");
  const [status, setStatus] = useState("idle"); // idle | loading | success | error
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  async function runPrediction(inputSmiles) {
    setStatus("loading");
    setError(null);
    try {
      const data = await predict(inputSmiles);
      setResult(data);
      setStatus("success");
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Unexpected error");
      setStatus("error");
    }
  }

  return (
    <div>
      <h1>Predict molecular properties</h1>
      <SmilesInput
        value={smiles}
        onChange={setSmiles}
        onSubmit={() => runPrediction(smiles)}
        disabled={status === "loading"}
      />
      <ExampleChips
        disabled={status === "loading"}
        onPick={(s) => {
          setSmiles(s);
          runPrediction(s);
        }}
      />

      {status === "error" && <ErrorBanner message={error} onRetry={() => runPrediction(smiles)} />}

      {status === "loading" && (
        <div style={{ marginTop: 24, textAlign: "center" }} className="text-muted" role="status" aria-live="polite">
          Predicting…
        </div>
      )}

      {status === "success" && result && (
        <>
          <div style={{ display: "flex", gap: 16, marginTop: 24, flexWrap: "wrap" }}>
            <MoleculeStructure svg={result.structure_svg} />
            <div style={{ flex: 1, minWidth: 240 }}>
              <ResultsCard result={result} />
            </div>
          </div>
          <div style={{ marginTop: 16 }}>
            <DescriptorBarChart descriptors={result.descriptors} />
          </div>
        </>
      )}
    </div>
  );
}
