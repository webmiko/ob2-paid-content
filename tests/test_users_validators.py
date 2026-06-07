"""Тесты нормализации телефона."""

import pytest

from users.validators import normalize_phone, validate_country


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("+7 (900) 123-45-67", "79001234567"),
        ("89001234567", "79001234567"),
        ("9001234567", "79001234567"),
        ("7 900 123 45 67", "79001234567"),
    ],
)
def test_normalize_phone_ru_accepts_common_formats(raw: str, expected: str) -> None:
    """Разные форматы России приводятся к 11 цифрам."""
    assert normalize_phone(raw, country="ru") == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("+7 (771) 123-45-67", "77711234567"),
        ("87711234567", "77711234567"),
    ],
)
def test_normalize_phone_kz(raw: str, expected: str) -> None:
    """Казахстан: тот же +7, 11 цифр."""
    assert normalize_phone(raw, country="kz") == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("+375 (29) 123-45-67", "375291234567"),
        ("375291234567", "375291234567"),
        ("291234567", "375291234567"),
    ],
)
def test_normalize_phone_by(raw: str, expected: str) -> None:
    """Беларусь: 12 цифр с префиксом 375."""
    assert normalize_phone(raw, country="by") == expected


@pytest.mark.parametrize(
    "invalid",
    [
        "",
        "123",
        "abc",
        "1' OR '1'='1",
        "+375 (29) 12",
    ],
)
def test_normalize_phone_rejects_invalid(invalid: str) -> None:
    """Некорректный ввод вызывает ValueError."""
    with pytest.raises(ValueError):
        normalize_phone(invalid)


def test_validate_country_rejects_unknown() -> None:
    """Неизвестная страна отклоняется."""
    with pytest.raises(ValueError):
        validate_country("us")
