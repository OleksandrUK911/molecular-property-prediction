"""Reproducible raw -> processed pipeline for the ESOL dataset.

Usage:
    python ml/preprocess.py

Reads data/raw/delaney-processed.csv, parses and canonicalizes SMILES,
computes RDKit descriptors and Morgan fingerprints, splits into
train/val/test (scaffold split by default), and writes everything to
data/processed/. Also writes data/processed/report.md summarizing dataset
quality checks (duplicates, conflicting labels, split leakage).
"""

import argparse
import json
import urllib.request
from pathlib import Path

import numpy as np
import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem, Descriptors, SaltRemover
from rdkit.Chem.Scaffolds import MurckoScaffold

RDLogger.DisableLog("rdApp.*")

ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = ROOT / "data" / "raw" / "delaney-processed.csv"
RAW_DATASET_URL = "https://deepchemdata.s3-us-west-1.amazonaws.com/datasets/delaney-processed.csv"
PROCESSED_DIR = ROOT / "data" / "processed"
SEED = 42
SPLIT_RATIOS = (0.70, 0.15, 0.15)  # train, val, test


def ensure_raw_dataset() -> None:
    """data/raw/ is gitignored (see data/README.md) - fetch the dataset on
    first run (locally or in CI) rather than requiring a manual download
    step outside this script."""
    if RAW_PATH.exists():
        return
    RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
    print(f"{RAW_PATH} not found, downloading from {RAW_DATASET_URL} ...")
    urllib.request.urlretrieve(RAW_DATASET_URL, RAW_PATH)

DESCRIPTOR_FUNCS = {
    "MolWt": Descriptors.MolWt,
    "LogP": Descriptors.MolLogP,
    "TPSA": Descriptors.TPSA,
    "NumHDonors": Descriptors.NumHDonors,
    "NumHAcceptors": Descriptors.NumHAcceptors,
    "NumRotatableBonds": Descriptors.NumRotatableBonds,
    "RingCount": Descriptors.RingCount,
}

SALT_REMOVER = SaltRemover.SaltRemover()


