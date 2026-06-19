"""Настройка кэша: общий для всех web-реплик при горизонтальном масштабировании."""

from __future__ import annotations

CACHE_TABLE_NAME = "ob2_django_cache"


def cache_backend_label(caches: dict[str, dict[str, str]]) -> str:
    """Короткая метка бэкенда для health/логов."""
    backend = caches["default"]["BACKEND"]
    if "redis" in backend.lower():
        return "redis"
    if "db" in backend.lower():
        return "database"
    return "locmem"


def build_caches(*, db_name: str | None, redis_url: str) -> dict[str, dict[str, str]]:
    """Собирает CACHES: Redis (если задан) → PostgreSQL → LocMem (локальная разработка).

    DatabaseCache и Redis дают один кэш на все Gunicorn-воркеры и контейнеры web:
    SMS-коды, DRF throttling и прочие cache.set/get работают при scale web=N.
    """
    if redis_url:
        return {
            "default": {
                "BACKEND": "django.core.cache.backends.redis.RedisCache",
                "LOCATION": redis_url,
            },
        }
    if db_name:
        return {
            "default": {
                "BACKEND": "django.core.cache.backends.db.DatabaseCache",
                "LOCATION": CACHE_TABLE_NAME,
            },
        }
    return {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "ob2-default-cache",
        },
    }


def ensure_database_cache_table() -> None:
    """Создаёт таблицу DatabaseCache при первом старте (без ошибки, если уже есть)."""
    from django.conf import settings
    from django.core.management import call_command
    from django.db import connection

    backend = settings.CACHES["default"]["BACKEND"]
    if "DatabaseCache" not in backend:
        return

    table = settings.CACHES["default"]["LOCATION"]
    if table in connection.introspection.table_names():
        return

    call_command("createcachetable", verbosity=0)
