# Evaluation report (winner: xgboost_optuna)

## Overfitting check (train vs val/test)

- train: RMSE=0.501, R2=0.941
- val: RMSE=0.825, R2=0.836
- test: RMSE=0.820, R2=0.838

Train-val RMSE gap: 0.324. Mild overfitting, expected for a tuned tree model on ~843 rows - not severe.

## Residuals on the 17 IQR-flagged outlier compounds

(PCBs, polyaromatic hydrocarbons, long-chain alkanes - kept in the dataset per data/README.md's decision; checking here whether the model systematically fails on them specifically.)

| Compound | Split | Actual | Predicted | Residual |
|---|---|---|---|---|
| Deltamethrin | test | -8.40 | -6.48 | -1.92 |
| Hexadecane | train | -8.40 | -8.20 | -0.20 |
| 1-Octadecanol | train | -8.40 | -7.34 | -1.06 |
| Etofenprox | val | -8.60 | -6.86 | -1.74 |
| 2,2',3,3',4,4',5,5',6,6'-PCB | train | -11.60 | -10.20 | -1.40 |
| 2,2',3,3',4,4',5,5'-PCB | train | -9.16 | -9.57 | +0.41 |
| 2,2',4,4',6,6'-PCB | train | -8.71 | -7.92 | -0.79 |
| 2,2',4,4',5,5'-PCB | train | -8.56 | -7.92 | -0.64 |
| 2,2',3,3',5,5',6,6'-PCB | train | -9.15 | -9.57 | +0.42 |
| 2,2',3,4,5,5',6-PCB | train | -8.94 | -8.37 | -0.57 |
| 2,2',3,3',5,6-PCB | train | -8.60 | -7.92 | -0.68 |
| Coronene | test | -9.33 | -7.46 | -1.87 |
| Benzo[ghi]perylene | val | -9.02 | -7.88 | -1.14 |
| Perylene | train | -8.80 | -8.12 | -0.68 |
| Benzo(a)pyrene | train | -8.70 | -8.12 | -0.58 |
| Benzo(k)fluoranthene | test | -8.49 | -7.87 | -0.62 |
| Napthacene | val | -8.60 | -6.81 | -1.79 |

Outlier-subset MAE: 0.971 vs whole-dataset MAE: 0.449
Model does noticeably worse on these compounds than average - document as an applicability-domain limitation in the model card.
