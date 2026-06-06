"""DRF throttling для auth и платежей."""

from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class AuthRateThrottle(AnonRateThrottle):
    """Лимит на login, register и refresh."""

    scope = "auth"


class PaymentRateThrottle(UserRateThrottle):
    """Лимит на создание и подтверждение платежей."""

    scope = "payment"
