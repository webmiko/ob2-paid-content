"""Сериализаторы комментариев к публикациям."""

from rest_framework import serializers

from posts.models import Comment, Post
from posts.services.comments import can_delete_comment
from users.services.display import get_public_author_label


class CommentSerializer(serializers.ModelSerializer):
    """Чтение комментария с публичным никнеймом автора."""

    author_label = serializers.SerializerMethodField()
    can_delete = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ("id", "author_id", "author_label", "text", "created_at", "can_delete")
        read_only_fields = fields

    def get_author_label(self, obj: Comment) -> str:
        """Публичное имя автора комментария."""
        return get_public_author_label(obj.author)

    def get_can_delete(self, obj: Comment) -> bool:
        """Может ли текущий пользователь удалить комментарий."""
        request = self.context.get("request")
        post: Post | None = self.context.get("post")
        if request is None or not request.user.is_authenticated or post is None:
            return False
        return can_delete_comment(request.user, obj, post)


class CommentWriteSerializer(serializers.ModelSerializer):
    """Создание комментария."""

    class Meta:
        model = Comment
        fields = ("text",)

    def validate_text(self, value: str) -> str:
        """Обрезает пробелы и проверяет непустой текст."""
        text = value.strip()
        if not text:
            raise serializers.ValidationError("Комментарий не может быть пустым.")
        if len(text) > 2000:
            raise serializers.ValidationError("Не больше 2000 символов.")
        return text
