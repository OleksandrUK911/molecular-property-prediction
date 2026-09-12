"""XGBoost hyperparameter search with real Optuna optimization (TPE sampler),
as the natural next step beyond the fixed 4-point grid in
ml/experiments_xgboost.py (which is deliberately simplified - see its
module docstring). This script does NOT replace or modify
ml/experiments_xgboost.py; it's a separate, additive experiment.

Requires the optional `optuna` dependency:
    pip install -r ml/requirements-optuna.txt

Usage:
    python ml/experiments_xgboost_optuna.py

Search space (all sampled by optuna.samplers.TPESampler, seed=42):
    max_depth          int,  2-8
    learning_rate      float, 0.01-0.3, log-uniform
    n_estimators       int,  100-800
    subsample          float, 0.5-1.0
    colsample_bytree   float, 0.5-1.0

Selection: best trial by val RMSE only (same train/val/test discipline as
every other script in ml/ - test is never touched until final reporting,
after the winning configuration is already fixed).

Writes ml/results/xgboost_optuna_metrics.json (same schema family as
ml/results/xgboost_metrics.json, plus a "data_version" field - see
ml/data_versioning.py) and ml/results/optuna_report.md (search space, best
params, and an honest comparison against the existing fixed-grid winner).
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import optuna
import pandas as pd
from optuna.samplers import TPESampler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor

# Allow running this script directly (`python ml/experiments_xgboost_optuna.py`,
# same as every other script in this directory) while still importing the
# sibling ml/data_versioning.py module.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from data_versioning import compute_data_version

ROOT = Path(__file__).resolve().parent.parent
PROCESSED_CSV = ROOT / "data" / "processed" / "esol_processed.csv"
RESULTS_PATH = ROOT / "ml" / "results" / "xgboost_optuna_metrics.json"
REPORT_PATH = ROOT / "ml" / "results" / "optuna_report.md"
HISTORY_PLOT_PATH = ROOT / "ml" / "results" / "optuna_history.png"

DESCRIPTOR_COLUMNS = [
    "MolWt", "LogP", "TPSA", "NumHDonors", "NumHAcceptors", "NumRotatableBonds", "RingCount",
]
SEED = 42
N_TRIALS = 50

# Existing fixed-grid winner (ml/experiments_xgboost.py, model_name=xgboost_tuned),
# recorded here so the honest comparison below doesn't depend on read order /
# whether that script has been re-run recently.
FIXED_GRID_VAL_RMSE = 0.864


def compute_metrics(y_true, y_pred) -> dict:
    return {
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "r2": float(r2_score(y_true, y_pred)),
    }


def make_objective(X_train, y_train, X_val, y_val):
    def objective(trial: optuna.Trial) -> float:
        params = {
            "max_depth": trial.suggest_int("max_depth", 2, 8),
            "learning_rate": trial.suggest_float("learning_rate", 0.01, 0.3, log=True),
            "n_estimators": trial.suggest_int("n_estimators", 100, 800),
            "subsample": trial.suggest_float("subsample", 0.5, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.5, 1.0),
        }
        model = XGBRegressor(random_state=SEED, n_jobs=-1, **params)
        model.fit(X_train, y_train)
        return compute_metrics(y_val, model.predict(X_val))["rmse"]

    return objective


def main() -> None:
    df = pd.read_csv(PROCESSED_CSV)
    train, val, test = (df[df["split"] == s] for s in ("train", "val", "test"))

    X_train, y_train = train[DESCRIPTOR_COLUMNS], train["target"]
    X_val, y_val = val[DESCRIPTOR_COLUMNS], val["target"]
    X_test, y_test = test[DESCRIPTOR_COLUMNS], test["target"]

    data_version = compute_data_version()
    trained_at = datetime.now(timezone.utc).isoformat()

    optuna.logging.set_verbosity(optuna.logging.WARNING)
    sampler = TPESampler(seed=SEED)
    study = optuna.create_study(direction="minimize", sampler=sampler)
    study.optimize(make_objective(X_train, y_train, X_val, y_val), n_trials=N_TRIALS, show_progress_bar=False)

    best_params = study.best_params
    best_model = XGBRegressor(random_state=SEED, n_jobs=-1, **best_params)
    best_model.fit(X_train, y_train)

    records = []
    for split_name, X, y in [("val", X_val, y_val), ("test", X_test, y_test)]:
        records.append({
            "model_name": "xgboost_optuna",
            "split": split_name,
            "trained_at": trained_at,
            "data_version": data_version,
            "hyperparameters": best_params,
            **compute_metrics(y, best_model.predict(X)),
        })

    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(json.dumps(records, indent=2), encoding="utf-8")

    val_record = next(r for r in records if r["split"] == "val")
    test_record = next(r for r in records if r["split"] == "test")
    improvement = FIXED_GRID_VAL_RMSE - val_record["rmse"]
    verdict = (
        "a meaningful improvement" if improvement >= 0.02
        else ("no real improvement (within noise)" if improvement > -0.02 else "actually worse")
    )

    # Optional nice-to-have: optimization-history plot, if matplotlib is
    # available (ml/requirements-interpretability.txt).
    plot_written = False
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        trial_numbers = [t.number for t in study.trials]
        trial_values = [t.value for t in study.trials]
        running_best = np.minimum.accumulate(trial_values)

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.scatter(trial_numbers, trial_values, s=20, alpha=0.6, label="trial val RMSE")
        ax.plot(trial_numbers, running_best, color="red", linewidth=2, label="best so far")
        ax.axhline(FIXED_GRID_VAL_RMSE, color="gray", linestyle="--", label=f"fixed-grid winner ({FIXED_GRID_VAL_RMSE:.3f})")
        ax.set_xlabel("Trial")
        ax.set_ylabel("Validation RMSE")
        ax.set_title("Optuna optimization history (xgboost_optuna)")
        ax.legend()
        fig.tight_layout()
        fig.savefig(HISTORY_PLOT_PATH, dpi=150)
        plt.close(fig)
        plot_written = True
    except ImportError:
        pass

    report_lines = [
        "# Optuna hyperparameter search report\n\n",
        f"Data version: `{data_version}` (sha256[:12] of `data/processed/esol_processed.csv`)\n\n",
        "## Search space\n\n",
        "| Hyperparameter | Range | Sampling |\n|---|---|---|\n",
        "| max_depth | 2-8 | int, uniform |\n",
        "| learning_rate | 0.01-0.3 | float, log-uniform |\n",
        "| n_estimators | 100-800 | int, uniform |\n",
        "| subsample | 0.5-1.0 | float, uniform |\n",
        "| colsample_bytree | 0.5-1.0 | float, uniform |\n\n",
        f"Sampler: `TPESampler(seed={SEED})`. Trials: {N_TRIALS}. Selection: best val RMSE (test never touched during search).\n\n",
        "## Best configuration found\n\n",
        f"```\n{json.dumps(best_params, indent=2)}\n```\n\n",
        "## Results\n\n",
        "| Model | Split | RMSE | MAE | R2 |\n|---|---|---|---|---|\n",
        f"| xgboost_optuna | val | {val_record['rmse']:.3f} | {val_record['mae']:.3f} | {val_record['r2']:.3f} |\n",
        f"| xgboost_optuna | test | {test_record['rmse']:.3f} | {test_record['mae']:.3f} | {test_record['r2']:.3f} |\n\n",
        "## Comparison to the existing fixed-grid winner (`xgboost_tuned`)\n\n",
        f"- Fixed-grid winner val RMSE: {FIXED_GRID_VAL_RMSE:.3f}\n",
        f"- Optuna best val RMSE: {val_record['rmse']:.3f}\n",
        f"- Difference: {improvement:+.3f} RMSE ({'improvement' if improvement > 0 else 'regression' if improvement < 0 else 'no change'})\n\n",
        f"**Honest verdict:** {verdict}. ",
    ]
    if improvement < 0.02:
        report_lines.append(
            "A 50-trial TPE search over a realistic space did not find a configuration "
            "that meaningfully beats the original small fixed grid on this dataset's val "
            "split (167 molecules) - the difference is within what we'd expect from "
            "noise/search variance at this scale. This is a useful negative result: it "
            "suggests the fixed-grid winner was already a reasonable choice, or that "
            "further gains here require more data/features rather than more hyperparameter "
            "search. This script's metrics file is available for `select_winner.py` to "
            "pick up if a human decides the small edge (or simplicity/reproducibility "
            "trade-off) is worth it, but no automatic change was made.\n"
        )
    else:
        report_lines.append(
            "Optuna found a configuration that beats the fixed-grid winner by a margin "
            "larger than typical noise on this dataset size. This metrics file is available "
            "for a human to consider promoting via `select_winner.py`.\n"
        )
    if plot_written:
        report_lines.append("\n![Optimization history](optuna_history.png)\n")

    REPORT_PATH.write_text("".join(report_lines), encoding="utf-8")

    print(f"Best params (by val RMSE): {best_params}")
    print(f"{'model':<16} {'split':<6} {'rmse':>8} {'mae':>8} {'r2':>8}")
    for r in records:
        print(f"{r['model_name']:<16} {r['split']:<6} {r['rmse']:>8.3f} {r['mae']:>8.3f} {r['r2']:>8.3f}")
    print(f"\nFixed-grid val RMSE: {FIXED_GRID_VAL_RMSE:.3f} | Optuna val RMSE: {val_record['rmse']:.3f} | "
          f"delta: {improvement:+.3f} -> {verdict}")
    print(f"\nWrote {RESULTS_PATH}\nWrote {REPORT_PATH}")
    if plot_written:
        print(f"Wrote {HISTORY_PLOT_PATH}")


if __name__ == "__main__":
    main()
