# TODO — Експерименти: моделі на fingerprints (Molecular Property Prediction)

## Підготовка даних
- [ ] Підготувати Morgan fingerprints (ECFP) як вхідний feature-вектор для моделей — **P1** | ~1h
- [ ] Визначити розмір бітового вектора (наприклад 1024/2048) і радіус fingerprint — **P1** | ~1h

## Random Forest
- [ ] Навчити Random Forest на дескрипторах (baseline-порівняння з деревоподібною моделлю) — **P1** | ~2h
- [ ] Навчити Random Forest на Morgan fingerprints — **P1** | ~2h
- [ ] Порівняти Random Forest на дескрипторах vs на fingerprints (RMSE/MAE/R²) — **P1** | ~1h

## Підбір гіперпараметрів
- [ ] Підбір гіперпараметрів Random Forest (n_estimators, max_depth, min_samples_leaf) через GridSearch/Optuna — **P2** | ~2h

## Додаткові варіанти
- [ ] (Опційно) Спробувати інший fingerprint-based алгоритм (наприклад XGBoost на fingerprints) для порівняння з табличним XGBoost — **P2** | ~2h
- [ ] Зафіксувати, чи fingerprints дають приріст якості порівняно з чистими дескрипторами для цього датасету — **P1** | ~1h

## Результати
- [ ] Залогувати гіперпараметри, метрики та артефакти моделей у трекінг експериментів — **P0** | ~1h

### Примітки
- Fingerprint-моделі корисні як альтернативне представлення молекули, особливо коли ручних дескрипторів замало для складних структурних закономірностей.

### Залежності
- Потребує Morgan fingerprints, згенерованих у `data/TODO_preprocessing_pipeline.md` / `ml/TODO_feature_engineering.md`.
- Результати логуються через `ml/TODO_experiments_tracking.md` і порівнюються з `ml/TODO_experiments_xgboost.md`.
