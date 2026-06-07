"""Валидаторы и нормализация данных пользователя."""

import re

from users.phone_regions import (
    BY_DIGITS_LENGTH,
    BY_PREFIX,
    RU_KZ_DIGITS_LENGTH,
    RU_KZ_PREFIX,
    PhoneCountry,
    SUPPORTED_COUNTRIES,
)

_DIGITS_RE = re.compile(r"\D")


def _digits_only(value: str) -> str:
    return _DIGITS_RE.sub("", value)


def _normalize_ru_kz(digits: str) -> str:
    if len(digits) == RU_KZ_DIGITS_LENGTH and digits[0] == "8":
        digits = RU_KZ_PREFIX + digits[1:]
    elif len(digits) == RU_KZ_DIGITS_LENGTH - 1:
        digits = RU_KZ_PREFIX + digits
    if len(digits) != RU_KZ_DIGITS_LENGTH or digits[0] != RU_KZ_PREFIX:
        raise ValueError(
            f"Номер должен содержать {RU_KZ_DIGITS_LENGTH} цифр в формате +7 …",
        )
    return digits


def _normalize_belarus(digits: str) -> str:
    if digits.startswith(BY_PREFIX) and len(digits) == BY_DIGITS_LENGTH:
        return digits
    if len(digits) == BY_DIGITS_LENGTH - len(BY_PREFIX):
        return BY_PREFIX + digits
    raise ValueError(
        f"Номер Беларуси должен содержать {BY_DIGITS_LENGTH} цифр в формате +375 …",
    )


def normalize_phone(value: str, country: PhoneCountry | None = None) -> str:
    """Приводит номер к единому формату для хранения и сравнения.

    Args:
        value: Введённый номер (маска, +, скобки).
        country: ru / by / kz — страна из селектора регистрации.

    Returns:
        Цифры без +: 11 для RU/KZ (7…), 12 для BY (375…).

    Raises:
        ValueError: Некорректный или неподдерживаемый формат.
    """
    digits = _digits_only(value)
    if not digits:
        raise ValueError("Номер телефона не может быть пустым")

    if country == "by":
        return _normalize_belarus(digits)
    if country in ("ru", "kz"):
        return _normalize_ru_kz(digits)

    if digits.startswith(BY_PREFIX):
        return _normalize_belarus(digits)
    return _normalize_ru_kz(digits)


def validate_country(value: str) -> PhoneCountry:
    """Проверяет код страны для API."""
    code = value.strip().lower()
    if code not in SUPPORTED_COUNTRIES:
        raise ValueError("Выберите страну: Россия, Беларусь или Казахстан.")
    return code  # type: ignore[return-value]
