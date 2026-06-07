"""Сериализаторы дашборда автора."""

from rest_framework import serializers


class AuthorTopicStatSerializer(serializers.Serializer):
    """Статистика по тематике."""

    slug = serializers.CharField()
    label = serializers.CharField()
    post_count = serializers.IntegerField()
    views = serializers.IntegerField()
    comments = serializers.IntegerField()


class AuthorTopPostSerializer(serializers.Serializer):
    """Публикация в топе по просмотрам."""

    id = serializers.IntegerField()
    title = serializers.CharField()
    is_paid = serializers.BooleanField()
    view_count = serializers.IntegerField()
    comment_count = serializers.IntegerField()
    created_at = serializers.DateTimeField()


class AuthorPostStatSerializer(serializers.Serializer):
    """Статистика одной публикации автора."""

    id = serializers.IntegerField()
    title = serializers.CharField()
    is_paid = serializers.BooleanField()
    topic_label = serializers.CharField()
    view_count = serializers.IntegerField()
    comment_count = serializers.IntegerField()
    created_at = serializers.DateTimeField()


class AuthorRecentViewSerializer(serializers.Serializer):
    """Недавний просмотр публикации автора."""

    post_id = serializers.IntegerField()
    post_title = serializers.CharField()
    viewed_at = serializers.DateTimeField()
    reader_type = serializers.CharField()


class AuthorDashboardStatsSerializer(serializers.Serializer):
    """Сводка метрик автора для профиля."""

    post_count = serializers.IntegerField()
    free_count = serializers.IntegerField()
    paid_count = serializers.IntegerField()
    total_views = serializers.IntegerField()
    unique_readers = serializers.IntegerField()
    total_comments = serializers.IntegerField()
    platform_subscribers = serializers.IntegerField()
    subscribers_who_viewed = serializers.IntegerField()
    posts_with_video = serializers.IntegerField()
    by_topic = AuthorTopicStatSerializer(many=True)
    top_posts = AuthorTopPostSerializer(many=True)
    post_stats = AuthorPostStatSerializer(many=True)
    recent_views = AuthorRecentViewSerializer(many=True)
