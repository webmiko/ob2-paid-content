"""Тесты видео в публикациях (мульти-провайдер embed и paywall)."""

import pytest
from rest_framework import status

from posts.services.video import (
    PROVIDER_DZEN,
    PROVIDER_RUTUBE,
    PROVIDER_VIMEO,
    PROVIDER_VK,
    PROVIDER_YOUTUBE,
    detect_video_provider,
    is_valid_video_url,
    video_embed_url,
)
from tests.conftest import POSTS_URL, post_detail_url

YOUTUBE_WATCH = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
YOUTUBE_SHORT = "https://youtu.be/dQw4w9WgXcQ"
YOUTUBE_EMBED = "https://www.youtube.com/embed/dQw4w9WgXcQ"
VIMEO_URL = "https://vimeo.com/148751763"
VIMEO_EMBED = "https://player.vimeo.com/video/148751763"
RUTUBE_URL = "https://rutube.ru/video/c7858c15d841423bbec1000002307a76/"
RUTUBE_EMBED = "https://rutube.ru/play/embed/c7858c15d841423bbec1000002307a76"
VK_URL = "https://vk.com/video-456239017_456239123"
VK_EMBED = "https://vk.com/video_ext.php?oid=-456239017&id=456239123&hd=2"
DZEN_URL = "https://dzen.ru/video/watch/speech-intro-lesson"
DZEN_EMBED = "https://dzen.ru/embed/speech-intro-lesson"


@pytest.mark.parametrize(
    ("url", "provider", "embed"),
    [
        (YOUTUBE_WATCH, PROVIDER_YOUTUBE, YOUTUBE_EMBED),
        (YOUTUBE_SHORT, PROVIDER_YOUTUBE, YOUTUBE_EMBED),
        (VIMEO_URL, PROVIDER_VIMEO, VIMEO_EMBED),
        (RUTUBE_URL, PROVIDER_RUTUBE, RUTUBE_EMBED),
        (VK_URL, PROVIDER_VK, VK_EMBED),
        (DZEN_URL, PROVIDER_DZEN, DZEN_EMBED),
    ],
)
def test_video_providers_embed(url: str, provider: str, embed: str) -> None:
    """Поддерживаемые провайдеры распознаются и дают embed URL."""
    assert detect_video_provider(url) == provider
    assert video_embed_url(url) == embed
    assert is_valid_video_url(url) is True


def test_video_embed_url_empty_returns_none() -> None:
    """Пустая строка не даёт embed URL."""
    assert video_embed_url("") is None


def test_is_valid_video_url_rejects_unknown_host() -> None:
    """Неподдерживаемые хосты отклоняются."""
    assert is_valid_video_url("https://example.com/video") is False


@pytest.mark.django_db
def test_guest_sees_has_video_but_not_embed_on_paid(api_client, author) -> None:
    """Guest видит флаг has_video, но не embed URL у платного поста."""
    from posts.models import Post

    post = Post.objects.create(
        title="Paid with video",
        body="Secret",
        is_paid=True,
        author=author,
        video_url=YOUTUBE_WATCH,
    )
    response = api_client.get(post_detail_url(post.pk))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["has_video"] is True
    assert response.data["video_provider"] == PROVIDER_YOUTUBE
    assert response.data["video_url"] is None
    assert response.data["video_embed_url"] is None


@pytest.mark.django_db
def test_guest_sees_rutube_embed_on_free_post(api_client, author) -> None:
    """Guest видит embed Rutube у бесплатного поста."""
    from posts.models import Post

    post = Post.objects.create(
        title="Free rutube",
        body="Open lesson",
        is_paid=False,
        author=author,
        video_url=RUTUBE_URL,
    )
    response = api_client.get(post_detail_url(post.pk))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["video_embed_url"] == RUTUBE_EMBED
    assert response.data["video_provider"] == PROVIDER_RUTUBE


@pytest.mark.django_db
def test_create_post_rejects_unknown_topic(auth_client) -> None:
    """Неизвестная тематика отклоняется при создании."""
    response = auth_client.post(
        POSTS_URL,
        {
            "title": "Bad topic",
            "body": "Text",
            "is_paid": False,
            "topic": "unknown-topic",
        },
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_create_post_rejects_invalid_video_url(auth_client) -> None:
    """При создании отклоняется неподдерживаемая ссылка."""
    response = auth_client.post(
        POSTS_URL,
        {
            "title": "Bad video",
            "body": "Text",
            "is_paid": False,
            "video_url": "https://example.com/video",
        },
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_create_post_accepts_vimeo_url(auth_client) -> None:
    """Автор может создать публикацию с Vimeo-ссылкой."""
    from posts.models import Post

    response = auth_client.post(
        POSTS_URL,
        {
            "title": "Vimeo lesson",
            "body": "Text",
            "is_paid": False,
            "video_url": VIMEO_URL,
        },
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    post = Post.objects.get(title="Vimeo lesson")
    assert post.video_url == VIMEO_URL
    detail = auth_client.get(post_detail_url(post.pk))
    assert detail.data["video_embed_url"] == VIMEO_EMBED


@pytest.mark.django_db
def test_post_includes_comment_count(api_client, free_post, other_user) -> None:
    """API поста возвращает comment_count."""
    from posts.models import Comment

    Comment.objects.create(post=free_post, author=other_user, text="Hi")
    response = api_client.get(post_detail_url(free_post.pk))
    assert response.status_code == status.HTTP_200_OK
    assert response.data["comment_count"] == 1
