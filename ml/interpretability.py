"""SHAP feature importance for the winning model (xgboost_tuned), global
and per-molecule, per ml/TODO_interpretability.md.

Usage:
    python ml/interpretability.py

Reads ml/artifacts/xgboost_model.joblib + data/processed/esol_processed.csv.
Writes ml/results/interpretability_report.md and a summary plot PNG.
"""

from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")  # headless - no display available in CI/containers
import matplotlib.pyplot as plt
import pandas as pd
import shap

ROOT = Path(__file__).resolve().parent.parent
PROCESSED_CSV = ROOT / "data" / "processed" / "esol_processed.csv"
MODEL_PATH = ROOT / "ml" / "artifacts" / "xgboost_model.joblib"
REPORT_PATH = ROOT / "ml" / "results" / "interpretability_report.md"
PLOT_PATH = ROOT / "ml" / "results" / "shap_summary.png"

# A couple of named molecules to explain individually - same examples used
# in frontend-spec/predict-page.md's "Try an example" chips, for continuity.
EXAMPLE_MOLECULES = {
    "Aspirin": "CC(=O)Oc1ccccc1C(=O)O",
    "Caffeine": "Cn1cnc2c1c(=O)n(C)c(=O)n2C",
}


def main() -> None:
    df = pd.read_csv(PROCESSED_CSV)
    bundle = joblib.load(MODEL_PATH)
    model, feature_names = bundle["model"], bundle["feature_names"]

    X_test = df[df["split"] == "test"][feature_names]

    explainer = shap.TreeExplainer(model)
    shap_values = explainer(X_test)

    global_importance = (
        pd.Series(abs(shap_values.values).mean(axis=0), index=feature_names)
        .sort_values(ascending=False)
    )

    plt.figure()
    shap.summary_plot(shap_values, X_test, show=False)
    plt.tight_layout()
    plt.savefig(PLOT_PATH, dpi=120)
    plt.close()

    lines = ["# Interpretability report (SHAP, winner: xgboost_tuned)\n\n"]
    lines.append("## Global feature importance (mean |SHAP value| on test set)\n\n")
    for name, value in global_importance.items():
        lines.append(f"- {name}: {value:.3f}\n")
    lines.append(f"\n![SHAP summary]({PLOT_PATH.name})\n")

    lines.append("\n## Per-molecule explanations\n\n")
    for name, smiles in EXAMPLE_MOLECULES.items():
        from rdkit import Chem
        from rdkit.Chem import Descriptors

        mol = Chem.MolFromSmiles(smiles)
        descriptor_funcs = {
            "MolWt": Descriptors.MolWt, "LogP": Descriptors.MolLogP, "TPSA": Descriptors.TPSA,
            "NumHDonors": Descriptors.NumHDonors, "NumHAcceptors": Descriptors.NumHAcceptors,
            "NumRotatableBonds": Descriptors.NumRotatableBonds, "RingCount": Descriptors.RingCount,
        }
        row = pd.DataFrame([{n: descriptor_funcs[n](mol) for n in feature_names}])
        row_shap = explainer(row)
        prediction = float(model.predict(row)[0])

        lines.append(f"### {name} (`{smiles}`)\n")
        lines.append(f"Predicted: {prediction:.2f} log(mol/L)\n\n")
        contributions = sorted(
            zip(feature_names, row_shap.values[0]), key=lambda x: abs(x[1]), reverse=True
        )
        for feat, contrib in contributions:
            direction = "pushes lower" if contrib < 0 else "pushes higher"
            lines.append(f"- {feat} ({row[feat].iloc[0]:.2f}): {contrib:+.3f} ({direction})\n")
        lines.append("\n")

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("".join(lines), encoding="utf-8")
    print("".join(lines))
    print(f"Wrote {REPORT_PATH}\nWrote {PLOT_PATH}")


if __name__ == "__main__":
    main()
