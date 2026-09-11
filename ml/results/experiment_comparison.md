# Experiment comparison

| Model | Split | RMSE | MAE | R2 | n_features |
|---|---|---|---|---|---|
| linear_regression | test | 0.890 | 0.724 | 0.809 | 7 |
| linear_regression | val | 1.105 | 0.872 | 0.706 | 7 |
| naive_mean | test | 2.300 | 1.808 | -0.273 | 7 |
| naive_mean | val | 2.190 | 1.686 | -0.156 | 7 |
| random_forest_combined | test | 0.901 | 0.636 | 0.805 | 1031 |
| random_forest_combined | val | 0.873 | 0.693 | 0.816 | 1031 |
| random_forest_descriptors_only | test | 0.922 | 0.648 | 0.796 | 7 |
| random_forest_descriptors_only | val | 0.907 | 0.724 | 0.802 | 7 |
| random_forest_fingerprints_only | test | 1.858 | 1.388 | 0.169 | 1024 |
| random_forest_fingerprints_only | val | 1.515 | 1.147 | 0.447 | 1024 |
| ridge | test | 0.890 | 0.724 | 0.809 | 7 |
| ridge | val | 1.105 | 0.871 | 0.706 | 7 |
| xgboost_default | test | 1.016 | 0.706 | 0.751 | 7 |
| xgboost_default | val | 0.995 | 0.778 | 0.761 | 7 |
| xgboost_tuned | test | 0.897 | 0.637 | 0.807 | 7 |
| xgboost_tuned | val | 0.864 | 0.689 | 0.820 | 7 |

## Winner: `xgboost_tuned`

- Val RMSE: 0.864 (best: 0.864, within 0.02 tiebreak margin considered)
- Test RMSE: 0.897, R2: 0.807
- Features used: 7
- Selection rule: best val RMSE; among near-ties (within 0.02), simplest/fewest-feature model wins for faster inference and easier interpretability.
