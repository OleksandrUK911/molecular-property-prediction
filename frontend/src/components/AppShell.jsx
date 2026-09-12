import { NavLink, Outlet } from "react-router-dom";

export function AppShell() {
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
          gap: 24,
          alignItems: "center",
          padding: "12px 24px",
          borderBottom: "1px solid var(--border)",
          position: "sticky",
          top: 0,
          background: "var(--bg)",
        }}
      >
        <strong>Molecular Property Prediction</strong>
        <nav aria-label="Main navigation" style={{ display: "flex", gap: 16 }}>
          <NavLink to="/" style={linkStyle} end>Predict</NavLink>
          <NavLink to="/history" style={linkStyle}>History</NavLink>
          <NavLink to="/about" style={linkStyle}>About</NavLink>
        </nav>
      </header>
      <main style={{ maxWidth: 700, margin: "0 auto", padding: "24px 16px" }}>
        <Outlet />
      </main>
    </div>
  );
}
