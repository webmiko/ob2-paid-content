"""Модели приложения users."""

from django.contrib.auth.models import AbstractUser
from django.db import models

from users.managers import UserManager

PHONE_MAX_LENGTH = 20


class User(AbstractUser):
    """Пользователь платформы платного контента.

    Авторизация по номеру телефона (USERNAME_FIELD = phone).
    """

    username = None  # type: ignore[assignment]
    phone = models.CharField(max_length=PHONE_MAX_LENGTH, unique=True, verbose_name="Телефон")

    objects: UserManager = UserManager()  # type: ignore[misc, assignment]

    USERNAME_FIELD: str = "phone"  # type: ignore[misc]
    REQUIRED_FIELDS: list[str] = []  # type: ignore[misc]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self) -> str:
        return self.phone
