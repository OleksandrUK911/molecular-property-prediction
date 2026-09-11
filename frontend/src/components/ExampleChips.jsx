const EXAMPLES = [
  { label: "Aspirin", smiles: "CC(=O)Oc1ccccc1C(=O)O" },
  { label: "Caffeine", smiles: "Cn1cnc2c1c(=O)n(C)c(=O)n2C" },
  { label: "Ibuprofen", smiles: "CC(C)Cc1ccc(cc1)C(C)C(=O)O" },
];

export function ExampleChips({ onPick, disabled }) {
  return (
    <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
      <span className="text-muted">Try an example:</span>
      {EXAMPLES.map((ex) => (
        <button
          key={ex.label}
          type="button"
          disabled={disabled}
          onClick={() => onPick(ex.smiles)}
          style={{
            padding: "4px 10px",
            borderRadius: "var(--radius-chip)",
            border: "1px solid var(--border)",
            background: "var(--surface)",
            color: "var(--text)",
            cursor: disabled ? "not-allowed" : "pointer",
          }}
        >
          {ex.label}
        </button>
      ))}
    </div>
  );
}
