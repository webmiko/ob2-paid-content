"""Тесты дашборда автора и учёта просмотров."""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from posts.models import Comment, Post, PostView
from tests.conftest import PASSWORD, POSTS_URL
from users.models import Subscription

STATS_URL = "/api/users/me/stats/"


def post_view_url(post_id: int) -> str:
    """URL записи просмотра."""
    return f"{POSTS_URL}{post_id}/view/"


@pytest.mark.django_db
def test_record_view_requires_existing_post(api_client) -> None:
    """POST view для несуществующего поста → 404."""
    response = api_client.post(post_view_url(99999))
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_record_view_counts_guest(api_client, free_post) -> None:
    """Гость учитывается один раз; повтор не увеличивает счётчик."""
    first = api_client.post(post_view_url(free_post.pk))
    second = api_client.post(post_view_url(free_post.pk))
    assert first.status_code == status.HTTP_200_OK
    assert first.data["recorded"] is True
    assert second.data["recorded"] is False
    free_post.refresh_from_db()
    assert free_post.view_count == 1
    assert PostView.objects.filter(post=free_post, user__isnull=True).count() == 1


@pytest.mark.django_db
def test_author_own_view_not_counted(auth_client, author) -> None:
    """Автор не увеличивает просмотры своих публикаций."""
    post = Post.objects.create(title="Mine", body="Body", author=author)
    response = auth_client.post(post_view_url(post.pk))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["recorded"] is False
    post.refresh_from_db()
    assert post.view_count == 0


@pytest.mark.django_db
def test_subscriber_view_counted(subscriber_client, author) -> None:
    """Подписчик учитывается в просмотрах."""
    post = Post.objects.create(title="Paid", body="Secret", is_paid=True, author=author)
    response = subscriber_client.post(post_view_url(post.pk))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["recorded"] is True
    post.refresh_from_db()
    assert post.view_count == 1


@pytest.mark.django_db
def test_author_stats_requires_auth(api_client) -> None:
    """GET /me/stats/ без авторизации → 401."""
    response = api_client.get(STATS_URL)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_author_stats_returns_metrics(auth_client, author, other_user, subscriber) -> None:
    """Дашборд автора возвращает просмотры, комментарии и подписчиков."""
    Subscription.objects.filter(user=subscriber).update(is_active=True)
    post = Post.objects.create(
        title="Stats post",
        body="Body",
        is_paid=True,
        author=author,
        topic="tech",
    )
    Comment.objects.create(post=post, author=other_user, text="Nice")
    viewer = APIClient()
    token = viewer.post(
        "/api/token/",
        {"phone": subscriber.phone, "password": PASSWORD},
        format="json",
    ).data
    viewer.credentials(HTTP_AUTHORIZATION=f"Bearer {token['access']}")
    viewer.post(post_view_url(post.pk))

    response = auth_client.get(STATS_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.data["post_count"] == 1
    assert response.data["total_comments"] == 1
    assert response.data["total_views"] == 1
    assert response.data["unique_readers"] == 1
    assert response.data["platform_subscribers"] >= 1
    assert response.data["subscribers_who_viewed"] == 1
    assert response.data["top_posts"][0]["id"] == post.pk
    assert response.data["recent_views"][0]["reader_type"] == "subscriber"
    assert response.data["post_stats"][0]["view_count"] == 1
