import pytest

from backend.app.inference import InvalidSmilesError, ModelService

ASPIRIN_SMILES = "CC(=O)Oc1ccccc1C(=O)O"


@pytest.fixture(scope="module")
def service():
    return ModelService()


def test_predict_valid_smiles_returns_expected_fields(service):
    result = service.predict(ASPIRIN_SMILES)
    assert result["smiles"]  # canonical echo, non-empty
    assert isinstance(result["predicted_target"], float)
    assert result["target_name"] == "log_solubility_mol_per_l"
    assert set(result["descriptors"].keys()) == {
        "MolWt", "LogP", "TPSA", "NumHDonors", "NumHAcceptors", "NumRotatableBonds", "RingCount",
    }
    assert result["structure_svg"].startswith("<?xml") or "<svg" in result["structure_svg"]
    assert result["confidence"] is None


def test_predict_invalid_smiles_raises(service):
    with pytest.raises(InvalidSmilesError):
        service.predict("this is not a smiles string!!!")


def test_predict_is_deterministic(service):
    first = service.predict(ASPIRIN_SMILES)
    second = service.predict(ASPIRIN_SMILES)
    assert first["predicted_target"] == second["predicted_target"]


def test_model_info_matches_metadata_schema(service):
    info = service.info()
    assert "model_version" in info
    assert "metrics" in info
    assert "val" in info["metrics"] and "test" in info["metrics"]
    assert "known_limitations" in info
