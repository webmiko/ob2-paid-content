"""Сквозные тесты безопасности: IDOR, утечки, SQLi-smoke."""

import pytest
from django.test import Client
from rest_framework import status

from posts.models import Post
from tests.conftest import PASSWORD, POSTS_URL, post_detail_url
from users.models import Payment, PaymentStatus
from users.payment_serializers import PaymentSerializer


@pytest.mark.django_db
def test_register_response_excludes_password(api_client) -> None:
    """Register не возвращает password в JSON."""
    response = api_client.post(
        "/api/users/register/",
        {"phone": "+7 900 777-88-99", "password": PASSWORD},
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert "password" not in response.data


@pytest.mark.django_db
def test_payment_serializer_excludes_stripe_fields(payer) -> None:
    """PaymentSerializer не отдаёт stripe_session_id."""
    payment = Payment.objects.create(
        user=payer,
        status=PaymentStatus.PENDING,
        amount=990,
        currency="rub",
        stripe_session_id="cs_secret_id",
        payment_url="https://checkout.stripe.com/test",
    )
    data = PaymentSerializer(payment).data
    assert "stripe_session_id" not in data
    assert set(data.keys()) == {"id", "status", "payment_url", "amount", "currency", "created_at"}


@pytest.mark.django_db
def test_paid_body_not_in_list_for_guest(api_client, paid_post) -> None:
    """Guest: paid body отсутствует в list API (нет утечки в JSON)."""
    response = api_client.get(POSTS_URL)
    item = response.data["results"][0]
    assert item["can_view_body"] is False
    assert item["body"] is None
    assert paid_post.body not in str(response.content)


@pytest.mark.django_db
def test_idor_post_update_returns_404(other_auth_client, free_post) -> None:
    """IDOR: update чужого поста → 404."""
    response = other_auth_client.patch(
        post_detail_url(free_post.pk),
        {"title": "stolen"},
        format="json",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_idor_payment_detail_returns_404(payer, other_auth_client) -> None:
    """IDOR: чужой Payment → 404."""
    payment = Payment.objects.create(
        user=payer,
        status=PaymentStatus.PAID,
        amount=990,
        currency="rub",
        stripe_session_id="cs_idor",
        payment_url="https://checkout.stripe.com/idor",
    )
    response = other_auth_client.get(f"/api/payments/{payment.pk}/")
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_sqli_phone_register_returns_400_not_500(api_client) -> None:
    """SQLi-подобная строка в phone → 400, не 500."""
    response = api_client.post(
        "/api/users/register/",
        {"phone": "1' OR '1'='1", "password": PASSWORD},
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_no_raw_sql_in_post_list(api_client, free_post) -> None:
    """Список постов работает через ORM (smoke: нет падения на типичном запросе)."""
    assert Post.objects.filter(pk=free_post.pk).exists()
    response = api_client.get(POSTS_URL)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_payment_success_page_renders(client: Client) -> None:
    """Страница успешной оплаты доступна без авторизации."""
    response = client.get("/payments/success/")
    assert response.status_code == status.HTTP_200_OK
    assert "Оплата прошла успешно".encode() in response.content
