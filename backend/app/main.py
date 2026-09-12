"""FastAPI application: POST /predict, POST /predict/batch, GET /health,
GET /model/info, GET /history."""

import logging
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from . import db
from .inference import InvalidSmilesError, ModelService
from .logging_config import log_requests_middleware, log_with_fields
from .schemas import (
    ErrorResponse,
    HealthResponse,
    HistoryItem,
    ModelInfoResponse,
    PredictBatchItem,
    PredictBatchItemError,
    PredictBatchRequest,
    PredictBatchResponse,
    PredictRequest,
    PredictResponse,
)

model_service: ModelService | None = None
limiter = Limiter(key_func=get_remote_address)

RATE_LIMIT_RESPONSE = {429: {"model": ErrorResponse, "description": "Too many requests - rate limit exceeded."}}
VALIDATION_RESPONSE = {422: {"model": ErrorResponse, "description": "Invalid input (e.g. unparseable SMILES, or request body failing schema validation)."}}


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model_service
    # Loaded once at startup, not per-request - see backend/TODO_api_design.md.
    model_service = ModelService()
    db.init_db()
    yield


app = FastAPI(
    title="Molecular Property Prediction API",
    description="SMILES -> RDKit descriptors -> predicted aqueous solubility (ESOL). Research/educational project.",
    version="0.1.0",
    lifespan=lifespan,
)
app.state.limiter = limiter
app.middleware("http")(log_requests_middleware)

# Frontend origin is configured via env var for prod; wide open here for local dev only.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(status_code=429, content={"detail": "Too many requests, please slow down."})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # Centralized so every unexpected (500) error gets one consistent
    # response shape and one place logging the full traceback - expected
    # errors (422 invalid SMILES, 429 rate limit) are raised explicitly
    # below and never reach this handler, per backend/TODO_logging_observability.md's
    # note on distinguishing expected vs unexpected failures in logs.
    log_with_fields(logging.ERROR, "unhandled_exception", path=request.url.path, error=str(exc))
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


def require_api_key(request: Request) -> None:
    """Optional API-key gate for the costly prediction endpoints (P2 in the
    project plan - this is a public portfolio demo, so auth is opt-in).

    Reads os.environ["API_KEY"] fresh on every call rather than caching it
    at import time, so that: (a) the default (unset) case leaves /predict
    and /predict/batch fully public, matching this project's actual
    public-demo deployment, and (b) tests can toggle it on/off per-test via
    monkeypatch.setenv without needing to reload the module.
    """
    expected = os.environ.get("API_KEY")
    if not expected:
        return
    provided = request.headers.get("X-API-Key")
    if provided != expected:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


def _record_history(result: dict) -> None:
    """Persist one successful prediction as a history row. Shared by
    /predict and /predict/batch so the uuid/timestamp/insert logic lives
    in exactly one place - the frontend never writes history directly,
    see backend-spec/api-contract.md."""
    db.insert_history(
        id=str(uuid.uuid4()),
        smiles=result["smiles"],
        predicted_target=result["predicted_target"],
        model_version=model_service.metadata["model_version"],
        created_at=datetime.now(timezone.utc).isoformat(),
    )


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Liveness check. Always returns `{\"status\": \"ok\"}` if the process is up.",
)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get(
    "/model/info",
    response_model=ModelInfoResponse,
    summary="Current model metadata",
    description="Returns the version, training date, dataset, evaluation metrics, and known "
    "limitations of the model currently loaded in production.",
)
def model_info() -> dict:
    return model_service.info()


@app.post(
    "/predict",
    response_model=PredictResponse,
    responses={**VALIDATION_RESPONSE, **RATE_LIMIT_RESPONSE},
    summary="Predict solubility from a single SMILES string",
    description="Parses the given SMILES with RDKit, computes molecular descriptors, and returns "
    "the model's predicted aqueous solubility along with a rendered structure. Successful "
    "predictions are persisted to /history. Rate limited to 30 requests/minute per client. "
    "Requires an X-API-Key header only if the API_KEY environment variable is configured "
    "(unset by default - see backend-spec/api-contract.md).",
    dependencies=[Depends(require_api_key)],
)
@limiter.limit("30/minute")
def predict(request: Request, body: PredictRequest) -> dict:
    try:
        result = model_service.predict(body.smiles)
    except InvalidSmilesError as exc:
        log_with_fields(logging.INFO, "predict_rejected", reason="invalid_smiles", smiles=body.smiles)
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    log_with_fields(logging.INFO, "predict_ok", smiles=result["smiles"], predicted_target=result["predicted_target"])

    # Every successful prediction is persisted server-side - the frontend
    # never writes history directly, see backend-spec/api-contract.md.
    _record_history(result)
    return result


@app.post(
    "/predict/batch",
    response_model=PredictBatchResponse,
    responses={**VALIDATION_RESPONSE, **RATE_LIMIT_RESPONSE},
    summary="Predict solubility for a batch of SMILES strings",
    description="Runs prediction for up to 20 SMILES strings in one call. A SMILES that fails to "
    "parse does not fail the whole batch - it comes back as a per-item `error` entry alongside the "
    "other items' `result` entries, in the same order as the request. Every successful item is "
    "persisted to /history. Rate limited to 30 requests/minute per client. Requires an "
    "X-API-Key header only if the API_KEY environment variable is configured (unset by "
    "default - see backend-spec/api-contract.md).",
    dependencies=[Depends(require_api_key)],
)
@limiter.limit("30/minute")
def predict_batch(request: Request, body: PredictBatchRequest) -> dict:
    items: list[PredictBatchItem] = []
    for smiles in body.smiles_list:
        try:
            result = model_service.predict(smiles)
        except InvalidSmilesError as exc:
            log_with_fields(logging.INFO, "predict_rejected", reason="invalid_smiles", smiles=smiles)
            items.append(PredictBatchItem(error=PredictBatchItemError(smiles=smiles, error=str(exc))))
            continue

        log_with_fields(logging.INFO, "predict_ok", smiles=result["smiles"], predicted_target=result["predicted_target"])
        _record_history(result)
        items.append(PredictBatchItem(result=result))

    return {"results": items}


@app.get(
    "/history",
    response_model=list[HistoryItem],
    summary="Recent prediction history",
    description="Returns the most recent successful predictions (newest first), persisted "
    "server-side by /predict and /predict/batch.",
)
def history() -> list[dict]:
    return db.list_history()
