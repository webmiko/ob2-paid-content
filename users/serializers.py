"""Сериализаторы пользователей для REST API."""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import User
from users.services.access import user_has_active_subscription
from users.validators import normalize_phone


class UserPublicSerializer(serializers.ModelSerializer):
    """Публичное представление пользователя без пароля."""

    class Meta:
        model = User
        fields = ("id", "phone", "display_name")


class UserProfileSerializer(serializers.ModelSerializer):
    """Профиль авторизованного пользователя."""

    subscription_active = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "phone", "display_name", "subscription_active")

    def get_subscription_active(self, obj: User) -> bool:
        """Возвращает флаг активной подписки пользователя.

        Args:
            obj: Пользователь из контекста serializer.

        Returns:
            True, если у пользователя есть активная подписка.
        """
        return user_has_active_subscription(obj)


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Обновление никнейма пользователя."""

    class Meta:
        model = User
        fields = ("display_name",)

    def validate_display_name(self, value: str) -> str:
        """Проверяет длину и формат никнейма."""
        nickname = value.strip()[:80]
        if len(nickname) < 2:
            raise serializers.ValidationError("Никнейм должен быть не короче 2 символов.")
        return nickname


class RegisterSerializer(serializers.ModelSerializer):
    """Регистрация пользователя по телефону, никнейму и паролю."""

    password = serializers.CharField(write_only=True, min_length=8, style={"input_type": "password"})
    display_name = serializers.CharField(max_length=80)

    class Meta:
        model = User
        fields = ("phone", "display_name", "password")

    def validate_display_name(self, value: str) -> str:
        """Проверяет никнейм при регистрации."""
        nickname = value.strip()[:80]
        if len(nickname) < 2:
            raise serializers.ValidationError("Никнейм должен быть не короче 2 символов.")
        return nickname

    def validate_phone(self, value: str) -> str:
        """Нормализует телефон и проверяет уникальность.

        Args:
            value: Введённый номер телефона.

        Returns:
            Нормализованная строка для сохранения в User.phone.

        Raises:
            serializers.ValidationError: Некорректный формат или занятый номер.
        """
        try:
            normalized = normalize_phone(value)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc
        if User.objects.filter(phone=normalized).exists():
            raise serializers.ValidationError("Не удалось зарегистрироваться. Проверьте данные.")
        return normalized

    def create(self, validated_data: dict[str, object]) -> User:
        """Создаёт пользователя с хешированным паролем.

        Args:
            validated_data: Поля phone и password после validate_phone.

        Returns:
            Новый User; пароль сохраняется только в виде хеша.
        """
        password = validated_data.pop("password")
        phone = validated_data.pop("phone")
        return User.objects.create_user(phone=str(phone), password=str(password), **validated_data)


class PhoneTokenObtainPairSerializer(TokenObtainPairSerializer):
    """JWT: вход по полю phone вместо username."""

    def validate(self, attrs: dict[str, object]) -> dict[str, str]:
        """Нормализует phone и выдаёт JWT-пару.

        Args:
            attrs: Поля phone и password из запроса.

        Returns:
            Словарь с ключами access и refresh.

        Raises:
            serializers.ValidationError: Неверный телефон или пароль.
        """
        phone = attrs.get(self.username_field)
        if isinstance(phone, str):
            try:
                attrs[self.username_field] = normalize_phone(phone)
            except ValueError as exc:
                raise serializers.ValidationError({self.username_field: str(exc)}) from exc
        return super().validate(attrs)
