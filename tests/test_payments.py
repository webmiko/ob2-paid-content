"""Тесты Stripe-платежей и активации подписки."""

from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from config.constants import STRIPE_CURRENCY_MULTIPLIER
from tests.conftest import PASSWORD
from users.models import Payment, PaymentStatus, Subscription
from users.services.stripe import StripeCheckoutSession, StripeServiceError

User = get_user_model()

CREATE_URL = "/api/payments/create/"
SUCCESS_URL = "/api/payments/success/"
SYNC_URL = "/api/payments/sync/"
WEBHOOK_URL = "/api/payments/webhook/"


def payment_detail_url(payment_id: int) -> str:
    """URL детального платежа."""
    return f"/api/payments/{payment_id}/"


def paid_session_for(payment: Payment) -> StripeCheckoutSession:
    """Stripe session с корректными metadata и суммой для payment."""
    return StripeCheckoutSession(
        session_id=str(payment.stripe_session_id),
        payment_url=payment.payment_url,
        payment_status="paid",
        payment_id=str(payment.pk),
        amount_total=payment.amount * STRIPE_CURRENCY_MULTIPLIER,
    )


@pytest.fixture
def payer_client(payer: User) -> APIClient:
    """JWT-клиент плательщика."""
    client = APIClient()
    token_response = client.post(
        "/api/token/",
        {"phone": payer.phone, "password": PASSWORD},
        format="json",
    )
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}")
    return client


MOCK_SESSION = StripeCheckoutSession(
    session_id="cs_test_123",
    payment_url="https://checkout.stripe.com/pay/cs_test_123",
    payment_status="unpaid",
)


@pytest.mark.django_db
@patch("users.payment_views.create_checkout_session", return_value=MOCK_SESSION)
def test_create_payment_returns_url(_mock_create, payer_client: APIClient) -> None:
    """POST create возвращает payment_url без stripe_session_id."""
    response = payer_client.post(CREATE_URL)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["payment_url"] == MOCK_SESSION.payment_url
    assert response.data["status"] == PaymentStatus.PENDING
    assert "stripe_session_id" not in response.data
    assert Payment.objects.filter(status=PaymentStatus.PENDING).count() == 1


@pytest.mark.django_db
@patch("users.payment_views.create_checkout_session", return_value=MOCK_SESSION)
def test_create_payment_idempotency(_mock_create, payer_client: APIClient) -> None:
    """Повторный POST возвращает тот же PENDING url."""
    first = payer_client.post(CREATE_URL)
    second = payer_client.post(CREATE_URL)
    assert first.status_code == status.HTTP_201_CREATED
    assert second.status_code == status.HTTP_200_OK
    assert first.data["payment_url"] == second.data["payment_url"]
    assert Payment.objects.count() == 1


@pytest.mark.django_db
def test_create_rejects_active_subscription(payer_client: APIClient, payer: User) -> None:
    """POST create при активной подписке → 400."""
    payment = Payment.objects.create(
        user=payer,
        status=PaymentStatus.PAID,
        amount=990,
        currency="rub",
    )
    Subscription.objects.create(user=payer, is_active=True, payment=payment)
    response = payer_client.post(CREATE_URL)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
