# TODO — Feature Engineering (Molecular Property Prediction)

## Дескриптори
- [ ] Відбір релевантних RDKit-дескрипторів для задачі (кореляція з таргетом) — **P0** | ~2h
- [ ] Аналіз мультиколінеарності дескрипторів (кореляційна матриця, VIF) — **P1** | ~2h
- [ ] Видалення дескрипторів з нульовою/малою дисперсією — **P1** | ~1h

## Fingerprints
- [ ] Порівняння типів fingerprints (Morgan/ECFP різного радіуса, MACCS keys) — **P1** | ~3h
- [ ] Оцінка розмірності fingerprint vs якість моделі (bit size trade-off) — **P2** | ~2h
- [ ] Комбінування дескрипторів і fingerprints в єдиний feature vector — **P1** | ~2h

## Масштабування
- [ ] Масштабування/нормалізація числових дескрипторів (StandardScaler/MinMaxScaler) — **P0** | ~1h
- [ ] Перевірка, що scaler навчається лише на train і застосовується до val/test без leakage — **P0** | ~1h
- [ ] Збереження fitted scaler разом з моделлю для інференсу — **P0** | ~1h

### Примітки
- Fingerprints добре працюють з деревоподібними моделями "як є", а лінійні моделі та GNN чутливіші до масштабування — враховувати при виборі пайплайна на модель.

### Залежності
- Виходи цього файлу (фічі, scaler) використовуються у `ml/TODO_experiments_xgboost.md` та `ml/TODO_experiments_fingerprint_models.md`.
- Збережений scaler потрібен `ml/TODO_model_registry.md` для пакування inference-пайплайна.
