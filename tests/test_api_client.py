"""Unit-тесты для модуля API-клиента (api_client.py)."""

import pytest
import requests
import requests_mock as rm

from currency_converter.api_client import ExchangeRateClient
from currency_converter.exceptions import NetworkError


@pytest.fixture
def client():
    """Фикстура с экземпляром API-клиента."""
    return ExchangeRateClient()


class TestExchangeRateClient:
    """Тесты класса ExchangeRateClient."""

    def test_get_exchange_rate_success(self, client):
        """Проверка успешного получения курса."""
        mock_response = {
            "result": "success",
            "base_code": "USD",
            "rates": {"RUB": 92.50, "EUR": 0.92},
        }
        with rm.Mocker() as m:
            m.get("https://open.er-api.com/v6/latest/USD", json=mock_response)
            rate = client.get_exchange_rate("USD", "RUB")
        assert rate == 92.50

    def test_get_exchange_rate_network_error(self, client):
        """Проверка обработки сетевой ошибки."""
        with rm.Mocker() as m:
            m.get(
                "https://open.er-api.com/v6/latest/USD",
                exc=requests.exceptions.ConnectionError,
            )
            with pytest.raises(NetworkError) as exc_info:
                client.get_exchange_rate("USD", "RUB")
        assert "Не удалось подключиться к API" in str(exc_info.value)

    def test_get_exchange_rate_api_error(self, client):
        """Проверка обработки ошибки API (не-200 статус или ошибка в теле)."""
        mock_response = {"result": "error", "error-type": "unsupported_code"}
        with rm.Mocker() as m:
            m.get(
                "https://open.er-api.com/v6/latest/INVALID",
                json=mock_response,
                status_code=200,
            )
            with pytest.raises(NetworkError) as exc_info:
                client.get_exchange_rate("INVALID", "RUB")
        assert "unsupported_code" in str(exc_info.value)

    def test_get_exchange_rate_missing_currency(self, client):
        """Проверка обработки отсутствия целевой валюты в ответе."""
        mock_response = {
            "result": "success",
            "base_code": "USD",
            "rates": {"EUR": 0.92},  # RUB отсутствует
        }
        with rm.Mocker() as m:
            m.get("https://open.er-api.com/v6/latest/USD", json=mock_response)
            with pytest.raises(NetworkError) as exc_info:
                client.get_exchange_rate("USD", "RUB")
        assert "не найден" in str(exc_info.value).lower()
