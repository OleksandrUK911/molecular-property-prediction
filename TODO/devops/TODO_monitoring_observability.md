# TODO — Моніторинг та спостережуваність (Molecular Property Prediction)

## Uptime
- [ ] Базовий uptime-моніторинг (UptimeRobot або аналог) для live demo — **P1** | ~1h
- [ ] Сповіщення при падінні сервісу (email/Telegram) — **P1** | ~1h

## Помилки
- [ ] Алертинг на критичні помилки (наприклад через Sentry або логи хостингу) — **P2** | ~2h

## Метрики
- [ ] Базовий дашборд метрик (кількість запитів, latency, error rate) — **P2** | ~2h
- [ ] Перевірка логів після деплою на предмет прихованих помилок, які не ловляться health-check'ом — **P1** | ~1h

### Примітки
- Для MVP достатньо безкоштовного uptime-монітора та базового error-алертингу — повноцінний Grafana/Prometheus стек тут надлишковий.

### Залежності
- Спирається на structured logging та метрики застосунку з `backend/TODO_logging_observability.md`, застосовується вже після деплою з `devops/TODO_infrastructure_deployment.md`.
