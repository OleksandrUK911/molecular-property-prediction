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
from datetime import datetime, timezone
from pathlib import Path

import joblib

ROOT = Path(__file__).resolve().parent.parent
WINNER_MODEL_PATH = ROOT / "ml" / "artifacts" / "xgboost_model.joblib"
WINNER_JSON_PATH = ROOT / "ml" / "results" / "winner.json"
PRODUCTION_DIR = ROOT / "models" / "production"

MODEL_VERSION = "0.1.0"


def main() -> None:
    winner_summary = json.loads(WINNER_JSON_PATH.read_text(encoding="utf-8"))
    bundle = joblib.load(WINNER_MODEL_PATH)

    PRODUCTION_DIR.mkdir(parents=True, exist_ok=True)
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
        "known_limitations": [
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
            (
                "Measurably worse on large hydrophobic/polyhalogenated compounds "
                "(PCBs, polyaromatic hydrocarbons, long-chain alkanes): MAE 0.90 on "
                "this 17-compound subset vs 0.40 dataset-wide - treat predictions "
                "for such molecules with reduced confidence."
            ),
        ],
        "model_type": "xgboost_tuned",
        "feature_names": bundle["feature_names"],
        "hyperparameters": bundle["hyperparameters"],
    }
    (PRODUCTION_DIR / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(json.dumps(metadata, indent=2))
    print(f"\nWrote {PRODUCTION_DIR / 'model.pkl'}")
    print(f"Wrote {PRODUCTION_DIR / 'metadata.json'}")


if __name__ == "__main__":
    main()
