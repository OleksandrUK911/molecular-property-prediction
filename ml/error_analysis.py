"""Whole-test-set error analysis for the winning model.

Usage:
    python ml/error_analysis.py

Complements the 17-outlier-compound check in ml/evaluate.py with a general
look at the full test set: which compounds have the largest absolute
residuals overall, and whether the worst-predicted molecules skew toward a
particular descriptor range (via a simple |residual| vs. descriptor
correlation, and a worst-10 vs. rest descriptor-mean comparison).

Also renders the top-5 (of the top-10) worst-residual molecules as 2D
structures with their actual/predicted/residual values, so the worst cases
identified numerically here are also visible as actual chemical structures.

Reads ml/artifacts/xgboost_model.joblib and data/processed/esol_processed.csv.
Writes ml/results/error_analysis_report.md and ml/results/worst_predictions.png.
"""

from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")  # headless - no display available in CI/containers
import matplotlib.pyplot as plt
import pandas as pd
from rdkit import Chem
from rdkit.Chem import Draw

ROOT = Path(__file__).resolve().parent.parent
PROCESSED_CSV = ROOT / "data" / "processed" / "esol_processed.csv"
MODEL_PATH = ROOT / "ml" / "artifacts" / "xgboost_model.joblib"
OUTPUT_PATH = ROOT / "ml" / "results" / "error_analysis_report.md"
WORST_PLOT_PATH = ROOT / "ml" / "results" / "worst_predictions.png"

TOP_N = 10
WORST_PLOT_N = 5


def plot_worst_predictions(worst: pd.DataFrame) -> None:
    """Render 2D structures for the top-N worst-residual molecules, each
    captioned with compound_id, actual, predicted and residual values.
    """
    top = worst.head(WORST_PLOT_N)
    fig, axes = plt.subplots(1, len(top), figsize=(4 * len(top), 5))
    if len(top) == 1:
        axes = [axes]
    for ax, (_, row) in zip(axes, top.iterrows()):
        mol = Chem.MolFromSmiles(row["smiles"])
        img = Draw.MolToImage(mol, size=(300, 300)) if mol is not None else None
        if img is not None:
            ax.imshow(img)
        ax.axis("off")
        ax.set_title(
            f"{row['compound_id']}\n"
            f"actual={row['target']:.2f}  pred={row['predicted']:.2f}\n"
            f"residual={row['residual']:+.2f}",
            fontsize=9,
        )
    fig.suptitle(f"Top {len(top)} worst-predicted test compounds (structures)")
    plt.tight_layout()
    plt.savefig(WORST_PLOT_PATH, dpi=120)
    plt.close(fig)


def main() -> None:
    df = pd.read_csv(PROCESSED_CSV)
    bundle = joblib.load(MODEL_PATH)
    model, feature_names = bundle["model"], bundle["feature_names"]

    test = df[df["split"] == "test"].copy()
    test["predicted"] = model.predict(test[feature_names])
    test["residual"] = test["target"] - test["predicted"]
    test["abs_residual"] = test["residual"].abs()

    worst = test.sort_values("abs_residual", ascending=False).head(TOP_N)
    rest = test.drop(worst.index)

    plot_worst_predictions(worst)

    lines = ["# Whole-test-set error analysis\n\n"]
    lines.append(
        f"Test set: {len(test)} compounds. This looks beyond the 17 known "
        "IQR-outlier compounds (see `ml/results/evaluation_report.md`) at "
        "error patterns across the *whole* test set.\n\n"
    )

    lines.append(f"## Top {TOP_N} worst-predicted test compounds (by |residual|)\n\n")
    lines.append("| Compound | Actual | Predicted | Residual | MolWt | LogP | TPSA |\n|---|---|---|---|---|---|---|\n")
    for _, row in worst.iterrows():
        lines.append(
            f"| {row['compound_id']} | {row['target']:.2f} | {row['predicted']:.2f} | "
            f"{row['residual']:+.2f} | {row['MolWt']:.1f} | {row['LogP']:.2f} | {row['TPSA']:.1f} |\n"
        )

    lines.append(f"\nWorst-{TOP_N} MAE: {worst['abs_residual'].mean():.3f} vs. rest-of-test MAE: {rest['abs_residual'].mean():.3f} "
                  f"vs. whole-test MAE: {test['abs_residual'].mean():.3f}\n")

    lines.append(
        f"\n![Top {WORST_PLOT_N} worst-predicted molecules, structures with "
        f"actual/predicted/residual]({WORST_PLOT_PATH.name})\n"
    )

    descriptor_columns = feature_names
    lines.append("\n## Correlation of |residual| with each descriptor (whole test set)\n\n")
    lines.append("| Descriptor | Pearson r with |residual| |\n|---|---|\n")
    correlations = {}
    for col in descriptor_columns:
        corr = test[[col, "abs_residual"]].corr().iloc[0, 1]
        correlations[col] = float(corr)
        lines.append(f"| {col} | {corr:+.3f} |\n")

    lines.append(f"\n## Descriptor means: worst-{TOP_N} vs. rest of test set\n\n")
    lines.append("| Descriptor | Worst-10 mean | Rest mean | Difference |\n|---|---|---|---|\n")
    diffs = {}
    for col in descriptor_columns:
        worst_mean = worst[col].mean()
        rest_mean = rest[col].mean()
        diffs[col] = worst_mean - rest_mean
        lines.append(f"| {col} | {worst_mean:.2f} | {rest_mean:.2f} | {worst_mean - rest_mean:+.2f} |\n")

    strongest_corr = max(correlations, key=lambda k: abs(correlations[k]))
    strongest_diff = max(diffs, key=lambda k: abs(diffs[k]))

    lines.append("\n## Pattern summary\n\n")
    lines.append(
        f"Strongest |residual| correlation: **{strongest_corr}** (r={correlations[strongest_corr]:+.3f}). "
        f"Largest worst-10-vs-rest mean gap: **{strongest_diff}** "
        f"({diffs[strongest_diff]:+.2f}).\n\n"
    )
    if abs(correlations[strongest_corr]) > 0.3:
        lines.append(
            f"There is a moderate-to-strong relationship between {strongest_corr} and prediction "
            f"error on this test set - predictions are less reliable at the "
            f"{'high' if diffs.get(strongest_corr, 0) > 0 else 'low'} end of this descriptor's range. "
            "This is broadly consistent with the applicability-domain limitation already documented "
            "for large/hydrophobic outlier compounds in `ml/results/evaluation_report.md` and "
            "`models/production/metadata.json`.\n"
        )
    else:
        lines.append(
            "No descriptor shows a strong correlation with prediction error on this test set - "
            "errors look fairly evenly spread across the descriptor ranges rather than concentrated "
            "in one region. The worst-predicted compounds may be individually unusual (e.g. the "
            "known PCB/PAH/long-chain-alkane outliers) rather than following one systematic "
            "descriptor-range pattern.\n"
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text("".join(lines), encoding="utf-8")

    print("".join(lines))
    print(f"Wrote {OUTPUT_PATH}\nWrote {WORST_PLOT_PATH}")


if __name__ == "__main__":
    main()
