# TODO — Безпека та compliance (Molecular Property Prediction)

## Залежності
- [ ] Сканування вразливостей у залежностях (pip-audit / Dependabot / npm audit) — **P1** | ~1h
- [ ] Автоматичне оновлення залежностей через Dependabot — **P2** | ~1h

## Секрети
- [ ] Перевірити, що секрети (DB credentials, API keys) не закомічені в репозиторій — **P0** | ~30хв
- [ ] Додати `.env` до `.gitignore`, задокументувати `.env.example` — **P0** | ~30хв

## Мережева безпека
- [ ] Примусовий HTTPS (redirect з HTTP) на продакшн-домені — **P1** | ~1h
- [ ] Базовий OWASP-чекліст для API (rate limiting, input validation, security headers) — **P1** | ~2h

### Примітки
- Секрет, закомічений в git-історію, не видаляється простим наступним комітом — перевіряти `.gitignore` до першого коміту з реальними credentials, а не після.

### Залежності
- OWASP-чекліст перевіряє заходи, вже реалізовані в `backend/TODO_auth_security.md` (rate limiting, санітизація вводу).
