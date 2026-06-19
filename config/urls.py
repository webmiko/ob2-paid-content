"""URL-маршруты проекта."""

from django.conf import settings
from django.contrib import admin
from django.db import connection
from django.http import HttpRequest, JsonResponse
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenBlacklistView, TokenObtainPairView, TokenRefreshView

from config.cache import cache_backend_label
from config.throttling import AuthRateThrottle
from posts.seo_views import llms_txt_view, robots_txt_view, sitemap_xml_view
from users.payment_views import payment_success_page
from users.serializers import PhoneTokenObtainPairSerializer


def health_view(_request: HttpRequest) -> JsonResponse:
    """Проверяет доступность backend-сервиса, БД и тип общего кэша."""
    try:
        connection.ensure_connection()
    except Exception:
        return JsonResponse({"status": "error", "database": "unavailable"}, status=503)
    return JsonResponse(
        {
            "status": "ok",
            "cache": cache_backend_label(settings.CACHES),
        },
    )


class PhoneTokenObtainPairView(TokenObtainPairView):
    """Выдача пары access/refresh по телефону и паролю."""

    permission_classes = [AllowAny]  # type: ignore[assignment]
    serializer_class = PhoneTokenObtainPairSerializer
    throttle_classes = (AuthRateThrottle,)


class PhoneTokenRefreshView(TokenRefreshView):
    """Обновление access-токена по refresh-токену."""

    permission_classes = [AllowAny]  # type: ignore[assignment]
    throttle_classes = (AuthRateThrottle,)


class PhoneTokenBlacklistView(TokenBlacklistView):
    """Инвалидация refresh-токена при выходе."""

    permission_classes = [AllowAny]  # type: ignore[assignment]
    throttle_classes = (AuthRateThrottle,)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("robots.txt", robots_txt_view, name="robots-txt"),
    path("llms.txt", llms_txt_view, name="llms-txt"),
    path("sitemap.xml", sitemap_xml_view, name="sitemap-xml"),
    path("payments/success/", payment_success_page, name="payment-success-page"),
    path("api/health/", health_view, name="health"),
    path("api/token/", PhoneTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", PhoneTokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/logout/", PhoneTokenBlacklistView.as_view(), name="token_logout"),
    path("api/users/", include("users.urls")),
    path("api/posts/", include("posts.urls")),
    path("api/payments/", include("users.payment_urls")),
]

if settings.DEBUG:
    schema_view = get_schema_view(
        openapi.Info(
            title="OB2 Paid Content API",
            default_version="v1",
            description="API платформы платного контента",
        ),
        public=True,
        permission_classes=(AllowAny,),
    )
    urlpatterns += [
        path(
            "api/docs/",
            schema_view.with_ui("swagger", cache_timeout=0),
            name="schema-swagger-ui",
        ),
    ]
