"""Unit tests for backend/app/schemas.py - these instantiate the Pydantic
models directly rather than going through the API, to check field
constraints (min/max length, required fields) that test_api.py only
exercises indirectly."""

import pytest
from pydantic import ValidationError

from backend.app.schemas import (
    Descriptors,
    HistoryItem,
    ModelInfoResponse,
    PredictBatchItem,
    PredictBatchItemError,
    PredictBatchRequest,
    PredictRequest,
    PredictResponse,
)

ASPIRIN_SMILES = "CC(=O)Oc1ccccc1C(=O)O"

SAMPLE_DESCRIPTORS = {
    "MolWt": 180.16,
    "LogP": 1.31,
    "TPSA": 63.6,
    "NumHDonors": 1,
    "NumHAcceptors": 3,
    "NumRotatableBonds": 2,
    "RingCount": 1,
}


class TestPredictRequest:
    def test_valid_smiles_passes(self):
        req = PredictRequest(smiles=ASPIRIN_SMILES)
        assert req.smiles == ASPIRIN_SMILES

    def test_empty_string_raises(self):
        with pytest.raises(ValidationError):
            PredictRequest(smiles="")

    def test_too_long_string_raises(self):
        with pytest.raises(ValidationError):
            PredictRequest(smiles="C" * 301)

    def test_max_length_boundary_passes(self):
        # Exactly 300 chars is still valid (max_length=300 is inclusive).
        PredictRequest(smiles="C" * 300)

    def test_missing_field_raises(self):
        with pytest.raises(ValidationError):
            PredictRequest()


class TestPredictBatchRequest:
    def test_single_item_passes(self):
        req = PredictBatchRequest(smiles_list=[ASPIRIN_SMILES])
        assert req.smiles_list == [ASPIRIN_SMILES]

    def test_twenty_items_passes(self):
        req = PredictBatchRequest(smiles_list=["CCO"] * 20)
        assert len(req.smiles_list) == 20

    def test_empty_list_raises(self):
        # smiles_list has min_length=1 in the source - an empty list must fail.
        with pytest.raises(ValidationError):
            PredictBatchRequest(smiles_list=[])

    def test_twenty_one_items_raises(self):
        with pytest.raises(ValidationError):
            PredictBatchRequest(smiles_list=["CCO"] * 21)


class TestPredictBatchItem:
    """The docstring on PredictBatchItem says 'either result or error is
    populated, never both' - but that's a comment, not an enforced
    constraint. These tests document the actual (permissive) behavior:
    Pydantic does NOT enforce mutual exclusivity here."""

    def _sample_response(self) -> PredictResponse:
        return PredictResponse(
            smiles=ASPIRIN_SMILES,
            predicted_target=-2.17,
            target_name="log_solubility_mol_per_l",
            descriptors=Descriptors(**SAMPLE_DESCRIPTORS),
            structure_svg="<svg></svg>",
            confidence=None,
        )

    def test_only_result_set(self):
        item = PredictBatchItem(result=self._sample_response())
        assert item.result is not None
        assert item.error is None

    def test_only_error_set(self):
        item = PredictBatchItem(error=PredictBatchItemError(smiles="bad", error="Could not parse"))
        assert item.error is not None
        assert item.result is None

    def test_neither_set_is_allowed(self):
        # Both fields default to None - this is NOT rejected by the schema,
        # even though it violates the documented intent.
        item = PredictBatchItem()
        assert item.result is None
        assert item.error is None

    def test_both_set_is_allowed(self):
        # Also NOT rejected - Pydantic has no "exactly one of" constraint
        # coded here. This is a finding, not an assumption: if stricter
        # behavior is desired, it would need an explicit validator.
        item = PredictBatchItem(
            result=self._sample_response(),
            error=PredictBatchItemError(smiles="bad", error="Could not parse"),
        )
        assert item.result is not None
        assert item.error is not None


class TestDescriptors:
    def test_round_trips_with_all_seven_fields(self):
        d = Descriptors(**SAMPLE_DESCRIPTORS)
        assert d.MolWt == 180.16
        assert d.LogP == 1.31
        assert d.TPSA == 63.6
        assert d.NumHDonors == 1
        assert d.NumHAcceptors == 3
        assert d.NumRotatableBonds == 2
        assert d.RingCount == 1

    @pytest.mark.parametrize("missing_field", list(SAMPLE_DESCRIPTORS.keys()))
    def test_missing_field_raises(self, missing_field):
        incomplete = {k: v for k, v in SAMPLE_DESCRIPTORS.items() if k != missing_field}
        with pytest.raises(ValidationError):
            Descriptors(**incomplete)


class TestModelInfoResponse:
    def test_realistic_metadata_validates(self):
        info = ModelInfoResponse(
            model_version="0.1.0",
            trained_at="2026-01-15",
            dataset="ESOL (Delaney)",
            metrics={
                "val": {"rmse": 0.864, "mae": 0.689, "r2": 0.82},
                "test": {"rmse": 0.897, "mae": 0.637, "r2": 0.807},
            },
            known_limitations=[
                "Trained on 1117 small drug-like molecules; unreliable outside this applicability domain.",
            ],
        )
        assert info.model_version == "0.1.0"
        assert info.metrics["val"].rmse == 0.864
        assert info.metrics["test"].r2 == 0.807


class TestHistoryItem:
    def test_realistic_history_row_validates(self):
        item = HistoryItem(
            id="123e4567-e89b-12d3-a456-426614174000",
            smiles=ASPIRIN_SMILES,
            predicted_target=-2.17,
            model_version="0.1.0",
            created_at="2026-09-12T12:00:00+00:00",
        )
        assert item.smiles == ASPIRIN_SMILES
        assert item.predicted_target == -2.17
