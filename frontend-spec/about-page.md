# About / Model Card page

Шлях `/about`. Статичний контент, без API-запитів (дані model card
підвантажуються один раз або зашиті в build з `ml/TODO_model_registry.md`).

## Layout

Одна колонка, секції одна під одною (без табів/акордеонів — короткий контент,
не потребує згортання):

```
1. Model description
   — коротко: SMILES → RDKit descriptors → XGBoost → predicted solubility

2. Training data
   — Dataset: ESOL (Delaney), 1128 compounds
   — Source + license (з data/README.md)
   — Train/val/test split sizes

3. Metrics (таблиця)
   | Split | RMSE | MAE | R² |
   |-------|------|-----|-----|
   | Val   | ...  | ... | ... |
   | Test  | ...  | ... | ... |

4. Limitations & disclaimer
   — Домен застосування (applicability domain): які типи молекул модель
     "бачила" під час тренування
   — "Research/educational project. Not for clinical or production
     chemistry use."

5. Version
   — Model version, дата останнього тренування, посилання на commit/тег
```

## Стани
Немає loading/error станів у звичайному сенсі — контент статичний і йде в
білд. Якщо метрики підвантажуються з окремого JSON (а не хардкодяться) —
Loading: skeleton для таблиці метрик; Error: таблиця ховається, лишається
текстовий опис моделі.
