"""Pydantic request/response schemas, matching backend-spec/api-contract.md."""

from pydantic import BaseModel, Field

ASPIRIN_SMILES = "CC(=O)Oc1ccccc1C(=O)O"
MAX_BATCH_SIZE = 20


class PredictRequest(BaseModel):
    smiles: str = Field(
        ...,
        min_length=1,
        max_length=300,
        description="A molecule in SMILES notation. Parsed and validated with RDKit; "
        "malformed SMILES are rejected with a 422.",
        examples=[ASPIRIN_SMILES],
    )


class PredictBatchRequest(BaseModel):
    smiles_list: list[str] = Field(
        ...,
        min_length=1,
        max_length=MAX_BATCH_SIZE,
        description=f"A batch of SMILES strings to predict in one call, up to {MAX_BATCH_SIZE} items. "
        "Invalid entries do not fail the whole batch - they come back as per-item errors "
        "alongside the successful predictions.",
        examples=[[ASPIRIN_SMILES, "CCO"]],
    )


class Descriptors(BaseModel):
    MolWt: float = Field(..., description="Molecular weight (g/mol).", examples=[180.16])
    LogP: float = Field(..., description="Crippen LogP, an estimate of lipophilicity.", examples=[1.31])
    TPSA: float = Field(..., description="Topological polar surface area (A^2).", examples=[63.6])
    NumHDonors: int = Field(..., description="Number of hydrogen bond donors.", examples=[1])
    NumHAcceptors: int = Field(..., description="Number of hydrogen bond acceptors.", examples=[3])
    NumRotatableBonds: int = Field(..., description="Number of rotatable bonds.", examples=[2])
    RingCount: int = Field(..., description="Number of rings in the molecule.", examples=[1])


class PredictResponse(BaseModel):
    smiles: str = Field(
        ...,
        description="The input SMILES, canonicalized by RDKit.",
        examples=[ASPIRIN_SMILES],
    )
    predicted_target: float = Field(
        ...,
        description="Predicted value of the target property.",
        examples=[-2.17],
    )
    target_name: str = Field(
        ...,
        description="Name of the predicted target property.",
        examples=["log_solubility_mol_per_l"],
    )
    descriptors: Descriptors = Field(..., description="RDKit descriptors computed from the input molecule.")
    structure_svg: str = Field(..., description="An SVG rendering of the molecule's 2D structure.")
    confidence: float | None = Field(
        None,
        description="Calibrated confidence for the prediction. Always null for this "
        "model - XGBoost point predictions carry no calibrated uncertainty.",
    )


class PredictBatchItemError(BaseModel):
    smiles: str = Field(..., description="The SMILES string that failed to parse or predict.")
    error: str = Field(..., description="Human-readable reason the prediction failed for this item.")


class PredictBatchItem(BaseModel):
    """One entry in a batch response: either `result` (successful prediction) or
    `error` (this SMILES failed) is populated, never both."""

    result: PredictResponse | None = Field(None, description="Present when this item predicted successfully.")
    error: PredictBatchItemError | None = Field(None, description="Present when this item failed to predict.")


class PredictBatchResponse(BaseModel):
    results: list[PredictBatchItem] = Field(
        ...,
        description="Per-item results in the same order as the request's smiles_list. "
        "One invalid SMILES does not fail the rest of the batch.",
    )


class HealthResponse(BaseModel):
    status: str = "ok"


class SplitMetrics(BaseModel):
    rmse: float
    mae: float
    r2: float


class ModelInfoResponse(BaseModel):
    model_version: str = Field(..., description="Semantic version of the currently loaded production model.", examples=["0.1.0"])
    trained_at: str = Field(..., description="Date the production model was trained/registered.", examples=["2026-01-15"])
    dataset: str = Field(..., description="Dataset the model was trained on.", examples=["ESOL (Delaney)"])
    metrics: dict[str, SplitMetrics] = Field(
        ...,
        description="Evaluation metrics (RMSE, MAE, R2) keyed by split name, e.g. 'val' and 'test'.",
    )
    known_limitations: list[str] = Field(
        ..., description="Known limitations and caveats about the model's applicability domain."
    )


class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Human-readable error message.", examples=["Could not parse this SMILES string"])


class HistoryItem(BaseModel):
    id: str = Field(..., description="Unique id (UUID4) of this history row.")
    smiles: str = Field(..., description="The canonicalized SMILES that was predicted.", examples=[ASPIRIN_SMILES])
    predicted_target: float = Field(..., description="The predicted target value for this row.", examples=[-2.17])
    model_version: str = Field(..., description="Model version that produced this prediction.", examples=["0.1.0"])
    created_at: str = Field(..., description="UTC timestamp (ISO 8601) when the prediction was made.")
