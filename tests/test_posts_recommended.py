"""Тесты блока рекомендаций в каталоге."""

import pytest
from rest_framework import status

from posts.models import Post
from tests.conftest import RECOMMENDED_URL


@pytest.mark.django_db
def test_recommended_returns_only_free_posts(api_client, author, other_user) -> None:
    """Рекомендации содержат только бесплатные публикации."""
    Post.objects.create(title="Free A", body="A", is_paid=False, author=author, topic="creative")
    Post.objects.create(title="Paid B", body="B", is_paid=True, author=other_user, topic="tech")
    response = api_client.get(RECOMMENDED_URL)
    assert response.status_code == status.HTTP_200_OK
    titles = [item["title"] for item in response.data]
    assert "Free A" in titles
    assert "Paid B" not in titles
    assert all(item["is_paid"] is False for item in response.data)


@pytest.mark.django_db
def test_recommended_excludes_own_posts_for_auth_user(auth_client, author) -> None:
    """Авторизованный пользователь не видит свои публикации в рекомендациях."""
    Post.objects.create(title="Mine", body="Own", is_paid=False, author=author, topic="other")
    Post.objects.create(
        title="Other free",
        body="Text",
        is_paid=False,
        author=author,
        topic="creative",
    )
    from users.models import User

    other = User.objects.create_user(phone="79009998877", password="SecurePass123")
    Post.objects.create(title="Peer", body="Peer text", is_paid=False, author=other, topic="tech")
    response = auth_client.get(RECOMMENDED_URL)
    assert response.status_code == status.HTTP_200_OK
    titles = [item["title"] for item in response.data]
    assert "Mine" not in titles
    assert "Other free" not in titles
    assert "Peer" in titles


@pytest.mark.django_db
def test_recommended_fills_limit_when_topics_repeat(api_client, author) -> None:
    """Если тем мало, добираем публикации до лимита."""
    for index in range(8):
        Post.objects.create(
            title=f"Same topic {index}",
            body="Body",
            is_paid=False,
            author=author,
            topic="other",
        )
    response = api_client.get(RECOMMENDED_URL)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 6


@pytest.mark.django_db
def test_recommended_for_subscriber_includes_body(subscriber_client, author) -> None:
    """Подписчик получает полный сериализатор в рекомендациях."""
    Post.objects.create(
        title="Free lesson",
        body="Visible body",
        is_paid=False,
        author=author,
        topic="education",
    )
    response = subscriber_client.get(RECOMMENDED_URL)
    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]["body"] == "Visible body"


@pytest.mark.django_db
def test_recommended_excludes_viewed_ids(api_client, author) -> None:
    """Query exclude убирает уже просмотренные ID."""
    first = Post.objects.create(title="Seen", body="A", is_paid=False, author=author, topic="other")
    Post.objects.create(title="Fresh", body="B", is_paid=False, author=author, topic="creative")
    response = api_client.get(f"{RECOMMENDED_URL}?exclude={first.pk}")
    assert response.status_code == status.HTTP_200_OK
    titles = [item["title"] for item in response.data]
    assert "Seen" not in titles
    assert "Fresh" in titles


@pytest.mark.django_db
def test_recommended_prefers_diverse_topics(api_client, author) -> None:
    """Подборка старается включить разные тематики."""
    Post.objects.create(title="Art", body="A", is_paid=False, author=author, topic="creative")
    Post.objects.create(title="Code", body="B", is_paid=False, author=author, topic="tech")
    Post.objects.create(title="Trip", body="C", is_paid=False, author=author, topic="travel")
    response = api_client.get(RECOMMENDED_URL)
    assert response.status_code == status.HTTP_200_OK
    topics = {item["topic"] for item in response.data}
    assert len(topics) >= 2
