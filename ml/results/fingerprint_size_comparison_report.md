# Fingerprint radius/bit-size sensitivity report

Extends `ml/experiments_fingerprint_models.py` (which only tested radius=2, 1024 bits) to check whether a different Morgan fingerprint radius or bit size changes the conclusion that fingerprints don't beat the 7 RDKit descriptors for this dataset. Same Random Forest config (`n_estimators=300, max_depth=None, random_state=42`) as `ml/experiments_fingerprint_models.py`.

## Results

| Model | Radius | n_bits | Split | RMSE | MAE | R2 | n_features |
|---|---|---|---|---|---|---|---|
| random_forest_descriptors_only | None | None | test | 0.922 | 0.648 | 0.796 | 7 |
| random_forest_descriptors_only | None | None | val | 0.907 | 0.724 | 0.802 | 7 |
| random_forest_fingerprints_r2_b1024 (existing) | 2 | 1024 | test | 1.858 | 1.388 | 0.169 | 1024 |
| random_forest_fingerprints_r2_b1024 (existing) | 2 | 1024 | val | 1.515 | 1.147 | 0.447 | 1024 |
| random_forest_fingerprints_r2_b2048 | 2 | 2048 | test | 1.834 | 1.382 | 0.191 | 2048 |
| random_forest_fingerprints_r2_b2048 | 2 | 2048 | val | 1.550 | 1.143 | 0.421 | 2048 |
| random_forest_fingerprints_r2_b512 | 2 | 512 | test | 2.031 | 1.520 | 0.008 | 512 |
| random_forest_fingerprints_r2_b512 | 2 | 512 | val | 1.564 | 1.166 | 0.410 | 512 |
| random_forest_fingerprints_r3_b1024 | 3 | 1024 | test | 1.907 | 1.455 | 0.125 | 1024 |
| random_forest_fingerprints_r3_b1024 | 3 | 1024 | val | 1.552 | 1.169 | 0.420 | 1024 |
| random_forest_fingerprints_r3_b2048 | 3 | 2048 | test | 1.868 | 1.420 | 0.160 | 2048 |
| random_forest_fingerprints_r3_b2048 | 3 | 2048 | val | 1.582 | 1.170 | 0.397 | 2048 |

## Conclusion

Descriptors-only (7 features): val R2=0.802, test R2=0.796.

Best fingerprint-only variant on val R2: `random_forest_fingerprints_r2_b1024 (existing)` (radius=2, n_bits=1024) with val R2=0.447.

**No fingerprint variant, at any tested radius or bit size, beats the 7-descriptor baseline.** Changing radius (2 vs 3) or bit size (512/1024/2048) does not change the conclusion from `ml/experiments_fingerprint_models.py`: for a dataset this small (~1100 molecules), a handful of well-chosen physicochemical descriptors capture the relevant chemistry better than high-dimensional sparse Morgan fingerprints, which need more training data to fit a Random Forest well. This is an honest negative result, not a modeling error.
