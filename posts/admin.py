"""Django admin для posts."""

from django.contrib import admin

from posts.forms import PostAdminForm
from posts.models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Админка публикаций с кастомной формой."""

    form = PostAdminForm
    list_display = ("title", "is_paid", "author", "created_at")
    list_filter = ("is_paid", "created_at")
    search_fields = ("title", "body", "author__phone")
    raw_id_fields = ("author",)
    readonly_fields = ("created_at", "updated_at")
