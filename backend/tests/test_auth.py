"""Tests for the optional X-API-Key gate on POST /predict and
POST /predict/batch (see require_api_key in backend/app/main.py).

The gate is opt-in via the API_KEY env var, unset by default so the public
demo stays fully open. These tests use monkeypatch.setenv so each test's
value is isolated - the dependency reads os.environ fresh on every request
(it does NOT cache the value at import/module load time), so monkeypatch
actually takes effect per-request rather than being silently ignored.
"""

from fastapi.testclient import TestClient

from backend.app.main import app

ASPIRIN_SMILES = "CC(=O)Oc1ccccc1C(=O)O"


def test_predict_works_with_no_header_when_api_key_unset(monkeypatch):
    monkeypatch.delenv("API_KEY", raising=False)
    with TestClient(app) as client:
        response = client.post("/predict", json={"smiles": ASPIRIN_SMILES})
    assert response.status_code == 200


def test_predict_rejects_missing_header_when_api_key_set(monkeypatch):
    monkeypatch.setenv("API_KEY", "secret123")
    with TestClient(app) as client:
        response = client.post("/predict", json={"smiles": ASPIRIN_SMILES})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or missing API key"


def test_predict_rejects_wrong_header_when_api_key_set(monkeypatch):
    monkeypatch.setenv("API_KEY", "secret123")
    with TestClient(app) as client:
        response = client.post(
            "/predict",
            json={"smiles": ASPIRIN_SMILES},
            headers={"X-API-Key": "wrong-key"},
        )
    assert response.status_code == 401


def test_predict_accepts_correct_header_when_api_key_set(monkeypatch):
    monkeypatch.setenv("API_KEY", "secret123")
    with TestClient(app) as client:
        response = client.post(
            "/predict",
            json={"smiles": ASPIRIN_SMILES},
            headers={"X-API-Key": "secret123"},
        )
    assert response.status_code == 200


def test_predict_batch_requires_key_when_configured(monkeypatch):
    monkeypatch.setenv("API_KEY", "secret123")
    with TestClient(app) as client:
        no_header = client.post("/predict/batch", json={"smiles_list": [ASPIRIN_SMILES]})
        with_header = client.post(
            "/predict/batch",
            json={"smiles_list": [ASPIRIN_SMILES]},
            headers={"X-API-Key": "secret123"},
        )
    assert no_header.status_code == 401
    assert with_header.status_code == 200


def test_health_stays_public_even_when_api_key_set(monkeypatch):
    # /health, /model/info, /history are read-only/non-costly and stay
    # public regardless of API_KEY configuration.
    monkeypatch.setenv("API_KEY", "secret123")
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200


def test_history_stays_public_even_when_api_key_set(monkeypatch):
    monkeypatch.setenv("API_KEY", "secret123")
    with TestClient(app) as client:
        response = client.get("/history")
    assert response.status_code == 200


def test_model_info_stays_public_even_when_api_key_set(monkeypatch):
    monkeypatch.setenv("API_KEY", "secret123")
    with TestClient(app) as client:
        response = client.get("/model/info")
    assert response.status_code == 200
