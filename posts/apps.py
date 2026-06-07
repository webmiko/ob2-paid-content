"""Конфигурация приложения posts."""

from django.apps import AppConfig


class PostsConfig(AppConfig):
    """Публикации free/paid."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "posts"
    verbose_name = "Публикации"

    def ready(self) -> None:
        """Подключает сигналы приложения."""
        import posts.signals  # noqa: F401, PLC0415
