"""Агрегаты статистики автора для дашборда профиля."""

from django.contrib.auth.models import AbstractBaseUser
from django.db.models import Count, Q, Sum

from posts.choices import PostTopic
from posts.models import Comment, Post, PostView
from posts.services.view_tracking import reader_type_for_view
from users.models import Subscription


def get_author_dashboard_stats(author: AbstractBaseUser) -> dict[str, object]:
    """Собирает метрики автора для GET /api/users/me/stats/."""
    posts = Post.objects.filter(author_id=author.pk)
    post_ids = posts.values_list("pk", flat=True)

    views_qs = PostView.objects.filter(post__author_id=author.pk).exclude(user_id=author.pk)
    auth_readers = views_qs.filter(user__isnull=False).values("user").distinct().count()
    guest_readers = views_qs.filter(user__isnull=True).count()
    total_views = views_qs.count()

    total_comments = Comment.objects.filter(post_id__in=post_ids).count()
    platform_subscribers = Subscription.objects.filter(is_active=True).count()
    subscribers_who_viewed = views_qs.filter(user__subscription__is_active=True).values("user").distinct().count()

    by_topic: list[dict[str, object]] = []
    for slug, label in PostTopic.choices:
        topic_posts = posts.filter(topic=slug)
        topic_ids = topic_posts.values_list("pk", flat=True)
        if not topic_posts.exists():
            continue
        by_topic.append(
            {
                "slug": slug,
                "label": label,
                "post_count": topic_posts.count(),
                "views": views_qs.filter(post_id__in=topic_ids).count(),
                "comments": Comment.objects.filter(post_id__in=topic_ids).count(),
            },
        )

    top_posts = posts.annotate(
        annotated_comments=Count("comments"),
    ).order_by("-view_count", "-annotated_comments", "-created_at")[:5]
    top_posts_payload = [
        {
            "id": post.pk,
            "title": post.title,
            "is_paid": post.is_paid,
            "view_count": post.view_count,
            "comment_count": post.annotated_comments,
            "created_at": post.created_at,
        }
        for post in top_posts
    ]

    post_stats = posts.annotate(annotated_comments=Count("comments")).order_by("-created_at")[:50]
    post_stats_payload = [
        {
            "id": post.pk,
            "title": post.title,
            "is_paid": post.is_paid,
            "topic_label": post.get_topic_display(),
            "view_count": post.view_count,
            "comment_count": post.annotated_comments,
            "created_at": post.created_at,
        }
        for post in post_stats
    ]

    recent_views_qs = views_qs.select_related("post", "user", "user__subscription").order_by("-viewed_at")[:8]
    recent_views = [
        {
            "post_id": view.post_id,
            "post_title": view.post.title,
            "viewed_at": view.viewed_at,
            "reader_type": reader_type_for_view(view.user),
        }
        for view in recent_views_qs
    ]

    posts_with_video = posts.exclude(video_url="").count()
    aggregates = posts.aggregate(
        post_count=Count("id"),
        free_count=Count("id", filter=Q(is_paid=False)),
        paid_count=Count("id", filter=Q(is_paid=True)),
        total_view_count=Sum("view_count"),
    )

    return {
        "post_count": aggregates["post_count"] or 0,
        "free_count": aggregates["free_count"] or 0,
        "paid_count": aggregates["paid_count"] or 0,
        "total_views": total_views,
        "unique_readers": auth_readers + guest_readers,
        "total_comments": total_comments,
        "platform_subscribers": platform_subscribers,
        "subscribers_who_viewed": subscribers_who_viewed,
        "posts_with_video": posts_with_video,
        "by_topic": by_topic,
        "top_posts": top_posts_payload,
        "post_stats": post_stats_payload,
        "recent_views": recent_views,
    }
