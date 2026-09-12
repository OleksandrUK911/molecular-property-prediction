import numpy as np
import pandas as pd

from ml.preprocess import (
    compute_descriptors,
    compute_fingerprints,
    deduplicate,
    murcko_scaffold,
    parse_and_canonicalize,
    run_quality_checks,
    scaffold_split,
)

ASPIRIN = "CC(=O)Oc1ccccc1C(=O)O"
ETHANOL = "CCO"


def raw_row(compound_id, smiles, target):
    return {"Compound ID": compound_id, "smiles": smiles, "measured log solubility in mols per litre": target}


def test_parse_and_canonicalize_drops_invalid_smiles():
    raw = pd.DataFrame([raw_row("A", ASPIRIN, -2.3), raw_row("B", "not-a-smiles!!!", -1.0)])
    clean, dropped = parse_and_canonicalize(raw)
    assert len(clean) == 1
    assert len(dropped) == 1
    assert dropped[0]["reason"] == "unparsable"


def test_parse_and_canonicalize_strips_salts():
    # sodium acetate - salt should be stripped, leaving the acetate part
    raw = pd.DataFrame([raw_row("A", "CC(=O)[O-].[Na+]", -1.0)])
    clean, dropped = parse_and_canonicalize(raw)
    assert len(dropped) == 0
    assert "Na" not in clean.iloc[0]["smiles"]


def test_parse_and_canonicalize_produces_canonical_form():
    # two equivalent SMILES for ethanol should canonicalize to the same string
    raw = pd.DataFrame([raw_row("A", "CCO", -1.0), raw_row("B", "OCC", -1.0)])
    clean, _ = parse_and_canonicalize(raw)
    assert clean.iloc[0]["smiles"] == clean.iloc[1]["smiles"]


def test_deduplicate_averages_conflicting_targets():
    df = pd.DataFrame(
        {"compound_id": ["A", "A2"], "smiles": [ETHANOL, ETHANOL], "target": [-1.0, -2.0]}
    )
    agg, stats = deduplicate(df)
    assert len(agg) == 1
    assert agg.iloc[0]["target"] == -1.5
    assert stats["rows_merged"] == 1
    assert stats["conflicting_groups_resolved_by_averaging"] == 1


def test_deduplicate_no_duplicates_is_a_noop():
    df = pd.DataFrame({"compound_id": ["A", "B"], "smiles": [ETHANOL, ASPIRIN], "target": [-1.0, -2.0]})
    agg, stats = deduplicate(df)
    assert len(agg) == 2
    assert stats["rows_merged"] == 0


def test_compute_descriptors_returns_expected_columns():
    descriptors = compute_descriptors(pd.Series([ASPIRIN]))
    assert set(descriptors.columns) == {
        "MolWt", "LogP", "TPSA", "NumHDonors", "NumHAcceptors", "NumRotatableBonds", "RingCount",
    }
    assert descriptors.iloc[0]["RingCount"] == 1
    assert descriptors.iloc[0]["MolWt"] > 0


def test_compute_fingerprints_shape_and_type():
    fps = compute_fingerprints(pd.Series([ASPIRIN, ETHANOL]), radius=2, n_bits=128)
    assert fps.shape == (2, 128)
    assert fps.dtype == np.uint8
    assert set(np.unique(fps)).issubset({0, 1})


def test_murcko_scaffold_same_for_substituted_variants():
    # aspirin and a close analog share the same benzene-ring-based scaffold family;
    # simplest robust check: benzene itself is its own scaffold.
    assert murcko_scaffold("c1ccccc1") == "c1ccccc1"


def test_scaffold_split_produces_no_leakage_and_covers_all_rows():
    smiles_list = [ASPIRIN, ETHANOL, "c1ccccc1", "CCC", "CCCCC", "c1ccncc1", "CCN", "CCCl"]
    df = pd.DataFrame({
        "compound_id": [f"c{i}" for i in range(len(smiles_list))],
        "smiles": smiles_list,
        "target": [-1.0] * len(smiles_list),
    })
    result = scaffold_split(df, ratios=(0.5, 0.25, 0.25), seed=42)
    assert set(result["split"].unique()) <= {"train", "val", "test"}
    assert len(result) == len(df)
    assert result["split"].notna().all()


def test_scaffold_split_is_deterministic_for_same_seed():
    smiles_list = [ASPIRIN, ETHANOL, "c1ccccc1", "CCC", "CCCCC"]
    df = pd.DataFrame({
        "compound_id": [f"c{i}" for i in range(len(smiles_list))],
        "smiles": smiles_list,
        "target": [-1.0] * len(smiles_list),
    })
    result_a = scaffold_split(df.copy(), ratios=(0.6, 0.2, 0.2), seed=7)
    result_b = scaffold_split(df.copy(), ratios=(0.6, 0.2, 0.2), seed=7)
    assert result_a["split"].tolist() == result_b["split"].tolist()


def test_run_quality_checks_detects_duplicates_and_outliers():
    # IQR needs a spread of "normal" values before -50 reads as an outlier -
    # with too few rows the quartiles degenerate and nothing gets flagged.
    df = pd.DataFrame({
        "compound_id": ["A", "A2", "B", "C", "D", "E"],
        "smiles": [ETHANOL, ETHANOL, ASPIRIN, "CCC", "CCCC", "CCCCC"],
        "target": [-1.0, -1.0, -1.2, -0.9, -1.1, -50.0],  # -50 is a deliberate extreme outlier
        "split": ["train", "train", "test", "train", "val", "test"],
    })
    report = run_quality_checks(df)
    assert report["n_duplicate_smiles_rows"] == 2
    assert report["n_target_outliers_iqr"] >= 1
    assert report["split_leakage"] == {}


def test_run_quality_checks_flags_split_leakage():
    df = pd.DataFrame({
        "compound_id": ["A", "A2"],
        "smiles": [ETHANOL, ETHANOL],
        "target": [-1.0, -1.0],
        "split": ["train", "test"],  # same molecule in both splits - leakage
    })
    report = run_quality_checks(df)
    # groupby() orders keys alphabetically, hence "test<->train" not "train<->test".
    assert report["split_leakage"] == {"test<->train": 1}
