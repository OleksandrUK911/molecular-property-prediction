# Frontend Spec — Molecular Property Prediction

Детальна специфікація вигляду й поведінки фронтенду: layout сторінок,
композиція компонентів, стани UI (loading/empty/error/success), конкретні
дані для графіків. Це доповнення до `TODO/frontend/*.md` (які лишаються
чеклістом задач з пріоритетами) — тут описано **як саме** кожен екран
виглядає і поводиться, щоб верстати без додаткових дизайн-рішень на льоту.

## Файли
- [app-shell.md](app-shell.md) — header/навігація/загальний каркас застосунку
- [predict-page.md](predict-page.md) — головна сторінка передбачення
- [history-page.md](history-page.md) — сторінка історії запитів
- [about-page.md](about-page.md) — сторінка About / Model Card
- [components.md](components.md) — переліки і специфікації окремих UI-компонентів
- [data-visualization.md](data-visualization.md) — специфікація графіків (осі, дані, нормалізація)

## Статус
🟡 Чернетка — описано на основі поточного бекенд-контракту `/predict` (ще не
зафіксованого остаточно в `backend/TODO_api_design.md`); можливі уточнення
після Sprint 4.
