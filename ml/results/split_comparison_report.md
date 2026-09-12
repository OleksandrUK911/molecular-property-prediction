# Scaffold split vs. random split comparison

Same descriptor set (7 columns) and same winning XGBoost hyperparameters `{'max_depth': 3, 'learning_rate': 0.03, 'n_estimators': 600, 'subsample': 0.9, 'colsample_bytree': 0.9}` trained on two different splits of the same 1117-row processed dataset:

- **scaffold** (`split` column, from `ml/preprocess.py`): whole Murcko scaffolds grouped into train/val/test, not i.i.d. by design.
- **random** (`random_split` column, generated fresh in this script via `train_test_split(..., random_state=42)`, 70/15/15): ordinary i.i.d. row split, independent of the scaffold split.

## Comparison

| Split type | Rows (train/val/test) | Metric | Val | Test |
|---|---|---|---|---|
| scaffold | 843/167/107 | RMSE | 0.864 | 0.897 |
| scaffold | 843/167/107 | MAE | 0.689 | 0.637 |
| scaffold | 843/167/107 | R2 | 0.820 | 0.807 |
| random | 781/168/168 | RMSE | 0.683 | 0.714 |
| random | 781/168/168 | MAE | 0.499 | 0.516 |
| random | 781/168/168 | R2 | 0.890 | 0.889 |

## Interpretation

Random-split test RMSE is 0.714 vs. scaffold-split test RMSE of 0.897 (difference: +0.183); random-split test R2 is 0.889 vs. scaffold-split 0.807 (difference: +0.083).

This supports the claim made elsewhere in this project's docs (`data/processed/report.md`, `models/production/metadata.json`) that random split looks easier: structurally similar molecules leak between train and test under i.i.d. splitting, inflating apparent test performance relative to the harder, scaffold-generalization test.
