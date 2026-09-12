"""FastAPI application: POST /predict, GET /health, GET /model/info,
GET /history."""

import logging
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request
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
    PredictRequest,
    PredictResponse,
)

model_service: ModelService | None = None
limiter = Limiter(key_func=get_remote_address)


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


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/model/info", response_model=ModelInfoResponse)
def model_info() -> dict:
    return model_service.info()


@app.post("/predict", response_model=PredictResponse, responses={422: {"model": ErrorResponse}})
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
    db.insert_history(
        id=str(uuid.uuid4()),
        smiles=result["smiles"],
        predicted_target=result["predicted_target"],
        model_version=model_service.metadata["model_version"],
        created_at=datetime.now(timezone.utc).isoformat(),
    )
    return result


@app.get("/history", response_model=list[HistoryItem])
def history() -> list[dict]:
    return db.list_history()
