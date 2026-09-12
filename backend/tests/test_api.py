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


def test_rate_limit_returns_429_after_threshold():
    with TestClient(app) as client:
        responses = [client.post("/predict", json={"smiles": "CCO"}) for _ in range(31)]
    assert responses[-1].status_code == 429
    assert "detail" in responses[-1].json()


def test_predict_batch_valid_smiles():
    with TestClient(app) as client:
        response = client.post(
            "/predict/batch",
            json={"smiles_list": ["CCO", ASPIRIN_SMILES, "CC(C)O"]},
        )
    assert response.status_code == 200
    results = response.json()["results"]
    assert len(results) == 3
    for item in results:
        assert item["result"] is not None
        assert item["error"] is None
        assert item["result"]["target_name"] == "log_solubility_mol_per_l"


def test_predict_batch_mixed_valid_and_invalid():
    with TestClient(app) as client:
        response = client.post(
            "/predict/batch",
            json={"smiles_list": [ASPIRIN_SMILES, "!!!not-a-smiles!!!"]},
        )
    assert response.status_code == 200
    results = response.json()["results"]
    assert len(results) == 2

    valid_item, invalid_item = results
    assert valid_item["result"] is not None
    assert valid_item["error"] is None

    assert invalid_item["result"] is None
    assert invalid_item["error"] is not None
    assert invalid_item["error"]["smiles"] == "!!!not-a-smiles!!!"


def test_predict_batch_writes_history_only_for_successes():
    with TestClient(app) as client:
        client.post(
            "/predict/batch",
            json={"smiles_list": [ASPIRIN_SMILES, "!!!not-a-smiles!!!", "CCO"]},
        )
        response = client.get("/history")
    rows = response.json()
    assert len(rows) == 2


def test_predict_batch_exceeding_max_size_returns_422():
    with TestClient(app) as client:
        response = client.post(
            "/predict/batch",
            json={"smiles_list": ["CCO"] * 21},
        )
    assert response.status_code == 422


def test_unhandled_exception_returns_generic_500(monkeypatch):
    import backend.app.main as main_module

    def boom(_smiles):
        raise RuntimeError("simulated failure")

    # raise_server_exceptions=False: otherwise TestClient re-raises the
    # original exception for debugging even though our handler already
    # produced a real 500 response - we want to assert on that response.
    with TestClient(app, raise_server_exceptions=False) as client:
        # Patch only after lifespan startup has run, so model_service is
        # already the real instance (not None) - patching before entering
        # the context would target a not-yet-initialized global.
        monkeypatch.setattr(main_module.model_service, "predict", boom)
        response = client.post("/predict", json={"smiles": "CCO"})
    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}
