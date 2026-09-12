import { useQuery } from "@tanstack/react-query";
import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { ApiError, getHistory } from "../api";
import { ErrorBanner } from "../components/ErrorBanner";
import { formatDate, formatNumber } from "../formatters";
import { getTrendChartData } from "../historyTrend";

function truncateSmiles(smiles, max = 24) {
  return smiles.length > max ? `${smiles.slice(0, max)}…` : smiles;
}

function HistoryTrendChart({ rows, language, t }) {
  const chartData = getTrendChartData(rows, language);

  return (
    <div style={{ marginBottom: 24 }}>
      <h2>{t("history.trendTitle")}</h2>
      <div
        role="img"
        aria-label={t("history.trendAriaLabel")}
        style={{ width: "100%", height: 240 }}
      >
        <ResponsiveContainer>
          <LineChart data={chartData}>
            <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" />
            <XAxis dataKey="label" tick={{ fill: "var(--text-muted)", fontSize: 11 }} />
            <YAxis
              tick={{ fill: "var(--text-muted)", fontSize: 11 }}
              tickFormatter={(value) => formatNumber(value, language)}
            />
            <Tooltip
              formatter={(value) => formatNumber(value, language)}
              contentStyle={{ background: "var(--surface)", border: "1px solid var(--border)" }}
            />
            <Line
              type="monotone"
              dataKey="predicted_target"
              stroke="var(--accent)"
              dot={{ fill: "var(--accent)" }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export function HistoryPage() {
  const { t, i18n } = useTranslation();
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
      {rows.length >= 2 && <HistoryTrendChart rows={rows} language={i18n.language} t={t} />}
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
                <td style={{ textAlign: "right", padding: "8px 4px" }}>
                  {formatNumber(row.predicted_target, i18n.language)}
                </td>
                <td style={{ padding: "8px 4px" }} className="text-muted">
                  {formatDate(row.created_at, i18n.language)}
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