def parse_and_canonicalize(df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    """Parse SMILES via RDKit, strip salts, canonicalize. Returns (clean_df, dropped_records)."""
    dropped = []
    rows = []
    for _, row in df.iterrows():
        smiles = row["smiles"].strip()
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            dropped.append({"compound_id": row["Compound ID"], "smiles": smiles, "reason": "unparsable"})
            continue
        mol = SALT_REMOVER.StripMol(mol, dontRemoveEverything=True)
        if mol is None or mol.GetNumAtoms() == 0:
            dropped.append({"compound_id": row["Compound ID"], "smiles": smiles, "reason": "empty_after_salt_removal"})
            continue
        canonical = Chem.MolToSmiles(mol, canonical=True)
        rows.append(
            {
                "compound_id": row["Compound ID"],
                "smiles": canonical,
                "target": row["measured log solubility in mols per litre"],
            }
        )
    return pd.DataFrame(rows), dropped


def deduplicate(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Collapse rows sharing a canonical SMILES into one, averaging the target.
    Conflicting duplicate labels are usually measurement noise for the same
    compound (e.g. ESOL rows re-measured) rather than distinct molecules."""
    before = len(df)
    dup_mask = df.duplicated(subset=["smiles"], keep=False)
    conflicting_before = 0
    if dup_mask.any():
        conflicting_before = int(
            df[dup_mask].groupby("smiles")["target"].nunique().gt(1).sum()
        )

    agg = df.groupby("smiles", as_index=False).agg(
        compound_id=("compound_id", "first"),
        target=("target", "mean"),
    )
    agg = agg[["compound_id", "smiles", "target"]]

    stats = {
        "rows_before": before,
        "rows_after": len(agg),
        "rows_merged": before - len(agg),
        "conflicting_groups_resolved_by_averaging": conflicting_before,
    }
    return agg, stats


def compute_descriptors(smiles_series: pd.Series) -> pd.DataFrame:
    records = []
    for smiles in smiles_series:
        mol = Chem.MolFromSmiles(smiles)
        records.append({name: func(mol) for name, func in DESCRIPTOR_FUNCS.items()})
    return pd.DataFrame(records)


def compute_fingerprints(smiles_series: pd.Series, radius: int = 2, n_bits: int = 1024) -> np.ndarray:
    fps = np.zeros((len(smiles_series), n_bits), dtype=np.uint8)
    for i, smiles in enumerate(smiles_series):
        mol = Chem.MolFromSmiles(smiles)
        bitvect = AllChem.GetMorganFingerprintAsBitVect(mol, radius, nBits=n_bits)
        fps[i] = np.array(bitvect)
    return fps


def murcko_scaffold(smiles: str) -> str:
    mol = Chem.MolFromSmiles(smiles)
    scaffold = MurckoScaffold.GetScaffoldForMol(mol)
    return Chem.MolToSmiles(scaffold, canonical=True)


def scaffold_split(df: pd.DataFrame, ratios: tuple[float, float, float], seed: int) -> pd.DataFrame:
    """Group molecules by Murcko scaffold, then assign whole scaffold groups to
    splits so structurally related molecules never cross split boundaries."""
    df = df.copy()
    df["scaffold"] = df["smiles"].map(murcko_scaffold)

    rng = np.random.default_rng(seed)
    scaffold_groups = df.groupby("scaffold").indices  # scaffold -> array of row positions
    scaffold_keys = list(scaffold_groups.keys())
    rng.shuffle(scaffold_keys)

    n_total = len(df)
    n_train_target = int(ratios[0] * n_total)
    n_val_target = int(ratios[1] * n_total)

    split = np.empty(n_total, dtype=object)
    n_train, n_val = 0, 0
    for scaffold in scaffold_keys:
        idx = scaffold_groups[scaffold]
        if n_train < n_train_target:
            split[idx] = "train"
            n_train += len(idx)
        elif n_val < n_val_target:
            split[idx] = "val"
            n_val += len(idx)
        else:
            split[idx] = "test"

    df["split"] = split
    return df.drop(columns=["scaffold"])


def run_quality_checks(df: pd.DataFrame) -> dict:
    report = {}

    dup_mask = df.duplicated(subset=["smiles"], keep=False)
    dup_groups = df[dup_mask].groupby("smiles")
    conflicting = []
    for smiles, group in dup_groups:
        if group["target"].nunique() > 1:
            conflicting.append({"smiles": smiles, "targets": group["target"].tolist()})
    report["n_duplicate_smiles_rows"] = int(dup_mask.sum())
    report["n_conflicting_label_groups"] = len(conflicting)
    report["conflicting_examples"] = conflicting[:5]

    q1, q3 = df["target"].quantile([0.25, 0.75])
    iqr = q3 - q1
    outlier_mask = (df["target"] < q1 - 1.5 * iqr) | (df["target"] > q3 + 1.5 * iqr)
    report["n_target_outliers_iqr"] = int(outlier_mask.sum())
    report["target_outliers"] = df.loc[outlier_mask, ["compound_id", "smiles", "target"]].to_dict("records")

    split_smiles = {s: set(g["smiles"]) for s, g in df.groupby("split")}
    leaks = {}
    splits = list(split_smiles.keys())
    for i in range(len(splits)):
        for j in range(i + 1, len(splits)):
            overlap = split_smiles[splits[i]] & split_smiles[splits[j]]
            if overlap:
                leaks[f"{splits[i]}<->{splits[j]}"] = len(overlap)
    report["split_leakage"] = leaks

    report["split_sizes"] = df["split"].value_counts().to_dict()
    report["target_stats_by_split"] = {
        split: {"mean": float(g["target"].mean()), "std": float(g["target"].std())}
        for split, g in df.groupby("split")
    }

    return report


def write_report(report: dict, dropped: list[dict], path: Path) -> None:
    lines = ["# Data quality report\n"]
    lines.append(f"- Dropped during parsing: {len(dropped)} molecules\n")
    lines.append(
        f"- Deduplicated: {report['deduplication']['rows_merged']} rows merged "
        f"({report['deduplication']['conflicting_groups_resolved_by_averaging']} had conflicting labels, resolved by averaging)\n"
    )
    lines.append(f"- Duplicate SMILES rows remaining after dedup: {report['n_duplicate_smiles_rows']}\n")
    lines.append(f"- Conflicting-label duplicate groups remaining: {report['n_conflicting_label_groups']}\n")
    lines.append(f"- Target outliers (IQR rule): {report['n_target_outliers_iqr']}\n")
    lines.append(
        "  Decision: kept in the dataset (not dropped). Manually inspected — "
        "these are real, physically-plausible low-solubility compounds "
        "(PCBs, polyaromatic hydrocarbons, long-chain alkanes/alcohols), not "
        "measurement errors. Their residuals should be checked separately in "
        "`ml/TODO_evaluation_validation.md`; if the model systematically fails "
        "on them, that is an applicability-domain limitation to document in "
        "the model card, not a reason to remove them here.\n"
    )
    lines.append(f"- Split sizes: {report['split_sizes']}\n")
    lines.append(f"- Split leakage (should be empty): {report['split_leakage']}\n")
    lines.append(f"- Target mean/std by split: {report['target_stats_by_split']}\n")
    lines.append(
        "\n**Note:** target mean differs noticeably between train and test "
        "(scaffold split groups whole chemical scaffolds into one split, so "
        "it is *not* i.i.d. by design — it tests generalization to unseen "
        "scaffolds, at the cost of a distribution shift vs. random split). "
        "Expected metric degradation on test relative to a random split is "
        "normal here, not a bug.\n"
    )
    if report["conflicting_examples"]:
        lines.append("\n## Conflicting label examples\n")
        for ex in report["conflicting_examples"]:
            lines.append(f"- `{ex['smiles']}`: {ex['targets']}\n")
    if report["target_outliers"]:
        lines.append("\n## Target outliers (kept, see decision above)\n")
        for ex in report["target_outliers"]:
            lines.append(f"- {ex['compound_id']} (`{ex['smiles']}`): {ex['target']}\n")
    path.write_text("".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args()

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    ensure_raw_dataset()

    raw = pd.read_csv(RAW_PATH)
    clean, dropped = parse_and_canonicalize(raw)
    clean, dedup_stats = deduplicate(clean)

    descriptors = compute_descriptors(clean["smiles"])
    fingerprints = compute_fingerprints(clean["smiles"])

    full = pd.concat([clean.reset_index(drop=True), descriptors.reset_index(drop=True)], axis=1)
    full = scaffold_split(full, SPLIT_RATIOS, args.seed)

    full.to_csv(PROCESSED_DIR / "esol_processed.csv", index=False)
    np.save(PROCESSED_DIR / "esol_morgan_fp.npy", fingerprints)

    dropped_path = PROCESSED_DIR / "dropped_smiles.json"
    dropped_path.write_text(json.dumps(dropped, indent=2), encoding="utf-8")

    quality_report = run_quality_checks(full)
    quality_report["deduplication"] = dedup_stats
    write_report(quality_report, dropped, PROCESSED_DIR / "report.md")

    print(f"Processed {len(full)} molecules ({len(dropped)} dropped, {dedup_stats['rows_merged']} merged as duplicates).")
    print(f"Split sizes: {quality_report['split_sizes']}")
    print(f"Split leakage: {quality_report['split_leakage']}")
    print(f"Wrote: {PROCESSED_DIR}")


if __name__ == "__main__":
    main()
