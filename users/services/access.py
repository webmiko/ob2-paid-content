"""Проверки доступа пользователя (подписка, права)."""

from typing import cast

from django.contrib.auth.models import AbstractBaseUser, AnonymousUser

from users.models import Subscription, User


def user_has_active_subscription(user: AbstractBaseUser | AnonymousUser | None) -> bool:
    """Проверяет, есть ли у пользователя активная подписка.

    Args:
        user: Текущий пользователь или None/AnonymousUser.

    Returns:
        True, если у пользователя активная Subscription.
    """
    if user is None or user.is_anonymous:
        return False
    auth_user = cast(User, user)
    return Subscription.objects.filter(user=auth_user, is_active=True).exists()
