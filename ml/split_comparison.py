"""Scaffold split vs. random split, same model, same data.

Usage:
    python ml/split_comparison.py

ml/preprocess.py only supports scaffold split today, and this script does
not modify it. Instead it loads the already-processed
data/processed/esol_processed.csv (post-dedup, descriptors already
computed) and generates a fresh 70/15/15 random split with
sklearn.model_selection.train_test_split (random_state=42), independent
of the existing `split` column (which is the scaffold split). It then
trains the same winning XGBoost hyperparameters on both splits and
compares val/test metrics side by side.

Writes ml/results/split_comparison_report.md.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from xgboost import XGBRegressor

ROOT = Path(__file__).resolve().parent.parent
PROCESSED_CSV = ROOT / "data" / "processed" / "esol_processed.csv"
WINNER_JSON = ROOT / "ml" / "results" / "winner.json"
PRODUCTION_METADATA = ROOT / "models" / "production" / "metadata.json"
OUTPUT_PATH = ROOT / "ml" / "results" / "split_comparison_report.md"

DESCRIPTOR_COLUMNS = [
    "MolWt", "LogP", "TPSA", "NumHDonors", "NumHAcceptors", "NumRotatableBonds", "RingCount",
]
SEED = 42
TRAIN_FRAC, VAL_FRAC, TEST_FRAC = 0.70, 0.15, 0.15


def compute_metrics(y_true, y_pred) -> dict:
    return {
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "r2": float(r2_score(y_true, y_pred)),
    }


def load_winning_hyperparameters() -> dict:
    if WINNER_JSON.exists():
        winner = json.loads(WINNER_JSON.read_text(encoding="utf-8"))
        params = winner.get("val", {}).get("hyperparameters")
        if params:
            return params
    if PRODUCTION_METADATA.exists():
        metadata = json.loads(PRODUCTION_METADATA.read_text(encoding="utf-8"))
        params = metadata.get("hyperparameters")
        if params:
            return params
    raise FileNotFoundError(
        "Could not find hyperparameters in ml/results/winner.json or "
        "models/production/metadata.json - run ml/experiments_xgboost.py, "
        "ml/select_winner.py, and ml/register_model.py first."
    )


def make_random_split(df: pd.DataFrame, seed: int) -> pd.DataFrame:
    """Fresh i.i.d. 70/15/15 random split, independent of the existing
    scaffold-based `split` column."""
    df = df.copy()
    train_df, rest_df = train_test_split(df, train_size=TRAIN_FRAC, random_state=seed)
    val_frac_of_rest = VAL_FRAC / (VAL_FRAC + TEST_FRAC)
    val_df, test_df = train_test_split(rest_df, train_size=val_frac_of_rest, random_state=seed)

    random_split = pd.Series(index=df.index, dtype=object)
    random_split.loc[train_df.index] = "train"
    random_split.loc[val_df.index] = "val"
    random_split.loc[test_df.index] = "test"
    df["random_split"] = random_split
    return df


def evaluate_split(df: pd.DataFrame, split_col: str, hyperparameters: dict) -> dict:
    train = df[df[split_col] == "train"]
    val = df[df[split_col] == "val"]
    test = df[df[split_col] == "test"]

    X_train, y_train = train[DESCRIPTOR_COLUMNS], train["target"]
    X_val, y_val = val[DESCRIPTOR_COLUMNS], val["target"]
    X_test, y_test = test[DESCRIPTOR_COLUMNS], test["target"]

    model = XGBRegressor(random_state=SEED, n_jobs=-1, **hyperparameters)
    model.fit(X_train, y_train)

    return {
        "n_train": len(train), "n_val": len(val), "n_test": len(test),
        "val": compute_metrics(y_val, model.predict(X_val)),
        "test": compute_metrics(y_test, model.predict(X_test)),
    }


def main() -> None:
    df = pd.read_csv(PROCESSED_CSV)
    hyperparameters = load_winning_hyperparameters()

    df = make_random_split(df, SEED)

    scaffold_result = evaluate_split(df, "split", hyperparameters)
    random_result = evaluate_split(df, "random_split", hyperparameters)

    lines = ["# Scaffold split vs. random split comparison\n\n"]
    lines.append(
        f"Same descriptor set (7 columns) and same winning XGBoost hyperparameters "
        f"`{hyperparameters}` trained on two different splits of the same "
        f"{len(df)}-row processed dataset:\n\n"
        "- **scaffold** (`split` column, from `ml/preprocess.py`): whole Murcko "
        "scaffolds grouped into train/val/test, not i.i.d. by design.\n"
        "- **random** (`random_split` column, generated fresh in this script via "
        "`train_test_split(..., random_state=42)`, 70/15/15): ordinary i.i.d. row "
        "split, independent of the scaffold split.\n\n"
    )

    lines.append("## Comparison\n\n")
    lines.append("| Split type | Rows (train/val/test) | Metric | Val | Test |\n|---|---|---|---|---|\n")
    for name, result in [("scaffold", scaffold_result), ("random", random_result)]:
        sizes = f"{result['n_train']}/{result['n_val']}/{result['n_test']}"
        for metric in ["rmse", "mae", "r2"]:
            lines.append(
                f"| {name} | {sizes} | {metric.upper()} | "
                f"{result['val'][metric]:.3f} | {result['test'][metric]:.3f} |\n"
            )

    rmse_diff_test = scaffold_result["test"]["rmse"] - random_result["test"]["rmse"]
    r2_diff_test = random_result["test"]["r2"] - scaffold_result["test"]["r2"]

    lines.append("\n## Interpretation\n\n")
    lines.append(
        f"Random-split test RMSE is {random_result['test']['rmse']:.3f} vs. "
        f"scaffold-split test RMSE of {scaffold_result['test']['rmse']:.3f} "
        f"(difference: {rmse_diff_test:+.3f}); random-split test R2 is "
        f"{random_result['test']['r2']:.3f} vs. scaffold-split {scaffold_result['test']['r2']:.3f} "
        f"(difference: {r2_diff_test:+.3f}).\n\n"
    )
    if rmse_diff_test > 0.02 or r2_diff_test > 0.02:
        lines.append(
            "This supports the claim made elsewhere in this project's docs "
            "(`data/processed/report.md`, `models/production/metadata.json`) that "
            "random split looks easier: structurally similar molecules leak between "
            "train and test under i.i.d. splitting, inflating apparent test "
            "performance relative to the harder, scaffold-generalization test.\n"
        )
    else:
        lines.append(
            "This does NOT clearly support the claim made elsewhere in this "
            "project's docs that random split looks meaningfully easier - the "
            "empirical difference here is small (within noise of a single split), "
            "so on this run the story is weaker than the docs suggest. Reporting "
            "the actual numbers as measured rather than forcing the expected "
            "conclusion; a single random seed is not strong evidence either way, "
            "and the CV stability check (`ml/results/cross_validation_report.md`) "
            "is a better guide to how much a single split's metrics can vary.\n"
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text("".join(lines), encoding="utf-8")

    print("".join(lines))
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
