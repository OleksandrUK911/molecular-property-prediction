# Interpretability report (SHAP, winner: xgboost_optuna)

## Global feature importance (mean |SHAP value| on test set)

- LogP: 1.304
- RingCount: 0.377
- TPSA: 0.325
- MolWt: 0.228
- NumHAcceptors: 0.092
- NumRotatableBonds: 0.087
- NumHDonors: 0.036

![SHAP summary](shap_summary.png)

## SHAP vs native XGBoost feature importance

Native importance is XGBoost's built-in `.feature_importances_` (gain-based: average improvement in the loss function attributable to each feature across all splits that use it), computed on the same fitted model, no test data needed. Ranks are 1 = most important for each method.

| Feature | SHAP mean\|value\| | SHAP rank | XGBoost gain importance | Native rank |
|---|---|---|---|---|
| MolWt | 0.228 | 4 | 0.125 | 2 |
| LogP | 1.304 | 1 | 0.606 | 1 |
| TPSA | 0.325 | 3 | 0.064 | 4 |
| NumHDonors | 0.036 | 7 | 0.027 | 7 |
| NumHAcceptors | 0.092 | 5 | 0.090 | 3 |
| NumRotatableBonds | 0.087 | 6 | 0.030 | 6 |
| RingCount | 0.377 | 2 | 0.059 | 5 |

**Agreement:** both methods rank `LogP` as the single most important feature.

## Partial dependence plots (top 2 features: LogP, RingCount)

Partial dependence shows the marginal effect of each feature on the predicted log solubility, averaging out the other features, using the same fitted `xgboost_optuna` model evaluated on the test set.

![Partial dependence plots](pdp_plots.png)

## Per-molecule explanations

### Aspirin (`CC(=O)Oc1ccccc1C(=O)O`)
Predicted: -1.62 log(mol/L)

- LogP (1.31): +1.092 (pushes higher)
- TPSA (63.60): +0.245 (pushes higher)
- RingCount (1.00): -0.091 (pushes lower)
- NumRotatableBonds (2.00): -0.056 (pushes lower)
- NumHAcceptors (3.00): +0.048 (pushes higher)
- MolWt (180.16): -0.022 (pushes lower)
- NumHDonors (1.00): -0.013 (pushes lower)

### Caffeine (`Cn1cnc2c1c(=O)n(C)c(=O)n2C`)
Predicted: -1.75 log(mol/L)

- LogP (-1.03): +1.785 (pushes higher)
- RingCount (2.00): -0.512 (pushes lower)
- MolWt (194.19): -0.210 (pushes lower)
- NumRotatableBonds (0.00): +0.042 (pushes higher)
- TPSA (61.82): -0.032 (pushes lower)
- NumHAcceptors (3.00): +0.029 (pushes higher)
- NumHDonors (0.00): -0.026 (pushes lower)

