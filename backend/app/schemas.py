"""Pydantic request/response schemas, matching backend-spec/api-contract.md."""

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    smiles: str = Field(..., min_length=1, max_length=300)


class Descriptors(BaseModel):
    MolWt: float
    LogP: float
    TPSA: float
    NumHDonors: int
    NumHAcceptors: int
    NumRotatableBonds: int
    RingCount: int


class PredictResponse(BaseModel):
    smiles: str
    predicted_target: float
    target_name: str
    descriptors: Descriptors
    structure_svg: str
    confidence: float | None = None


class HealthResponse(BaseModel):
    status: str = "ok"


class SplitMetrics(BaseModel):
    rmse: float
    mae: float
    r2: float


class ModelInfoResponse(BaseModel):
    model_version: str
    trained_at: str
    dataset: str
    metrics: dict[str, SplitMetrics]
    known_limitations: list[str]


class ErrorResponse(BaseModel):
    detail: str


class HistoryItem(BaseModel):
    id: str
    smiles: str
    predicted_target: float
    model_version: str
    created_at: str
