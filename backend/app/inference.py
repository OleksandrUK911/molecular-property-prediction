"""Inference logic, isolated from FastAPI so it can be unit-tested and
reused without spinning up the web layer (per backend/TODO_api_design.md's
note to keep inference independent of the API framework).

Field names in the returned dict match backend-spec/api-contract.md's
POST /predict response exactly.
"""

import json
from pathlib import Path
from typing import TypedDict

import joblib
from rdkit import Chem, RDLogger
from rdkit.Chem import Descriptors
from rdkit.Chem.Draw import rdMolDraw2D

RDLogger.DisableLog("rdApp.*")

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PRODUCTION_DIR = REPO_ROOT / "models" / "production"

DESCRIPTOR_FUNCS = {
    "MolWt": Descriptors.MolWt,
    "LogP": Descriptors.MolLogP,
    "TPSA": Descriptors.TPSA,
    "NumHDonors": Descriptors.NumHDonors,
    "NumHAcceptors": Descriptors.NumHAcceptors,
    "NumRotatableBonds": Descriptors.NumRotatableBonds,
    "RingCount": Descriptors.RingCount,
}
TARGET_NAME = "log_solubility_mol_per_l"


class InvalidSmilesError(ValueError):
    """Raised when RDKit cannot parse the input SMILES string."""


class PredictionResult(TypedDict):
    smiles: str
    predicted_target: float
    target_name: str
    descriptors: dict
    structure_svg: str
    confidence: float | None


class ModelService:
    """Loads the production model once and serves predictions. Instantiate
    a single instance at application startup - do not reload per request."""

    def __init__(self, production_dir: Path = PRODUCTION_DIR):
        model_path = production_dir / "model.pkl"
        metadata_path = production_dir / "metadata.json"
        if not model_path.exists():
            raise FileNotFoundError(
                f"No production model at {model_path}. Run ml/preprocess.py, "
                "ml/experiments_xgboost.py, ml/select_winner.py, and "
                "ml/register_model.py first."
            )
        bundle = joblib.load(model_path)
        self.model = bundle["model"]
        self.feature_names = bundle["feature_names"]
        self.metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    def render_structure_svg(self, mol) -> str:
        drawer = rdMolDraw2D.MolDraw2DSVG(240, 240)
        drawer.DrawMolecule(mol)
        drawer.FinishDrawing()
        return drawer.GetDrawingText()

    def predict(self, smiles: str) -> PredictionResult:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            raise InvalidSmilesError("Could not parse this SMILES string")

        canonical_smiles = Chem.MolToSmiles(mol, canonical=True)
        descriptor_values = {name: func(mol) for name, func in DESCRIPTOR_FUNCS.items()}
        feature_row = [[descriptor_values[name] for name in self.feature_names]]
        predicted_target = float(self.model.predict(feature_row)[0])

        return {
            "smiles": canonical_smiles,
            "predicted_target": predicted_target,
            "target_name": TARGET_NAME,
            "descriptors": descriptor_values,
            "structure_svg": self.render_structure_svg(mol),
            # XGBoost point predictions carry no calibrated uncertainty -
            # null per api-contract.md, not a fabricated number.
            "confidence": None,
        }

    def info(self) -> dict:
        return self.metadata
