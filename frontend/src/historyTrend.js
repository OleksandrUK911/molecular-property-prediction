import { formatDate } from "./formatters";

export const TREND_MAX_POINTS = 20;

// The API returns history newest-first, but charting needs chronological
// (oldest-first) order, capped to the most recent TREND_MAX_POINTS entries
// so the chart stays legible even when history has grown large.
export function getTrendChartData(rows, language, maxPoints = TREND_MAX_POINTS) {
  return rows
    .slice(0, maxPoints)
    .slice()
    .reverse()
    .map((row) => ({
      created_at: row.created_at,
      predicted_target: row.predicted_target,
      label: formatDate(row.created_at, language),
    }));
}
