"""Валидаторы и нормализация данных пользователя."""

import re

from config.constants import PHONE_COUNTRY_DIGIT, PHONE_DIGITS_LENGTH

_DIGITS_RE = re.compile(r"\D")


def normalize_phone(value: str) -> str:
    """Приводит номер телефона к единому формату для хранения и сравнения.

    Args:
        value: Введённый номер (может содержать +7, 8, пробелы, скобки).

    Returns:
        Строка из PHONE_DIGITS_LENGTH цифр, начинается с PHONE_COUNTRY_DIGIT.

    Raises:
        ValueError: Если после нормализации длина не равна PHONE_DIGITS_LENGTH.

    Example:
        >>> normalize_phone("+7 (900) 123-45-67")
        '79001234567'
    """
    digits = _DIGITS_RE.sub("", value)
    if not digits:
        raise ValueError("Номер телефона не может быть пустым")
    if len(digits) == PHONE_DIGITS_LENGTH and digits[0] == "8":
        digits = PHONE_COUNTRY_DIGIT + digits[1:]
    elif len(digits) == PHONE_DIGITS_LENGTH - 1:
        digits = PHONE_COUNTRY_DIGIT + digits
    if len(digits) != PHONE_DIGITS_LENGTH or digits[0] != PHONE_COUNTRY_DIGIT:
        raise ValueError(
            f"Номер телефона должен содержать {PHONE_DIGITS_LENGTH} цифр и начинаться с {PHONE_COUNTRY_DIGIT}",
        )
    return digits
