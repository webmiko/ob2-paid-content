"""Модели приложения posts."""

from django.conf import settings
from django.db import models


class Post(models.Model):
    """Публикация на платформе (бесплатная или платная)."""

    title = models.CharField(max_length=200, verbose_name="Заголовок")
    body = models.TextField(verbose_name="Текст")
    is_paid = models.BooleanField(default=False, verbose_name="Платная")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Автор",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Публикация"
        verbose_name_plural = "Публикации"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.title
