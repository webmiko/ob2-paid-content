"""API записи просмотра публикации."""

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from config.throttling import ViewRecordThrottle
from posts.models import Post
from posts.services.view_tracking import record_post_view


class PostRecordViewView(APIView):
    """Фиксирует уникальный просмотр публикации."""

    permission_classes = (AllowAny,)
    throttle_classes = (ViewRecordThrottle,)

    def post(self, request: Request, post_id: int) -> Response:
        """Записывает просмотр, если читатель ещё не учитывался."""
        post = get_object_or_404(Post.objects.select_related("author"), pk=post_id)
        created = record_post_view(post, request)
        return Response({"recorded": created}, status=status.HTTP_200_OK)
