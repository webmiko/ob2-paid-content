"""Фильтрация queryset публикаций для списка API."""

from django.db.models import Q, QuerySet
from rest_framework.request import Request

from posts.models import Post


def filter_posts_list_queryset(
    queryset: QuerySet[Post],
    request: Request,
    *,
    user_has_active_subscription: bool,
) -> QuerySet[Post]:
    """Применяет query-параметры к списку публикаций.

    Args:
        queryset: Базовый queryset публикаций.
        request: HTTP-запрос с query-параметрами.
        user_has_active_subscription: Кэш активной подписки текущего пользователя.

    Returns:
        Отфильтрованный queryset без изменения порядка по умолчанию.
    """
    params = request.query_params

    is_paid = params.get("is_paid")
    if is_paid in ("true", "false"):
        queryset = queryset.filter(is_paid=(is_paid == "true"))

    author = params.get("author")
    if author and author.isdigit():
        queryset = queryset.filter(author_id=int(author))

    topic = params.get("topic")
    if topic:
        queryset = queryset.filter(topic=topic)

    search = params.get("search", "").strip()
    if search:
        queryset = queryset.filter(Q(title__icontains=search) | Q(body__icontains=search))

    access = params.get("access")
    if access == "available":
        user = request.user
        if user.is_authenticated:
            if not user_has_active_subscription:
                queryset = queryset.filter(Q(is_paid=False) | Q(author=user))
        else:
            queryset = queryset.filter(is_paid=False)

    return queryset
