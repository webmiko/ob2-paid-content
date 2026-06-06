"""API списков авторов и тематик."""

from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from posts.meta_serializers import AuthorListSerializer, TopicListSerializer
from posts.models import Post

User = get_user_model()


class AuthorListView(APIView):
    """Публичный список авторов, у которых есть публикации."""

    permission_classes = (AllowAny,)

    def get(self, request: Request) -> Response:
        """Возвращает авторов с количеством бесплатных и платных публикаций.

        Args:
            request: HTTP-запрос (без обязательных параметров).

        Returns:
            Response со списком авторов, отсортированных по числу публикаций.
        """
        search = request.query_params.get("search", "").strip()
        queryset = (
            User.objects.filter(posts__isnull=False)
            .annotate(
                post_count=Count("posts", distinct=True),
                paid_count=Count("posts", filter=Q(posts__is_paid=True), distinct=True),
                free_count=Count("posts", filter=Q(posts__is_paid=False), distinct=True),
            )
            .distinct()
        )
        if search:
            queryset = queryset.filter(
                Q(display_name__icontains=search) | Q(phone__icontains=search),
            )
        authors = queryset.order_by("-post_count", "id")
        serializer = AuthorListSerializer(authors, many=True)
        return Response(serializer.data)


class AuthorDetailView(APIView):
    """Публичная карточка автора."""

    permission_classes = (AllowAny,)

    def get(self, request: Request, author_id: int) -> Response:
        """Возвращает метаданные автора по id.

        Args:
            request: HTTP-запрос.
            author_id: PK пользователя-автора.

        Returns:
            Response с label и счётчиками публикаций.
        """
        author = get_object_or_404(
            User.objects.annotate(
                post_count=Count("posts", distinct=True),
                paid_count=Count("posts", filter=Q(posts__is_paid=True), distinct=True),
                free_count=Count("posts", filter=Q(posts__is_paid=False), distinct=True),
            ).filter(posts__isnull=False),
            pk=author_id,
        )
        serializer = AuthorListSerializer(author)
        return Response(serializer.data)


class TopicListView(APIView):
    """Список тематик с количеством публикаций."""

    permission_classes = (AllowAny,)

    def get(self, request: Request) -> Response:
        """Возвращает все тематики платформы и число публикаций в каждой.

        Args:
            request: HTTP-запрос.

        Returns:
            Response со списком тем; пустые темы включены с post_count=0.
        """
        counts = {
            row["topic"]: row["post_count"]
            for row in Post.objects.values("topic").annotate(post_count=Count("id"))
        }
        payload = TopicListSerializer.from_counts(counts)
        serializer = TopicListSerializer(payload, many=True)
        return Response(serializer.data)
