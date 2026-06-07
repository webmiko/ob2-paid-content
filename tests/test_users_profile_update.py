"""Тест обновления публичного имени автора."""

import pytest
from rest_framework import status

ME_URL = "/api/users/me/"


@pytest.mark.django_db
def test_patch_display_name_too_short(auth_client) -> None:
    """PATCH /me/ отклоняет слишком короткий display_name."""
    response = auth_client.patch(ME_URL, {"display_name": "A"}, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_patch_display_name(auth_client, author) -> None:
    """PATCH /me/ обновляет display_name."""
    response = auth_client.patch(ME_URL, {"display_name": "Creavity Author"}, format="json")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["display_name"] == "Creavity Author"
    author.refresh_from_db()
    assert author.display_name == "Creavity Author"
