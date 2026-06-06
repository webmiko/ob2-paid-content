"""API-представления приложения users."""

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers import RegisterSerializer, UserProfileSerializer, UserPublicSerializer


class UserMeView(APIView):
    """Профиль текущего авторизованного пользователя."""

    permission_classes = (IsAuthenticated,)

    def get(self, request: Request) -> Response:
        """Возвращает профиль текущего пользователя.

        Args:
            request: HTTP-запрос авторизованного пользователя.

        Returns:
            Response с id, phone и subscription_active.
        """
        return Response(UserProfileSerializer(request.user).data)


class RegisterView(APIView):
    """Регистрация нового пользователя по телефону и паролю."""

    permission_classes = (AllowAny,)

    def post(self, request: Request) -> Response:
        """Регистрирует пользователя по телефону.

        Args:
            request: HTTP-запрос с JSON {phone, password}.

        Returns:
            Response 201 с id и phone без password.

        Raises:
            serializers.ValidationError: Ошибки валидации (ответ 400).
        """
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserPublicSerializer(user).data, status=status.HTTP_201_CREATED)
