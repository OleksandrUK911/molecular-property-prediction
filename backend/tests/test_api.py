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


def test_predict_writes_history_row():
    with TestClient(app) as client:
        client.post("/predict", json={"smiles": ASPIRIN_SMILES})
        response = client.get("/history")
    assert response.status_code == 200
    rows = response.json()
    assert len(rows) == 1
    assert rows[0]["smiles"]
    assert "model_version" in rows[0]
    assert "created_at" in rows[0]


def test_history_newest_first():
    with TestClient(app) as client:
        client.post("/predict", json={"smiles": "CCO"})
        client.post("/predict", json={"smiles": ASPIRIN_SMILES})
        response = client.get("/history")
    rows = response.json()
    assert len(rows) == 2
    assert rows[0]["created_at"] >= rows[1]["created_at"]


def test_history_empty_when_no_predictions_made():
    with TestClient(app) as client:
        response = client.get("/history")
    assert response.status_code == 200
    assert response.json() == []


def test_failed_prediction_does_not_write_history():
    with TestClient(app) as client:
        client.post("/predict", json={"smiles": "!!!not-a-smiles!!!"})
        response = client.get("/history")
    assert response.json() == []
