"""Бизнес-логика конвертации валют."""

from decimal import ROUND_HALF_UP, Decimal

from . import config
from .api_client import ExchangeRateClient
from .exceptions import ConversionError, ValidationError


class CurrencyConverter:
    """Конвертер валют с валидацией и точной арифметикой."""

    # Точность округления: 2 знака после запятой
    QUANTIZE_EXPONENT = Decimal("0.01")

    def __init__(self, client: ExchangeRateClient) -> None:
        self.client = client

    def convert(
        self,
        amount: float | Decimal | str,
        from_currency: str,
        to_currency: str,
    ) -> dict[str, object]:
        """Конвертирует amount из from_currency в to_currency.

        Возвращает словарь с результатом и метаинформацией.
        """
        # Нормализация входных данных
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        # Валидация (Fail-Fast)
        self._validate_currencies(from_currency, to_currency)
        amount_decimal = self._validate_and_parse_amount(amount)

        # Оптимизация: одинаковые валюты
        if from_currency == to_currency:
            return {
                "from": from_currency,
                "to": to_currency,
                "amount": amount_decimal,
                "result": amount_decimal,
                "rate": Decimal("1"),
            }

        # Получение курсов через API
        rates = self.client.get_rates(from_currency)

        if to_currency not in rates:
            raise ConversionError(f"Rate for {to_currency} not found in API response")

        rate = rates[to_currency]
        result = (amount_decimal * rate).quantize(
            self.QUANTIZE_EXPONENT, rounding=ROUND_HALF_UP
        )

        return {
            "from": from_currency,
            "to": to_currency,
            "amount": amount_decimal,
            "result": result,
            "rate": rate,
        }

    def _validate_currencies(self, from_currency: str, to_currency: str) -> None:
        """Проверяет, что коды валют входят в список поддерживаемых."""
        if from_currency not in config.VALID_CURRENCIES:
            raise ValidationError(f"Unsupported source currency: {from_currency}")
        if to_currency not in config.VALID_CURRENCIES:
            raise ValidationError(f"Unsupported target currency: {to_currency}")

    def _validate_and_parse_amount(self, amount: object) -> Decimal:
        """Парсит сумму и проверяет её положительность."""
        try:
            decimal_amount = Decimal(str(amount))
        except Exception as exc:
            raise ValidationError(f"Invalid amount value: {amount}") from exc

        if decimal_amount <= 0:
            raise ValidationError(f"Amount must be positive, got {decimal_amount}")
        if decimal_amount.is_nan() or decimal_amount.is_infinite():
            raise ValidationError(f"Amount must be finite number, got {amount}")
        return decimal_amount
