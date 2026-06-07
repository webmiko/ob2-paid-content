"""Сериализаторы метаданных: авторы и тематики."""

from rest_framework import serializers

from posts.choices import PostTopic
from users.services.display import get_public_author_label


class AuthorListSerializer(serializers.Serializer):
    """Автор с количеством публикаций для страницы каталога."""

    id = serializers.IntegerField()
    label = serializers.SerializerMethodField()
    post_count = serializers.IntegerField()
    paid_count = serializers.IntegerField()
    free_count = serializers.IntegerField()

    def get_label(self, obj) -> str:
        """Публичное имя автора без телефона."""
        return get_public_author_label(obj)


class TopicListSerializer(serializers.Serializer):
    """Тематика с количеством публикаций."""

    slug = serializers.CharField()
    label = serializers.CharField()
    post_count = serializers.IntegerField()

    @staticmethod
    def from_counts(counts_by_topic: dict[str, int]) -> list[dict[str, object]]:
        """Собирает список тем с нулевыми счётчиками для пустых категорий.

        Args:
            counts_by_topic: Словарь topic → количество публикаций.

        Returns:
            Список dict для TopicListSerializer.
        """
        items: list[dict[str, object]] = []
        for slug, label in PostTopic.choices:
            items.append(
                {
                    "slug": slug,
                    "label": label,
                    "post_count": counts_by_topic.get(slug, 0),
                },
            )
        return items
