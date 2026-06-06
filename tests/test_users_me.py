"""Тесты профиля текущего пользователя."""

import pytest
from rest_framework import status

ME_URL = "/api/users/me/"


@pytest.mark.django_db
def test_me_requires_auth(api_client) -> None:
    """GET профиля без авторизации → 401."""
    response = api_client.get(ME_URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_me_returns_profile(auth_client, author) -> None:
    """GET профиля возвращает phone и subscription_active."""
    response = auth_client.get(ME_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.data == {
        "id": author.pk,
        "phone": author.phone,
        "subscription_active": False,
    }


@pytest.mark.django_db
def test_me_shows_active_subscription(auth_client, author) -> None:
    """Подписчик видит subscription_active=True."""
    from users.models import Subscription

    Subscription.objects.create(user=author, is_active=True)
    response = auth_client.get(ME_URL)
    assert response.data["subscription_active"] is True
