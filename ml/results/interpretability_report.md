# Interpretability report (SHAP, winner: xgboost_tuned)

## Global feature importance (mean |SHAP value| on test set)

- LogP: 1.272
- MolWt: 0.328
- RingCount: 0.326
- TPSA: 0.274
- NumHAcceptors: 0.108
- NumRotatableBonds: 0.051
- NumHDonors: 0.049

![SHAP summary](shap_summary.png)

## Per-molecule explanations

### Aspirin (`CC(=O)Oc1ccccc1C(=O)O`)
Predicted: -1.68 log(mol/L)

- LogP (1.31): +1.140 (pushes higher)
- TPSA (63.60): +0.265 (pushes higher)
- RingCount (1.00): -0.134 (pushes lower)
- MolWt (180.16): -0.104 (pushes lower)
- NumRotatableBonds (2.00): -0.048 (pushes lower)
- NumHAcceptors (3.00): +0.043 (pushes higher)
- NumHDonors (1.00): -0.017 (pushes lower)

### Caffeine (`Cn1cnc2c1c(=O)n(C)c(=O)n2C`)
Predicted: -2.40 log(mol/L)

- LogP (-1.03): +1.416 (pushes higher)
- RingCount (2.00): -0.575 (pushes lower)
- MolWt (194.19): -0.339 (pushes lower)
- NumHDonors (0.00): -0.042 (pushes lower)
- NumRotatableBonds (0.00): -0.015 (pushes lower)
- TPSA (61.82): -0.008 (pushes lower)
- NumHAcceptors (3.00): -0.003 (pushes lower)

