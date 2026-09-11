from fastapi.testclient import TestClient

from backend.app.main import app

ASPIRIN_SMILES = "CC(=O)Oc1ccccc1C(=O)O"


def test_health():
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_valid_smiles():
    with TestClient(app) as client:
        response = client.post("/predict", json={"smiles": ASPIRIN_SMILES})
    assert response.status_code == 200
    body = response.json()
    assert body["target_name"] == "log_solubility_mol_per_l"
    assert "structure_svg" in body


def test_predict_invalid_smiles_returns_422():
    with TestClient(app) as client:
        response = client.post("/predict", json={"smiles": "!!!not-a-smiles!!!"})
    assert response.status_code == 422
    assert "detail" in response.json()


def test_predict_empty_smiles_rejected_by_schema():
    with TestClient(app) as client:
        response = client.post("/predict", json={"smiles": ""})
    assert response.status_code == 422  # Pydantic min_length validation


def test_model_info():
    with TestClient(app) as client:
        response = client.get("/model/info")
    assert response.status_code == 200
    assert "model_version" in response.json()
