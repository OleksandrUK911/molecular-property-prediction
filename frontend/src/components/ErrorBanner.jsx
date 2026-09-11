export function ErrorBanner({ message, onRetry }) {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "8px 12px",
        borderRadius: "var(--radius-card)",
        background: "var(--surface)",
        border: "1px solid var(--error)",
        color: "var(--error)",
        marginTop: 8,
      }}
    >
      <span>⚠ {message}</span>
      {onRetry && (
        <button
          type="button"
          onClick={onRetry}
          style={{ border: "1px solid var(--error)", background: "none", color: "var(--error)", borderRadius: "var(--radius-chip)", padding: "2px 10px", cursor: "pointer" }}
        >
          Retry
        </button>
      )}
    </div>
  );
}
