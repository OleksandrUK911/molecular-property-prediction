const DESCRIPTOR_LABELS = {
  MolWt: "Molecular weight",
  LogP: "LogP",
  TPSA: "TPSA",
  NumHDonors: "H-Bond Donors",
  NumHAcceptors: "H-Bond Acceptors",
  NumRotatableBonds: "Rotatable Bonds",
  RingCount: "Num Rings",
};

export function ResultsCard({ result }) {
  return (
    <div
      style={{
        padding: 16,
        borderRadius: "var(--radius-card)",
        background: "var(--surface)",
        border: "1px solid var(--border)",
      }}
    >
      <h2>Predicted solubility: {result.predicted_target.toFixed(2)} log(mol/L)</h2>
      <hr style={{ border: "none", borderTop: "1px solid var(--border)", margin: "12px 0" }} />
      {Object.entries(result.descriptors).map(([key, value]) => (
        <div key={key} style={{ display: "flex", justifyContent: "space-between", padding: "4px 0" }}>
          <span className="text-muted">{DESCRIPTOR_LABELS[key] || key}</span>
          <span>{typeof value === "number" ? value.toFixed(2) : value}</span>
        </div>
      ))}
      {result.confidence === null && (
        <p className="text-muted" style={{ marginTop: 12, fontSize: 12 }}>
          This model does not provide a calibrated confidence score (point prediction only).
        </p>
      )}
    </div>
  );
}
