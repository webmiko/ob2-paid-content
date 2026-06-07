"""Unit-тесты сериализаторов posts."""

from posts.comment_serializers import CommentWriteSerializer
from posts.serializers import PostWriteSerializer


def test_post_write_serializer_accepts_empty_video_url() -> None:
    """Пустая ссылка на видео сохраняется как пустая строка."""
    serializer = PostWriteSerializer(
        data={
            "title": "Title",
            "body": "Body",
            "is_paid": False,
            "topic": "other",
            "video_url": "   ",
        },
    )
    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["video_url"] == ""


def test_post_write_serializer_rejects_unknown_topic() -> None:
    """Неизвестная тематика отклоняется на уровне сериализатора."""
    serializer = PostWriteSerializer(
        data={
            "title": "Title",
            "body": "Body",
            "is_paid": False,
            "topic": "space",
        },
    )
    assert not serializer.is_valid()
    assert "topic" in serializer.errors


def test_comment_write_serializer_rejects_empty_text() -> None:
    """Пустой текст комментария отклоняется."""
    serializer = CommentWriteSerializer(data={"text": "   "})
    assert not serializer.is_valid()
    assert "text" in serializer.errors


def test_comment_write_serializer_rejects_too_long_text() -> None:
    """Текст длиннее 2000 символов отклоняется."""
    serializer = CommentWriteSerializer(data={"text": "a" * 2001})
    assert not serializer.is_valid()
    assert "text" in serializer.errors
