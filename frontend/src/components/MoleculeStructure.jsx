import { useTranslation } from "react-i18next";

export function MoleculeStructure({ svg }) {
  const { t } = useTranslation();
  return (
    <div
      role="img"
      aria-label={t("structure.ariaLabel")}
      style={{
        width: 240,
        height: 240,
        borderRadius: "var(--radius-card)",
        background: "var(--surface)",
        border: "1px solid var(--border)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      {svg ? (
        // eslint-disable-next-line react/no-danger -- trusted, same-origin backend RDKit SVG, not user input
        <div dangerouslySetInnerHTML={{ __html: svg }} />
      ) : (
        <span className="text-muted">{t("structure.unavailable")}</span>
      )}
    </div>
  );
}
