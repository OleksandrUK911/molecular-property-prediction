# TODO — Dashboard Layout (Molecular Property Prediction)

## Структура застосунку
- [ ] App shell: header + sidebar + основна робоча область (main) — **P0** | ~2h
- [ ] Навігаційне меню між розділами (Predict / History / About) — **P1** | ~1h
- [ ] Роутинг верхнього рівня застосунку (обгортка над сторінками з `frontend/TODO_pages_flows.md`) — **P0** | ~1h

## Стан застосунку
- [ ] Глобальний стан теми (dark/light) на рівні застосунку — **P2** | ~1h
- [ ] Глобальний стан поточної мови (i18n locale) — **P1** | ~1h

## Завантаження та помилки
- [ ] Skeleton-стани завантаження для розділів дашборду (поки вантажаться дані) — **P1** | ~2h
- [ ] Error boundary на рівні застосунку (graceful fallback при неочікуваному падінні рендеру) — **P0** | ~2h

## Layout
- [ ] Адаптивний grid/flex layout для header/sidebar/main-областей — **P1** | ~2h

### Примітки
- Це "рамка" застосунку — окремий шар над сторінками з `frontend/TODO_pages_flows.md`: тут живе те, що показується на кожній сторінці однаково (header, навігація, глобальні стани, error boundary).
- Для MVP-проєкту sidebar може бути мінімальним (2-3 пункти навігації) — не варто over-engineer'ити layout заради портфоліо-демо.

### Залежності
- Роутинг верхнього рівня використовує сторінки, описані в `frontend/TODO_pages_flows.md`.
- Глобальний стан мови узгоджується з `frontend/TODO_i18n_localization.md`.
- Skeleton-стани завантаження доповнюють обробку loading-станів з `frontend/TODO_state_data_layer.md` на рівні окремих компонентів.
