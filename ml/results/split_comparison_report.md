# Scaffold split vs. random split comparison

Same descriptor set (7 columns) and same winning XGBoost hyperparameters `{'max_depth': 2, 'learning_rate': 0.03393891168826373, 'n_estimators': 697, 'subsample': 0.676174595034123, 'colsample_bytree': 0.9089797234514216}` trained on two different splits of the same 1117-row processed dataset:

- **scaffold** (`split` column, from `ml/preprocess.py`): whole Murcko scaffolds grouped into train/val/test, not i.i.d. by design.
- **random** (`random_split` column, generated fresh in this script via `train_test_split(..., random_state=42)`, 70/15/15): ordinary i.i.d. row split, independent of the scaffold split.

## Comparison

| Split type | Rows (train/val/test) | Metric | Val | Test |
|---|---|---|---|---|
| scaffold | 843/167/107 | RMSE | 0.825 | 0.820 |
| scaffold | 843/167/107 | MAE | 0.678 | 0.611 |
| scaffold | 843/167/107 | R2 | 0.836 | 0.838 |
| random | 781/168/168 | RMSE | 0.721 | 0.743 |
| random | 781/168/168 | MAE | 0.541 | 0.546 |
| random | 781/168/168 | R2 | 0.877 | 0.880 |

## Interpretation

Random-split test RMSE is 0.743 vs. scaffold-split test RMSE of 0.820 (difference: +0.078); random-split test R2 is 0.880 vs. scaffold-split 0.838 (difference: +0.042).

This supports the claim made elsewhere in this project's docs (`data/processed/report.md`, `models/production/metadata.json`) that random split looks easier: structurally similar molecules leak between train and test under i.i.d. splitting, inflating apparent test performance relative to the harder, scaffold-generalization test.
