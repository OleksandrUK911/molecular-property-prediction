# GNN experiment report

Optional (P2) experiment: does a graph neural network beat the winning XGBoost model (7 RDKit descriptors, val RMSE=0.864, test RMSE=0.897)? Uses the same scaffold train/val/test split as every other experiment in this repo (843/167/107 molecules) - no re-splitting.

## Architecture

- Node features (4): atomic number, degree, formal charge, aromaticity.
- Edge features (4, one-hot): bond type (single/double/triple/aromatic).
- 3 GCNConv layers (hidden dim=64) + ReLU, global mean pool, linear regression head.
- Adam (lr=0.001), MSE loss, batch size 32.
- Early stopping on val MSE, patience=30 epochs, max 300 epochs. Actually trained for 214 epochs.
- No hyperparameter search - fixed, reasonable architecture, per this experiment's explicitly exploratory ("does it even help") scope.

## Results

| Model | Split | RMSE | MAE | R2 |
|---|---|---|---|---|
| gnn_gcn | val | 1.310 | 0.996 | 0.586 |
| gnn_gcn | test | 1.624 | 1.193 | 0.365 |
| xgboost_tuned (winner) | val | 0.864 | 0.689 | 0.820 |
| xgboost_tuned (winner) | test | 0.897 | 0.637 | 0.807 |

## Conclusion

**The GNN does not beat XGBoost.** This is the expected, honest outcome for this dataset: ~1100 molecules is tiny for a GNN (which typically needs thousands-to-millions of examples to learn useful graph representations from scratch), while the 7 hand-picked RDKit descriptors (dominated by LogP, per the SHAP analysis in `ml/results/interpretability_report.md`) already encode the chemistry that matters for aqueous solubility. A portfolio project correctly reporting a negative result here is more credible than one that only shows successes.
