# Покрытие тестами

**Порог:** ≥ **85 %** (branch coverage включён).

## Запуск

```bash
poetry run pytest
# или явно:
poetry run pytest --cov=config --cov=users --cov=posts --cov-fail-under=85
```

Настройки: `pyproject.toml` → `[tool.pytest.ini_options]`, `[tool.coverage.*]`.

## Что входит в coverage

| Пакет | Содержимое |
|-------|------------|
| `config/` | settings, urls, constants, form_mixins |
| `users/` | models, views, serializers, services, forms |
| `posts/` | models, views, serializers, permissions, services |

## Исключено из отчёта (omit)

- `*/migrations/*`
- `manage.py`
- `**/asgi.py`, `**/wsgi.py`

## Не входит в backend coverage

- `frontend/` — отдельный стек (TypeScript, `npm run build`)
- `scripts/`, `deploy/` — инфраструктура
- `tests/` — сами тесты

## Типичные пропуски (допустимо)

- `config/settings.py` — ветки SQLite / `USE_HTTPS` (prod-only)
- `config/urls.py` — drf-yasg только при `DEBUG=True`
- `users/managers.py` — редкие ветки `create_superuser` validation

## Security-тесты

См. `tests/test_security.py`: IDOR, утечка paid body, SQLi-smoke, serializer fields.