@patch("users.payment_views.retrieve_checkout_session")
def test_success_activate_subscription(
    mock_retrieve: MagicMock,
    payer_client: APIClient,
    payer: User,
) -> None:
    """POST success активирует подписку."""
    payment = Payment.objects.create(
        user=payer,
        status=PaymentStatus.PENDING,
        amount=990,
        currency="rub",
        stripe_session_id=MOCK_SESSION.session_id,
        payment_url=MOCK_SESSION.payment_url,
    )
    mock_retrieve.return_value = paid_session_for(payment)
    response = payer_client.post(
        SUCCESS_URL,
        {"session_id": MOCK_SESSION.session_id},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["status"] == PaymentStatus.PAID
    assert response.data["subscription_active"] is True
    payment.refresh_from_db()
    assert payment.status == PaymentStatus.PAID
    assert Subscription.objects.filter(user=payer, is_active=True).exists()


@pytest.mark.django_db
@patch("users.payment_views.retrieve_checkout_session")
def test_success_idempotent(mock_retrieve: MagicMock, payer_client: APIClient, payer: User) -> None:
    """Повторный success не ломает уже активную подписку."""
    payment = Payment.objects.create(
        user=payer,
        status=PaymentStatus.PAID,
        amount=990,
        currency="rub",
        stripe_session_id=MOCK_SESSION.session_id,
        payment_url=MOCK_SESSION.payment_url,
    )
    Subscription.objects.create(user=payer, is_active=True, payment=payment)
    mock_retrieve.return_value = paid_session_for(payment)
    response = payer_client.post(
        SUCCESS_URL,
        {"session_id": MOCK_SESSION.session_id},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.data["subscription_active"] is True


@pytest.mark.django_db
@patch("users.payment_views.create_checkout_session", side_effect=StripeServiceError)
def test_create_stripe_error_returns_502(_mock_create, payer_client: APIClient) -> None:
    """Ошибка Stripe при create → 502 без деталей провайдера."""
    response = payer_client.post(CREATE_URL)
    assert response.status_code == status.HTTP_502_BAD_GATEWAY
    assert response.data["detail"] == "Payment service unavailable"


@pytest.mark.django_db
@patch("users.payment_views.retrieve_checkout_session", side_effect=StripeServiceError)
def test_success_stripe_error_returns_502(_mock_retrieve, payer_client: APIClient, payer: User) -> None:
    """Ошибка Stripe при success → 502."""
    Payment.objects.create(
        user=payer,
        status=PaymentStatus.PENDING,
        amount=990,
        currency="rub",
        stripe_session_id=MOCK_SESSION.session_id,
        payment_url=MOCK_SESSION.payment_url,
    )
    response = payer_client.post(
        SUCCESS_URL,
        {"session_id": MOCK_SESSION.session_id},
        format="json",
    )
    assert response.status_code == status.HTTP_502_BAD_GATEWAY


@pytest.mark.django_db
@patch("users.payment_views.retrieve_checkout_session")
def test_sync_activate_subscription(
    mock_retrieve: MagicMock,
    payer_client: APIClient,
    payer: User,
) -> None:
    """POST sync активирует подписку по последнему PENDING."""
    payment = Payment.objects.create(
        user=payer,
        status=PaymentStatus.PENDING,
        amount=990,
        currency="rub",
        stripe_session_id=MOCK_SESSION.session_id,
        payment_url=MOCK_SESSION.payment_url,
    )
    mock_retrieve.return_value = paid_session_for(payment)
    response = payer_client.post(SYNC_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["subscription_active"] is True


@pytest.mark.django_db
def test_payment_detail_other_user_returns_404(
    payer_client: APIClient,
    other_auth_client: APIClient,
    payer: User,
) -> None:
    """Чужой payment → 404 (IDOR)."""
    payment = Payment.objects.create(
        user=payer,
        status=PaymentStatus.PENDING,
        amount=990,
        currency="rub",
        stripe_session_id="cs_other",
        payment_url="https://checkout.stripe.com/other",
    )
    response = other_auth_client.get(payment_detail_url(payment.pk))
    assert response.status_code == status.HTTP_404_NOT_FOUND
    own = payer_client.get(payment_detail_url(payment.pk))
    assert own.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_success_wrong_session_returns_404(other_auth_client: APIClient, payer: User) -> None:
    """session_id чужого платежа → 404."""
    Payment.objects.create(
        user=payer,
        status=PaymentStatus.PENDING,
        amount=990,
        currency="rub",
        stripe_session_id="cs_owner_only",
        payment_url="https://checkout.stripe.com/owner",
    )
    response = other_auth_client.post(
        SUCCESS_URL,
        {"session_id": "cs_owner_only"},
        format="json",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
@patch("users.payment_views.stripe.Webhook.construct_event")
@patch("users.payment_views.retrieve_checkout_session")
def test_webhook_activates_subscription(
    mock_retrieve: MagicMock,
    mock_construct: MagicMock,
    payer: User,
    api_client: APIClient,
) -> None:
    """Webhook checkout.session.completed активирует подписку."""
    payment = Payment.objects.create(
        user=payer,
        status=PaymentStatus.PENDING,
        amount=990,
        currency="rub",
        stripe_session_id="cs_webhook",
        payment_url="https://checkout.stripe.com/webhook",
    )
    mock_construct.return_value = {
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_webhook",
                "payment_status": "paid",
                "metadata": {"payment_id": str(payment.pk)},
            },
        },
    }
    mock_retrieve.return_value = paid_session_for(payment)

    with patch("users.payment_views.settings.STRIPE_WEBHOOK_SECRET", "whsec_test"):
        response = api_client.post(
            WEBHOOK_URL,
            data=b"{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="sig",
        )

    assert response.status_code == status.HTTP_200_OK
    payment.refresh_from_db()
    assert payment.status == PaymentStatus.PAID
    assert Subscription.objects.filter(user=payer, is_active=True).exists()
