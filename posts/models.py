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
    view_count = models.PositiveIntegerField(default=0, verbose_name="Просмотры")
    meta_title = models.CharField(
        max_length=70,
        blank=True,
        default="",
        verbose_name="SEO заголовок",
        help_text="Заполняется автоматически при сохранении.",
    )
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        default="",
        verbose_name="SEO описание",
        help_text="Meta description для поисковиков и Open Graph.",
    )
    meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="SEO ключевые слова",
        help_text="Keywords через запятую; генерируются автоматически.",
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


class PostView(models.Model):
    """Уникальный просмотр публикации (авторизованный или гость по IP)."""

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="views",
        verbose_name="Публикация",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="post_views",
        verbose_name="Читатель",
    )
    ip_hash = models.CharField(max_length=64, blank=True, default="", verbose_name="Хеш IP")
    viewed_at = models.DateTimeField(auto_now_add=True, verbose_name="Когда")

    class Meta:
        verbose_name = "Просмотр публикации"
        verbose_name_plural = "Просмотры публикаций"
        ordering = ("-viewed_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("post", "user"),
                condition=models.Q(user__isnull=False),
                name="unique_post_view_user",
            ),
            models.UniqueConstraint(
                fields=("post", "ip_hash"),
                condition=models.Q(user__isnull=True) & ~models.Q(ip_hash=""),
                name="unique_post_view_ip",
            ),
        ]
        indexes = [
            models.Index(fields=("post", "-viewed_at")),
        ]

    def __str__(self) -> str:
        reader = self.user_id or "guest"
        return f"View post {self.post_id} by {reader}"
