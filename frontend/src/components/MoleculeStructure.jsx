export function MoleculeStructure({ svg }) {
  return (
    <div
      role="img"
      aria-label="2D structure of the input molecule"
      style={{
        width: 240,
        height: 240,
        borderRadius: "var(--radius-card)",
        background: "var(--surface)",
        border: "1px solid var(--border)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      {svg ? (
        // eslint-disable-next-line react/no-danger -- trusted, same-origin backend RDKit SVG, not user input
        <div dangerouslySetInnerHTML={{ __html: svg }} />
      ) : (
        <span className="text-muted">Structure preview unavailable</span>
      )}
    </div>
  );
}
