import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { ApiError, getHistory } from "../api";
import { ErrorBanner } from "../components/ErrorBanner";

function truncateSmiles(smiles, max = 24) {
  return smiles.length > max ? `${smiles.slice(0, max)}…` : smiles;
}

export function HistoryPage() {
  const { t } = useTranslation();
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
        setError(e instanceof ApiError ? e.message : t("errors.unexpected"));
        setStatus("error");
      });
  }

  useEffect(load, []);

  if (status === "loading") {
    return (
      <div>
        <h1>{t("history.title")}</h1>
        <p className="text-muted">{t("history.loading")}</p>
      </div>
    );
  }

  if (status === "error") {
    return (
      <div>
        <h1>{t("history.title")}</h1>
        <ErrorBanner message={error} onRetry={load} />
      </div>
    );
  }

  if (rows.length === 0) {
    return (
      <div style={{ textAlign: "center", marginTop: 48 }}>
        <h1>{t("history.title")}</h1>
        <p className="text-muted">{t("history.empty")}</p>
        <Link to="/" style={{ color: "var(--accent)" }}>
          {t("history.firstPrediction")}
        </Link>
      </div>
    );
  }

  return (
    <div>
      <h1>{t("history.title")}</h1>
      <div className="table-scroll">
        <table style={{ width: "100%", borderCollapse: "collapse", minWidth: 480 }}>
          <thead>
            <tr style={{ borderBottom: "1px solid var(--border)" }}>
              <th style={{ textAlign: "left", padding: "8px 4px" }}>{t("history.columnSmiles")}</th>
              <th style={{ textAlign: "right", padding: "8px 4px" }}>{t("history.columnPredicted")}</th>
              <th style={{ textAlign: "left", padding: "8px 4px" }}>{t("history.columnDate")}</th>
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
                    {t("history.viewButton")}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
