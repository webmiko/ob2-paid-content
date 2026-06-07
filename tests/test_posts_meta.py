"""Тесты API авторов и тематик."""

import pytest
from rest_framework import status

AUTHORS_URL = "/api/posts/authors/"
TOPICS_URL = "/api/posts/topics/"


@pytest.mark.django_db
def test_authors_list(api_client, author, free_post, paid_post) -> None:
    """Список авторов содержит счётчики без телефона."""
    response = api_client.get(AUTHORS_URL)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    item = response.data[0]
    assert item["id"] == author.pk
    assert item["post_count"] == 2
    assert item["paid_count"] == 1
    assert item["free_count"] == 1
    assert "phone" not in item
    assert item["label"].startswith("Автор")


@pytest.mark.django_db
def test_author_search_by_display_name(api_client, author, free_post) -> None:
    """Поиск авторов работает по display_name."""
    author.display_name = "UniqueCatalogAuthor"
    author.save(update_fields=["display_name"])
    response = api_client.get(AUTHORS_URL, {"search": "CatalogAuthor"})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]["id"] == author.pk


@pytest.mark.django_db
def test_author_search_does_not_match_phone(api_client, author, free_post) -> None:
    """Поиск авторов не использует телефон (нет enumeration)."""
    author.display_name = "NoPhoneMatchName"
    author.save(update_fields=["display_name"])
    response = api_client.get(AUTHORS_URL, {"search": author.phone[:6]})
    assert response.status_code == status.HTTP_200_OK
    assert response.data == []


@pytest.mark.django_db
def test_author_detail(api_client, author, free_post) -> None:
    """Детальная карточка автора доступна гостю."""
    response = api_client.get(f"{AUTHORS_URL}{author.pk}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == author.pk
    assert response.data["post_count"] == 1


@pytest.mark.django_db
def test_topics_list(api_client, author) -> None:
    """Список тем содержит все категории и счётчики."""
    from posts.models import Post

    Post.objects.create(title="T", body="B", is_paid=False, author=author, topic="tech")
    response = api_client.get(TOPICS_URL)
    assert response.status_code == status.HTTP_200_OK
    tech = next(item for item in response.data if item["slug"] == "tech")
    assert tech["post_count"] == 1
    assert tech["label"] == "Технологии"
