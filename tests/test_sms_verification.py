"""Тесты имитации SMS-подтверждения."""

import pytest
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIClient

SEND_CODE_URL = "/api/users/phone/send-code/"
REGISTER_URL = "/api/users/register/"


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def user_password() -> str:
    return "SecurePass123"


@pytest.mark.django_db
@override_settings(SMS_SHOW_CODE_IN_RESPONSE=True, SMS_VERIFICATION_REQUIRED=True)
def test_send_code_returns_simulation_code(api_client: APIClient) -> None:
    """POST send-code возвращает демо-код в ответе."""
    response = api_client.post(
        SEND_CODE_URL,
        {"phone": "+7 (900) 555-12-34", "country": "ru"},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK
    assert "simulation_code" in response.data
    assert len(response.data["simulation_code"]) == 6


@pytest.mark.django_db
@override_settings(SMS_SHOW_CODE_IN_RESPONSE=True, SMS_VERIFICATION_REQUIRED=True)
def test_register_with_sms_code(api_client: APIClient, user_password: str) -> None:
    """Регистрация с кодом из send-code проходит успешно."""
    send = api_client.post(
        SEND_CODE_URL,
        {"phone": "79006667788", "country": "ru"},
        format="json",
    )
    code = send.data["simulation_code"]
    response = api_client.post(
        REGISTER_URL,
        {
            "phone": "79006667788",
            "country": "ru",
            "display_name": "SmsUser",
            "password": user_password,
            "sms_code": code,
        },
        format="json",
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["phone"] == "79006667788"


@pytest.mark.django_db
@override_settings(SMS_SHOW_CODE_IN_RESPONSE=True, SMS_VERIFICATION_REQUIRED=True)
def test_register_wrong_sms_code_returns_400(api_client: APIClient, user_password: str) -> None:
    """Неверный SMS-код блокирует регистрацию."""
    api_client.post(
        SEND_CODE_URL,
        {"phone": "79007778899", "country": "ru"},
        format="json",
    )
    response = api_client.post(
        REGISTER_URL,
        {
            "phone": "79007778899",
            "country": "ru",
            "display_name": "BadSms",
            "password": user_password,
            "sms_code": "000000",
        },
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
