# Whole-test-set error analysis

Test set: 107 compounds. This looks beyond the 17 known IQR-outlier compounds (see `ml/results/evaluation_report.md`) at error patterns across the *whole* test set.

## Top 10 worst-predicted test compounds (by |residual|)

| Compound | Actual | Predicted | Residual | MolWt | LogP | TPSA |
|---|---|---|---|---|---|---|
| Antipyrene | 0.71 | -1.99 | +2.70 | 188.2 | 1.48 | 26.9 |
| TEFLUBENZURON | -7.28 | -5.23 | -2.05 | 381.1 | 4.51 | 58.2 |
| Anthraquinone | -5.19 | -3.14 | -2.05 | 208.2 | 2.46 | 34.1 |
| aminopyrine | -0.36 | -2.37 | +2.01 | 231.3 | 1.55 | 30.2 |
| Deltamethrin | -8.40 | -6.48 | -1.92 | 505.2 | 6.49 | 59.3 |
| Coronene | -9.33 | -7.46 | -1.87 | 300.4 | 6.92 | 0.0 |
| Flumethasone | -5.61 | -3.80 | -1.81 | 410.5 | 1.84 | 94.8 |
| Cyhalothrin | -8.18 | -6.48 | -1.70 | 449.9 | 6.54 | 59.3 |
| difluron | -6.02 | -4.34 | -1.68 | 310.7 | 3.58 | 58.2 |
| Dienochlor | -7.28 | -8.75 | +1.47 | 474.6 | 7.73 | 0.0 |

Worst-10 MAE: 1.926 vs. rest-of-test MAE: 0.475 vs. whole-test MAE: 0.611

![Top 5 worst-predicted molecules, structures with actual/predicted/residual](worst_predictions.png)

## Correlation of |residual| with each descriptor (whole test set)

| Descriptor | Pearson r with |residual| |
|---|---|
| MolWt | +0.306 |
| LogP | +0.174 |
| TPSA | +0.110 |
| NumHDonors | -0.038 |
| NumHAcceptors | +0.109 |
| NumRotatableBonds | +0.247 |
| RingCount | +0.175 |

## Descriptor means: worst-10 vs. rest of test set

| Descriptor | Worst-10 mean | Rest mean | Difference |
|---|---|---|---|
| MolWt | 346.01 | 249.41 | +96.59 |
| LogP | 4.31 | 2.97 | +1.34 |
| TPSA | 42.11 | 38.87 | +3.24 |
| NumHDonors | 0.70 | 0.75 | -0.05 |
| NumHAcceptors | 2.20 | 2.34 | -0.14 |
| NumRotatableBonds | 2.20 | 1.80 | +0.40 |
| RingCount | 3.00 | 2.34 | +0.66 |

## Pattern summary

Strongest |residual| correlation: **MolWt** (r=+0.306). Largest worst-10-vs-rest mean gap: **MolWt** (+96.59).

There is a moderate-to-strong relationship between MolWt and prediction error on this test set - predictions are less reliable at the high end of this descriptor's range. This is broadly consistent with the applicability-domain limitation already documented for large/hydrophobic outlier compounds in `ml/results/evaluation_report.md` and `models/production/metadata.json`.
