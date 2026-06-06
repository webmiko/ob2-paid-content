"""Активация подписки после успешной оплаты."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from users.models import Payment, PaymentStatus, Subscription


def _setup_logger() -> logging.Logger:
    """Настраивает логгер модуля subscription в logs/subscription.log."""
    log = logging.getLogger(__name__)
    if log.handlers:
        return log
    log.setLevel(logging.INFO)
    logs_dir = Path(settings.BASE_DIR) / "logs"
    logs_dir.mkdir(exist_ok=True)
    handler = RotatingFileHandler(
        logs_dir / "subscription.log",
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    log.addHandler(handler)
    return log


logger = _setup_logger()


@transaction.atomic
def activate_subscription(payment_id: int) -> Subscription:
    """Активирует подписку пользователя после оплаты (idempotent).

    Единственная точка активации подписки в v1.

    Args:
        payment_id: ID записи Payment.

    Returns:
        Активная подписка пользователя.

    Raises:
        Payment.DoesNotExist: Если платёж не найден.
        ValueError: Если платёж не в статусе PAID.
    """
    payment = Payment.objects.select_for_update().get(pk=payment_id)
    subscription, _ = Subscription.objects.select_for_update().get_or_create(
        user=payment.user,
        defaults={"is_active": False},
    )

    if payment.status == PaymentStatus.PAID and subscription.is_active:
        logger.info("Subscription already active for payment %s", payment_id)
        return subscription

    if payment.status != PaymentStatus.PAID:
        raise ValueError("Payment must be PAID before subscription activation")

    subscription.is_active = True
    subscription.activated_at = timezone.now()
    subscription.payment = payment
    subscription.save(update_fields=["is_active", "activated_at", "payment"])
    logger.info("Subscription activated for user %s via payment %s", payment.user_id, payment_id)
    return subscription
