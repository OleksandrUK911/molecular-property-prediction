# TODO — Контейнеризація (Molecular Property Prediction)

## Dockerfiles
- [ ] Dockerfile для backend (FastAPI + RDKit + модель) — **P0** | ~3h
- [ ] Dockerfile для frontend (build + serve статики) — **P0** | ~2h
- [ ] Multi-stage build для зменшення розміру образів — **P1** | ~2h

## Оркестрація
- [ ] docker-compose.yml (backend + frontend + postgres) — **P0** | ~2h
- [ ] Налаштування volumes для персистентності БД у docker-compose — **P1** | ~1h
- [ ] Змінні середовища через `.env`-файл для docker-compose — **P0** | ~1h

## Перевірка
- [ ] Локальний запуск повного стеку через `docker-compose up` і перевірка happy path — **P0** | ~2h

### Примітки
- RDKit-залежності (conda/pip) можуть суттєво роздувати образ — варто одразу оцінити slim-базовий образ або офіційний rdkit-pypi wheel.

### Залежності
- Dockerfile для backend пакує "production"-модель, визначену в `ml/TODO_model_registry.md`.
- docker-compose потребує схеми БД з `backend/TODO_database.md`.
