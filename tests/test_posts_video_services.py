"""Unit-тесты сервисов video и recommendations."""

import pytest
from django.contrib.auth.models import AnonymousUser

from posts.models import Post
from posts.services.recommendations import DEFAULT_RECOMMENDED_LIMIT, get_recommended_posts, get_similar_posts
from posts.services.video import youtube_embed_url


def test_youtube_embed_url_mobile_host() -> None:
    """Мобильный домен youtube.com поддерживается."""
    url = "https://m.youtube.com/watch?v=abc123XYZ-_"
    assert youtube_embed_url(url) == "https://www.youtube.com/embed/abc123XYZ-_"


@pytest.mark.django_db
def test_get_recommended_posts_returns_empty_for_no_free(author) -> None:
    """Без бесплатных публикаций список пуст."""
    Post.objects.create(title="Paid only", body="X", is_paid=True, author=author)
    assert get_recommended_posts(AnonymousUser()) == []


@pytest.mark.django_db
def test_get_recommended_posts_stops_at_limit_with_diverse_topics(author) -> None:
    """При достаточном числе тем возвращаем ровно limit без добора."""
    topics = ("creative", "tech", "travel", "education", "fitness", "other")
    for index, topic in enumerate(topics):
        Post.objects.create(
            title=f"Diverse {index}",
            body="Text",
            is_paid=False,
            author=author,
            topic=topic,
        )
    result = get_recommended_posts(AnonymousUser(), limit=6)
    assert len(result) == 6


@pytest.mark.django_db
def test_get_recommended_posts_prioritizes_video(author) -> None:
    """Публикации с видео попадают в рекомендации раньше."""
    text_only = Post.objects.create(
        title="Text only",
        body="A",
        is_paid=False,
        author=author,
        topic="other",
    )
    with_video = Post.objects.create(
        title="With video",
        body="B",
        is_paid=False,
        author=author,
        topic="other",
        video_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    )
    result = get_recommended_posts(AnonymousUser(), limit=1)
    assert result[0].pk == with_video.pk
    assert text_only.pk != result[0].pk


@pytest.mark.django_db
def test_get_recommended_posts_excludes_ids(author) -> None:
    """exclude_ids убирает просмотренные публикации."""
    first = Post.objects.create(title="First", body="A", is_paid=False, author=author, topic="other")
    Post.objects.create(title="Second", body="B", is_paid=False, author=author, topic="creative")
    result = get_recommended_posts(AnonymousUser(), limit=2, exclude_ids=[first.pk])
    titles = [post.title for post in result]
    assert "First" not in titles


@pytest.mark.django_db
def test_get_similar_posts_excludes_current(author) -> None:
    """Похожие не включают текущую публикацию."""
    main = Post.objects.create(title="Main", body="X", is_paid=False, author=author, topic="tech")
    result = get_similar_posts(main, AnonymousUser())
    assert all(post.pk != main.pk for post in result)
