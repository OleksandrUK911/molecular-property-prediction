# Evaluation report (winner: xgboost_tuned)

## Overfitting check (train vs val/test)

- train: RMSE=0.403, R2=0.962
- val: RMSE=0.864, R2=0.820
- test: RMSE=0.897, R2=0.807

Train-val RMSE gap: 0.462. Mild overfitting, expected for a tuned tree model on ~843 rows - not severe.

## Residuals on the 17 IQR-flagged outlier compounds

(PCBs, polyaromatic hydrocarbons, long-chain alkanes - kept in the dataset per data/README.md's decision; checking here whether the model systematically fails on them specifically.)

| Compound | Split | Actual | Predicted | Residual |
|---|---|---|---|---|
| Deltamethrin | test | -8.40 | -6.16 | -2.24 |
| Hexadecane | train | -8.40 | -8.21 | -0.19 |
| 1-Octadecanol | train | -8.40 | -7.74 | -0.66 |
| Etofenprox | val | -8.60 | -6.27 | -2.33 |
| 2,2',3,3',4,4',5,5',6,6'-PCB | train | -11.60 | -10.80 | -0.80 |
| 2,2',3,3',4,4',5,5'-PCB | train | -9.16 | -9.33 | +0.17 |
| 2,2',4,4',6,6'-PCB | train | -8.71 | -7.95 | -0.76 |
| 2,2',4,4',5,5'-PCB | train | -8.56 | -7.95 | -0.61 |
| 2,2',3,3',5,5',6,6'-PCB | train | -9.15 | -9.33 | +0.18 |
| 2,2',3,4,5,5',6-PCB | train | -8.94 | -8.33 | -0.61 |
| 2,2',3,3',5,6-PCB | train | -8.60 | -7.95 | -0.65 |
| Coronene | test | -9.33 | -7.21 | -2.12 |
| Benzo[ghi]perylene | val | -9.02 | -7.94 | -1.08 |
| Perylene | train | -8.80 | -8.25 | -0.55 |
| Benzo(a)pyrene | train | -8.70 | -8.25 | -0.45 |
| Benzo(k)fluoranthene | test | -8.49 | -8.13 | -0.36 |
| Napthacene | val | -8.60 | -7.08 | -1.52 |

Outlier-subset MAE: 0.898 vs whole-dataset MAE: 0.400
Model does noticeably worse on these compounds than average - document as an applicability-domain limitation in the model card.
