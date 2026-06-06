"""API-представления приложения users."""

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers import RegisterSerializer, UserPublicSerializer


class RegisterView(APIView):
    """POST /api/users/register/ — регистрация по телефону."""

    permission_classes = (AllowAny,)

    def post(self, request: Request) -> Response:
        """Создаёт пользователя и возвращает id и phone без пароля."""
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserPublicSerializer(user).data, status=status.HTTP_201_CREATED)
