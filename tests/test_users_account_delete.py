"""Тесты удаления аккаунта пользователя."""

import pytest
from rest_framework import status

from posts.models import Comment, Post
from tests.conftest import ME_URL, PASSWORD
from users.models import User


@pytest.mark.django_db
def test_delete_account_requires_auth(api_client) -> None:
    """DELETE /me/ без авторизации → 401."""
    response = api_client.delete(
        ME_URL,
        {"password": PASSWORD, "confirm": True},
        format="json",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_delete_account_wrong_password(auth_client, author) -> None:
    """DELETE /me/ с неверным паролем → 400."""
    response = auth_client.delete(
        ME_URL,
        {"password": "WrongPass99", "confirm": True},
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert User.objects.filter(pk=author.pk).exists()


@pytest.mark.django_db
def test_delete_account_without_confirm(auth_client) -> None:
    """DELETE /me/ без confirm → 400."""
    response = auth_client.delete(
        ME_URL,
        {"password": PASSWORD, "confirm": False},
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_delete_account_removes_user_and_content(auth_client, author) -> None:
    """DELETE /me/ удаляет пользователя, посты и комментарии."""
    post = Post.objects.create(title="Mine", body="Text", author=author)
    other = User.objects.create_user(phone="79008887766", password=PASSWORD)
    Comment.objects.create(post=post, author=other, text="Reply")
    author_id = author.pk

    response = auth_client.delete(
        ME_URL,
        {"password": PASSWORD, "confirm": True},
        format="json",
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not User.objects.filter(pk=author_id).exists()
    assert not Post.objects.filter(author_id=author_id).exists()
    assert Comment.objects.filter(post=post).count() == 0
