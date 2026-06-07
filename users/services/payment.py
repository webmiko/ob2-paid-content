"""Подтверждение оплаты и синхронизация со Stripe."""

from __future__ import annotations

from django.db import transaction

from config.constants import STRIPE_CURRENCY_MULTIPLIER
from users.models import Payment, PaymentStatus, Subscription
from users.services.stripe import StripeCheckoutSession
from users.services.subscription import activate_subscription

STRIPE_PAID_STATUS = "paid"


class PaymentValidationError(Exception):
    """Stripe session не соответствует записи Payment."""


def validate_stripe_session_for_payment(
    session: StripeCheckoutSession,
    payment: Payment,
) -> None:
    """Сверяет metadata и сумму Checkout Session с локальным платежом.

    Raises:
        PaymentValidationError: Несовпадение payment_id или amount_total.
    """
    if session.payment_id is not None and session.payment_id != str(payment.pk):
        raise PaymentValidationError("Stripe session metadata mismatch")
    expected_amount = payment.amount * STRIPE_CURRENCY_MULTIPLIER
    if session.amount_total is not None and session.amount_total != expected_amount:
        raise PaymentValidationError("Stripe session amount mismatch")


@transaction.atomic
def complete_paid_payment(payment_id: int) -> tuple[Payment, Subscription]:
    """Помечает платёж оплаченным и активирует подписку в одной транзакции."""
    payment = Payment.objects.select_for_update().get(pk=payment_id)
    if payment.status != PaymentStatus.PAID:
        payment.status = PaymentStatus.PAID
        payment.save(update_fields=["status", "updated_at"])
    subscription = activate_subscription(payment.pk)
    return payment, subscription
