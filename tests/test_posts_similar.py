"""Тесты похожих публикаций."""

import pytest
from rest_framework import status

from posts.models import Post
from tests.conftest import post_similar_url


@pytest.mark.django_db
def test_similar_returns_same_topic(api_client, author) -> None:
    """Похожие публикации той же тематики."""
    main = Post.objects.create(
        title="Main",
        body="Body",
        is_paid=False,
        author=author,
        topic="education",
    )
    Post.objects.create(
        title="Same topic",
        body="Other",
        is_paid=False,
        author=author,
        topic="education",
    )
    Post.objects.create(
        title="Other topic",
        body="X",
        is_paid=False,
        author=author,
        topic="tech",
    )
    response = api_client.get(post_similar_url(main.pk))
    assert response.status_code == status.HTTP_200_OK
    titles = [item["title"] for item in response.data]
    assert "Same topic" in titles
    assert "Other topic" not in titles
    assert "Main" not in titles


@pytest.mark.django_db
def test_similar_prefers_free_posts(api_client, author) -> None:
    """Бесплатные похожие публикации идут первыми."""
    main = Post.objects.create(
        title="Main",
        body="Body",
        is_paid=False,
        author=author,
        topic="creative",
    )
    paid = Post.objects.create(
        title="Paid similar",
        body="Paid",
        is_paid=True,
        author=author,
        topic="creative",
    )
    free = Post.objects.create(
        title="Free similar",
        body="Free",
        is_paid=False,
        author=author,
        topic="creative",
    )
    response = api_client.get(post_similar_url(main.pk))
    assert response.status_code == status.HTTP_200_OK
    ids = [item["id"] for item in response.data]
    assert ids.index(free.pk) < ids.index(paid.pk)
