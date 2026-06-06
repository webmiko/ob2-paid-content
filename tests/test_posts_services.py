"""Unit-тесты can_view_post_body."""

from unittest.mock import patch

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
@patch("posts.services.access.user_has_active_subscription", return_value=True)
def test_can_view_paid_post_for_subscriber(_mock_sub, other_user, paid_post) -> None:
    """Подписчик видит body чужого платного поста."""
    from django.contrib.auth import get_user_model

    user = get_user_model().objects.get(pk=other_user.pk)
    assert can_view_post_body(user, paid_post) is True


@pytest.mark.django_db
def test_can_view_paid_post_denied_for_auth_without_sub(other_user, paid_post) -> None:
    """Авторизованный без подписки не видит чужой paid body."""
    assert can_view_post_body(other_user, paid_post) is False
