# TODO — Molecular Property Prediction Platform

## Опис проєкту

Веб-платформа, яка приймає молекулу у форматі SMILES, обчислює її фізико-хімічні
дескриптори (RDKit) і передбачає властивості (наприклад, LogP, розчинність,
молекулярну масу як baseline-задачу) за допомогою ML-моделі (XGBoost/PyTorch).
Це перший і найпростіший проєкт у серії "Molecular AI Lab" — навчальний MVP,
який має дійти до продакшн-деплою (Docker + FastAPI + React + live demo).

**Мета:** показати повний цикл AI/ML-розробки — від сирих даних (SMILES) до
задеплоєного продукту з передбаченнями в реальному часі.

Цільова аудиторія — міжнародна (англомовні рекрутери/рев'юери), тому продукт
орієнтований на англійську мову як основну.

**Статус:** 🟡 Планування / ще не розпочато

## Мовна політика

Продукт (UI, README, код, коментарі, API-документація) — англійською мовою як
основною. Українська — друга мова (i18n locale), опційна. TODO-плани
залишаються українською для зручності автора.

**[ROADMAP.md](ROADMAP.md)** — послідовність спринтів для реалізації проєкту.

## Категорії

## Data
- [Джерела та ліцензування](data/TODO_sources_licensing.md)
- [Пайплайн препроцесингу](data/TODO_preprocessing_pipeline.md)
- [Якість та валідація](data/TODO_quality_validation.md)
- [Версіонування та відтворюваність](data/TODO_versioning_reproducibility.md)

## ML
- [Baseline](ml/TODO_baseline.md)
- [Feature engineering](ml/TODO_feature_engineering.md)
- [Експерименти: XGBoost](ml/TODO_experiments_xgboost.md)
- [Експерименти: fingerprint-моделі](ml/TODO_experiments_fingerprint_models.md)
- [Експерименти: GNN](ml/TODO_experiments_gnn.md)
- [Трекінг експериментів](ml/TODO_experiments_tracking.md)
- [Оцінка та валідація](ml/TODO_evaluation_validation.md)
- [Інтерпретованість](ml/TODO_interpretability.md)
- [Model registry](ml/TODO_model_registry.md)

## Backend
- [API design](backend/TODO_api_design.md)
- [База даних](backend/TODO_database.md)
- [Автентифікація та безпека](backend/TODO_auth_security.md)
- [Тестування](backend/TODO_testing.md)
- [Логування та спостережуваність](backend/TODO_logging_observability.md)

## Frontend
- [UI-компоненти](frontend/TODO_ui_components.md)
- [Сторінки та флоу](frontend/TODO_pages_flows.md)
- [Стан та шар даних](frontend/TODO_state_data_layer.md)
- [Доступність та адаптивність](frontend/TODO_accessibility_responsive.md)
- [Тестування](frontend/TODO_testing.md)
- [Dashboard layout](frontend/TODO_dashboard_layout.md)
- [Візуалізація даних](frontend/TODO_data_visualization.md)
- [i18n / Локалізація](frontend/TODO_i18n_localization.md)

## DevOps
- [Контейнеризація](devops/TODO_containerization.md)
- [CI/CD](devops/TODO_cicd.md)
- [Інфраструктура та деплой](devops/TODO_infrastructure_deployment.md)
- [Моніторинг та спостережуваність](devops/TODO_monitoring_observability.md)
- [Безпека та compliance](devops/TODO_security_compliance.md)

## Загальний прогрес

| Категорія | Виконано | Всього |
|---|---|---|
| Data | 0 | 35 |
| ML | 0 | 73 |
| Backend | 0 | 39 |
| Frontend | 0 | 52 |
| DevOps | 0 | 31 |
| **Разом** | **0** | **230** |

### Примітки
- Кожна категорія розбита на кілька фокусованих файлів у відповідній підпапці — див. посилання вище.
- Кожна задача має позначку пріоритету (**P0**/**P1**/**P2**) та орієнтовну оцінку часу — див. окремі TODO-файли. P0 — критичний шлях, P1 — потрібно для якісного MVP, P2 — можна відкласти.
- Детальний план по спринтах — у [ROADMAP.md](ROADMAP.md).
- Пріоритет: спершу data + ml (baseline-модель), потім backend, потім frontend, потім devops/деплой.
- Не переходити до проєкту №2 (ADMET), поки цей не задеплоєний як live demo.
