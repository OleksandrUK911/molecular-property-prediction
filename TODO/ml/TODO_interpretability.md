# TODO — Інтерпретованість (Molecular Property Prediction)

## Feature importance
- [ ] Feature importance (SHAP) для найкращої моделі — **P1** | ~3h
- [ ] Порівняння вбудованого feature importance (XGBoost) із SHAP-значеннями — **P2** | ~1h
- [ ] Візуалізація глобальної важливості ознак (summary plot) — **P1** | ~1h

## Локальні пояснення
- [ ] Пояснення окремого передбачення (SHAP force/waterfall plot для конкретної молекули) — **P1** | ~2h
- [ ] Partial dependence plots для ключових дескрипторів (наприклад LogP, MolWt) — **P2** | ~2h

## Інтеграція
- [ ] Рішення, чи виводити top-фактори передбачення користувачу через API/UI — **P2** | ~1h

### Примітки
- Для fingerprint-based моделей SHAP-значення важче інтерпретувати людині (біти не мають прямого сенсу) — для пояснень користувачу краще опиратись на дескриптор-модель.

### Залежності
- Потребує фінальної переможної моделі з `ml/TODO_experiments_tracking.md`.
- Рішення про вивід факторів в UI впливає на `frontend/TODO_ui_components.md` (картка результатів) та `backend/TODO_api_design.md` (структура відповіді `/predict`).
