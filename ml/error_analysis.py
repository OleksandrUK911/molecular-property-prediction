"""Whole-test-set error analysis for the winning model.

Usage:
    python ml/error_analysis.py

Complements the 17-outlier-compound check in ml/evaluate.py with a general
look at the full test set: which compounds have the largest absolute
residuals overall, and whether the worst-predicted molecules skew toward a
particular descriptor range (via a simple |residual| vs. descriptor
correlation, and a worst-10 vs. rest descriptor-mean comparison).

Reads ml/artifacts/xgboost_model.joblib and data/processed/esol_processed.csv.
Writes ml/results/error_analysis_report.md.
"""

from pathlib import Path

import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROCESSED_CSV = ROOT / "data" / "processed" / "esol_processed.csv"
MODEL_PATH = ROOT / "ml" / "artifacts" / "xgboost_model.joblib"
OUTPUT_PATH = ROOT / "ml" / "results" / "error_analysis_report.md"

TOP_N = 10


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
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
