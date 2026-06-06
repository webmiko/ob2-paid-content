"""Менеджеры моделей приложения users."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.contrib.auth.base_user import BaseUserManager

from users.validators import normalize_phone

if TYPE_CHECKING:
    from users.models import User
else:
    User = Any  # noqa: UP037 — циклический импорт для mypy


class UserManager(BaseUserManager["User"]):
    """Менеджер пользователей с авторизацией по телефону."""

    use_in_migrations = True

    def _create_user(self, phone: str, password: str | None, **extra_fields: object) -> User:
        """Создаёт и сохраняет пользователя с указанным телефоном и паролем.

        Args:
            phone: Номер телефона (будет нормализован).
            password: Пароль (будет хеширован через set_password).
            **extra_fields: Дополнительные поля модели.

        Returns:
            Созданный экземпляр пользователя.

        Raises:
            ValueError: Если телефон не указан.
        """
        if not phone:
            raise ValueError("Телефон обязателен для создания пользователя")
        normalized_phone = normalize_phone(phone)
        user: User = self.model(phone=normalized_phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone: str, password: str | None = None, **extra_fields: object) -> User:
        """Создаёт обычного пользователя.

        Args:
            phone: Номер телефона нового пользователя.
            password: Пароль (будет хеширован).
            **extra_fields: Дополнительные поля модели.

        Returns:
            Созданный экземпляр пользователя.
        """
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(phone, password, **extra_fields)

    def create_superuser(self, phone: str, password: str | None = None, **extra_fields: object) -> User:
        """Создаёт суперпользователя с полными правами.

        Args:
            phone: Номер телефона суперпользователя.
            password: Пароль (будет хеширован).
            **extra_fields: Дополнительные поля модели.

        Returns:
            Созданный экземпляр суперпользователя.

        Raises:
            ValueError: Если is_staff или is_superuser не равны True.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True")
        return self._create_user(phone, password, **extra_fields)
