"""Unit-тесты для модуля бизнес-логики (converter.py)."""

from unittest.mock import MagicMock

import pytest

from currency_converter.converter import CurrencyConverter
from currency_converter.exceptions import NetworkError, ValidationError


@pytest.fixture
def mock_client():
    """Фикстура с мок-объектом HTTP-клиента."""
    return MagicMock()


@pytest.fixture
def converter(mock_client):
    """Фикстура с экземпляром конвертера."""
    return CurrencyConverter(client=mock_client)


class TestCurrencyConverter:
    """Тесты класса CurrencyConverter."""

    def test_convert_success(self, converter, mock_client):
        """Проверка успешной конвертации с прямым запросом курса."""
        mock_client.get_exchange_rate.return_value = 92.50
        result = converter.convert(100.0, "USD", "RUB")
        assert result["amount"] == 100.0
        assert result["from_currency"] == "USD"
        assert result["to_currency"] == "RUB"
        assert result["result"] == pytest.approx(9250.0, rel=1e-4)
        assert result["rate"] == pytest.approx(92.50, rel=1e-4)

    def test_convert_same_currency(self, converter):
        """Проверка конвертации валюты в саму себя (без запроса к API)."""
        result = converter.convert(50.0, "EUR", "EUR")
        assert result["result"] == 50.0
        assert result["rate"] == 1.0

    def test_convert_invalid_currency(self, converter):
        """Проверка обработки невалидного кода валюты."""
        with pytest.raises(ValidationError) as exc_info:
            converter.convert(100.0, "USD", "XYZ")
        assert "Неизвестный код валюты" in str(exc_info.value)

    def test_convert_invalid_amount(self, converter):
        """Проверка обработки отрицательной суммы."""
        with pytest.raises(ValidationError):
            converter.convert(-10.0, "USD", "RUB")

    def test_convert_missing_rate(self, converter, mock_client):
        """Проверка обработки отсутствия курса."""
        mock_client.get_exchange_rate.side_effect = NetworkError(
            "Курс для валюты RUB не найден в ответе API"
        )
        with pytest.raises(NetworkError) as exc_info:
            converter.convert(100.0, "USD", "RUB")
        assert "не найден" in str(exc_info.value).lower()
