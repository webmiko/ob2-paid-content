"""Проверки прав доступа к публикациям."""

from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

from posts.models import Post


class IsAuthorOrReadOnly(BasePermission):
    """Изменение и удаление — только автор; чтение доступно всем."""

    def has_object_permission(self, request: Request, view: APIView, obj: Post) -> bool:
        """Проверяет право изменения объекта.

        Args:
            request: HTTP-запрос.
            view: Представление, обрабатывающее запрос.
            obj: Публикация.

        Returns:
            True для GET, HEAD и OPTIONS; для остальных методов — только если пользователь автор поста.
        """
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return bool(request.user and request.user.is_authenticated and obj.author_id == request.user.pk)
