"""Unit-тесты модуля API-клиента (api_client.py)."""

from decimal import Decimal

import pytest
import requests
import requests_mock as rm

from currency_converter.api_client import ExchangeRateClient
from currency_converter.exceptions import APIError, NetworkError, RateLimitError


@pytest.fixture
def client() -> ExchangeRateClient:
    """Фикстура с экземпляром API-клиента."""
    return ExchangeRateClient()


class TestExchangeRateClient:
    """Тесты класса ExchangeRateClient."""

    def test_get_rates_success(self, client: ExchangeRateClient) -> None:
        """Проверка успешного получения курсов."""
        mock_response = {
            "result": "success",
            "base_code": "USD",
            "rates": {"USD": 1.0, "RUB": 92.50, "EUR": 0.92},
        }
        with rm.Mocker() as m:
            m.get("https://open.er-api.com/v6/latest/USD", json=mock_response)
            rates = client.get_rates("USD")

        assert rates["RUB"] == Decimal("92.50")
        assert rates["EUR"] == Decimal("0.92")
        assert rates["USD"] == Decimal("1.0")

    def test_get_rates_from_cache(self, client: ExchangeRateClient) -> None:
        """Проверка работы кэша (второй запрос не делает HTTP-вызов)."""
        mock_response = {
            "result": "success",
            "base_code": "USD",
            "rates": {"USD": 1.0, "RUB": 92.50},
        }
        with rm.Mocker() as m:
            m.get("https://open.er-api.com/v6/latest/USD", json=mock_response)
            client.get_rates("USD")
            client.get_rates("USD")  # второй вызов — из кэша

        assert m.call_count == 1  # HTTP-запрос выполнен только один раз

    def test_get_rates_network_error(self, client: ExchangeRateClient) -> None:
        """Проверка обработки сетевой ошибки."""
        with rm.Mocker() as m:
            m.get(
                "https://open.er-api.com/v6/latest/USD",
                exc=requests.exceptions.ConnectionError,
            )
            with pytest.raises(NetworkError):
                client.get_rates("USD")

    def test_get_rates_api_error(self, client: ExchangeRateClient) -> None:
        """Проверка обработки логической ошибки API."""
        mock_response = {"result": "error", "error-type": "unsupported-code"}
        with rm.Mocker() as m:
            m.get(
                "https://open.er-api.com/v6/latest/INVALID",
                json=mock_response,
            )
            with pytest.raises(APIError) as exc_info:
                client.get_rates("INVALID")

        assert exc_info.value.error_type == "unsupported-code"

    def test_get_rates_rate_limit(self, client: ExchangeRateClient) -> None:
        """Проверка обработки HTTP 429."""
        with rm.Mocker() as m:
            m.get(
                "https://open.er-api.com/v6/latest/USD",
                status_code=429,
            )
            with pytest.raises(RateLimitError):
                client.get_rates("USD")


