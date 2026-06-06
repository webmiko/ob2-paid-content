"""Тесты нормализации телефона."""

import pytest

from users.validators import normalize_phone


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("+7 (900) 123-45-67", "79001234567"),
        ("89001234567", "79001234567"),
        ("9001234567", "79001234567"),
        ("7 900 123 45 67", "79001234567"),
    ],
)
def test_normalize_phone_accepts_common_formats(raw: str, expected: str) -> None:
    """Разные форматы приводятся к одной строке из 11 цифр."""
    assert normalize_phone(raw) == expected


@pytest.mark.parametrize(
    "invalid",
    [
        "",
        "123",
        "abc",
        "1' OR '1'='1",
    ],
)
def test_normalize_phone_rejects_invalid(invalid: str) -> None:
    """Некорректный ввод вызывает ValueError."""
    with pytest.raises(ValueError):
        normalize_phone(invalid)
