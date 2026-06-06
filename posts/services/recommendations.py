"""Подбор публикаций для рекомендаций и блока «Похожие»."""

from django.contrib.auth.models import AbstractBaseUser, AnonymousUser
from django.db.models import Case, IntegerField, QuerySet, Value, When

from posts.models import Post

DEFAULT_RECOMMENDED_LIMIT = 6
DEFAULT_SIMILAR_LIMIT = 4


def _free_posts_queryset(
    user: AbstractBaseUser | AnonymousUser | None,
    *,
    exclude_ids: list[int] | None = None,
) -> QuerySet[Post]:
    """Базовый queryset бесплатных публикаций с приоритетом видео."""
    queryset = (
        Post.objects.filter(is_paid=False)
        .select_related("author")
        .annotate(
            has_video_rank=Case(
                When(video_url="", then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            ),
        )
        .order_by("-has_video_rank", "-created_at")
    )
    if user is not None and user.is_authenticated:
        queryset = queryset.exclude(author=user)
    if exclude_ids:
        queryset = queryset.exclude(pk__in=exclude_ids)
    return queryset


def get_recommended_posts(
    user: AbstractBaseUser | AnonymousUser | None,
    *,
    limit: int = DEFAULT_RECOMMENDED_LIMIT,
    exclude_ids: list[int] | None = None,
) -> list[Post]:
    """Возвращает бесплатные публикации для блока «Рекомендуем».

    Приоритет — посты с видео и разные тематики; без своих (для авторизованных).

    Args:
        user: Текущий пользователь или гость.
        limit: Максимальное число публикаций.
        exclude_ids: ID уже просмотренных публикаций (из localStorage клиента).

    Returns:
        Список Post.
    """
    queryset = _free_posts_queryset(user, exclude_ids=exclude_ids)
    candidates = list(queryset[: limit * 4])
    picked: list[Post] = []
    seen_topics: set[str] = set()

    for post in candidates:
        if post.topic in seen_topics:
            continue
        picked.append(post)
        seen_topics.add(post.topic)
        if len(picked) >= limit:
            return picked

    picked_ids = {post.pk for post in picked}
    for post in candidates:
        if post.pk in picked_ids:
            continue
        picked.append(post)
        if len(picked) >= limit:
            break

    return picked


def get_similar_posts(
    post: Post,
    user: AbstractBaseUser | AnonymousUser | None,
    *,
    limit: int = DEFAULT_SIMILAR_LIMIT,
) -> list[Post]:
    """Возвращает похожие публикации той же тематики (бесплатные первыми).

    Args:
        post: Текущая публикация.
        user: Текущий пользователь или гость.
        limit: Максимальное число публикаций.

    Returns:
        Список Post той же темы, без текущей.
    """
    queryset = (
        Post.objects.filter(topic=post.topic)
        .exclude(pk=post.pk)
        .select_related("author")
        .annotate(
            paid_rank=Case(
                When(is_paid=True, then=Value(1)),
                default=Value(0),
                output_field=IntegerField(),
            ),
            has_video_rank=Case(
                When(video_url="", then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            ),
        )
        .order_by("paid_rank", "-has_video_rank", "-created_at")
    )
    if user is not None and user.is_authenticated:
        queryset = queryset.exclude(author=user)
    return list(queryset[:limit])
