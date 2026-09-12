#!/usr/bin/env node
// Programmatic WCAG AA contrast check for theme.css design tokens.
// Computes relative luminance / contrast ratio per WCAG 2.x formula and
// checks every meaningful foreground/background pair used in the app
// against the AA thresholds (4.5:1 normal text, 3:1 large text/UI).
//
// Usage: node scripts/check-contrast.mjs

// ---- Token sets (kept in sync with src/theme.css) ----
const LIGHT_TOKENS = {
  bg: "#ffffff",
  surface: "#f5f6f8",
  border: "#e2e4e8",
  text: "#1a1d23",
  "text-muted": "#5b6472",
  accent: "#2563eb",
  "accent-hover": "#1d4ed8",
  success: "#16a34a",
  warning: "#d97706",
  error: "#c81e1e",
};

const DARK_TOKENS = {
  bg: "#0f1115",
  surface: "#1a1d23",
  border: "#2a2e37",
  text: "#e8e9ec",
  "text-muted": "#9aa0ab",
  accent: "#3b82f6",
  "accent-hover": "#2f6fe0",
  success: "#22c55e",
  warning: "#f59e0b",
  error: "#f25454",
};

const WHITE = "#ffffff";

// ---- WCAG relative luminance / contrast ratio ----
function hexToRgb(hex) {
  const clean = hex.replace("#", "");
  const bigint = parseInt(clean, 16);
  return {
    r: (bigint >> 16) & 255,
    g: (bigint >> 8) & 255,
    b: bigint & 255,
  };
}

function channelLuminance(c) {
  const cs = c / 255;
  return cs <= 0.03928 ? cs / 12.92 : Math.pow((cs + 0.055) / 1.055, 2.4);
}

function relativeLuminance(hex) {
  const { r, g, b } = hexToRgb(hex);
  return 0.2126 * channelLuminance(r) + 0.7152 * channelLuminance(g) + 0.0722 * channelLuminance(b);
}

function contrastRatio(hexA, hexB) {
  const lA = relativeLuminance(hexA);
  const lB = relativeLuminance(hexB);
  const lighter = Math.max(lA, lB);
  const darker = Math.min(lA, lB);
  return (lighter + 0.05) / (darker + 0.05);
}

// ---- Pairs to check ----
// "large" = large text / UI component threshold (3:1); otherwise normal text (4.5:1)
function buildPairs(tokens) {
  return [
    { label: "--text on --bg", fg: tokens.text, bg: tokens.bg, kind: "normal" },
    { label: "--text on --surface", fg: tokens.text, bg: tokens.surface, kind: "normal" },
    { label: "--text-muted on --bg", fg: tokens["text-muted"], bg: tokens.bg, kind: "normal" },
    { label: "--text-muted on --surface", fg: tokens["text-muted"], bg: tokens.surface, kind: "normal" },
    // AppShell nav active link: color var(--accent) text directly on header background var(--bg)
    { label: "--accent (nav link) on --bg", fg: tokens.accent, bg: tokens.bg, kind: "normal" },
    // SmilesInput submit button (enabled): white text on var(--accent-hover)
    { label: "white text on --accent-hover (submit button)", fg: WHITE, bg: tokens["accent-hover"], kind: "normal" },
    // SmilesInput submit button (disabled): white text on var(--text-muted).
    // Disabled controls are exempt from WCAG contrast requirements (see
    // "Understanding SC 1.4.3/1.4.11": inactive UI components have no
    // contrast requirement), kept here for visibility/documentation only.
    { label: "white text on --text-muted (disabled button, exempt)", fg: WHITE, bg: tokens["text-muted"], kind: "exempt" },
    // ErrorBanner: var(--error) text + border on var(--surface) background
    { label: "--error text on --surface (error banner)", fg: tokens.error, bg: tokens.surface, kind: "normal" },
    // icon-button (theme toggle / language select): var(--text) on var(--surface), border var(--border)
    { label: "--border on --surface (icon-button border, UI component)", fg: tokens.border, bg: tokens.surface, kind: "large" },
  ];
}

// "exempt" = WCAG explicitly does not require a contrast minimum here
// (e.g. disabled/inactive controls) - reported for visibility only.
const THRESHOLDS = { normal: 4.5, large: 3, exempt: null };

function evaluate(setName, tokens) {
  const pairs = buildPairs(tokens);
  const rows = pairs.map((p) => {
    const ratio = contrastRatio(p.fg, p.bg);
    const threshold = THRESHOLDS[p.kind];
    const pass = threshold === null ? true : ratio >= threshold;
    return { ...p, ratio, threshold, pass };
  });
  return { setName, rows };
}

function printReport(result) {
  console.log(`\n=== ${result.setName} ===`);
  const colWidth = Math.max(...result.rows.map((r) => r.label.length)) + 2;
  for (const row of result.rows) {
    const status = row.kind === "exempt" ? "N/A (exempt)" : row.pass ? "PASS" : "FAIL";
    const thresholdLabel = row.threshold === null ? "n/a" : `${row.threshold}:1`;
    console.log(
      `${row.label.padEnd(colWidth)} ratio=${row.ratio.toFixed(2)}:1  threshold=${thresholdLabel}  [${status}]`,
    );
  }
}

const lightResult = evaluate("Light theme", LIGHT_TOKENS);
const darkResult = evaluate("Dark theme", DARK_TOKENS);

printReport(lightResult);
printReport(darkResult);

const allRows = [...lightResult.rows.map((r) => ({ ...r, set: "light" })), ...darkResult.rows.map((r) => ({ ...r, set: "dark" }))];
const failures = allRows.filter((r) => !r.pass);

console.log(`\nTotal pairs checked: ${allRows.length}, failures: ${failures.length}`);
if (failures.length > 0) {
  process.exitCode = 1;
}

export { contrastRatio, relativeLuminance, LIGHT_TOKENS, DARK_TOKENS, buildPairs, evaluate };
