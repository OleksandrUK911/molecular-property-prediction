import { useTranslation } from "react-i18next";

const DESCRIPTOR_KEYS = {
  MolWt: "MolWt",
  LogP: "LogP",
  TPSA: "TPSA",
  NumHDonors: "NumHDonors",
  NumHAcceptors: "NumHAcceptors",
  NumRotatableBonds: "NumRotatableBonds",
  RingCount: "RingCount",
};

export function ResultsCard({ result }) {
  const { t } = useTranslation();
  return (
    <div
      style={{
        padding: 16,
        borderRadius: "var(--radius-card)",
        background: "var(--surface)",
        border: "1px solid var(--border)",
      }}
    >
      <h2>{t("results.predictedSolubility", { value: result.predicted_target.toFixed(2) })}</h2>
      <hr style={{ border: "none", borderTop: "1px solid var(--border)", margin: "12px 0" }} />
      {Object.entries(result.descriptors).map(([key, value]) => (
        <div key={key} style={{ display: "flex", justifyContent: "space-between", padding: "4px 0" }}>
          <span className="text-muted">
            {DESCRIPTOR_KEYS[key] ? t(`results.descriptors.${DESCRIPTOR_KEYS[key]}`) : key}
          </span>
          <span>{typeof value === "number" ? value.toFixed(2) : value}</span>
        </div>
      ))}
      {result.confidence === null && (
        <p className="text-muted" style={{ marginTop: 12, fontSize: 12 }}>
          {t("results.noConfidence")}
        </p>
      )}
    </div>
  );
}
