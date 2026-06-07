"""DRF throttling для auth, платежей, комментариев и удаления аккаунта."""

from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class AuthRateThrottle(AnonRateThrottle):
    """Лимит на login, register и refresh."""

    scope = "auth"


class PaymentRateThrottle(UserRateThrottle):
    """Лимит на создание и подтверждение платежей."""

    scope = "payment"


class CommentCreateThrottle(UserRateThrottle):
    """Лимит на создание комментариев."""

    scope = "comment_create"


class CommentDeleteThrottle(UserRateThrottle):
    """Лимит на удаление комментариев."""

    scope = "comment_delete"


class AccountDeleteThrottle(UserRateThrottle):
    """Лимит на удаление аккаунта (защита от перебора пароля)."""

    scope = "account_delete"


class WebhookRateThrottle(AnonRateThrottle):
    """Лимит на Stripe webhook."""

    scope = "webhook"


class ViewRecordThrottle(AnonRateThrottle):
    """Лимит на запись просмотров публикаций."""

    scope = "view_record"
