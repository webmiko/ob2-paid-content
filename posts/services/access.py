"""Проверки доступа к публикациям."""

from django.contrib.auth.models import AbstractBaseUser, AnonymousUser

from posts.models import Post
from users.services.access import user_has_active_subscription


def can_view_post_body(
    user: AbstractBaseUser | AnonymousUser | None,
    post: Post,
    *,
    subscription_active: bool | None = None,
) -> bool:
    """Определяет, может ли пользователь видеть body публикации.

    Args:
        user: Текущий пользователь; guest — AnonymousUser или None.
        post: Публикация.
        subscription_active: Кэш флага подписки (один запрос на list).

    Returns:
        True для бесплатных постов, для автора своего paid-поста
        или для пользователя с активной подпиской на paid-посты.
    """
    if not post.is_paid:
        return True
    if user is None or user.is_anonymous:
        return False
    if post.author_id == user.pk:
        return True
    if subscription_active is not None:
        return subscription_active
    return user_has_active_subscription(user)
