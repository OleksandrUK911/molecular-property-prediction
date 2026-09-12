"""FastAPI application: POST /predict, GET /health, GET /model/info.

GET /history is deferred (needs the DB schema from backend/TODO_database.md,
not yet implemented) - tracked as a follow-up, not silently dropped.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .inference import InvalidSmilesError, ModelService
from .schemas import (
    ErrorResponse,
    HealthResponse,
    ModelInfoResponse,
    PredictRequest,
    PredictResponse,
)

model_service: ModelService | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model_service
    # Loaded once at startup, not per-request - see backend/TODO_api_design.md.
    model_service = ModelService()
    yield


app = FastAPI(
    title="Molecular Property Prediction API",
    description="SMILES -> RDKit descriptors -> predicted aqueous solubility (ESOL). Research/educational project.",
    version="0.1.0",
    lifespan=lifespan,
)

# Frontend origin is configured via env var for prod; wide open here for local dev only.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.get("/model/info", response_model=ModelInfoResponse)
def model_info() -> dict:
    return model_service.info()


@app.post("/predict", response_model=PredictResponse, responses={422: {"model": ErrorResponse}})
def predict(request: PredictRequest) -> dict:
    try:
        return model_service.predict(request.smiles)
    except InvalidSmilesError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
