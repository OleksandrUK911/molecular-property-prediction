import { useEffect, useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { applyTheme, getStoredTheme, setStoredTheme } from "../theme";
import { setStoredLanguage, SUPPORTED_LANGUAGES } from "../i18n";
import { ErrorBoundary } from "./ErrorBoundary";

function getSystemPrefersDark() {
  return typeof window !== "undefined" && window.matchMedia?.("(prefers-color-scheme: dark)").matches;
}

export function AppShell() {
  const { t, i18n } = useTranslation();
  // null = no explicit override yet, follow the OS preference (theme.css
  // handles that case via the prefers-color-scheme media query).
  const [theme, setTheme] = useState(() => getStoredTheme());

  useEffect(() => {
    applyTheme(theme);
  }, [theme]);

  function toggleTheme() {
    const current = theme || (getSystemPrefersDark() ? "dark" : "light");
    const next = current === "dark" ? "light" : "dark";
    setStoredTheme(next);
    setTheme(next);
  }

  function changeLanguage(language) {
    setStoredLanguage(language);
    i18n.changeLanguage(language);
  }

  const isDark = theme ? theme === "dark" : getSystemPrefersDark();

  const linkStyle = ({ isActive }) => ({
    color: isActive ? "var(--accent)" : "var(--text)",
    fontWeight: isActive ? 600 : 400,
    textDecoration: "none",
  });

  return (
    <div>
      <header
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: 16,
          alignItems: "center",
          padding: "12px 24px",
          borderBottom: "1px solid var(--border)",
          position: "sticky",
          top: 0,
          background: "var(--bg)",
        }}
      >
        <strong>{t("common.appTitle")}</strong>
        <nav aria-label={t("common.mainNavigation")} style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
          <NavLink to="/" style={linkStyle} end>{t("nav.predict")}</NavLink>
          <NavLink to="/history" style={linkStyle}>{t("nav.history")}</NavLink>
          <NavLink to="/about" style={linkStyle}>{t("nav.about")}</NavLink>
        </nav>
        <div style={{ display: "flex", gap: 8, alignItems: "center", marginLeft: "auto" }}>
          <button
            type="button"
            className="icon-button"
            onClick={toggleTheme}
            aria-label={isDark ? t("theme.toggleToLight") : t("theme.toggleToDark")}
            title={isDark ? t("theme.toggleToLight") : t("theme.toggleToDark")}
          >
            {isDark ? "☀️" : "\u{1F319}"}
          </button>
          <select
            aria-label={t("language.label")}
            value={i18n.resolvedLanguage || i18n.language}
            onChange={(e) => changeLanguage(e.target.value)}
            className="icon-button"
          >
            {SUPPORTED_LANGUAGES.map((lng) => (
              <option key={lng} value={lng}>
                {lng.toUpperCase()}
              </option>
            ))}
          </select>
        </div>
      </header>
      <main style={{ maxWidth: 700, margin: "0 auto", padding: "24px 16px" }}>
        <ErrorBoundary>
          <Outlet />
        </ErrorBoundary>
      </main>
    </div>
  );
}
