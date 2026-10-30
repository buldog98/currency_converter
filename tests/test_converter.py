"""Unit-тесты модуля бизнес-логики (converter.py)."""

from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from currency_converter.converter import CurrencyConverter
from currency_converter.exceptions import ConversionError, ValidationError


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
        """Проверка успешной конвертации."""
        mock_client.get_rates.return_value = {
            "USD": Decimal("1.0"),
            "RUB": Decimal("92.50"),
        }
        result = converter.convert(100.0, "USD", "RUB")

        assert result["amount"] == Decimal("100.0")
        assert result["from"] == "USD"
        assert result["to"] == "RUB"
        assert result["result"] == Decimal("9250.00")
        assert result["rate"] == Decimal("92.50")

    def test_convert_same_currency(self, converter):
        """Проверка конвертации валюты в саму себя (без запроса к API)."""
        result = converter.convert(50.0, "EUR", "EUR")
        assert result["result"] == Decimal("50.0")
        assert result["rate"] == Decimal("1")

    def test_convert_invalid_currency(self, converter):
        """Проверка обработки невалидного кода валюты."""
        with pytest.raises(ValidationError):
            converter.convert(100.0, "USD", "XYZ")

    def test_convert_invalid_amount(self, converter):
        """Проверка обработки отрицательной суммы."""
        with pytest.raises(ValidationError):
            converter.convert(-10.0, "USD", "RUB")

    def test_convert_missing_rate(self, converter, mock_client):
        """Проверка обработки отсутствия курса в ответе API."""
        mock_client.get_rates.return_value = {"USD": Decimal("1.0")}
        with pytest.raises(ConversionError):
            converter.convert(100.0, "USD", "RUB")
