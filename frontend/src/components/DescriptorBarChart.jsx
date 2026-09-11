import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

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
  const data = Object.entries(descriptors).map(([name, raw]) => ({
    name,
    raw: typeof raw === "number" ? raw.toFixed(2) : raw,
    normalized: normalize(name, raw),
  }));

  return (
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
  );
}
