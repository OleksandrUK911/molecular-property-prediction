"""Consolidate all experiment result files, rank candidates, and select
the production model by a fixed, documented criterion.

This is a lightweight stand-in for full MLflow tracking (ml/TODO_experiments_tracking.md
plans MLflow as a P0 item) - deliberately deferred: for ~10 total runs across
2 scripts, a consolidated JSON/markdown is sufficient and much cheaper than
standing up a tracking server for this project's scale. Revisit if the
number of experiment runs grows significantly (e.g. once GNN experiments
or heavy hyperparameter search are added).

Usage:
    python ml/select_winner.py

Reads ml/results/{baseline,xgboost,fingerprint_model,xgboost_optuna}_metrics.json.
Writes ml/results/experiment_comparison.md and ml/results/winner.json.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS_DIR = ROOT / "ml" / "results"
RESULT_FILES = [
    "baseline_metrics.json",
    "xgboost_metrics.json",
    "fingerprint_model_metrics.json",
    "xgboost_optuna_metrics.json",
]

# Selection criteria (documented, applied in this order):
# 1. Best val RMSE (primary metric - test is never used for selection)
# 2. Among candidates within 0.02 RMSE of the best (~noise level for this
#    dataset size), prefer fewer features / simpler model for faster inference
SIMPLICITY_TIEBREAK_MARGIN = 0.02


def main() -> None:
    all_records = []
    for filename in RESULT_FILES:
        path = RESULTS_DIR / filename
        if path.exists():
            all_records.extend(json.loads(path.read_text(encoding="utf-8")))

    val_records = [r for r in all_records if r["split"] == "val"]
    val_records.sort(key=lambda r: r["rmse"])

    best_rmse = val_records[0]["rmse"]
    contenders = [r for r in val_records if r["rmse"] <= best_rmse + SIMPLICITY_TIEBREAK_MARGIN]
    winner = min(contenders, key=lambda r: r.get("n_features", 7))  # descriptor-only models default to 7

    test_record = next(
        r for r in all_records
        if r["model_name"] == winner["model_name"] and r["split"] == "test"
    )

    lines = ["# Experiment comparison\n\n"]
    lines.append("| Model | Split | RMSE | MAE | R2 | n_features |\n|---|---|---|---|---|---|\n")
    for r in sorted(all_records, key=lambda r: (r["model_name"], r["split"])):
        lines.append(
            f"| {r['model_name']} | {r['split']} | {r['rmse']:.3f} | {r['mae']:.3f} "
            f"| {r['r2']:.3f} | {r.get('n_features', 7)} |\n"
        )

    lines.append(f"\n## Winner: `{winner['model_name']}`\n\n")
    lines.append(
        f"- Val RMSE: {winner['rmse']:.3f} (best: {best_rmse:.3f}, "
        f"within {SIMPLICITY_TIEBREAK_MARGIN} tiebreak margin considered)\n"
    )
    lines.append(f"- Test RMSE: {test_record['rmse']:.3f}, R2: {test_record['r2']:.3f}\n")
    lines.append(f"- Features used: {winner.get('n_features', 7)}\n")
    lines.append(
        "- Selection rule: best val RMSE; among near-ties (within "
        f"{SIMPLICITY_TIEBREAK_MARGIN}), simplest/fewest-feature model wins "
        "for faster inference and easier interpretability.\n"
    )

    (RESULTS_DIR / "experiment_comparison.md").write_text("".join(lines), encoding="utf-8")
    (RESULTS_DIR / "winner.json").write_text(
        json.dumps({"val": winner, "test": test_record}, indent=2), encoding="utf-8"
    )

    print("".join(lines))
    print(f"Wrote {RESULTS_DIR / 'experiment_comparison.md'}")
    print(f"Wrote {RESULTS_DIR / 'winner.json'}")


if __name__ == "__main__":
    main()
