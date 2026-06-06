"""Сериализаторы публикаций для REST API."""

from rest_framework import serializers

from posts.models import Post
from posts.services.access import can_view_post_body


class PostSerializer(serializers.ModelSerializer):
    """Чтение публикации; body скрывается без права доступа."""

    can_view_body = serializers.SerializerMethodField()
    body = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "body",
            "is_paid",
            "can_view_body",
            "author_id",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_can_view_body(self, obj: Post) -> bool:
        """Возвращает флаг доступа к полному тексту публикации.

        Args:
            obj: Публикация из queryset.

        Returns:
            True, если body можно показать текущему пользователю.
        """
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


class PostWriteSerializer(serializers.ModelSerializer):
    """Создание и редактирование публикации автором."""

    class Meta:
        model = Post
        fields = ("title", "body", "is_paid")
