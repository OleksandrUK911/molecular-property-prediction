"""Evaluate the winning model: overfitting check (train vs val/test) and
residuals specifically on the 17 IQR-flagged outlier compounds identified
in ml/preprocess.py (kept in the dataset - see data/README.md).

Usage:
    python ml/evaluate.py

Reads ml/artifacts/xgboost_model.joblib and data/processed/{esol_processed.csv,report.md}.
Writes ml/results/evaluation_report.md.
"""

import re
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT = Path(__file__).resolve().parent.parent
PROCESSED_CSV = ROOT / "data" / "processed" / "esol_processed.csv"
DATA_REPORT = ROOT / "data" / "processed" / "report.md"
MODEL_PATH = ROOT / "ml" / "artifacts" / "xgboost_model.joblib"
OUTPUT_PATH = ROOT / "ml" / "results" / "evaluation_report.md"


def compute_metrics(y_true, y_pred) -> dict:
    return {
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "r2": float(r2_score(y_true, y_pred)),
    }


def extract_outlier_compound_ids(report_text: str) -> list[str]:
    section = report_text.split("## Target outliers")[-1]
    return re.findall(r"^- (.+?) \(`", section, flags=re.MULTILINE)


def main() -> None:
    df = pd.read_csv(PROCESSED_CSV)
    bundle = joblib.load(MODEL_PATH)
    model, feature_names = bundle["model"], bundle["feature_names"]

    lines = ["# Evaluation report (winner: xgboost_tuned)\n\n"]

    # Overfitting check
    lines.append("## Overfitting check (train vs val/test)\n\n")
    for split in ["train", "val", "test"]:
        subset = df[df["split"] == split]
        metrics = compute_metrics(subset["target"], model.predict(subset[feature_names]))
        lines.append(f"- {split}: RMSE={metrics['rmse']:.3f}, R2={metrics['r2']:.3f}\n")
    train_rmse = compute_metrics(df[df["split"] == "train"]["target"], model.predict(df[df["split"] == "train"][feature_names]))["rmse"]
    val_rmse = compute_metrics(df[df["split"] == "val"]["target"], model.predict(df[df["split"] == "val"][feature_names]))["rmse"]
    gap = val_rmse - train_rmse
    lines.append(
        f"\nTrain-val RMSE gap: {gap:.3f}. "
        + ("Mild overfitting, expected for a tuned tree model on ~843 rows - not severe.\n" if gap < 0.5 else "Notable gap - consider stronger regularization.\n")
    )

    # Residuals on the 17 known outlier compounds
    outlier_ids = []
    if DATA_REPORT.exists():
        outlier_ids = extract_outlier_compound_ids(DATA_REPORT.read_text(encoding="utf-8"))

    lines.append("\n## Residuals on the 17 IQR-flagged outlier compounds\n\n")
    lines.append(
        "(PCBs, polyaromatic hydrocarbons, long-chain alkanes - kept in the "
        "dataset per data/README.md's decision; checking here whether the "
        "model systematically fails on them specifically.)\n\n"
    )
    if outlier_ids:
        outlier_rows = df[df["compound_id"].isin(outlier_ids)]
        if len(outlier_rows):
            preds = model.predict(outlier_rows[feature_names])
            residuals = outlier_rows["target"].to_numpy() - preds
            lines.append("| Compound | Split | Actual | Predicted | Residual |\n|---|---|---|---|---|\n")
            for (_, row), pred, resid in zip(outlier_rows.iterrows(), preds, residuals):
                lines.append(f"| {row['compound_id']} | {row['split']} | {row['target']:.2f} | {pred:.2f} | {resid:+.2f} |\n")
            overall_metrics = compute_metrics(df["target"], model.predict(df[feature_names]))
            outlier_mae = float(np.abs(residuals).mean())
            lines.append(f"\nOutlier-subset MAE: {outlier_mae:.3f} vs whole-dataset MAE: {overall_metrics['mae']:.3f}\n")
            verdict = (
                "Model does noticeably worse on these compounds than average - "
                "document as an applicability-domain limitation in the model card.\n"
                if outlier_mae > overall_metrics["mae"] * 1.5 else
                "Model handles these compounds reasonably (not much worse than "
                "average) - no special applicability-domain caveat needed for this subset.\n"
            )
            lines.append(verdict)
        else:
            lines.append("None of the flagged outlier compound_ids matched the processed dataset (dedup may have merged/renamed rows) — skipped.\n")
    else:
        lines.append("data/processed/report.md not found - run ml/preprocess.py first.\n")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text("".join(lines), encoding="utf-8")
    print("".join(lines))
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
