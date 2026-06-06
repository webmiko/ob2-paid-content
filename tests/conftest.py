"""Общие фикстуры для тестов."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from posts.models import Post
from users.models import Subscription

User = get_user_model()

POSTS_URL = "/api/posts/"
PASSWORD = "SecurePass123"


@pytest.fixture(autouse=True)
def disable_api_throttling(monkeypatch) -> None:
    """Отключает rate limit DRF в тестах."""
    monkeypatch.setattr(
        "rest_framework.throttling.SimpleRateThrottle.allow_request",
        lambda self, request, view: True,
    )


@pytest.fixture
def api_client() -> APIClient:
    """HTTP-клиент API без авторизации."""
    return APIClient()


@pytest.fixture
def user(author: User) -> User:
    """Алиас author — пользователь по умолчанию в тестах."""
    return author


@pytest.fixture
def jwt_client(auth_client: APIClient) -> APIClient:
    """Алиас auth_client — JWT-клиент автора."""
    return auth_client


@pytest.fixture
def post_free(free_post: Post) -> Post:
    """Алиас free_post."""
    return free_post


@pytest.fixture
def post_paid(paid_post: Post) -> Post:
    """Алиас paid_post."""
    return paid_post


@pytest.fixture
def payer(db) -> User:
    """Пользователь-плательщик без подписки."""
    return User.objects.create_user(phone="79005556677", password=PASSWORD)


@pytest.fixture
def author(db) -> User:
    """Автор публикаций."""
    return User.objects.create_user(phone="79001111111", password=PASSWORD)


@pytest.fixture
def other_user(db) -> User:
    """Другой пользователь (не автор)."""
    return User.objects.create_user(phone="79002222222", password=PASSWORD)


@pytest.fixture
def auth_client(author: User) -> APIClient:
    """API client с JWT автора."""
    client = APIClient()
    token_response = client.post(
        "/api/token/",
        {"phone": author.phone, "password": PASSWORD},
        format="json",
    )
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}")
    return client


@pytest.fixture
def other_auth_client(other_user: User) -> APIClient:
    """API client с JWT другого пользователя."""
    client = APIClient()
    token_response = client.post(
        "/api/token/",
        {"phone": other_user.phone, "password": PASSWORD},
        format="json",
    )
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}")
    return client


@pytest.fixture
def subscriber(other_user: User) -> User:
    """Пользователь с активной подпиской."""
    Subscription.objects.create(user=other_user, is_active=True)
    return other_user


@pytest.fixture
def subscriber_client(subscriber: User) -> APIClient:
    """JWT-клиент подписчика."""
    client = APIClient()
    token_response = client.post(
        "/api/token/",
        {"phone": subscriber.phone, "password": PASSWORD},
        format="json",
    )
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}")
    return client


@pytest.fixture
def free_post(author: User) -> Post:
    """Бесплатная публикация."""
    return Post.objects.create(
        title="Free post",
        body="Free body text",
        is_paid=False,
        author=author,
    )


@pytest.fixture
def paid_post(author: User) -> Post:
    """Платная публикация."""
    return Post.objects.create(
        title="Paid post",
        body="Paid secret body",
        is_paid=True,
        author=author,
    )


def post_detail_url(post_id: int) -> str:
    """URL детальной публикации."""
    return f"{POSTS_URL}{post_id}/"


RECOMMENDED_URL = f"{POSTS_URL}recommended/"


def post_comments_url(post_id: int) -> str:
    """URL комментариев к публикации."""
    return f"{POSTS_URL}{post_id}/comments/"


def post_comment_detail_url(post_id: int, comment_id: int) -> str:
    """URL удаления комментария."""
    return f"{POSTS_URL}{post_id}/comments/{comment_id}/"


def post_similar_url(post_id: int) -> str:
    """URL похожих публикаций."""
    return f"{POSTS_URL}{post_id}/similar/"
