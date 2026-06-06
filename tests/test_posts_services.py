"""Unit-тесты проверки доступа к body публикации."""

import pytest
from django.contrib.auth.models import AnonymousUser

from posts.services.access import can_view_post_body


@pytest.mark.django_db
def test_can_view_free_post_for_guest(author, free_post) -> None:
    """Guest видит body бесплатного поста."""
    assert can_view_post_body(AnonymousUser(), free_post) is True
    assert can_view_post_body(None, free_post) is True


@pytest.mark.django_db
def test_can_view_paid_post_denied_for_guest(paid_post) -> None:
    """Guest не видит body платного поста."""
    assert can_view_post_body(AnonymousUser(), paid_post) is False


@pytest.mark.django_db
def test_can_view_paid_post_for_author(author, paid_post) -> None:
    """Автор видит body своего платного поста."""
    assert can_view_post_body(author, paid_post) is True


@pytest.mark.django_db
def test_can_view_paid_post_for_subscriber(other_user, paid_post) -> None:
    """Подписчик видит body чужого платного поста."""
    from users.models import Subscription

    Subscription.objects.create(user=other_user, is_active=True)
    assert can_view_post_body(other_user, paid_post) is True


@pytest.mark.django_db
def test_can_view_paid_post_denied_for_auth_without_sub(other_user, paid_post) -> None:
    """Авторизованный без подписки не видит чужой paid body."""
    assert can_view_post_body(other_user, paid_post) is False
