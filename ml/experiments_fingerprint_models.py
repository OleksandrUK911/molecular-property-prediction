"""Random Forest on descriptors vs Morgan fingerprints vs combined.

Unlike the Ridge comparison in ml/feature_engineering.py (which unfairly
penalizes the 1024-bit fingerprint representation for a linear model),
Random Forest handles high-dimensional sparse binary features natively -
this is the real verdict on whether fingerprints help for this dataset.

Usage:
    python ml/experiments_fingerprint_models.py

Writes ml/results/fingerprint_model_metrics.json.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT = Path(__file__).resolve().parent.parent
PROCESSED_CSV = ROOT / "data" / "processed" / "esol_processed.csv"
FINGERPRINT_NPY = ROOT / "data" / "processed" / "esol_morgan_fp.npy"
RESULTS_PATH = ROOT / "ml" / "results" / "fingerprint_model_metrics.json"

DESCRIPTOR_COLUMNS = [
    "MolWt", "LogP", "TPSA", "NumHDonors", "NumHAcceptors", "NumRotatableBonds", "RingCount",
]
SEED = 42


def compute_metrics(y_true, y_pred) -> dict:
    return {
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "r2": float(r2_score(y_true, y_pred)),
    }


def main() -> None:
    df = pd.read_csv(PROCESSED_CSV)
    fingerprints = np.load(FINGERPRINT_NPY)
    assert len(df) == len(fingerprints)

    train_mask = (df["split"] == "train").to_numpy()
    val_mask = (df["split"] == "val").to_numpy()
    test_mask = (df["split"] == "test").to_numpy()

    X_desc = df[DESCRIPTOR_COLUMNS].to_numpy()
    X_fp = fingerprints.astype(float)
    X_combined = np.hstack([X_desc, X_fp])
    y = df["target"].to_numpy()

    trained_at = datetime.now(timezone.utc).isoformat()
    records = []
    for name, X in [("descriptors_only", X_desc), ("fingerprints_only", X_fp), ("combined", X_combined)]:
        model = RandomForestRegressor(n_estimators=300, max_depth=None, random_state=SEED, n_jobs=-1)
        model.fit(X[train_mask], y[train_mask])
        for split_name, mask in [("val", val_mask), ("test", test_mask)]:
            metrics = compute_metrics(y[mask], model.predict(X[mask]))
            records.append({
                "model_name": f"random_forest_{name}", "split": split_name,
                "trained_at": trained_at, "n_features": X.shape[1], **metrics,
            })

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(records, indent=2), encoding="utf-8")

    print(f"{'model':<32} {'split':<6} {'n_feat':>7} {'rmse':>8} {'mae':>8} {'r2':>8}")
    for r in records:
        print(f"{r['model_name']:<32} {r['split']:<6} {r['n_features']:>7} {r['rmse']:>8.3f} {r['mae']:>8.3f} {r['r2']:>8.3f}")
    print(f"\nWrote {RESULTS_PATH}")


if __name__ == "__main__":
    main()
