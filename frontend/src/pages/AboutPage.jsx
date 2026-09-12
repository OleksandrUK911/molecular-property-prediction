import { useQuery } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { getModelInfo } from "../api";

export function AboutPage() {
  const { t } = useTranslation();

  // Same info/null behavior as before: on error `info` stays null (via
  // `data` being undefined) and the UI falls back to the loading-metrics
  // copy, matching the original catch(() => setInfo(null)) contract.
  const { data: info } = useQuery({
    queryKey: ["modelInfo"],
    queryFn: getModelInfo,
  });

  return (
    <div>
      <h1>{t("about.title")}</h1>
      <p>{t("about.description")}</p>

      <h2>{t("about.metricsTitle")}</h2>
      {info ? (
        <div className="table-scroll">
          <table style={{ width: "100%", borderCollapse: "collapse", minWidth: 360 }}>
            <thead>
              <tr>
                <th style={{ textAlign: "left" }}>{t("about.columnSplit")}</th>
                <th>{t("about.columnRmse")}</th>
                <th>{t("about.columnMae")}</th>
                <th>{t("about.columnR2")}</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(info.metrics).map(([split, m]) => (
                <tr key={split}>
                  <td>{split}</td>
                  <td>{m.rmse}</td>
                  <td>{m.mae}</td>
                  <td>{m.r2}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p className="text-muted">{t("about.loadingMetrics")}</p>
      )}

      <h2>{t("about.limitationsTitle")}</h2>
      <ul>
        {(info?.known_limitations || []).map((limitation) => (
          <li key={limitation}>{limitation}</li>
        ))}
      </ul>

      <h2>{t("about.disclaimerTitle")}</h2>
      <p className="text-muted">{t("about.disclaimerText")}</p>
    </div>
  );
}
