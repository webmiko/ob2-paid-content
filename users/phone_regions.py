"""Регионы телефонов: Россия, Беларусь, Казахстан."""

from typing import Literal

PhoneCountry = Literal["ru", "by", "kz"]

SUPPORTED_COUNTRIES: tuple[PhoneCountry, ...] = ("ru", "by", "kz")

RU_KZ_DIGITS_LENGTH = 11
BY_DIGITS_LENGTH = 12
BY_PREFIX = "375"
RU_KZ_PREFIX = "7"
