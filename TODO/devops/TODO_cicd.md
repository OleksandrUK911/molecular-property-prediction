# TODO — CI/CD (Molecular Property Prediction)

## Continuous Integration
- [ ] GitHub Actions: lint (ruff/flake8 для backend, eslint для frontend) при push — **P1** | ~2h
- [ ] GitHub Actions: запуск тестів (pytest, frontend-тести) при push/PR — **P0** | ~2h
- [ ] Кешування залежностей у CI для прискорення прогонів — **P2** | ~1h

## Continuous Delivery
- [ ] GitHub Actions: build Docker-образів — **P1** | ~2h
- [ ] GitHub Actions: push образів у container registry (Docker Hub/GHCR) — **P1** | ~1h
- [ ] Автоматичний деплой на обраний хостинг при мерджі в main (опційно) — **P2** | ~3h

### Примітки
- Навіть без автодеплою варто мати CI, що блокує мердж при падінні тестів/лінтера — це базова гігієна, яку перевіряють на технічних співбесідах.

### Залежності
- Прогін тестів у CI спирається на набори тестів з `backend/TODO_testing.md` та `frontend/TODO_testing.md`.
- Build/push образів залежить від готових Dockerfile з `devops/TODO_containerization.md`.
