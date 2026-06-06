"""Модели приложения users."""

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from users.managers import UserManager

PHONE_MAX_LENGTH = 20


class PaymentStatus(models.TextChoices):
    """Статусы платежа Stripe Checkout."""

    PENDING = "pending", "Ожидает оплаты"
    PAID = "paid", "Оплачен"
    FAILED = "failed", "Ошибка"
    CANCELLED = "cancelled", "Отменён"


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


class Payment(models.Model):
    """Платёж за разовую подписку через Stripe Checkout."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Пользователь",
    )
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        verbose_name="Статус",
    )
    amount = models.PositiveIntegerField(verbose_name="Сумма")
    currency = models.CharField(max_length=3, verbose_name="Валюта")
    stripe_session_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Stripe session ID",
    )
    payment_url = models.URLField(max_length=500, blank=True, verbose_name="URL оплаты")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлён")

    class Meta:
        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"Payment #{self.pk} ({self.status})"


class Subscription(models.Model):
    """Разовая подписка пользователя на платный контент."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subscription",
        verbose_name="Пользователь",
    )
    is_active = models.BooleanField(default=False, verbose_name="Активна")
    activated_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата активации")
    payment = models.OneToOneField(
        Payment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subscription",
        verbose_name="Платёж",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"

    def __str__(self) -> str:
        state = "active" if self.is_active else "inactive"
        return f"Subscription {self.user_id} ({state})"
