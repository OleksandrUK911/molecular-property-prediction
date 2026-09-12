import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

export function MoleculeStructure({ svg }) {
  const { t } = useTranslation();
  const [isZoomed, setIsZoomed] = useState(false);

  useEffect(() => {
    if (!isZoomed) return undefined;
    function handleKeyDown(event) {
      if (event.key === "Escape") {
        setIsZoomed(false);
      }
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isZoomed]);

  const boxStyle = {
    width: 240,
    height: 240,
    borderRadius: "var(--radius-card)",
    background: "var(--surface)",
    border: "1px solid var(--border)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  };

  if (!svg) {
    return (
      <div role="img" aria-label={t("structure.ariaLabel")} style={boxStyle}>
        <span className="text-muted">{t("structure.unavailable")}</span>
      </div>
    );
  }

  return (
    <>
      <button
        type="button"
        aria-label={t("structure.zoomTrigger")}
        onClick={() => setIsZoomed(true)}
        style={{
          ...boxStyle,
          padding: 0,
          cursor: "zoom-in",
        }}
      >
        {/* eslint-disable-next-line react/no-danger -- trusted, same-origin backend RDKit SVG, not user input */}
        <div dangerouslySetInnerHTML={{ __html: svg }} />
      </button>

      {isZoomed && (
        <div
          role="presentation"
          onClick={() => setIsZoomed(false)}
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0, 0, 0, 0.6)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1000,
          }}
        >
          <div
            role="dialog"
            aria-modal="true"
            aria-label={t("structure.ariaLabel")}
            onClick={(event) => event.stopPropagation()}
            style={{
              position: "relative",
              width: "min(480px, 90vw)",
              height: "min(480px, 90vw)",
              background: "var(--surface)",
              border: "1px solid var(--border)",
              borderRadius: "var(--radius-card)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <button
              type="button"
              onClick={() => setIsZoomed(false)}
              aria-label={t("structure.closeZoom")}
              className="icon-button"
              style={{
                position: "absolute",
                top: 8,
                right: 8,
              }}
            >
              {t("structure.closeZoomSymbol")}
            </button>
            {/* eslint-disable-next-line react/no-danger -- trusted, same-origin backend RDKit SVG, not user input */}
            <div dangerouslySetInnerHTML={{ __html: svg }} />
          </div>
        </div>
      )}
    </>
  );
}
