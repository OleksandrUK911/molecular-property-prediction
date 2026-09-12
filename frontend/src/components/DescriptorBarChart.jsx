import { useState } from "react";
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useTranslation } from "react-i18next";
import { formatNumber } from "../formatters";

// Reference ranges for normalization - see ../frontend-spec/data-visualization.md
const REFERENCE_RANGES = {
  MolWt: [0, 500],
  LogP: [-2, 5],
  TPSA: [0, 140],
  NumHDonors: [0, 5],
  NumHAcceptors: [0, 10],
  NumRotatableBonds: [0, 10],
  RingCount: [0, 6],
};

function normalize(key, value) {
  const [lo, hi] = REFERENCE_RANGES[key];
  return Math.min(1, Math.max(0, (value - lo) / (hi - lo)));
}

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const { name, raw } = payload[0].payload;
  return (
    <div style={{ background: "var(--surface)", border: "1px solid var(--border)", padding: 8, borderRadius: 4 }}>
      <strong>{name}</strong>: {raw}
    </div>
  );
}

export function DescriptorBarChart({ descriptors }) {
  const { t, i18n } = useTranslation();
  const [showTable, setShowTable] = useState(false);

  const data = Object.entries(descriptors).map(([name, raw]) => ({
    name,
    raw: typeof raw === "number" ? formatNumber(raw, i18n.language) : raw,
    normalized: normalize(name, raw),
  }));

  return (
    <div>
      <div style={{ width: "100%", height: 220 }}>
        <ResponsiveContainer>
          <BarChart data={data}>
            <XAxis dataKey="name" tick={{ fill: "var(--text-muted)", fontSize: 11 }} />
            <YAxis domain={[0, 1]} tick={{ fill: "var(--text-muted)", fontSize: 11 }} />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="normalized" fill="var(--accent)" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <button
        type="button"
        className="icon-button"
        onClick={() => setShowTable((prev) => !prev)}
        aria-expanded={showTable}
        aria-controls="descriptor-table"
        style={{ marginTop: 8 }}
      >
        {showTable ? t("results.chart.hideTable") : t("results.chart.showTable")}
      </button>
      {showTable && (
        <div className="table-scroll" style={{ marginTop: 8 }}>
          <table id="descriptor-table" style={{ width: "100%", borderCollapse: "collapse" }}>
            <caption style={{ textAlign: "left", color: "var(--text-muted)", fontSize: 12, marginBottom: 4 }}>
              {t("results.chart.tableCaption")}
            </caption>
            <thead>
              <tr>
                <th style={{ textAlign: "left", borderBottom: "1px solid var(--border)", padding: "4px 8px" }}>
                  {t("results.chart.columnDescriptor")}
                </th>
                <th style={{ textAlign: "left", borderBottom: "1px solid var(--border)", padding: "4px 8px" }}>
                  {t("results.chart.columnRawValue")}
                </th>
                <th style={{ textAlign: "left", borderBottom: "1px solid var(--border)", padding: "4px 8px" }}>
                  {t("results.chart.columnNormalizedValue")}
                </th>
              </tr>
            </thead>
            <tbody>
              {data.map((row) => (
                <tr key={row.name}>
                  <td style={{ padding: "4px 8px", borderBottom: "1px solid var(--border)" }}>
                    {t(`results.descriptors.${row.name}`, row.name)}
                  </td>
                  <td style={{ padding: "4px 8px", borderBottom: "1px solid var(--border)" }}>{row.raw}</td>
                  <td style={{ padding: "4px 8px", borderBottom: "1px solid var(--border)" }}>
                    {formatNumber(row.normalized, i18n.language)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
