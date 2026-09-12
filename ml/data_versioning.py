"""Small reusable helper for tying an experiment run back to the exact
processed data it was trained on.

Recommended pattern going forward for NEW experiment scripts: call
compute_data_version() and store the result as a "data_version" field
alongside the other metadata (model_name, split, trained_at, hyperparameters,
...) in each record written to ml/results/*_metrics.json. This is intentionally
not retrofitted into every existing script (ml/baseline.py,
ml/experiments_xgboost.py, ml/experiments_fingerprint_models.py) - that would be
a larger, riskier schema change than a single new script warrants. See
ml/experiments_xgboost_optuna.py for a worked example.
"""

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROCESSED_CSV = ROOT / "data" / "processed" / "esol_processed.csv"


def compute_data_version(path: Path = PROCESSED_CSV) -> str:
    """Return a short (12 hex char) sha256 hash of the processed dataset's
    raw file contents, to be recorded as a "data_version" field so a given
    experiment run can be traced back to the exact data that produced it.
    """
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    return digest[:12]


if __name__ == "__main__":
    print(compute_data_version())
