"""Фильтрация queryset публикаций для списка API."""

from django.contrib.auth.models import AbstractBaseUser, AnonymousUser
from django.db.models import Q, QuerySet
from rest_framework.request import Request

from posts.models import Post


def build_post_search_filter(
    search: str,
    user: AbstractBaseUser | AnonymousUser,
    *,
    user_has_active_subscription: bool,
) -> Q:
    """Строит Q для поиска без oracle по body платных постов.

    Заголовок ищется всегда; body — только там, где у пользователя есть доступ
    к содержимому (как в can_view_post_body).
    """
    title_q = Q(title__icontains=search)
    if user_has_active_subscription:
        return title_q | Q(body__icontains=search)
    if user.is_authenticated:
        body_q = Q(body__icontains=search) & (Q(is_paid=False) | Q(author_id=user.pk))
    else:
        body_q = Q(body__icontains=search) & Q(is_paid=False)
    return title_q | body_q


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
    user = request.user

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
        search_q = build_post_search_filter(
            search,
            user,
            user_has_active_subscription=user_has_active_subscription,
        )
        queryset = queryset.filter(search_q)

    access = params.get("access")
    if access == "available":
        if user.is_authenticated:
            if not user_has_active_subscription:
                queryset = queryset.filter(Q(is_paid=False) | Q(author=user))
        else:
            queryset = queryset.filter(is_paid=False)

    return queryset
