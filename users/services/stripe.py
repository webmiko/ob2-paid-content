"""Интеграция со Stripe Checkout."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from logging.handlers import RotatingFileHandler
from pathlib import Path

import stripe
from django.conf import settings

from config.constants import STRIPE_CURRENCY_MULTIPLIER
from users.models import Payment

STRIPE_CHECKOUT_PRODUCT_NAME = "Подписка OB2"
STRIPE_SESSION_ID_PLACEHOLDER = "{CHECKOUT_SESSION_ID}"


class StripeServiceError(Exception):
    """Ошибка вызова Stripe API."""


@dataclass(frozen=True)
class StripeCheckoutSession:
    """Данные Checkout Session после создания или синхронизации."""

    session_id: str
    payment_url: str
    payment_status: str


def _setup_logger() -> logging.Logger:
    """Настраивает логгер модуля stripe в logs/stripe.log."""
    logger = logging.getLogger(__name__)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    logs_dir = Path(settings.BASE_DIR) / "logs"
    logs_dir.mkdir(exist_ok=True)
    handler = RotatingFileHandler(
        logs_dir / "stripe.log",
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(handler)
    return logger


logger = _setup_logger()


def _configure_stripe() -> None:
    """Устанавливает секретный ключ Stripe из settings."""
    stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(payment: Payment) -> StripeCheckoutSession:
    """Создаёт Stripe Checkout Session для платежа.

    Args:
        payment: Запись Payment в статусе PENDING.

    Returns:
        Данные session_id и payment_url для редиректа пользователя.

    Raises:
        StripeServiceError: При ошибке Stripe API.
    """
    _configure_stripe()
    unit_amount = payment.amount * STRIPE_CURRENCY_MULTIPLIER
    success_url = f"{settings.STRIPE_SUCCESS_URL}?session_id={STRIPE_SESSION_ID_PLACEHOLDER}"
    try:
        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=[
                {
                    "price_data": {
                        "currency": payment.currency,
                        "unit_amount": unit_amount,
                        "product_data": {"name": STRIPE_CHECKOUT_PRODUCT_NAME},
                    },
                    "quantity": 1,
                },
            ],
            success_url=success_url,
            cancel_url=settings.STRIPE_CANCEL_URL,
            metadata={"payment_id": str(payment.pk)},
        )
    except stripe.StripeError as exc:
        logger.exception("Stripe Checkout Session create failed for payment %s", payment.pk)
        raise StripeServiceError from exc

    if not session.url or not session.id:
        logger.error("Stripe session missing url or id for payment %s", payment.pk)
        raise StripeServiceError("Stripe session incomplete")

    return StripeCheckoutSession(
        session_id=session.id,
        payment_url=session.url,
        payment_status=str(session.payment_status or "unpaid"),
    )


def retrieve_checkout_session(session_id: str) -> StripeCheckoutSession:
    """Синхронизирует статус Checkout Session через Stripe API.

    Args:
        session_id: Идентификатор Checkout Session.

    Returns:
        Актуальные данные session, включая payment_status.

    Raises:
        StripeServiceError: При ошибке Stripe API.
    """
    _configure_stripe()
    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except stripe.StripeError as exc:
        logger.exception("Stripe Checkout Session retrieve failed: %s", session_id)
        raise StripeServiceError from exc

    return StripeCheckoutSession(
        session_id=session.id,
        payment_url=str(session.url or ""),
        payment_status=str(session.payment_status or "unpaid"),
    )
