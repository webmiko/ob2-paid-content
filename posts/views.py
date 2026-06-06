"""API-представления posts."""

from django.db.models import QuerySet
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, BasePermission, IsAuthenticated
from rest_framework.serializers import BaseSerializer

from posts.models import Post
from posts.permissions import IsAuthorOrReadOnly
from posts.serializers import PostSerializer, PostWriteSerializer


class PostViewSet(viewsets.ModelViewSet):
    """CRUD публикаций с paywall на body."""

    queryset = Post.objects.select_related("author").all()
    permission_classes = (IsAuthorOrReadOnly,)

    def get_permissions(self) -> list[BasePermission]:
        """List/retrieve — публично; create/update/delete — только авторизованные."""
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAuthenticated(), IsAuthorOrReadOnly()]

    def get_serializer_class(self) -> type[PostSerializer | PostWriteSerializer]:
        """Write-действия используют PostWriteSerializer."""
        if self.action in ("create", "update", "partial_update"):
            return PostWriteSerializer
        return PostSerializer

    def get_queryset(self) -> QuerySet[Post]:
        """Mutate — только свои публикации (чужие → 404)."""
        queryset = super().get_queryset()
        if self.action in ("update", "partial_update", "destroy"):
            return queryset.filter(author=self.request.user)
        return queryset

    def perform_create(self, serializer: BaseSerializer) -> None:
        """Назначает текущего пользователя автором."""
        serializer.save(author=self.request.user)
