"""Management-команда: пересчёт SEO для всех публикаций."""

from django.core.management.base import BaseCommand

from posts.models import Post
from posts.services.seo import sync_post_seo


class Command(BaseCommand):
    """Прописывает meta title, description и keywords для существующих постов."""

    help = "Пересчитывает SEO-метаданные всех публикаций (meta title, description, keywords)."

    def handle(self, *args, **options) -> None:
        updated = 0
        total = 0
        for post in Post.objects.select_related("author").iterator():
            total += 1
            if sync_post_seo(post):
                updated += 1
        self.stdout.write(
            self.style.SUCCESS(f"SEO обновлено: {updated} из {total} публикаций."),
        )
