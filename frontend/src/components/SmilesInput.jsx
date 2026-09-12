export function SmilesInput({ value, onChange, onSubmit, disabled }) {
  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit();
      }}
      style={{ display: "flex", gap: 8 }}
    >
      <label htmlFor="smiles-input" style={{ position: "absolute", left: -9999 }}>
        SMILES string
      </label>
      <input
        id="smiles-input"
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="e.g. CC(=O)Oc1ccccc1C(=O)O"
        aria-label="SMILES string"
        disabled={disabled}
        style={{
          flex: 1,
          padding: "8px 12px",
          borderRadius: "var(--radius-card)",
          border: "1px solid var(--border)",
          background: "var(--surface)",
          color: "var(--text)",
        }}
      />
      <button
        type="submit"
        disabled={disabled || !value.trim()}
        style={{
          padding: "8px 20px",
          borderRadius: "var(--radius-card)",
          border: "none",
          background: disabled ? "var(--text-muted)" : "var(--accent)",
          color: "white",
          cursor: disabled ? "not-allowed" : "pointer",
        }}
      >
        Predict
      </button>
    </form>
  );
}
