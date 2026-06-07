"""Сигналы posts: автоматическое SEO при сохранении публикации."""

from django.db.models.signals import post_save
from django.dispatch import receiver

from posts.models import Post
from posts.services.seo import sync_post_seo


@receiver(post_save, sender=Post)
def refresh_post_seo_on_save(sender: type[Post], instance: Post, **kwargs: object) -> None:
    """Пересчитывает meta-теги после создания или редактирования поста."""
    sync_post_seo(instance)
