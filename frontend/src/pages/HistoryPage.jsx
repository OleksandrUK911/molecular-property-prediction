import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ApiError, getHistory } from "../api";
import { ErrorBanner } from "../components/ErrorBanner";

function truncateSmiles(smiles, max = 24) {
  return smiles.length > max ? `${smiles.slice(0, max)}…` : smiles;
}

export function HistoryPage() {
  const [status, setStatus] = useState("loading"); // loading | success | error
  const [rows, setRows] = useState([]);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  function load() {
    setStatus("loading");
    getHistory()
      .then((data) => {
        setRows(data);
        setStatus("success");
      })
      .catch((e) => {
        setError(e instanceof ApiError ? e.message : "Unexpected error");
        setStatus("error");
      });
  }

  useEffect(load, []);

  if (status === "loading") {
    return (
      <div>
        <h1>Prediction history</h1>
        <p className="text-muted">Loading…</p>
      </div>
    );
  }

  if (status === "error") {
    return (
      <div>
        <h1>Prediction history</h1>
        <ErrorBanner message={error} onRetry={load} />
      </div>
    );
  }

  if (rows.length === 0) {
    return (
      <div style={{ textAlign: "center", marginTop: 48 }}>
        <h1>Prediction history</h1>
        <p className="text-muted">No predictions yet.</p>
        <Link to="/" style={{ color: "var(--accent)" }}>
          Make your first prediction
        </Link>
      </div>
    );
  }

  return (
    <div>
      <h1>Prediction history</h1>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr style={{ borderBottom: "1px solid var(--border)" }}>
            <th style={{ textAlign: "left", padding: "8px 4px" }}>SMILES</th>
            <th style={{ textAlign: "right", padding: "8px 4px" }}>Predicted</th>
            <th style={{ textAlign: "left", padding: "8px 4px" }}>Date</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.id} style={{ borderBottom: "1px solid var(--border)" }}>
              <td title={row.smiles} style={{ padding: "8px 4px" }}>
                {truncateSmiles(row.smiles)}
              </td>
              <td style={{ textAlign: "right", padding: "8px 4px" }}>{row.predicted_target.toFixed(2)}</td>
              <td style={{ padding: "8px 4px" }} className="text-muted">
                {new Date(row.created_at).toLocaleString()}
              </td>
              <td style={{ padding: "8px 4px" }}>
                <button
                  type="button"
                  onClick={() => navigate("/", { state: { smiles: row.smiles } })}
                  style={{ background: "none", border: "none", color: "var(--accent)", cursor: "pointer" }}
                >
                  View
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
