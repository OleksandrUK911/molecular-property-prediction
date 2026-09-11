"""Baseline models for ESOL solubility prediction.

Usage:
    python ml/baseline.py

Reads data/processed/esol_processed.csv (produced by ml/preprocess.py),
trains a naive mean baseline, linear regression, and Ridge regression on
the RDKit descriptors, and writes val/test metrics to
ml/results/baseline_metrics.json.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent.parent
PROCESSED_PATH = ROOT / "data" / "processed" / "esol_processed.csv"
RESULTS_PATH = ROOT / "ml" / "results" / "baseline_metrics.json"

DESCRIPTOR_COLUMNS = [
    "MolWt", "LogP", "TPSA", "NumHDonors", "NumHAcceptors", "NumRotatableBonds", "RingCount",
]


def compute_metrics(y_true, y_pred) -> dict:
    return {
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "r2": float(r2_score(y_true, y_pred)),
    }


def main() -> None:
    df = pd.read_csv(PROCESSED_PATH)

    train = df[df["split"] == "train"]
    val = df[df["split"] == "val"]
    test = df[df["split"] == "test"]

    X_train, y_train = train[DESCRIPTOR_COLUMNS], train["target"]
    X_val, y_val = val[DESCRIPTOR_COLUMNS], val["target"]
    X_test, y_test = test[DESCRIPTOR_COLUMNS], test["target"]

    scaler = StandardScaler().fit(X_train)
    X_train_scaled = scaler.transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)

    models = {
        "naive_mean": DummyRegressor(strategy="mean").fit(X_train, y_train),
        "linear_regression": LinearRegression().fit(X_train_scaled, y_train),
        "ridge": Ridge(alpha=1.0, random_state=42).fit(X_train_scaled, y_train),
    }

    trained_at = datetime.now(timezone.utc).isoformat()
    records = []
    for name, model in models.items():
        uses_scaled = name != "naive_mean"
        for split_name, X, y in [
            ("val", X_val_scaled if uses_scaled else X_val, y_val),
            ("test", X_test_scaled if uses_scaled else X_test, y_test),
        ]:
            preds = model.predict(X)
            metrics = compute_metrics(y, preds)
            records.append({"model_name": name, "split": split_name, "trained_at": trained_at, **metrics})

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(records, indent=2), encoding="utf-8")

    print(f"{'model':<18} {'split':<6} {'rmse':>8} {'mae':>8} {'r2':>8}")
    for r in records:
        print(f"{r['model_name']:<18} {r['split']:<6} {r['rmse']:>8.3f} {r['mae']:>8.3f} {r['r2']:>8.3f}")
    print(f"\nWrote {RESULTS_PATH}")


if __name__ == "__main__":
    main()
