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
from sklearn.inspection import PartialDependenceDisplay

ROOT = Path(__file__).resolve().parent.parent
PROCESSED_CSV = ROOT / "data" / "processed" / "esol_processed.csv"
MODEL_PATH = ROOT / "ml" / "artifacts" / "xgboost_model.joblib"
REPORT_PATH = ROOT / "ml" / "results" / "interpretability_report.md"
PLOT_PATH = ROOT / "ml" / "results" / "shap_summary.png"
PDP_PLOT_PATH = ROOT / "ml" / "results" / "pdp_plots.png"

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

    # Native XGBoost feature importance (gain-based), compared side by side
    # with the SHAP ranking above - do the two methods agree on what matters?
    native_importance = (
        pd.Series(model.feature_importances_, index=feature_names)
        .sort_values(ascending=False)
    )

    lines = ["# Interpretability report (SHAP, winner: xgboost_tuned)\n\n"]
    lines.append("## Global feature importance (mean |SHAP value| on test set)\n\n")
    for name, value in global_importance.items():
        lines.append(f"- {name}: {value:.3f}\n")
    lines.append(f"\n![SHAP summary]({PLOT_PATH.name})\n")

    lines.append("\n## SHAP vs native XGBoost feature importance\n\n")
    lines.append(
        "Native importance is XGBoost's built-in `.feature_importances_` "
        "(gain-based: average improvement in the loss function attributable "
        "to each feature across all splits that use it), computed on the "
        "same fitted model, no test data needed. Ranks are 1 = most "
        "important for each method.\n\n"
    )
    shap_rank = {name: i + 1 for i, name in enumerate(global_importance.index)}
    native_rank = {name: i + 1 for i, name in enumerate(native_importance.index)}
    lines.append("| Feature | SHAP mean\\|value\\| | SHAP rank | XGBoost gain importance | Native rank |\n")
    lines.append("|---|---|---|---|---|\n")
    for name in feature_names:
        lines.append(
            f"| {name} | {global_importance[name]:.3f} | {shap_rank[name]} | "
            f"{native_importance[name]:.3f} | {native_rank[name]} |\n"
        )
    top_shap = global_importance.index[0]
    top_native = native_importance.index[0]
    if top_shap == top_native:
        lines.append(
            f"\n**Agreement:** both methods rank `{top_shap}` as the single "
            "most important feature.\n"
        )
    else:
        lines.append(
            f"\n**Disagreement on top feature:** SHAP ranks `{top_shap}` "
            f"highest, while native XGBoost gain ranks `{top_native}` "
            "highest. This can happen because gain-based importance is "
            "biased toward high-cardinality/frequently-split features and "
            "ignores the direction and interaction effects that SHAP "
            "accounts for.\n"
        )

    # Partial dependence plots for the top 2 features by this comparison
    # (whichever method's top-2 differ, prefer the SHAP ranking as the
    # primary signal since it accounts for interactions - but report both
    # rankings above regardless).
    top2 = list(global_importance.index[:2])
    _fig, ax = plt.subplots(1, len(top2), figsize=(6 * len(top2), 5))
    PartialDependenceDisplay.from_estimator(
        model, X_test, top2, feature_names=feature_names, ax=ax if len(top2) > 1 else [ax]
    )
    plt.tight_layout()
    plt.savefig(PDP_PLOT_PATH, dpi=120)
    plt.close()

    lines.append(
        f"\n## Partial dependence plots (top 2 features: {', '.join(top2)})\n\n"
    )
    lines.append(
        "Partial dependence shows the marginal effect of each feature on the "
        "predicted log solubility, averaging out the other features, using "
        "the same fitted `xgboost_tuned` model evaluated on the test set.\n\n"
    )
    lines.append(f"![Partial dependence plots]({PDP_PLOT_PATH.name})\n")

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
