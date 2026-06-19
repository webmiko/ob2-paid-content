"""Smoke-тесты каркаса проекта."""

import pytest
from django.test import Client


@pytest.mark.django_db
def test_health_endpoint_returns_ok() -> None:
    """Health-check возвращает status ok."""
    client = Client()
    response = client.get("/api/health/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["cache"] in ("database", "redis", "locmem")
