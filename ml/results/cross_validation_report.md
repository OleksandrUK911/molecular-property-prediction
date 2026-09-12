# Cross-validation stability report

5-fold `KFold(n_splits=5, shuffle=True, random_state=42)` on the train+val pool (1010 rows) using the winning XGBoost hyperparameters `{'max_depth': 3, 'learning_rate': 0.03, 'n_estimators': 600, 'subsample': 0.9, 'colsample_bytree': 0.9}`. Test split (107 rows) is excluded entirely - it stays a clean holdout, never used for CV or any other model selection/validation step.

**Simplification:** this is a plain row-level K-fold, not a scaffold-aware CV - folds are i.i.d. resamples of the train+val pool, unlike the project's scaffold split used for train/val/test. A fully scaffold-aware CV (grouping whole Murcko scaffolds into folds) would be a more faithful stability check but is a bigger redesign than this check aims to be; noted here rather than silently treated as equivalent.

## Per-fold metrics

| Fold | n_val | RMSE | MAE | R2 |
|---|---|---|---|---|
| 1 | 202 | 0.621 | 0.479 | 0.906 |
| 2 | 202 | 0.676 | 0.502 | 0.905 |
| 3 | 202 | 0.627 | 0.487 | 0.897 |
| 4 | 202 | 0.694 | 0.512 | 0.883 |
| 5 | 202 | 0.738 | 0.558 | 0.884 |

## Summary (mean +/- std across folds)

- RMSE: 0.671 +/- 0.043
- MAE:  0.508 +/- 0.028
- R2:   0.895 +/- 0.010

The standard deviation here is small relative to the mean (roughly 6% of mean RMSE), which suggests the val-set RMSE reported elsewhere in this project (~0.86-0.90) is a reasonably stable estimate of this model's performance on i.i.d. resamples of this data, not an artifact of one lucky split. This does NOT validate stability under the harder scaffold-split generalization test used for the project's actual train/val/test split - it only checks stability of the descriptor-based XGBoost fit itself.
