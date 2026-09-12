"""Grouped bar chart comparing validation RMSE and MAE across every candidate
model currently recorded in ml/results/*_metrics.json.

Kept as a separate script from ml/select_winner.py (cleaner separation - the
selection logic there is untouched) and run after it.

Requires the optional matplotlib dependency:
    pip install -r ml/requirements-interpretability.txt

Usage:
    python ml/plot_experiment_comparison.py

Reads the same *_metrics.json files ml/select_winner.py reads (plus
xgboost_optuna_metrics.json, if present, so a new candidate shows up here
without any code change) and writes
ml/results/experiment_comparison_chart.png.
"""

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "ml" / "results"
CHART_PATH = RESULTS_DIR / "experiment_comparison_chart.png"

# Same base files ml/select_winner.py reads, plus any additional experiment
# metrics files that follow the same schema (e.g. the Optuna search) - picked
# up automatically here so this chart doesn't need touching for new
# candidates. New scripts writing ml/results/*_metrics.json should keep the
# "model_name"/"split"/"rmse"/"mae" fields so they show up automatically.
RESULT_FILES = [
    "baseline_metrics.json",
    "xgboost_metrics.json",
    "fingerprint_model_metrics.json",
    "xgboost_optuna_metrics.json",
]

# Fixed categorical color order (never cycled/reassigned) for the two metrics
# shown per model - a colorblind-safe blue/orange pair.
RMSE_COLOR = "#1f77b4"
MAE_COLOR = "#ff7f0e"


def load_val_records() -> list[dict]:
    records = []
    for filename in RESULT_FILES:
        path = RESULTS_DIR / filename
        if path.exists():
            records.extend(json.loads(path.read_text(encoding="utf-8")))
    val_records = [r for r in records if r["split"] == "val"]
    val_records.sort(key=lambda r: r["rmse"])
    return val_records


def main() -> None:
    val_records = load_val_records()
    if not val_records:
        raise SystemExit("No val-split metrics found under ml/results/ - run the experiment scripts first.")

    model_names = [r["model_name"] for r in val_records]
    rmse_values = [r["rmse"] for r in val_records]
    mae_values = [r["mae"] for r in val_records]

    x = np.arange(len(model_names))
    width = 0.38

    fig, ax = plt.subplots(figsize=(max(8, len(model_names) * 1.1), 6))
    bars_rmse = ax.bar(x - width / 2, rmse_values, width, label="Val RMSE", color=RMSE_COLOR)
    bars_mae = ax.bar(x + width / 2, mae_values, width, label="Val MAE", color=MAE_COLOR)

    for bars in (bars_rmse, bars_mae):
        ax.bar_label(bars, fmt="%.3f", padding=2, fontsize=8)

    ax.set_ylabel("Error (log mol/L)")
    ax.set_title("Validation RMSE / MAE across candidate models\n(sorted by RMSE, best first)")
    ax.set_xticks(x)
    ax.set_xticklabels(model_names, rotation=30, ha="right")
    ax.legend()
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    fig.tight_layout()

    CHART_PATH.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(CHART_PATH, dpi=150)
    plt.close(fig)

    print(f"{'model':<32} {'val_rmse':>10} {'val_mae':>10}")
    for name, rmse, mae in zip(model_names, rmse_values, mae_values):
        print(f"{name:<32} {rmse:>10.3f} {mae:>10.3f}")
    print(f"\nWrote {CHART_PATH}")


if __name__ == "__main__":
    main()
