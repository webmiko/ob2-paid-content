"""Тесты автогенерации SEO публикаций."""

import pytest
from rest_framework import status

from posts.models import Post


@pytest.mark.django_db
def test_post_save_fills_seo_fields(author) -> None:
    """При создании поста автоматически прописываются meta-теги."""
    post = Post.objects.create(
        title="Как начать писать на Creavity",
        body="Полезные советы для новых авторов платформы.",
        is_paid=False,
        topic="creative",
        author=author,
    )
    post.refresh_from_db()

    assert post.meta_title == "Как начать писать на Creavity"
    assert "Creavity" in post.meta_description
    assert "Творчество" in post.meta_keywords
    assert author.display_name[:3] in post.meta_keywords or "Автор" in post.meta_keywords


@pytest.mark.django_db
def test_paid_post_seo_description(author) -> None:
    """Платная публикация получает описание без утечки текста."""
    post = Post.objects.create(
        title="Секретный курс",
        body="Конфиденциальный материал подписки.",
        is_paid=True,
        topic="education",
        author=author,
    )
    post.refresh_from_db()

    assert "Платная публикация" in post.meta_description
    assert "Конфиденциальный" not in post.meta_description
    assert "платный контент" in post.meta_keywords


@pytest.mark.django_db
def test_post_update_refreshes_seo(author) -> None:
    """Изменение заголовка пересчитывает SEO."""
    post = Post.objects.create(
        title="Старый заголовок",
        body="Текст",
        author=author,
    )
    post.title = "Новый заголовок SEO"
    post.save(update_fields=["title"])
    post.refresh_from_db()

    assert post.meta_title == "Новый заголовок SEO"


@pytest.mark.django_db
def test_post_api_returns_seo_fields(api_client, free_post) -> None:
    """API отдаёт SEO-поля для страницы публикации."""
    free_post.refresh_from_db()
    assert free_post.meta_title

    response = api_client.get(f"/api/posts/{free_post.pk}/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["meta_title"] == free_post.meta_title
    assert response.data["meta_description"] == free_post.meta_description
    assert response.data["meta_keywords"] == free_post.meta_keywords
