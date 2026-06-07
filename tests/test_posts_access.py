"""Тесты матрицы доступа к body публикаций."""

import pytest
from rest_framework import status

from tests.conftest import POSTS_URL, post_detail_url


def _first_result(response_data: dict) -> dict:
    """Первый элемент paginated list."""
    return response_data["results"][0]


@pytest.mark.django_db
def test_guest_sees_free_body_in_list(api_client, free_post) -> None:
    """Guest видит body бесплатной публикации в списке."""
    response = api_client.get(POSTS_URL)
    assert response.status_code == status.HTTP_200_OK
    item = _first_result(response.data)
    assert item["title"] == free_post.title
    assert item["body"] == free_post.body
    assert item["can_view_body"] is True


@pytest.mark.django_db
def test_guest_does_not_see_paid_body_in_list(api_client, paid_post) -> None:
    """Guest не видит body платной публикации в списке."""
    response = api_client.get(POSTS_URL)
    item = _first_result(response.data)
    assert item["title"] == paid_post.title
    assert item["body"] is None
    assert item["can_view_body"] is False


@pytest.mark.django_db
def test_guest_does_not_see_paid_body_on_retrieve(api_client, paid_post) -> None:
    """Guest на retrieve получает 200 без body (paywall)."""
    response = api_client.get(post_detail_url(paid_post.pk))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["body"] is None
    assert response.data["can_view_body"] is False


@pytest.mark.django_db
def test_auth_without_sub_does_not_see_paid_body(other_auth_client, paid_post) -> None:
    """Авторизованный без подписки не видит чужой paid body."""
    response = other_auth_client.get(post_detail_url(paid_post.pk))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["body"] is None
    assert response.data["can_view_body"] is False


@pytest.mark.django_db
def test_subscriber_sees_paid_body(subscriber_client, paid_post) -> None:
    """Подписчик видит body платной публикации."""
    response = subscriber_client.get(post_detail_url(paid_post.pk))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["body"] == paid_post.body
    assert response.data["can_view_body"] is True


@pytest.mark.django_db
def test_author_sees_own_paid_body(auth_client, paid_post) -> None:
    """Автор видит body своей платной публикации без подписки."""
    response = auth_client.get(post_detail_url(paid_post.pk))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["body"] == paid_post.body
    assert response.data["can_view_body"] is True


@pytest.mark.django_db
def test_list_always_includes_title_for_paid(api_client, paid_post) -> None:
    """Список всегда содержит title даже для paid."""
    response = api_client.get(POSTS_URL)
    item = _first_result(response.data)
    assert item["title"] == paid_post.title
    assert "body" in item
