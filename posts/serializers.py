"""Сериализаторы DRF для posts."""

from rest_framework import serializers

from posts.models import Post
from posts.services.access import can_view_post_body


class PostSerializer(serializers.ModelSerializer):
    """Чтение публикации: body скрывается без can_view_post_body."""

    can_view_body = serializers.SerializerMethodField()
    body = serializers.SerializerMethodField()
    author_phone = serializers.CharField(source="author.phone", read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "body",
            "is_paid",
            "can_view_body",
            "author_phone",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_can_view_body(self, obj: Post) -> bool:
        """Флаг доступа к body для SPA (paywall UI)."""
        request = self.context.get("request")
        user = request.user if request else None
        return can_view_post_body(user, obj)

    def get_body(self, obj: Post) -> str | None:
        """Возвращает body только при наличии доступа."""
        if self.get_can_view_body(obj):
            return obj.body
        return None


class PostWriteSerializer(serializers.ModelSerializer):
    """Создание и редактирование публикации автором."""

    class Meta:
        model = Post
        fields = ("title", "body", "is_paid")
