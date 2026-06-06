"""Django admin для posts."""

from django.contrib import admin

from posts.forms import PostAdminForm
from posts.models import Comment, Post


class CommentInline(admin.TabularInline):
    """Комментарии в карточке публикации."""

    model = Comment
    extra = 0
    raw_id_fields = ("author",)
    readonly_fields = ("created_at",)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Админка публикаций с кастомной формой."""

    form = PostAdminForm
    inlines = (CommentInline,)
    list_display = ("title", "is_paid", "topic", "author", "created_at")
    list_filter = ("is_paid", "topic", "created_at")
    search_fields = ("title", "body", "author__phone")
    raw_id_fields = ("author",)
    readonly_fields = ("created_at", "updated_at")
