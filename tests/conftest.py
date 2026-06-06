"""Общие фикстуры для тестов."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from posts.models import Post

User = get_user_model()

POSTS_URL = "/api/posts/"
PASSWORD = "SecurePass123"


@pytest.fixture
def api_client() -> APIClient:
    """DRF API client без авторизации."""
    return APIClient()


@pytest.fixture
def author(db) -> User:
    """Автор публикаций."""
    return User.objects.create_user(phone="79001111111", password=PASSWORD)


@pytest.fixture
def other_user(db) -> User:
    """Другой пользователь (не автор)."""
    return User.objects.create_user(phone="79002222222", password=PASSWORD)


@pytest.fixture
def auth_client(api_client: APIClient, author: User) -> APIClient:
    """API client с JWT автора."""
    token_response = api_client.post(
        "/api/token/",
        {"phone": author.phone, "password": PASSWORD},
        format="json",
    )
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}")
    return api_client


@pytest.fixture
def other_auth_client(api_client: APIClient, other_user: User) -> APIClient:
    """API client с JWT другого пользователя."""
    token_response = api_client.post(
        "/api/token/",
        {"phone": other_user.phone, "password": PASSWORD},
        format="json",
    )
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token_response.data['access']}")
    return api_client


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
