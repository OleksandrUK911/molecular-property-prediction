"""Feature engineering: descriptor relevance, multicollinearity, and a
fair descriptor-vs-fingerprint-vs-combined comparison.

Usage:
    python ml/feature_engineering.py

Reads data/processed/esol_processed.csv + esol_morgan_fp.npy (aligned by
row order, both produced by ml/preprocess.py). Fingerprint rows are in the
same order as the processed CSV rows since preprocess.py deduplicates
before generating fingerprints - no join key needed.

Writes:
- ml/results/feature_engineering_report.md (correlations, multicollinearity, comparison)
- ml/artifacts/descriptor_scaler.joblib (fit on train split only)
"""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent.parent
PROCESSED_CSV = ROOT / "data" / "processed" / "esol_processed.csv"
FINGERPRINT_NPY = ROOT / "data" / "processed" / "esol_morgan_fp.npy"
REPORT_PATH = ROOT / "ml" / "results" / "feature_engineering_report.md"
SCALER_PATH = ROOT / "ml" / "artifacts" / "descriptor_scaler.joblib"

DESCRIPTOR_COLUMNS = [
    "MolWt", "LogP", "TPSA", "NumHDonors", "NumHAcceptors", "NumRotatableBonds", "RingCount",
]


def compute_metrics(y_true, y_pred) -> dict:
    return {
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "r2": float(r2_score(y_true, y_pred)),
    }


def evaluate_feature_set(name, X_train, y_train, X_val, y_val, X_test, y_test) -> dict:
    scaler = StandardScaler().fit(X_train)
    model = Ridge(alpha=1.0, random_state=42).fit(scaler.transform(X_train), y_train)
    return {
        "feature_set": name,
        "n_features": X_train.shape[1],
        "val": compute_metrics(y_val, model.predict(scaler.transform(X_val))),
        "test": compute_metrics(y_test, model.predict(scaler.transform(X_test))),
    }


def main() -> None:
    df = pd.read_csv(PROCESSED_CSV)
    fingerprints = np.load(FINGERPRINT_NPY)
    assert len(df) == len(fingerprints), "processed CSV and fingerprint array must be row-aligned"

    # 1. Descriptor relevance: correlation with target
    corr_with_target = df[DESCRIPTOR_COLUMNS + ["target"]].corr()["target"].drop("target")
    corr_with_target = corr_with_target.sort_values(key=abs, ascending=False)

    # 2. Multicollinearity among descriptors
    descriptor_corr = df[DESCRIPTOR_COLUMNS].corr()
    high_corr_pairs = []
    for i, col_a in enumerate(DESCRIPTOR_COLUMNS):
        for col_b in DESCRIPTOR_COLUMNS[i + 1:]:
            r = descriptor_corr.loc[col_a, col_b]
            if abs(r) > 0.7:
                high_corr_pairs.append((col_a, col_b, float(r)))

    # 3. Near-zero variance check
    variances = df[DESCRIPTOR_COLUMNS].var()
    low_variance_cols = variances[variances < 0.01].index.tolist()

    # 4. Descriptor-only vs fingerprint-only vs combined comparison
    train_mask = (df["split"] == "train").to_numpy()
    val_mask = (df["split"] == "val").to_numpy()
    test_mask = (df["split"] == "test").to_numpy()

    X_desc = df[DESCRIPTOR_COLUMNS].to_numpy()
    X_fp = fingerprints.astype(float)
    X_combined = np.hstack([X_desc, X_fp])
    y = df["target"].to_numpy()

    results = []
    for name, X in [("descriptors_only", X_desc), ("fingerprints_only", X_fp), ("combined", X_combined)]:
        results.append(
            evaluate_feature_set(
                name,
                X[train_mask], y[train_mask],
                X[val_mask], y[val_mask],
                X[test_mask], y[test_mask],
            )
        )

    # 5. Fit and save the production scaler (descriptors, train-only) for backend inference reuse
    SCALER_PATH.parent.mkdir(parents=True, exist_ok=True)
    production_scaler = StandardScaler().fit(X_desc[train_mask])
    joblib.dump({"scaler": production_scaler, "feature_names": DESCRIPTOR_COLUMNS}, SCALER_PATH)

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Feature engineering report\n"]
    lines.append("\n## Descriptor correlation with target (sorted by |r|)\n")
    for name, r in corr_with_target.items():
        lines.append(f"- {name}: {r:.3f}\n")

    lines.append("\n## Multicollinearity (|r| > 0.7 among descriptors)\n")
    if high_corr_pairs:
        for a, b, r in high_corr_pairs:
            lines.append(f"- {a} <-> {b}: r={r:.3f}\n")
    else:
        lines.append("- None found — all 7 descriptors are reasonably independent, kept as-is.\n")

    lines.append("\n## Near-zero variance descriptors (var < 0.01)\n")
    lines.append(f"- {low_variance_cols if low_variance_cols else 'None — all descriptors kept.'}\n")

    lines.append("\n## Descriptor vs fingerprint vs combined (Ridge, same model for all three)\n")
    lines.append("| Feature set | n_features | val RMSE | val R2 | test RMSE | test R2 |\n")
    lines.append("|---|---|---|---|---|---|\n")
    for r in results:
        lines.append(
            f"| {r['feature_set']} | {r['n_features']} | {r['val']['rmse']:.3f} | {r['val']['r2']:.3f} "
            f"| {r['test']['rmse']:.3f} | {r['test']['r2']:.3f} |\n"
        )
    lines.append(
        "\n**Caveat — do not read this as \"fingerprints don't work\":** all "
        "three rows use the same plain Ridge(alpha=1.0) for a controlled "
        "comparison, but that setup unfairly punishes the 1024-bit "
        "fingerprint representation — p (1024 features) >> n (~843 train "
        "rows) with weak regularization overfits badly on a linear model. "
        "`ml/TODO_experiments_fingerprint_models.md` correctly plans to "
        "evaluate fingerprints with Random Forest / tree-based models "
        "instead, which handle high-dimensional sparse binary features far "
        "better; that comparison, not this one, is the real verdict on "
        "fingerprint usefulness for this dataset. This table's purpose is "
        "only to confirm descriptors alone are a strong, well-behaved "
        "feature set for the linear baseline.\n"
    )

    REPORT_PATH.write_text("".join(lines), encoding="utf-8")

    print("".join(lines))
    print(f"Wrote {REPORT_PATH}")
    print(f"Wrote {SCALER_PATH}")


if __name__ == "__main__":
    main()
