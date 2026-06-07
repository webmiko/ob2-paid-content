"""API статистики автора."""

from typing import cast

from django.contrib.auth.models import AbstractBaseUser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from posts.services.analytics import get_author_dashboard_stats
from posts.stats_serializers import AuthorDashboardStatsSerializer


class AuthorStatsView(APIView):
    """Дашборд метрик текущего автора."""

    permission_classes = (IsAuthenticated,)

    def get(self, request: Request) -> Response:
        """Возвращает агрегаты просмотров, комментариев и публикаций."""
        stats = get_author_dashboard_stats(cast(AbstractBaseUser, request.user))
        serializer = AuthorDashboardStatsSerializer(stats)
        return Response(serializer.data)
