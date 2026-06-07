"""Тесты UserManager."""

import pytest

from users.managers import UserManager
from users.models import User


@pytest.mark.django_db
def test_create_superuser_requires_staff_flag() -> None:
    """create_superuser требует is_staff=True."""
    manager = UserManager()
    manager.model = User
    with pytest.raises(ValueError, match="is_staff"):
        manager.create_superuser(phone="79009998877", password="SecurePass123", is_staff=False)


@pytest.mark.django_db
def test_create_superuser_success() -> None:
    """create_superuser создаёт пользователя с правами."""
    user = User.objects.create_superuser(phone="79008887766", password="SecurePass123")
    assert user.is_staff is True
    assert user.is_superuser is True
    assert user.check_password("SecurePass123")
