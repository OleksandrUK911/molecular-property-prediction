# Molecular Property Prediction Platform

AI platform that predicts physicochemical properties of molecules from SMILES
strings, using RDKit descriptors and machine learning (XGBoost / GNN).

## Status
🟡 In planning — implementation not started yet.

## Stack
- **ML:** Python, RDKit, XGBoost, PyTorch Geometric
- **Backend:** FastAPI, PostgreSQL
- **Frontend:** React
- **Infra:** Docker, GitHub Actions

## How it works
```
SMILES → RDKit descriptors/fingerprints → ML model → predicted property
```

## Disclaimer
Research/educational project. Not for clinical or production chemistry use.

## License
TBD
