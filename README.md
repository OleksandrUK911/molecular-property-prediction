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
python ml/experiments_xgboost_optuna.py
python ml/select_winner.py
python ml/evaluate.py
python ml/register_model.py
```

`ml/select_winner.py` picks by best val RMSE automatically — `register_model.py`
and `evaluate.py` load whichever model that is (currently `xgboost_optuna`),
not a hardcoded one, so this order always registers the true current winner.

## Model Card

- **Task:** predict aqueous solubility (log mol/L) from a molecule's SMILES.
- **Model:** XGBoost regressor on 7 RDKit physicochemical descriptors
  (MolWt, LogP, TPSA, H-bond donors/acceptors, rotatable bonds, ring count),
  hyperparameters found via a 50-trial Optuna TPE search
  (`ml/experiments_xgboost_optuna.py`). Chosen over linear/Ridge baselines,
  a fixed-grid-tuned XGBoost, and Random Forest on Morgan fingerprints —
  see `ml/results/experiment_comparison.md` for the full comparison and
  `ml/results/optuna_report.md` for the search itself.
- **Training data:** [ESOL (Delaney) dataset](data/README.md) — 1117 unique
  small drug-like molecules after deduplication, scaffold-split into
  train/val/test (843/167/107) so test performance reflects generalization
  to *unseen chemical scaffolds*, not just unseen molecules.
- **Metrics** (scaffold split, not directly comparable to papers using a
  random split on the same dataset):

  | Split | RMSE | MAE | R² |
  |---|---|---|---|
  | Val | 0.825 | 0.678 | 0.836 |
  | Test | 0.820 | 0.611 | 0.838 |

- **Known limitations:**
  - Trained on 1117 small drug-like molecules; unreliable outside this
    applicability domain.
  - Measurably worse on large hydrophobic/polyhalogenated compounds (PCBs,
    polyaromatic hydrocarbons, long-chain alkanes): MAE 0.97 on that
    17-compound subset vs. 0.45 dataset-wide, 2.16x worse (see
    `ml/results/evaluation_report.md`) — treat predictions for such
    molecules with reduced confidence.
  - Point predictions only — no calibrated uncertainty (`confidence: null`
    in the API). Project #2 (ADMET Prediction) is where calibrated
    uncertainty is the core focus.
  - Morgan fingerprints were evaluated (multiple radii/bit sizes) and
    rejected as a feature: they underperform the 7 hand-picked descriptors
    on this dataset size (see `ml/results/fingerprint_model_metrics.json`
    and `ml/results/fingerprint_size_comparison_report.md`).
  - A graph neural network (GNN) was also tried and did not beat XGBoost
    on this small dataset (see `ml/results/gnn_report.md`) — an expected,
    honest negative result, not a bug.

## Disclaimer
Research/educational project. Not for clinical or production chemistry use.

## License
TBD
