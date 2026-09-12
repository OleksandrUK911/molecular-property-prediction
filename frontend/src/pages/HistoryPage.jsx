import { useQuery } from "@tanstack/react-query";
import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { ApiError, getHistory } from "../api";
import { ErrorBanner } from "../components/ErrorBanner";

function truncateSmiles(smiles, max = 24) {
  return smiles.length > max ? `${smiles.slice(0, max)}…` : smiles;
}

export function HistoryPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();

  // useQuery replaces the manual load()/useState/useEffect trio: React
  // Query owns the loading/error/data state machine, which is also what
  // eliminates the old set-state-in-effect and exhaustive-deps warnings
  // (there's no longer a raw useEffect calling setState here at all).
  const { status, data, error, refetch } = useQuery({
    queryKey: ["history"],
    queryFn: getHistory,
  });
  const rows = data ?? [];

  if (status === "pending") {
    return (
      <div>
        <h1>{t("history.title")}</h1>
        <p className="text-muted">{t("history.loading")}</p>
      </div>
    );
  }

  if (status === "error") {
    const message = error instanceof ApiError ? error.message : t("errors.unexpected");
    return (
      <div>
        <h1>{t("history.title")}</h1>
        <ErrorBanner message={message} onRetry={refetch} />
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
