"""Сквозные тесты безопасности: IDOR, утечки, SQLi-smoke."""

from unittest.mock import patch

import pytest
from django.test import Client
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from config.constants import MAX_RECOMMENDED_EXCLUDE_IDS
from posts.models import Comment, Post
from tests.conftest import ME_URL, PASSWORD, POSTS_URL, RECOMMENDED_URL, post_detail_url
from users.models import Payment, PaymentStatus, User
from users.payment_serializers import PaymentSerializer

YOUTUBE_WATCH = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"


@pytest.mark.django_db
def test_register_response_excludes_password(api_client) -> None:
    """Register не возвращает password в JSON."""
    response = api_client.post(
        "/api/users/register/",
        {
            "phone": "+7 900 777-88-99",
            "password": PASSWORD,
            "display_name": "Security Tester",
        },
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


@pytest.mark.django_db
def test_paid_post_hides_video_metadata_for_guest(api_client, author) -> None:
    """Guest не получает has_video и video_provider у paid-публикации."""
    post = Post.objects.create(
        title="Paid video",
        body="Secret",
        is_paid=True,
        author=author,
        video_url=YOUTUBE_WATCH,
    )
    response = api_client.get(post_detail_url(post.pk))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["has_video"] is False
    assert response.data["video_provider"] is None


@pytest.mark.django_db
def test_paid_post_hides_comment_count_for_guest(api_client, paid_post, other_user) -> None:
    """Guest не видит реальное число комментариев у paid-публикации."""
    Comment.objects.create(post=paid_post, author=other_user, text="Hidden count")
    response = api_client.get(post_detail_url(paid_post.pk))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["comment_count"] == 0


@pytest.mark.django_db
def test_recommended_exclude_ids_capped(api_client, author) -> None:
    """Query exclude обрезается до MAX_RECOMMENDED_EXCLUDE_IDS."""
    posts = [
        Post.objects.create(title=f"Free {index}", body="Body", author=author)
        for index in range(MAX_RECOMMENDED_EXCLUDE_IDS + 5)
    ]
    exclude = ",".join(str(post.pk) for post in posts)
    response = api_client.get(f"{RECOMMENDED_URL}?exclude={exclude}")
    assert response.status_code == status.HTTP_200_OK
    returned_ids = {item["id"] for item in response.data}
    assert posts[MAX_RECOMMENDED_EXCLUDE_IDS].pk in returned_ids


@pytest.mark.django_db
def test_delete_account_blacklists_refresh_token(author) -> None:
    """DELETE /me/ инвалидирует refresh-токен пользователя."""
    client = APIClient()
    token_response = client.post(
        "/api/token/",
        {"phone": author.phone, "password": PASSWORD},
        format="json",
    )
    refresh = token_response.data["refresh"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}")

    response = client.delete(
        ME_URL,
        {"password": PASSWORD, "confirm": True, "refresh": refresh},
        format="json",
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    refresh_response = client.post("/api/token/refresh/", {"refresh": refresh}, format="json")
    assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED
    assert BlacklistedToken.objects.filter(token__token=refresh).exists()
    assert not User.objects.filter(pk=author.pk).exists()
    assert OutstandingToken.objects.filter(user_id=author.pk).count() == 0


@pytest.mark.django_db
@patch("users.payment_views.stripe.Webhook.construct_event")
def test_webhook_rejects_invalid_signature(mock_construct, api_client) -> None:
    """Stripe webhook с неверной подписью → 400."""
    mock_construct.side_effect = ValueError("invalid signature")
    with patch("users.payment_views.settings.STRIPE_WEBHOOK_SECRET", "whsec_test"):
        response = api_client.post(
            "/api/payments/webhook/",
            data=b"{}",
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="bad",
        )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
