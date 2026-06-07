"""API комментариев, рекомендаций и похожих публикаций."""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from config.constants import MAX_RECOMMENDED_EXCLUDE_IDS
from config.throttling import CommentCreateThrottle, CommentDeleteThrottle
from posts.comment_serializers import CommentSerializer, CommentWriteSerializer
from posts.models import Comment, Post
from posts.serializers import PostSerializer
from posts.services.access import can_view_post_body
from posts.services.comments import can_delete_comment
from posts.services.recommendations import get_recommended_posts, get_similar_posts
from users.services.access import user_has_active_subscription

COMMENTS_PAGE_SIZE = 20


class CommentPagination(PageNumberPagination):
    """Пагинация комментариев к публикации."""

    page_size = COMMENTS_PAGE_SIZE
    page_size_query_param = "page_size"
    max_page_size = 50


def _parse_exclude_ids(raw: str, *, limit: int = MAX_RECOMMENDED_EXCLUDE_IDS) -> list[int]:
    """Разбирает query exclude=1,2,3 в список ID (не больше limit)."""
    result: list[int] = []
    for part in raw.split(","):
        if len(result) >= limit:
            break
        cleaned = part.strip()
        if cleaned.isdigit():
            result.append(int(cleaned))
    return result


def _post_serializer_context(request: Request) -> dict:
    """Контекст PostSerializer с флагом подписки."""
    subscription_active = False
    if request.user.is_authenticated:
        subscription_active = user_has_active_subscription(request.user)
    return {
        "request": request,
        "user_has_active_subscription": subscription_active,
    }


class RecommendedPostsView(APIView):
    """Бесплатные публикации для блока «Рекомендуем» в каталоге."""

    permission_classes = (AllowAny,)

    def get(self, request: Request) -> Response:
        """Возвращает подборку бесплатных публикаций разных тематик."""
        exclude_ids = _parse_exclude_ids(request.query_params.get("exclude", ""))
        posts = get_recommended_posts(request.user, exclude_ids=exclude_ids or None)
        serializer = PostSerializer(
            posts,
            many=True,
            context=_post_serializer_context(request),
        )
        return Response(serializer.data)


class SimilarPostsView(APIView):
    """Похожие публикации той же тематики."""

    permission_classes = (AllowAny,)

    def get(self, request: Request, post_id: int) -> Response:
        """Возвращает похожие публикации для страницы поста."""
        post = get_object_or_404(Post.objects.select_related("author"), pk=post_id)
        posts = get_similar_posts(post, request.user)
        serializer = PostSerializer(
            posts,
            many=True,
            context=_post_serializer_context(request),
        )
        return Response(serializer.data)


class PostCommentListCreateView(APIView):
    """Список и создание комментариев к публикации."""

    pagination_class = CommentPagination

    def get_permissions(self) -> list:
        """POST только для авторизованных; GET — для всех с доступом к посту."""
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_throttles(self) -> list:
        """Throttling на создание комментариев."""
        if self.request.method == "POST":
            return [CommentCreateThrottle()]
        return []

    def get(self, request: Request, post_id: int) -> Response:
        """Возвращает страницу комментариев при доступе к публикации."""
        post = get_object_or_404(Post.objects.select_related("author"), pk=post_id)
        if not self._can_access_post(request, post):
            return Response(
                {"detail": "Комментарии доступны после получения доступа к публикации."},
                status=status.HTTP_403_FORBIDDEN,
            )
        comments = Comment.objects.filter(post=post).select_related("author").order_by("created_at")
        paginator = self.pagination_class()
        page = paginator.paginate_queryset(comments, request, view=self)
        serializer = CommentSerializer(
            page,
            many=True,
            context={"request": request, "post": post},
        )
        return paginator.get_paginated_response(serializer.data)

    def post(self, request: Request, post_id: int) -> Response:
        """Создаёт комментарий от текущего пользователя."""
        post = get_object_or_404(Post.objects.select_related("author"), pk=post_id)
        if not self._can_access_post(request, post):
            return Response(
                {"detail": "Нельзя комментировать публикацию без доступа к содержимому."},
                status=status.HTTP_403_FORBIDDEN,
            )
        write_serializer = CommentWriteSerializer(data=request.data)
        write_serializer.is_valid(raise_exception=True)
        comment = Comment.objects.create(
            post=post,
            author=request.user,
            text=write_serializer.validated_data["text"],
        )
        return Response(
            CommentSerializer(comment, context={"request": request, "post": post}).data,
            status=status.HTTP_201_CREATED,
        )

    def _can_access_post(self, request: Request, post: Post) -> bool:
        """Проверяет право читать/комментировать публикацию."""
        subscription_active = False
        if request.user.is_authenticated:
            subscription_active = user_has_active_subscription(request.user)
        return can_view_post_body(
            request.user,
            post,
            subscription_active=subscription_active,
        )


class PostCommentDetailView(APIView):
    """Удаление комментария."""

    permission_classes = (IsAuthenticated,)
    throttle_classes = (CommentDeleteThrottle,)

    def delete(self, request: Request, post_id: int, comment_id: int) -> Response:
        """Удаляет комментарий автором, автором поста или staff."""
        post = get_object_or_404(Post.objects.select_related("author"), pk=post_id)
        comment = get_object_or_404(Comment, pk=comment_id, post=post)
        if not can_view_post_body(
            request.user,
            post,
            subscription_active=user_has_active_subscription(request.user)
            if request.user.is_authenticated
            else False,
        ):
            return Response(
                {"detail": "Нет доступа к комментариям этой публикации."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if not can_delete_comment(request.user, comment, post):
            return Response(
                {"detail": "Нельзя удалить этот комментарий."},
                status=status.HTTP_403_FORBIDDEN,
            )
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
