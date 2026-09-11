import { Link } from "react-router-dom";

// GET /history isn't implemented on the backend yet (needs the DB schema
// from backend/TODO_database.md) - always render the empty state honestly
// rather than fabricate data.
export function HistoryPage() {
  return (
    <div style={{ textAlign: "center", marginTop: 48 }}>
      <h1>Prediction history</h1>
      <p className="text-muted">No predictions yet — history storage isn't wired up on the backend yet.</p>
      <Link to="/" style={{ color: "var(--accent)" }}>
        Make your first prediction
      </Link>
    </div>
  );
}
