"""API-представления приложения users."""

from typing import cast

from django.contrib.auth.models import AbstractBaseUser
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from config.throttling import AccountDeleteThrottle, AuthRateThrottle
from users.serializers import (
    PhoneSendCodeSerializer,
    RegisterSerializer,
    UserDeleteAccountSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    UserPublicSerializer,
)
from users.services.sms_verification import send_verification_code
from users.services.tokens import blacklist_user_tokens


class UserMeView(APIView):
    """Профиль текущего авторизованного пользователя."""

    permission_classes = (IsAuthenticated,)

    def get_throttles(self) -> list:
        """Throttling только для удаления аккаунта."""
        if self.request.method == "DELETE":
            return [AccountDeleteThrottle()]
        return []

    def get(self, request: Request) -> Response:
        """Возвращает профиль текущего пользователя.

        Args:
            request: HTTP-запрос авторизованного пользователя.

        Returns:
            Response с id, phone и subscription_active.
        """
        return Response(UserProfileSerializer(request.user).data)

    def patch(self, request: Request) -> Response:
        """Обновляет публичное имя автора.

        Args:
            request: HTTP-запрос с JSON {display_name}.

        Returns:
            Response с обновлённым профилем.
        """
        serializer = UserProfileUpdateSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserProfileSerializer(request.user).data)

    def delete(self, request: Request) -> Response:
        """Удаляет аккаунт текущего пользователя после подтверждения пароля.

        Args:
            request: HTTP-DELETE с JSON {password, confirm: true}.

        Returns:
            Response 204 без тела.
        """
        serializer = UserDeleteAccountSerializer(
            data=request.data,
            context={"user": request.user},
        )
        serializer.is_valid(raise_exception=True)
        user = cast(AbstractBaseUser, request.user)
        refresh = serializer.validated_data.get("refresh") or None
        blacklist_user_tokens(user, refresh=refresh)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PhoneSendCodeView(APIView):
    """Имитация отправки SMS-кода для подтверждения номера при регистрации."""

    permission_classes = (AllowAny,)
    throttle_classes = (AuthRateThrottle,)

    def post(self, request: Request) -> Response:
        serializer = PhoneSendCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = str(serializer.validated_data["phone"])
        simulation_code, detail = send_verification_code(phone)
        payload: dict[str, str] = {"detail": detail}
        if simulation_code:
            payload["simulation_code"] = simulation_code
        return Response(payload, status=status.HTTP_200_OK)


class RegisterView(APIView):
    """Регистрация нового пользователя по телефону и паролю."""

    permission_classes = (AllowAny,)
    throttle_classes = (AuthRateThrottle,)

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
