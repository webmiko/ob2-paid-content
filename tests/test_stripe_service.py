"""Unit-тесты Stripe-сервиса."""

from unittest.mock import MagicMock, patch

import pytest

from config.constants import STRIPE_CURRENCY_MULTIPLIER
from users.models import Payment, PaymentStatus
from users.services.stripe import create_checkout_session


@pytest.mark.django_db
@patch("users.services.stripe.stripe.checkout.Session.create")
def test_create_checkout_session_uses_currency_multiplier(
    mock_create: MagicMock,
    author,
) -> None:
    """unit_amount = amount * STRIPE_CURRENCY_MULTIPLIER."""
    mock_create.return_value = MagicMock(id="cs_x", url="https://pay.example", payment_status="unpaid")
    payment = Payment.objects.create(
        user=author,
        status=PaymentStatus.PENDING,
        amount=990,
        currency="rub",
    )
    create_checkout_session(payment)
    line_item = mock_create.call_args.kwargs["line_items"][0]
    assert line_item["price_data"]["unit_amount"] == 990 * STRIPE_CURRENCY_MULTIPLIER
