import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { getModelInfo } from "../api";

export function AboutPage() {
  const { t } = useTranslation();
  const [info, setInfo] = useState(null);

  useEffect(() => {
    getModelInfo().then(setInfo).catch(() => setInfo(null));
  }, []);

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
