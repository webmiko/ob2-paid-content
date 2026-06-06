"""Сериализаторы DRF для users."""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import User
from users.validators import normalize_phone


class UserPublicSerializer(serializers.ModelSerializer):
    """Публичное представление пользователя без пароля."""

    class Meta:
        model = User
        fields = ("id", "phone")


class RegisterSerializer(serializers.ModelSerializer):
    """Регистрация пользователя по телефону и паролю."""

    password = serializers.CharField(write_only=True, min_length=8, style={"input_type": "password"})

    class Meta:
        model = User
        fields = ("phone", "password")

    def validate_phone(self, value: str) -> str:
        """Нормализует телефон и проверяет уникальность."""
        try:
            normalized = normalize_phone(value)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc
        if User.objects.filter(phone=normalized).exists():
            raise serializers.ValidationError("Пользователь с таким телефоном уже существует.")
        return normalized

    def create(self, validated_data: dict[str, object]) -> User:
        """Создаёт пользователя с хешированным паролем."""
        password = validated_data.pop("password")
        phone = validated_data.pop("phone")
        return User.objects.create_user(phone=str(phone), password=str(password), **validated_data)


class PhoneTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT: вход по полю phone вместо username."""

    def validate(self, attrs: dict[str, object]) -> dict[str, str]:
        """Нормализует phone перед аутентификацией."""
        phone = attrs.get(self.username_field)
        if isinstance(phone, str):
            try:
                attrs[self.username_field] = normalize_phone(phone)
            except ValueError as exc:
                raise serializers.ValidationError({self.username_field: str(exc)}) from exc
        return super().validate(attrs)
