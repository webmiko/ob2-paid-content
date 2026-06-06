"""Тесты CRUD публикаций и IDOR."""

import pytest
from rest_framework import status

from posts.models import Post
from tests.conftest import POSTS_URL, post_detail_url


@pytest.mark.django_db
def test_guest_cannot_create_post(api_client) -> None:
    """Guest не может создать публикацию."""
    response = api_client.post(
        POSTS_URL,
        {"title": "New", "body": "Text", "is_paid": False},
        format="json",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_auth_user_creates_post(auth_client, author) -> None:
    """Авторизованный пользователь создаёт публикацию."""
    response = auth_client.post(
        POSTS_URL,
        {"title": "My post", "body": "Content", "is_paid": True},
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    post = Post.objects.get(title="My post")
    assert post.author_id == author.pk
    assert post.is_paid is True


@pytest.mark.django_db
def test_author_updates_own_post(auth_client, free_post) -> None:
    """Автор может обновить свою публикацию."""
    response = auth_client.patch(
        post_detail_url(free_post.pk),
        {"title": "Updated title"},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    free_post.refresh_from_db()
    assert free_post.title == "Updated title"


@pytest.mark.django_db
def test_author_deletes_own_post(auth_client, free_post) -> None:
    """Автор может удалить свою публикацию."""
    post_id = free_post.pk
    response = auth_client.delete(post_detail_url(post_id))
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Post.objects.filter(pk=post_id).exists()


@pytest.mark.django_db
def test_other_user_update_returns_404(other_auth_client, free_post) -> None:
    """Чужая публикация: update → 404 (IDOR)."""
    response = other_auth_client.patch(
        post_detail_url(free_post.pk),
        {"title": "Hacked"},
        format="json",
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    free_post.refresh_from_db()
    assert free_post.title == "Free post"


@pytest.mark.django_db
def test_other_user_delete_returns_404(other_auth_client, paid_post) -> None:
    """Чужая публикация: delete → 404 (IDOR)."""
    response = other_auth_client.delete(post_detail_url(paid_post.pk))
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert Post.objects.filter(pk=paid_post.pk).exists()
