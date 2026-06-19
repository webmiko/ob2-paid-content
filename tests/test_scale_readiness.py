"""Тесты готовности к горизонтальному масштабированию (auth, paywall, payments)."""

import pytest
from django.conf import settings

from config.cache import CACHE_TABLE_NAME, build_caches, ensure_database_cache_table
from users.models import Payment, PaymentStatus, Subscription
from users.services.payment import complete_paid_payment
from users.services.sms_verification import send_verification_code, verify_sms_code


@pytest.fixture
def shared_cache_table(db) -> None:
    """Таблица DatabaseCache для тестов с PostgreSQL (как на prod при scale web=N)."""
    ensure_database_cache_table()


@pytest.mark.django_db
def test_prod_cache_backend_is_shared_not_locmem(shared_cache_table) -> None:
    """При PostgreSQL кэш общий (DatabaseCache), не LocMem в памяти процесса."""
    backend = settings.CACHES["default"]["BACKEND"]
    assert "LocMemCache" not in backend
    assert "DatabaseCache" in backend or "RedisCache" in backend


@pytest.mark.django_db
def test_sms_verification_uses_shared_cache_roundtrip(shared_cache_table) -> None:
    """SMS: код из send_verification_code проверяется через тот же общий кэш (все реплики web)."""
    phone = "79008887766"
    code, _ = send_verification_code(phone)
    assert code is not None
    assert verify_sms_code(phone, code) is True


@pytest.mark.django_db
def test_complete_paid_payment_idempotent_on_repeat(author, shared_cache_table) -> None:
    """Повторный complete_paid_payment (два инстанса / success+webhook) — одна подписка."""
    payment = Payment.objects.create(
        user=author,
        status=PaymentStatus.PENDING,
        amount=990,
        currency="rub",
    )

    _, sub_first = complete_paid_payment(payment.pk)
    payment.refresh_from_db()
    assert payment.status == PaymentStatus.PAID
    _, sub_second = complete_paid_payment(payment.pk)

    assert sub_first.pk == sub_second.pk
    assert sub_second.is_active is True
    assert Subscription.objects.filter(user=author, is_active=True).count() == 1


def test_build_caches_prefers_redis_over_database() -> None:
    """REDIS_URL имеет приоритет над DatabaseCache."""
    caches = build_caches(db_name="ob2", redis_url="redis://localhost:6379/0")
    assert "RedisCache" in caches["default"]["BACKEND"]


def test_build_caches_uses_database_with_postgres_only() -> None:
    """Без Redis при PostgreSQL — DatabaseCache (scale-ready)."""
    caches = build_caches(db_name="ob2", redis_url="")
    assert caches["default"]["LOCATION"] == CACHE_TABLE_NAME
    assert "DatabaseCache" in caches["default"]["BACKEND"]


def test_build_caches_locmem_for_sqlite_dev() -> None:
    """Локальная SQLite-разработка без общего кэша."""
    caches = build_caches(db_name=None, redis_url="")
    assert "LocMemCache" in caches["default"]["BACKEND"]
