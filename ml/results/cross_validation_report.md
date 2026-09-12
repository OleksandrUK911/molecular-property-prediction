# Cross-validation stability report

5-fold `KFold(n_splits=5, shuffle=True, random_state=42)` on the train+val pool (1010 rows) using the winning XGBoost hyperparameters `{'max_depth': 2, 'learning_rate': 0.03393891168826373, 'n_estimators': 697, 'subsample': 0.676174595034123, 'colsample_bytree': 0.9089797234514216}`. Test split (107 rows) is excluded entirely - it stays a clean holdout, never used for CV or any other model selection/validation step.

**Simplification:** this is a plain row-level K-fold, not a scaffold-aware CV - folds are i.i.d. resamples of the train+val pool, unlike the project's scaffold split used for train/val/test. A fully scaffold-aware CV (grouping whole Murcko scaffolds into folds) would be a more faithful stability check but is a bigger redesign than this check aims to be; noted here rather than silently treated as equivalent.

## Per-fold metrics

| Fold | n_val | RMSE | MAE | R2 |
|---|---|---|---|---|
| 1 | 202 | 0.653 | 0.500 | 0.896 |
| 2 | 202 | 0.709 | 0.528 | 0.895 |
| 3 | 202 | 0.643 | 0.500 | 0.892 |
| 4 | 202 | 0.725 | 0.542 | 0.872 |
| 5 | 202 | 0.750 | 0.566 | 0.880 |

## Summary (mean +/- std across folds)

- RMSE: 0.696 +/- 0.041
- MAE:  0.527 +/- 0.025
- R2:   0.887 +/- 0.009

The standard deviation here is small relative to the mean (roughly 6% of mean RMSE), which suggests the val-set RMSE reported elsewhere in this project (~0.86-0.90) is a reasonably stable estimate of this model's performance on i.i.d. resamples of this data, not an artifact of one lucky split. This does NOT validate stability under the harder scaffold-split generalization test used for the project's actual train/val/test split - it only checks stability of the descriptor-based XGBoost fit itself.
