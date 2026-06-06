"""Модели приложения posts."""

from django.conf import settings
from django.db import models

from posts.choices import PostTopic


class Post(models.Model):
    """Публикация на платформе (бесплатная или платная)."""

    title = models.CharField(max_length=200, verbose_name="Заголовок")
    body = models.TextField(verbose_name="Текст")
    is_paid = models.BooleanField(default=False, verbose_name="Платная")
    topic = models.CharField(
        max_length=32,
        choices=PostTopic.choices,
        default=PostTopic.OTHER,
        verbose_name="Тематика",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Автор",
    )
    video_url = models.URLField(
        max_length=500,
        blank=True,
        default="",
        verbose_name="Ссылка на видео",
        help_text="YouTube, Vimeo, Rutube, VK Video или Дзен — показывается при доступе к публикации.",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        verbose_name = "Публикация"
        verbose_name_plural = "Публикации"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.title


class Comment(models.Model):
    """Комментарий к публикации."""

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Публикация",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="post_comments",
        verbose_name="Автор комментария",
    )
    text = models.TextField(max_length=2000, verbose_name="Текст")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создан")

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ("created_at",)

    def __str__(self) -> str:
        return f"Comment #{self.pk} on post {self.post_id}"
