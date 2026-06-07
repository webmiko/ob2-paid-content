"""Сериализаторы публикаций для REST API."""

from rest_framework import serializers

from posts.choices import PostTopic
from posts.models import Post
from posts.services.access import can_view_post_body
from posts.services.video import detect_video_provider, is_valid_video_url, video_embed_url
from users.services.display import get_public_author_label


class PostSerializer(serializers.ModelSerializer):
    """Чтение публикации; body скрывается без права доступа."""

    can_view_body = serializers.SerializerMethodField()
    body = serializers.SerializerMethodField()
    author_label = serializers.SerializerMethodField()
    topic_label = serializers.SerializerMethodField()
    has_video = serializers.SerializerMethodField()
    video_provider = serializers.SerializerMethodField()
    video_url = serializers.SerializerMethodField()
    video_embed_url = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "body",
            "is_paid",
            "topic",
            "topic_label",
            "meta_title",
            "meta_description",
            "meta_keywords",
            "has_video",
            "video_provider",
            "video_url",
            "video_embed_url",
            "comment_count",
            "can_view_body",
            "author_id",
            "author_label",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_author_label(self, obj: Post) -> str:
        """Публичное имя автора без телефона."""
        return get_public_author_label(obj.author)

    def get_topic_label(self, obj: Post) -> str:
        """Человекочитаемая подпись тематики."""
        return obj.get_topic_display()

    def get_can_view_body(self, obj: Post) -> bool:
        """Возвращает флаг доступа к полному тексту публикации."""
        request = self.context.get("request")
        user = request.user if request else None
        subscription_active = self.context.get("user_has_active_subscription")
        result = can_view_post_body(user, obj, subscription_active=subscription_active)
        obj._can_view_body_cached = result  # noqa: SLF001
        return result

    def get_body(self, obj: Post) -> str | None:
        """Возвращает текст публикации или None без права доступа."""
        cached = getattr(obj, "_can_view_body_cached", None)
        if cached is None:
            cached = self.get_can_view_body(obj)
        return obj.body if cached else None

    def get_has_video(self, obj: Post) -> bool:
        """Есть ли у публикации прикреплённое видео (без утечки для paid без доступа)."""
        if obj.is_paid and not self.get_can_view_body(obj):
            return False
        return bool(obj.video_url)

    def get_video_provider(self, obj: Post) -> str | None:
        """Провайдер видео или None без доступа к paid."""
        if obj.is_paid and not self.get_can_view_body(obj):
            return None
        if not obj.video_url:
            return None
        return detect_video_provider(obj.video_url)

    def get_video_url(self, obj: Post) -> str | None:
        """URL видео только при доступе к содержимому."""
        if not obj.video_url or not self.get_can_view_body(obj):
            return None
        return obj.video_url

    def get_video_embed_url(self, obj: Post) -> str | None:
        """Embed URL только при доступе к содержимому."""
        if not obj.video_url or not self.get_can_view_body(obj):
            return None
        return video_embed_url(obj.video_url)

    def get_comment_count(self, obj: Post) -> int:
        """Число комментариев (скрыто для paid без доступа)."""
        if obj.is_paid and not self.get_can_view_body(obj):
            return 0
        annotated = getattr(obj, "comment_count", None)
        if annotated is not None:
            return int(annotated)
        return obj.comments.count()


class PostWriteSerializer(serializers.ModelSerializer):
    """Создание и редактирование публикации автором."""

    class Meta:
        model = Post
        fields = ("title", "body", "is_paid", "topic", "video_url")

    def validate_video_url(self, value: str) -> str:
        """Проверяет ссылку на видео или пустое значение."""
        cleaned = (value or "").strip()
        if not cleaned:
            return ""
        if not is_valid_video_url(cleaned):
            raise serializers.ValidationError(
                "Поддерживаются ссылки YouTube, Vimeo, Rutube, VK Video и Дзен.",
            )
        return cleaned

    def validate_topic(self, value: str) -> str:
        """Проверяет, что тематика из разрешённого набора."""
        valid = {choice[0] for choice in PostTopic.choices}
        if value not in valid:
            raise serializers.ValidationError("Неизвестная тематика.")
        return value
