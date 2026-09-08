# ROADMAP — Molecular Property Prediction Platform

Послідовність спринтів для соло-розробки в режимі part-time (орієнтовно ~10-15 год/тиждень) з допомогою Claude Code. Кожен спринт спирається на P0/P1-задачі з відповідних TODO-файлів; P2-задачі можна переносити між спринтами або залишати на "Sprint 6 — Polish" за нестачі часу.

## Sprint 0 — Setup та вибір даних
**Мета:** зафіксувати датасет, ліцензію та базову структуру репозиторію, щоб було на чому будувати пайплайн.
- [Джерела та ліцензування](data/TODO_sources_licensing.md) — P0/P1
- Ініціалізація репозиторію, структура папок (`data/`, `ml/`, `backend/`, `frontend/`) — поза TODO-файлами, базова гігієна проєкту
**Тривалість:** ~3-4 дні

## Sprint 1 — Дата-пайплайн та якість даних
**Мета:** отримати чистий, відтворюваний, провалідований набір train/val/test, готовий для навчання моделей.
- [Пайплайн препроцесингу](data/TODO_preprocessing_pipeline.md) — P0/P1
- [Якість та валідація](data/TODO_quality_validation.md) — P0/P1
- [Версіонування та відтворюваність](data/TODO_versioning_reproducibility.md) — P0/P1
**Тривалість:** ~1 тиждень

## Sprint 2 — Baseline та feature engineering
**Мета:** мати чесний baseline і якісний feature-набір (дескриптори + fingerprints) як фундамент для подальших експериментів.
- [Baseline](ml/TODO_baseline.md) — P0/P1
- [Feature engineering](ml/TODO_feature_engineering.md) — P0/P1
**Тривалість:** ~4-5 днів

## Sprint 3 — ML-експерименти та вибір моделі
**Мета:** прогнати основні кандидати моделей (XGBoost, fingerprint-моделі, опційно GNN), налаштувати трекінг і обрати переможну модель.
- [Експерименти: XGBoost](ml/TODO_experiments_xgboost.md) — P0/P1
- [Експерименти: fingerprint-моделі](ml/TODO_experiments_fingerprint_models.md) — P1
- [Трекінг експериментів](ml/TODO_experiments_tracking.md) — P0/P1
- [Оцінка та валідація](ml/TODO_evaluation_validation.md) — P0/P1
- [Експерименти: GNN](ml/TODO_experiments_gnn.md) — P2, опційно, за наявності часу
**Тривалість:** ~1 тиждень

## Sprint 4 — Model registry, інтерпретованість та backend API
**Мета:** запакувати переможну модель у відтворюваному форматі та підняти FastAPI-бекенд, що її обслуговує.
- [Model registry](ml/TODO_model_registry.md) — P0/P1
- [Інтерпретованість](ml/TODO_interpretability.md) — P1 (частково)
- [API design](backend/TODO_api_design.md) — P0/P1
- [База даних](backend/TODO_database.md) — P0/P1
- [Автентифікація та безпека](backend/TODO_auth_security.md) — P0/P1
- [Логування та спостережуваність](backend/TODO_logging_observability.md) — P1
- [Тестування Backend](backend/TODO_testing.md) — P0/P1
**Тривалість:** ~1 тиждень

## Sprint 5 — Frontend
**Мета:** зібрати робочий React-інтерфейс, що звертається до API та показує передбачення, історію і опис моделі.
- [UI-компоненти](frontend/TODO_ui_components.md) — P0/P1
- [Сторінки та флоу](frontend/TODO_pages_flows.md) — P0/P1
- [Стан та шар даних](frontend/TODO_state_data_layer.md) — P0/P1
- [Тестування Frontend](frontend/TODO_testing.md) — P1
- [Доступність та адаптивність](frontend/TODO_accessibility_responsive.md) — P1 (частково)
**Тривалість:** ~1 тиждень

## Sprint 6 — DevOps, деплой та polish
**Мета:** задеплоїти повний стек як публічне live demo, закрити безпеку/моніторинг і довести документацію (model card, README) до портфоліо-якості.
- [Контейнеризація](devops/TODO_containerization.md) — P0/P1
- [CI/CD](devops/TODO_cicd.md) — P0/P1
- [Інфраструктура та деплой](devops/TODO_infrastructure_deployment.md) — P0/P1
- [Безпека та compliance](devops/TODO_security_compliance.md) — P0/P1
- [Моніторинг та спостережуваність](devops/TODO_monitoring_observability.md) — P1
- Залишкові P2-задачі з усіх категорій (dark theme, GNN-порівняння, розширені e2e-тести тощо)
**Тривалість:** ~1 тиждень

---

### Примітки
- Спринти орієнтовані на послідовність залежностей: дані → ML → backend → frontend → devops, як і зафіксовано в `TODO_MAIN.md`.
- P2-задачі свідомо не прив'язані жорстко до спринтів — переносити їх туди, де залишається час, або в Sprint 6.
- Проєкт вважається завершеним, коли live demo задеплоєно і доступне публічно — до цього моменту не варто починати проєкт №2 серії ("Molecular AI Lab").
