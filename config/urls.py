"""URL-маршруты проекта."""

from django.conf import settings
from django.contrib import admin
from django.http import HttpRequest, JsonResponse
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.payment_views import payment_success_page
from users.serializers import PhoneTokenObtainPairSerializer


def health_view(_request: HttpRequest) -> JsonResponse:
    """Проверяет доступность backend-сервиса.

    Returns:
        JsonResponse {"status": "ok"}.
    """
    return JsonResponse({"status": "ok"})


class PhoneTokenObtainPairView(TokenObtainPairView):
    """Выдача пары access/refresh по телефону и паролю."""

    permission_classes = [AllowAny]  # type: ignore[assignment]
    serializer_class = PhoneTokenObtainPairSerializer


class PhoneTokenRefreshView(TokenRefreshView):
    """Обновление access-токена по refresh-токену."""

    permission_classes = [AllowAny]  # type: ignore[assignment]


urlpatterns = [
    path("admin/", admin.site.urls),
    path("payments/success/", payment_success_page, name="payment-success-page"),
    path("api/health/", health_view, name="health"),
    path("api/token/", PhoneTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", PhoneTokenRefreshView.as_view(), name="token_refresh"),
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
