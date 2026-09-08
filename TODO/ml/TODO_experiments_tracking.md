# TODO — Трекінг експериментів та вибір переможця (Molecular Property Prediction)

## Налаштування трекінгу
- [ ] Налаштувати трекінг експериментів (MLflow локально з SQLite backend, або Weights & Biases) — **P0** | ~2h
- [ ] Визначити конвенцію іменування runs/experiments (модель, дата, версія фіч) — **P1** | ~1h

## Логування
- [ ] Логувати гіперпараметри, метрики (RMSE/MAE/R²) та артефакти моделі для кожного запуску — **P0** | ~2h
- [ ] Логувати версію feature-набору та посилання на дані, використані в запуску — **P1** | ~1h

## Порівняння
- [ ] Порівняльна таблиця/дашборд моделей (baseline vs XGBoost vs RF/fingerprints vs GNN) — **P0** | ~2h
- [ ] Візуалізація порівняння метрик між кандидатами (bar chart RMSE/MAE по моделях) — **P2** | ~1h

## Вибір переможця
- [ ] Визначити критерії вибору фінальної моделі (метрика + складність + час інференсу) — **P0** | ~1h
- [ ] Промоутнути переможну модель для подальшого пакування у `ml/TODO_model_registry.md` — **P0** | ~1h

### Примітки
- Навіть простий MLflow локально (SQLite backend) виглядає значно професійніше на співбесіді, ніж ручні CSV з результатами.

### Залежності
- Агрегує результати з `ml/TODO_baseline.md`, `ml/TODO_experiments_xgboost.md`, `ml/TODO_experiments_fingerprint_models.md` та `ml/TODO_experiments_gnn.md`.
- Вихід (переможна модель) — вхід для `ml/TODO_evaluation_validation.md`, `ml/TODO_interpretability.md` та `ml/TODO_model_registry.md`.
