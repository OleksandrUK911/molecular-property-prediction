import { useState } from "react";
import { useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { ApiError, predict } from "../api";
import { SmilesInput } from "../components/SmilesInput";
import { ExampleChips } from "../components/ExampleChips";
import { MoleculeStructure } from "../components/MoleculeStructure";
import { ResultsCard } from "../components/ResultsCard";
import { ErrorBanner } from "../components/ErrorBanner";
import { DescriptorBarChart } from "../components/DescriptorBarChart";

export function PredictPage() {
  const { t } = useTranslation();
  const location = useLocation();
  const queryClient = useQueryClient();
  // Came from History page's "View" action - pre-fill, let the user
  // re-submit (we don't cache full prediction detail in history rows).
  const [smiles, setSmiles] = useState(location.state?.smiles || "");

  // A prediction is submitted as a discrete action (not something that
  // should auto-run/refetch on mount or on window refocus like a plain
  // useQuery), so useMutation is the right hook for the "predicting..."
  // /success/error lifecycle here. But we still want repeat submissions
  // of the same SMILES to be served from cache instead of re-hitting the
  // API, so the mutationFn itself routes through the query cache via
  // queryClient.fetchQuery(), keyed by the SMILES string: fetchQuery
  // returns cached data immediately when a fresh entry for that key
  // already exists, and only calls predict() otherwise. This gets us
  // mutation semantics (loading/error UX, imperative trigger) plus
  // query-cache-backed memoization keyed by variables, without needing
  // a separate manually-triggered useQuery per submission.
  const mutation = useMutation({
    mutationFn: (inputSmiles) =>
      queryClient.fetchQuery({
        queryKey: ["predict", inputSmiles],
        queryFn: () => predict(inputSmiles),
        staleTime: Infinity, // same SMILES within this session -> cached result
      }),
  });

  function runPrediction(inputSmiles) {
    mutation.mutate(inputSmiles);
  }

  const status = mutation.status === "pending" ? "loading" : mutation.status;
  const result = mutation.data;
  const error = mutation.error instanceof ApiError ? mutation.error.message : t("errors.unexpected");

  return (
    <div>
      <h1>{t("predict.title")}</h1>
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
          {t("predict.predicting")}
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
