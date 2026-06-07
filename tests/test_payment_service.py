"""Unit-тесты payment service."""

import pytest

from config.constants import STRIPE_CURRENCY_MULTIPLIER
from users.models import Payment, PaymentStatus
from users.services.payment import PaymentValidationError, validate_stripe_session_for_payment
from users.services.stripe import StripeCheckoutSession


@pytest.mark.django_db
def test_validate_session_rejects_metadata_mismatch(author) -> None:
    """validate_stripe_session_for_payment отклоняет чужой payment_id."""
    payment = Payment.objects.create(
        user=author,
        status=PaymentStatus.PENDING,
        amount=990,
        currency="rub",
    )
    session = StripeCheckoutSession(
        session_id="cs_x",
        payment_url="https://pay.example",
        payment_status="paid",
        payment_id="999",
        amount_total=990 * STRIPE_CURRENCY_MULTIPLIER,
    )
    with pytest.raises(PaymentValidationError):
        validate_stripe_session_for_payment(session, payment)


@pytest.mark.django_db
def test_validate_session_rejects_amount_mismatch(author) -> None:
    """validate_stripe_session_for_payment отклоняет неверную сумму."""
    payment = Payment.objects.create(
        user=author,
        status=PaymentStatus.PENDING,
        amount=990,
        currency="rub",
    )
    session = StripeCheckoutSession(
        session_id="cs_x",
        payment_url="https://pay.example",
        payment_status="paid",
        payment_id=str(payment.pk),
        amount_total=1,
    )
    with pytest.raises(PaymentValidationError):
        validate_stripe_session_for_payment(session, payment)
