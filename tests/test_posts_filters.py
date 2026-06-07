"""Тесты фильтрации списка публикаций."""

import pytest
from rest_framework import status

from posts.models import Post
from tests.conftest import POSTS_URL


@pytest.mark.django_db
def test_filter_free_posts(api_client, free_post, paid_post) -> None:
    """?is_paid=false возвращает только бесплатные."""
    response = api_client.get(POSTS_URL, {"is_paid": "false"})
    assert response.status_code == status.HTTP_200_OK
    ids = {item["id"] for item in response.data["results"]}
    assert free_post.pk in ids
    assert paid_post.pk not in ids


@pytest.mark.django_db
def test_filter_by_author(api_client, author, other_user, free_post) -> None:
    """?author=id ограничивает публикации одним автором."""
    Post.objects.create(
        title="Other",
        body="Body",
        is_paid=False,
        author=other_user,
        topic="other",
    )
    response = api_client.get(POSTS_URL, {"author": author.pk})
    assert response.status_code == status.HTTP_200_OK
    assert all(item["author_id"] == author.pk for item in response.data["results"])


@pytest.mark.django_db
def test_filter_by_topic(api_client, author) -> None:
    """?topic=tech возвращает публикации выбранной тематики."""
    Post.objects.create(title="Tech", body="T", is_paid=False, author=author, topic="tech")
    Post.objects.create(title="Biz", body="B", is_paid=False, author=author, topic="business")
    response = api_client.get(POSTS_URL, {"topic": "tech"})
    titles = [item["title"] for item in response.data["results"]]
    assert titles == ["Tech"]


@pytest.mark.django_db
def test_search_in_title(api_client, free_post) -> None:
    """?search= ищет по заголовку."""
    response = api_client.get(POSTS_URL, {"search": "Free"})
    assert response.status_code == status.HTTP_200_OK
    assert response.data["results"][0]["id"] == free_post.pk


@pytest.mark.django_db
def test_search_does_not_match_paid_body_for_guest(api_client, author) -> None:
    """Гость не находит paid-пост по секретному слову только в body."""
    paid = Post.objects.create(
        title="Public paid title",
        body="UniquePaidBodySecretXYZ",
        is_paid=True,
        author=author,
    )
    response = api_client.get(POSTS_URL, {"search": "UniquePaidBodySecretXYZ"})
    ids = {item["id"] for item in response.data["results"]}
    assert paid.pk not in ids


@pytest.mark.django_db
def test_search_matches_paid_body_for_subscriber(subscriber_client, author) -> None:
    """Подписчик находит paid-пост по слову в body."""
    paid = Post.objects.create(
        title="Subscriber search",
        body="SubscriberBodyTokenABC",
        is_paid=True,
        author=author,
    )
    response = subscriber_client.get(POSTS_URL, {"search": "SubscriberBodyTokenABC"})
    ids = {item["id"] for item in response.data["results"]}
    assert paid.pk in ids


@pytest.mark.django_db
def test_search_matches_own_paid_body_for_author(auth_client, author) -> None:
    """Автор без подписки находит свой paid-пост по body."""
    paid = Post.objects.create(
        title="My paid",
        body="AuthorOwnBodyTokenDEF",
        is_paid=True,
        author=author,
    )
    response = auth_client.get(POSTS_URL, {"search": "AuthorOwnBodyTokenDEF"})
    ids = {item["id"] for item in response.data["results"]}
    assert paid.pk in ids


@pytest.mark.django_db
def test_access_available_guest(api_client, free_post, paid_post) -> None:
    """Гость с ?access=available видит только бесплатные."""
    response = api_client.get(POSTS_URL, {"access": "available"})
    ids = {item["id"] for item in response.data["results"]}
    assert free_post.pk in ids
    assert paid_post.pk not in ids


@pytest.mark.django_db
def test_access_available_author_sees_own_paid(auth_client, author, paid_post, other_user) -> None:
    """Автор без подписки видит свои платные в ?access=available."""
    Post.objects.create(
        title="Foreign paid",
        body="Secret",
        is_paid=True,
        author=other_user,
        topic="other",
    )
    response = auth_client.get(POSTS_URL, {"access": "available"})
    ids = {item["id"] for item in response.data["results"]}
    assert paid_post.pk in ids
    assert len(ids) == 1


@pytest.mark.django_db
def test_post_response_includes_topic_and_author_label(api_client, free_post, author) -> None:
    """Ответ содержит topic, topic_label и author_label."""
    author.display_name = "Тестовый автор"
    author.save(update_fields=["display_name"])
    response = api_client.get(f"{POSTS_URL}{free_post.pk}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["topic"] == "other"
    assert response.data["topic_label"] == "Другое"
    assert response.data["author_label"] == "Тестовый автор"
