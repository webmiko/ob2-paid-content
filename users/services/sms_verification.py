"""Имитация SMS-подтверждения номера (без внешних SMS-провайдеров)."""

import secrets

from django.conf import settings
from django.core.cache import cache

_CODE_KEY = "sms:code:{phone}"
_VERIFIED_KEY = "sms:verified:{phone}"


def _code_cache_key(phone: str) -> str:
    return _CODE_KEY.format(phone=phone)


def _verified_cache_key(phone: str) -> str:
    return _VERIFIED_KEY.format(phone=phone)


def send_verification_code(phone: str) -> tuple[str | None, str]:
    """Генерирует код и сохраняет в кэше.

    Returns:
        (simulation_code или None, сообщение для клиента).
    """
    code = f"{secrets.randbelow(1_000_000):06d}"
    cache.set(_code_cache_key(phone), code, timeout=settings.SMS_CODE_TTL_SECONDS)
    message = "Код подтверждения отправлен."
    if settings.SMS_SHOW_CODE_IN_RESPONSE:
        return code, f"{message} (демо: код в ответе API)"
    return None, message


def verify_sms_code(phone: str, code: str) -> bool:
    """Проверяет код и помечает номер как подтверждённый."""
    stored = cache.get(_code_cache_key(phone))
    if not stored or not isinstance(code, str):
        return False
    if stored != code.strip():
        return False
    cache.delete(_code_cache_key(phone))
    cache.set(_verified_cache_key(phone), True, timeout=settings.SMS_VERIFIED_TTL_SECONDS)
    return True


def is_phone_verified(phone: str) -> bool:
    """True, если номер недавно подтверждён по SMS."""
    return cache.get(_verified_cache_key(phone)) is True


def consume_phone_verification(phone: str) -> None:
    """Снимает флаг подтверждения после успешной регистрации."""
    cache.delete(_verified_cache_key(phone))
