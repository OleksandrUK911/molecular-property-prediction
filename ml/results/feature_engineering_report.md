# Feature engineering report

## Descriptor correlation with target (sorted by |r|)
- LogP: -0.828
- MolWt: -0.639
- RingCount: -0.513
- NumRotatableBonds: -0.245
- NumHDonors: 0.202
- TPSA: 0.118
- NumHAcceptors: 0.047

## Multicollinearity (|r| > 0.7 among descriptors)
- TPSA <-> NumHDonors: r=0.755
- TPSA <-> NumHAcceptors: r=0.899

## Near-zero variance descriptors (var < 0.01)
- None — all descriptors kept.

## Descriptor vs fingerprint vs combined (Ridge, same model for all three)
| Feature set | n_features | val RMSE | val R2 | test RMSE | test R2 |
|---|---|---|---|---|---|
| descriptors_only | 7 | 1.105 | 0.706 | 0.890 | 0.809 |
| fingerprints_only | 1024 | 4.532 | -3.950 | 6.645 | -9.628 |
| combined | 1031 | 2.754 | -0.827 | 4.002 | -2.854 |

**Caveat — do not read this as "fingerprints don't work":** all three rows use the same plain Ridge(alpha=1.0) for a controlled comparison, but that setup unfairly punishes the 1024-bit fingerprint representation — p (1024 features) >> n (~843 train rows) with weak regularization overfits badly on a linear model. `ml/TODO_experiments_fingerprint_models.md` correctly plans to evaluate fingerprints with Random Forest / tree-based models instead, which handle high-dimensional sparse binary features far better; that comparison, not this one, is the real verdict on fingerprint usefulness for this dataset. This table's purpose is only to confirm descriptors alone are a strong, well-behaved feature set for the linear baseline.
