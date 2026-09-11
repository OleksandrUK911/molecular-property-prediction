import { useEffect, useState } from "react";
import { getModelInfo } from "../api";

export function AboutPage() {
  const [info, setInfo] = useState(null);

  useEffect(() => {
    getModelInfo().then(setInfo).catch(() => setInfo(null));
  }, []);

  return (
    <div>
      <h1>About</h1>
      <p>
        SMILES → RDKit descriptors → XGBoost → predicted aqueous solubility
        (log mol/L), trained on the ESOL (Delaney) dataset.
      </p>

      <h2>Metrics</h2>
      {info ? (
        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              <th style={{ textAlign: "left" }}>Split</th>
              <th>RMSE</th>
              <th>MAE</th>
              <th>R²</th>
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
      ) : (
        <p className="text-muted">Loading model metrics…</p>
      )}

      <h2>Known limitations</h2>
      <ul>
        {(info?.known_limitations || []).map((limitation) => (
          <li key={limitation}>{limitation}</li>
        ))}
      </ul>

      <h2>Disclaimer</h2>
      <p className="text-muted">
        Research/educational project. Not for clinical or production chemistry use.
      </p>
    </div>
  );
}
