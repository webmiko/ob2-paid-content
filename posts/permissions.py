"""DRF permissions для posts."""

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from posts.models import Post


class IsAuthorOrReadOnly(BasePermission):
    """Изменение и удаление — только автор; чтение доступно всем."""

    def has_object_permission(self, request: Request, view: APIView, obj: Post) -> bool:
        """Разрешает mutate только автору публикации."""
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return bool(request.user and request.user.is_authenticated and obj.author_id == request.user.pk)
