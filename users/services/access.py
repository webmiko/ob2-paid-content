"""Проверки доступа пользователя (подписка, права)."""

from django.contrib.auth.models import AbstractBaseUser, AnonymousUser


def user_has_active_subscription(user: AbstractBaseUser | AnonymousUser | None) -> bool:
    """Проверяет, есть ли у пользователя активная подписка.

    Заглушка до итерации 4 (модели Subscription/Payment).

    Args:
        user: Текущий пользователь или None/AnonymousUser.

    Returns:
        False до реализации Stripe-подписки.
    """
    if user is None or user.is_anonymous:
        return False
    return False
