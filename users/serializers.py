"""Сериализаторы пользователей для REST API."""

from django.conf import settings
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from users.models import User
from users.phone_regions import SUPPORTED_COUNTRIES, PhoneCountry
from users.services.access import user_has_active_subscription
from users.services.sms_verification import (
    consume_phone_verification,
    is_phone_verified,
    verify_sms_code,
)
from users.validators import normalize_phone, validate_country


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


class UserDeleteAccountSerializer(serializers.Serializer):
    """Удаление аккаунта с подтверждением пароля."""

    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    confirm = serializers.BooleanField()
    refresh = serializers.CharField(required=False, write_only=True, allow_blank=True)

    def validate_confirm(self, value: bool) -> bool:
        """Требует явного подтверждения удаления."""
        if not value:
            raise serializers.ValidationError("Подтвердите, что понимаете последствия удаления.")
        return value

    def validate(self, attrs: dict[str, object]) -> dict[str, object]:
        """Проверяет пароль текущего пользователя."""
        user = self.context.get("user")
        password = attrs.get("password")
        if user is None or not isinstance(password, str):
            raise serializers.ValidationError("Не удалось проверить пароль.")
        if not user.check_password(password):
            raise serializers.ValidationError({"password": "Неверный пароль."})
        return attrs


class PhoneSendCodeSerializer(serializers.Serializer):
    """Запрос SMS-кода (имитация) для подтверждения номера."""

    phone = serializers.CharField(max_length=32)
    country = serializers.ChoiceField(choices=[(c, c) for c in SUPPORTED_COUNTRIES])

    def validate(self, attrs: dict[str, object]) -> dict[str, object]:
        phone_raw = attrs.get("phone")
        country_raw = attrs.get("country")
        if not isinstance(phone_raw, str) or not isinstance(country_raw, str):
            raise serializers.ValidationError("Укажите телефон и страну.")
        try:
            country = validate_country(country_raw)
            normalized = normalize_phone(phone_raw, country=country)
        except ValueError as exc:
            raise serializers.ValidationError({"phone": str(exc)}) from exc
        if User.objects.filter(phone=normalized).exists():
            raise serializers.ValidationError(
                {"phone": "Этот номер уже зарегистрирован."},
            )
        attrs["phone"] = normalized
        attrs["country"] = country
        return attrs


class RegisterSerializer(serializers.ModelSerializer):
    """Регистрация пользователя по телефону, никнейму и паролю."""

    password = serializers.CharField(write_only=True, min_length=8, style={"input_type": "password"})
    display_name = serializers.CharField(max_length=80)
    country = serializers.ChoiceField(
        choices=[(c, c) for c in SUPPORTED_COUNTRIES],
        required=False,
        write_only=True,
    )
    sms_code = serializers.CharField(
        max_length=6,
        min_length=4,
        required=False,
        write_only=True,
    )

    class Meta:
        model = User
        fields = ("phone", "display_name", "password", "country", "sms_code")

    def validate_display_name(self, value: str) -> str:
        """Проверяет никнейм при регистрации."""
        nickname = value.strip()[:80]
        if len(nickname) < 2:
            raise serializers.ValidationError("Никнейм должен быть не короче 2 символов.")
        return nickname

    def validate_phone(self, value: str) -> str:
        """Нормализует телефон и проверяет уникальность."""
        country_raw = self.initial_data.get("country")
        country: PhoneCountry | None = None
        if isinstance(country_raw, str) and country_raw.strip():
            try:
                country = validate_country(country_raw)
            except ValueError as exc:
                raise serializers.ValidationError(str(exc)) from exc
        try:
            normalized = normalize_phone(value, country=country)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc
        if User.objects.filter(phone=normalized).exists():
            raise serializers.ValidationError("Не удалось зарегистрироваться. Проверьте данные.")
        return normalized

    def validate(self, attrs: dict[str, object]) -> dict[str, object]:
        if not settings.SMS_VERIFICATION_REQUIRED:
            attrs.pop("country", None)
            attrs.pop("sms_code", None)
            return attrs
        sms_code = attrs.pop("sms_code", None)
        attrs.pop("country", None)
        phone = attrs.get("phone")
        if not isinstance(phone, str):
            raise serializers.ValidationError({"phone": "Некорректный телефон."})
        if not isinstance(sms_code, str) or not sms_code.strip():
            raise serializers.ValidationError(
                {"sms_code": "Введите код из SMS."},
            )
        if is_phone_verified(phone):
            return attrs
        if verify_sms_code(phone, sms_code):
            return attrs
        raise serializers.ValidationError({"sms_code": "Неверный или просроченный код."})

    def create(self, validated_data: dict[str, object]) -> User:
        """Создаёт пользователя с хешированным паролем.

        Args:
            validated_data: Поля phone и password после validate_phone.

        Returns:
            Новый User; пароль сохраняется только в виде хеша.
        """
        password = validated_data.pop("password")
        phone = validated_data.pop("phone")
        user = User.objects.create_user(phone=str(phone), password=str(password), **validated_data)
        if settings.SMS_VERIFICATION_REQUIRED:
            consume_phone_verification(str(phone))
        return user


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
