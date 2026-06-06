"""Тесты Stripe-платежей и активации подписки."""

from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from tests.conftest import PASSWORD
from users.models import Payment, PaymentStatus, Subscription
from users.services.stripe import StripeCheckoutSession, StripeServiceError

User = get_user_model()

CREATE_URL = "/api/payments/create/"
SUCCESS_URL = "/api/payments/success/"


def payment_detail_url(payment_id: int) -> str:
    """URL детального платежа."""
    return f"/api/payments/{payment_id}/"


@pytest.fixture
def payer(db) -> User:
    """Пользователь без подписки."""
    return User.objects.create_user(phone="79005556677", password=PASSWORD)


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

MOCK_PAID_SESSION = StripeCheckoutSession(
    session_id="cs_test_123",
    payment_url="https://checkout.stripe.com/pay/cs_test_123",
    payment_status="paid",
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
@patch("users.payment_views.retrieve_checkout_session", return_value=MOCK_PAID_SESSION)
def test_success_activate_subscription(
    _mock_retrieve,
    payer_client: APIClient,
    payer: User,
) -> None:
    """Success sync активирует подписку."""
    payment = Payment.objects.create(
        user=payer,
        status=PaymentStatus.PENDING,
        amount=990,
        currency="rub",
        stripe_session_id=MOCK_SESSION.session_id,
        payment_url=MOCK_SESSION.payment_url,
    )
    response = payer_client.get(SUCCESS_URL, {"session_id": MOCK_SESSION.session_id})
    assert response.status_code == status.HTTP_200_OK
    assert response.data["status"] == PaymentStatus.PAID
    assert response.data["subscription_active"] is True
    payment.refresh_from_db()
    assert payment.status == PaymentStatus.PAID
    assert Subscription.objects.filter(user=payer, is_active=True).exists()


@pytest.mark.django_db
@patch("users.payment_views.retrieve_checkout_session", return_value=MOCK_PAID_SESSION)
def test_success_idempotent(_mock_retrieve, payer_client: APIClient, payer: User) -> None:
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
    response = payer_client.get(SUCCESS_URL, {"session_id": MOCK_SESSION.session_id})
    assert response.status_code == status.HTTP_200_OK
    assert response.data["subscription_active"] is True


@pytest.mark.django_db
@patch("users.payment_views.create_checkout_session", side_effect=StripeServiceError)
def test_create_stripe_error_returns_502(_mock_create, payer_client: APIClient) -> None:
    """Ошибка Stripe при create → 502 без деталей SDK."""
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
    response = payer_client.get(SUCCESS_URL, {"session_id": MOCK_SESSION.session_id})
    assert response.status_code == status.HTTP_502_BAD_GATEWAY


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
    response = other_auth_client.get(SUCCESS_URL, {"session_id": "cs_owner_only"})
    assert response.status_code == status.HTTP_404_NOT_FOUND
