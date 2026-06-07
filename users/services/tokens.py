"""Инвалидация JWT при выходе и удалении аккаунта."""

from django.contrib.auth.models import AbstractBaseUser
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken


def blacklist_user_tokens(user: AbstractBaseUser, *, refresh: str | None = None) -> None:
    """Добавляет refresh-токены пользователя в blacklist.

    Args:
        user: Пользователь, чьи сессии нужно завершить.
        refresh: Текущий refresh из тела запроса (logout/delete), если есть.
    """
    if refresh:
        try:
            RefreshToken(refresh).blacklist()
        except TokenError:
            pass

    for outstanding in OutstandingToken.objects.filter(user_id=user.pk):
        BlacklistedToken.objects.get_or_create(token=outstanding)
