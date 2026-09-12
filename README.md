# Molecular Property Prediction Platform

AI platform that predicts physicochemical properties of molecules from SMILES
strings, using RDKit descriptors and machine learning (XGBoost).

## Status
🟢 Working end-to-end locally (ML pipeline, backend, frontend, Docker, CI).
Not yet deployed as a public live demo — see the portfolio's sequencing rule.

## Stack
- **ML:** Python, RDKit, XGBoost, scikit-learn
- **Backend:** FastAPI, SQLite
- **Frontend:** React (Vite)
- **Infra:** Docker, GitHub Actions

## How it works
```
SMILES → RDKit descriptors/fingerprints → ML model → predicted property
```

## Run locally

```bash
docker compose up --build
# frontend: http://localhost:5173
# backend:  http://localhost:8000
```

The production model (`models/production/model.pkl`) isn't committed to
git — it's a generated artifact, not source. Build it first:

```bash
pip install -r requirements-dev.txt
python ml/preprocess.py
python ml/baseline.py
python ml/experiments_xgboost.py
python ml/experiments_fingerprint_models.py
python ml/select_winner.py
python ml/register_model.py
```

## Model Card

- **Task:** predict aqueous solubility (log mol/L) from a molecule's SMILES.
- **Model:** XGBoost regressor on 7 RDKit physicochemical descriptors
  (MolWt, LogP, TPSA, H-bond donors/acceptors, rotatable bonds, ring count).
  Chosen over linear/Ridge baselines and Random Forest on Morgan
  fingerprints — see `ml/results/experiment_comparison.md` for the full
  comparison.
- **Training data:** [ESOL (Delaney) dataset](data/README.md) — 1117 unique
  small drug-like molecules after deduplication, scaffold-split into
  train/val/test (843/167/107) so test performance reflects generalization
  to *unseen chemical scaffolds*, not just unseen molecules.
- **Metrics** (scaffold split, not directly comparable to papers using a
  random split on the same dataset):

  | Split | RMSE | MAE | R² |
  |---|---|---|---|
  | Val | 0.864 | 0.689 | 0.820 |
  | Test | 0.897 | 0.637 | 0.807 |

- **Known limitations:**
  - Trained on 1117 small drug-like molecules; unreliable outside this
    applicability domain.
  - Measurably worse on large hydrophobic/polyhalogenated compounds (PCBs,
    polyaromatic hydrocarbons, long-chain alkanes): MAE 0.90 on that
    17-compound subset vs. 0.40 dataset-wide (see
    `ml/results/evaluation_report.md`) — treat predictions for such
    molecules with reduced confidence.
  - Point predictions only — no calibrated uncertainty (`confidence: null`
    in the API). Project #2 (ADMET Prediction) is where calibrated
    uncertainty is the core focus.
  - Morgan fingerprints were evaluated and rejected as a feature: they
    underperform the 7 hand-picked descriptors on this dataset size (see
    `ml/results/fingerprint_model_metrics.json`).

## Disclaimer
Research/educational project. Not for clinical or production chemistry use.

## License
TBD
