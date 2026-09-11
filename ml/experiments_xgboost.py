"""XGBoost experiments on RDKit descriptors: default hyperparameters, then
a light Optuna-free random search (kept dependency-light for this MVP).

Usage:
    python ml/experiments_xgboost.py

Writes results to ml/results/xgboost_metrics.json (same schema family as
ml/results/baseline_metrics.json) and the tuned model to
ml/artifacts/xgboost_model.joblib.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor

ROOT = Path(__file__).resolve().parent.parent
PROCESSED_CSV = ROOT / "data" / "processed" / "esol_processed.csv"
RESULTS_PATH = ROOT / "ml" / "results" / "xgboost_metrics.json"
MODEL_PATH = ROOT / "ml" / "artifacts" / "xgboost_model.joblib"

DESCRIPTOR_COLUMNS = [
    "MolWt", "LogP", "TPSA", "NumHDonors", "NumHAcceptors", "NumRotatableBonds", "RingCount",
]
SEED = 42

# Small, fixed hyperparameter grid - a lightweight stand-in for full Optuna
# tuning (tracked as a follow-up in ml/TODO_experiments_xgboost.md); budget
# kept small deliberately to avoid overfitting the tiny (167-row) val split.
PARAM_GRID = [
    {"max_depth": 3, "learning_rate": 0.1, "n_estimators": 200, "subsample": 0.8, "colsample_bytree": 0.8},
    {"max_depth": 4, "learning_rate": 0.05, "n_estimators": 400, "subsample": 0.8, "colsample_bytree": 0.8},
    {"max_depth": 5, "learning_rate": 0.05, "n_estimators": 300, "subsample": 0.7, "colsample_bytree": 0.7},
    {"max_depth": 3, "learning_rate": 0.03, "n_estimators": 600, "subsample": 0.9, "colsample_bytree": 0.9},
]


def compute_metrics(y_true, y_pred) -> dict:
    return {
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "r2": float(r2_score(y_true, y_pred)),
    }


def main() -> None:
    df = pd.read_csv(PROCESSED_CSV)
    train, val, test = (df[df["split"] == s] for s in ("train", "val", "test"))

    X_train, y_train = train[DESCRIPTOR_COLUMNS], train["target"]
    X_val, y_val = val[DESCRIPTOR_COLUMNS], val["target"]
    X_test, y_test = test[DESCRIPTOR_COLUMNS], test["target"]

    trained_at = datetime.now(timezone.utc).isoformat()
    records = []

    # Default hyperparameters, as the first candidate above baseline
    default_model = XGBRegressor(random_state=SEED, n_jobs=-1)
    default_model.fit(X_train, y_train)
    for split_name, X, y in [("val", X_val, y_val), ("test", X_test, y_test)]:
        records.append({
            "model_name": "xgboost_default", "split": split_name,
            "trained_at": trained_at, **compute_metrics(y, default_model.predict(X)),
        })

    # Small grid search, selected on val RMSE only (test never touched for selection)
    best_val_rmse = float("inf")
    best_model = None
    best_params = None
    for params in PARAM_GRID:
        model = XGBRegressor(random_state=SEED, n_jobs=-1, **params)
        model.fit(X_train, y_train)
        val_rmse = compute_metrics(y_val, model.predict(X_val))["rmse"]
        if val_rmse < best_val_rmse:
            best_val_rmse, best_model, best_params = val_rmse, model, params

    for split_name, X, y in [("val", X_val, y_val), ("test", X_test, y_test)]:
        records.append({
            "model_name": "xgboost_tuned", "split": split_name,
            "trained_at": trained_at, "hyperparameters": best_params,
            **compute_metrics(y, best_model.predict(X)),
        })

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(records, indent=2), encoding="utf-8")

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"model": best_model, "feature_names": DESCRIPTOR_COLUMNS, "hyperparameters": best_params}, MODEL_PATH)

    print(f"Best params (by val RMSE): {best_params}")
    print(f"{'model':<18} {'split':<6} {'rmse':>8} {'mae':>8} {'r2':>8}")
    for r in records:
        print(f"{r['model_name']:<18} {r['split']:<6} {r['rmse']:>8.3f} {r['mae']:>8.3f} {r['r2']:>8.3f}")
    print(f"\nWrote {RESULTS_PATH}\nWrote {MODEL_PATH}")


if __name__ == "__main__":
    main()
