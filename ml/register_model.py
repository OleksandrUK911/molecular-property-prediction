"""Package the winning model into models/production/, following the
`models/production/model.pkl` + `models/production/metadata.json`
convention from ml/TODO_model_registry.md.

metadata.json's shape matches backend-spec/api-contract.md's GET
/model/info response exactly - the backend serves this file close to
verbatim.

Usage:
    python ml/register_model.py
"""

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

import joblib

ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = ROOT / "ml" / "artifacts"
WINNER_JSON_PATH = ROOT / "ml" / "results" / "winner.json"
EVALUATION_SUMMARY_PATH = ROOT / "ml" / "results" / "evaluation_summary.json"
PRODUCTION_DIR = ROOT / "models" / "production"
ARCHIVE_DIR = ROOT / "models" / "archive"

MODEL_VERSION = "0.1.0"

# Maps a winning model_name (from ml/results/winner.json, itself sourced from
# each experiment script's *_metrics.json) to the artifact file that script
# saved. Add an entry here whenever a new experiment script's candidate
# becomes eligible to win - select_winner.py picking a model by metrics alone
# isn't enough to register it without a real trained object to load.
MODEL_ARTIFACTS = {
    "xgboost_tuned": "xgboost_model.joblib",
    "xgboost_optuna": "xgboost_optuna_model.joblib",
}


def _archive_previous_production() -> None:
    """Before overwriting models/production/, copy its current contents to
    models/archive/<old_version>/ so a bad rollout can be rolled back by
    restoring an archived version - see backend/ROLLBACK.md."""
    old_metadata_path = PRODUCTION_DIR / "metadata.json"
    if not old_metadata_path.exists():
        return  # Nothing registered yet - first run, nothing to archive.

    old_metadata = json.loads(old_metadata_path.read_text(encoding="utf-8"))
    old_version = old_metadata.get("model_version", "unknown")
    dest = ARCHIVE_DIR / old_version
    if dest.exists():
        # Re-registering the same version - don't clobber an existing archive.
        return
    dest.mkdir(parents=True, exist_ok=True)
    for item in PRODUCTION_DIR.iterdir():
        if item.is_file():
            shutil.copy2(item, dest / item.name)
    print(f"Archived previous production model (version {old_version}) to {dest}")


def _build_known_limitations(model_name: str) -> list[str]:
    limitations = [
        (
            "Trained on 1117 small drug-like molecules (ESOL/Delaney dataset); "
            "unreliable outside this applicability domain."
        ),
        (
            "Scaffold split means test metrics reflect generalization to unseen "
            "scaffolds, not i.i.d. performance - a harder, more honest evaluation "
            "than a random split, but not directly comparable to papers using "
            "random splits on the same dataset."
        ),
    ]

    # Sourced from ml/evaluate.py's evaluation_summary.json, keyed to THIS
    # winner - not a hardcoded historical finding, so it stays honest if the
    # winner changes (e.g. Optuna's candidate gets promoted over the fixed-grid
    # one). Run `python ml/evaluate.py` after this script if the summary is
    # missing or stale for the current winner.
    if EVALUATION_SUMMARY_PATH.exists():
        summary = json.loads(EVALUATION_SUMMARY_PATH.read_text(encoding="utf-8"))
        if summary.get("model_name") == model_name and summary.get("outlier_caveat_warranted"):
            limitations.append(
                "Measurably worse on large hydrophobic/polyhalogenated compounds "
                "(PCBs, polyaromatic hydrocarbons, long-chain alkanes): MAE "
                f"{summary['outlier_mae']:.2f} on this 17-compound subset vs "
                f"{summary['dataset_mae']:.2f} dataset-wide ({summary['outlier_ratio']}x worse) "
                "- treat predictions for such molecules with reduced confidence."
            )
    else:
        limitations.append(
            "Applicability-domain check (17 known outlier compounds) not yet run for "
            "this model version - run `python ml/evaluate.py` and re-register to fill "
            "this in with real numbers."
        )
    return limitations


def main() -> None:
    winner_summary = json.loads(WINNER_JSON_PATH.read_text(encoding="utf-8"))
    model_name = winner_summary["val"]["model_name"]
    if model_name not in MODEL_ARTIFACTS:
        raise ValueError(
            f"select_winner.py picked '{model_name}' but no artifact mapping exists for it "
            f"in MODEL_ARTIFACTS - add one (the script that produced this candidate must "
            f"also save its trained model via joblib, not just metrics)."
        )
    winner_model_path = ARTIFACTS_DIR / MODEL_ARTIFACTS[model_name]
    bundle = joblib.load(winner_model_path)

    PRODUCTION_DIR.mkdir(parents=True, exist_ok=True)
    _archive_previous_production()
    joblib.dump(bundle, PRODUCTION_DIR / "model.pkl")

    metadata = {
        "model_version": MODEL_VERSION,
        "trained_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "dataset": "ESOL (Delaney)",
        "metrics": {
            "val": {
                "rmse": round(winner_summary["val"]["rmse"], 3),
                "mae": round(winner_summary["val"]["mae"], 3),
                "r2": round(winner_summary["val"]["r2"], 3),
            },
            "test": {
                "rmse": round(winner_summary["test"]["rmse"], 3),
                "mae": round(winner_summary["test"]["mae"], 3),
                "r2": round(winner_summary["test"]["r2"], 3),
            },
        },
        "known_limitations": _build_known_limitations(model_name),
        "model_type": model_name,
        "feature_names": bundle["feature_names"],
        "hyperparameters": bundle["hyperparameters"],
    }
    (PRODUCTION_DIR / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(json.dumps(metadata, indent=2))
    print(f"\nWrote {PRODUCTION_DIR / 'model.pkl'}")
    print(f"Wrote {PRODUCTION_DIR / 'metadata.json'}")


if __name__ == "__main__":
    main()
