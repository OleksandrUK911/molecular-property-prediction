# API contract

Single source of truth for request/response shapes. Field names here MUST
match `ml/preprocess.py` (`DESCRIPTOR_FUNCS`) and whatever `frontend-spec/`
assumes — if one changes, update all three.

## `POST /predict`

### Request
```json
{
  "smiles": "CC(=O)Oc1ccccc1C(=O)O"
}
```
| Field | Type | Constraints |
|---|---|---|
| `smiles` | string | required, 1–300 chars |

### Response — 200 OK
```json
{
  "smiles": "CC(=O)Oc1ccccc1C(=O)O",
  "predicted_target": -2.31,
  "target_name": "log_solubility_mol_per_l",
  "descriptors": {
    "MolWt": 180.16,
    "LogP": 1.19,
    "TPSA": 63.6,
    "NumHDonors": 1,
    "NumHAcceptors": 3,
    "NumRotatableBonds": 2,
    "RingCount": 1
  },
  "structure_svg": "<svg>...</svg>",
  "confidence": null
}
```
| Field | Type | Notes |
|---|---|---|
| `smiles` | string | canonicalized echo of input |
| `predicted_target` | float | model prediction |
| `target_name` | string | fixed value `"log_solubility_mol_per_l"` for this project |
| `descriptors` | object | exactly the 7 keys from `ml/preprocess.py::DESCRIPTOR_FUNCS` — `MolWt`, `LogP`, `TPSA`, `NumHDonors`, `NumHAcceptors`, `NumRotatableBonds`, `RingCount` |
| `structure_svg` | string | inline SVG markup from RDKit, ready to render |
| `confidence` | float \| null | 0–1 if the model supports uncertainty; `null` otherwise (baseline model does not — see `ml/TODO_baseline.md`) |

### Response — 422 Unprocessable Entity (invalid SMILES)
```json
{ "detail": "Could not parse this SMILES string" }
```

### Response — 5xx (model/server error)
```json
{ "detail": "Server unavailable, please try again" }
```

## `GET /health`
```json
{ "status": "ok" }
```

## `GET /model/info`
```json
{
  "model_version": "0.1.0",
  "trained_at": "2026-09-20",
  "dataset": "ESOL (Delaney)",
  "metrics": { "val": { "rmse": 0.85, "mae": 0.62, "r2": 0.78 }, "test": { "rmse": 0.91, "mae": 0.68, "r2": 0.74 } },
  "known_limitations": [
    "Trained on 1117 small drug-like molecules; unreliable outside this applicability domain.",
    "Scaffold split means test metrics reflect generalization to unseen scaffolds, not i.i.d. performance."
  ]
}
```
Consumed by `frontend-spec/about-page.md` (Model Card page) and `ResultsCard`'s confidence badge, once the model registry (`ml/TODO_model_registry.md`) fixes real metric values.

### Залежності
- `descriptors` field names are generated from `ml/preprocess.py`; if that
  dict changes, update this file AND `frontend-spec/components.md` /
  `frontend-spec/data-visualization.md` in the same change.
- `structure_svg` needs an RDKit SVG-rendering step in the API layer — not
  yet implemented, tracked as a new task in `backend/TODO_api_design.md`.
