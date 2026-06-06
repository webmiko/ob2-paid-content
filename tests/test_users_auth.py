"""Тесты регистрации, JWT и CORS."""

import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()

REGISTER_URL = "/api/users/register/"
TOKEN_URL = "/api/token/"
REFRESH_URL = "/api/token/refresh/"


@pytest.fixture
def api_client() -> APIClient:
    """HTTP-клиент API."""
    return APIClient()


@pytest.fixture
def user_password() -> str:
    """Пароль для тестовых пользователей."""
    return "SecurePass123"


@pytest.mark.django_db
def test_register_returns_201_without_password(
    api_client: APIClient,
    user_password: str,
) -> None:
    """POST register создаёт пользователя и не возвращает password."""
    response = api_client.post(
        REGISTER_URL,
        {
            "phone": "+7 (900) 111-22-33",
            "display_name": "CreavityUser",
            "password": user_password,
        },
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data == {
        "id": response.data["id"],
        "phone": "79001112233",
        "display_name": "CreavityUser",
    }
    assert "password" not in response.data
    user = User.objects.get(pk=response.data["id"])
    assert user.check_password(user_password)


@pytest.mark.django_db
def test_register_requires_display_name(api_client: APIClient, user_password: str) -> None:
    """Регистрация без никнейма → 400."""
    response = api_client.post(
        REGISTER_URL,
        {"phone": "79009998877", "password": user_password},
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_register_duplicate_phone_returns_400(
    api_client: APIClient,
    user_password: str,
) -> None:
    """Повторная регистрация с тем же телефоном в другом формате → 400."""
    User.objects.create_user(phone="79001112233", password=user_password)
    response = api_client.post(
        REGISTER_URL,
        {"phone": "89001112233", "password": user_password, "display_name": "Duplicate"},
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_register_sqli_string_in_phone_returns_400(api_client: APIClient) -> None:
    """SQLi-подобная строка в phone не вызывает 500."""
    response = api_client.post(
        REGISTER_URL,
        {"phone": "1' OR '1'='1", "password": "SecurePass123", "display_name": "Test"},
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_jwt_obtain_and_refresh(api_client: APIClient, user_password: str) -> None:
    """JWT obtain по phone и refresh возвращают новую пару токенов."""
    User.objects.create_user(phone="79002223344", password=user_password)
    token_response = api_client.post(
        TOKEN_URL,
        {"phone": "+7 900 222-33-44", "password": user_password},
        format="json",
    )
    assert token_response.status_code == status.HTTP_200_OK
    assert "access" in token_response.data
    assert "refresh" in token_response.data

    refresh_response = api_client.post(
        REFRESH_URL,
        {"refresh": token_response.data["refresh"]},
        format="json",
    )
    assert refresh_response.status_code == status.HTTP_200_OK
    assert "access" in refresh_response.data


@pytest.mark.django_db
def test_jwt_wrong_password_returns_401(api_client: APIClient, user_password: str) -> None:
    """Неверный пароль → 401 без утечки деталей."""
    User.objects.create_user(phone="79003334455", password=user_password)
    response = api_client.post(
        TOKEN_URL,
        {"phone": "79003334455", "password": "WrongPassword1"},
        format="json",
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_cors_preflight_for_register(settings, client) -> None:
    """OPTIONS с Origin из CORS_ALLOWED_ORIGINS возвращает CORS-заголовки."""
    settings.CORS_ALLOWED_ORIGINS = ["http://localhost:5173"]
    response = client.options(
        REGISTER_URL,
        HTTP_ORIGIN="http://localhost:5173",
        HTTP_ACCESS_CONTROL_REQUEST_METHOD="POST",
    )
    assert response.status_code == 200
    assert response["Access-Control-Allow-Origin"] == "http://localhost:5173"
