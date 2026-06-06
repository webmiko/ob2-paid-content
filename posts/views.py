"""API-представления posts."""

from django.db.models import QuerySet
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from rest_framework.serializers import BaseSerializer

from posts.models import Post
from posts.permissions import IsAuthorOrReadOnly
from posts.serializers import PostSerializer, PostWriteSerializer
from users.services.access import user_has_active_subscription


class PostViewSet(viewsets.ModelViewSet):
    """CRUD публикаций с paywall на body."""

    queryset = Post.objects.select_related("author").all()
    permission_classes = (IsAuthorOrReadOnly,)

    def get_permissions(self) -> list[BasePermission]:
        """Определяет права доступа по типу операции.

        Returns:
            Чтение — для всех; создание, изменение и удаление — только для автора.
        """
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAuthenticated(), IsAuthorOrReadOnly()]

    def get_serializer_class(self) -> type[PostSerializer | PostWriteSerializer]:
        """Выбирает сериализатор для чтения или записи.

        Returns:
            Сериализатор записи при create/update; иначе — для чтения.
        """
        if self.action in ("create", "update", "partial_update"):
            return PostWriteSerializer
        return PostSerializer

    def get_queryset(self) -> QuerySet[Post]:
        """Ограничивает изменение и удаление публикациями текущего автора.

        Returns:
            Все публикации для списка и просмотра; только свои — для изменения и удаления.
        """
        queryset = super().get_queryset()
        if self.action in ("update", "partial_update", "destroy"):
            return queryset.filter(author=self.request.user)
        return queryset

    def perform_create(self, serializer: BaseSerializer) -> None:
        """Сохраняет публикацию с автором из request.user.

        Args:
            serializer: Валидированные данные новой публикации.
        """
        serializer.save(author=self.request.user)

    def get_serializer_context(self) -> dict:
        """Добавляет кэш флага подписки для list/retrieve без N+1."""
        context = super().get_serializer_context()
        request = self.request
        user = request.user
        if user.is_authenticated:
            context["user_has_active_subscription"] = user_has_active_subscription(user)
        else:
            context["user_has_active_subscription"] = False
        return context
