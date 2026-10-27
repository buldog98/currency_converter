"""Бизнес-логика конвертации валют."""

from decimal import ROUND_HALF_UP, Decimal
from typing import Any

from currency_converter import config
from currency_converter.exceptions import ConversionError, NetworkError, ValidationError


class CurrencyConverter:
    """Конвертер валют с финансовой точностью.

    Attributes:
        client: HTTP-клиент для получения курсов (ExchangeRateClient).
    """

    def __init__(self, client: Any) -> None:
        self.client = client

    def convert(
        self,
        amount: float,
        from_currency: str,
        to_currency: str,
    ) -> dict[str, Any]:
        """Конвертирует сумму из одной валюты в другую.

        Args:
            amount: Сумма для конвертации (должна быть > 0).
            from_currency: Код исходной валюты ISO 4217 (например, 'USD').
            to_currency: Код целевой валюты ISO 4217 (например, 'RUB').

        Returns:
            Словарь с результатом конвертации:
            {
                "amount": float,       # Исходная сумма
                "from_currency": str,  # Код исходной валюты
                "to_currency": str,    # Код целевой валюты
                "rate": float,         # Курс обмена
                "result": float,       # Результат конвертации
            }

        Raises:
            ValidationError: Если сумма <= 0 или код валюты не в списке VALID_CURRENCIES.
            ConversionError: Если произошла ошибка при получении курса или математической конвертации.
            NetworkError: Если произошла сетевая ошибка при запросе к API.
        """
        # Fail-Fast: валидация до запроса к API
        self._validate_amount(amount)
        self._validate_currency(from_currency, "Исходная")
        self._validate_currency(to_currency, "Целевая")

        # Оптимизация: если валюты совпадают, курс = 1.0
        if from_currency == to_currency:
            rate = 1.0
        else:
            # Получение курса через клиент (Data Access Layer)
            try:
                rate = self.client.get_exchange_rate(from_currency, to_currency)
            except NetworkError:
                raise
            except Exception as exc:
                raise ConversionError(
                    f"Не удалось получить курс {from_currency} -> {to_currency}: {exc}"
                ) from exc

        # Математическая конвертация через Decimal
        try:
            result = self._calculate(amount, rate)
        except Exception as exc:
            raise ConversionError(
                f"Ошибка конвертации {amount} {from_currency} в {to_currency}: {exc}"
            ) from exc

        return {
            "amount": amount,
            "from_currency": from_currency,
            "to_currency": to_currency,
            "rate": rate,
            "result": result,
        }

    def _validate_amount(self, amount: float) -> None:
        """Проверяет корректность суммы."""
        if amount <= 0:
            raise ValidationError(
                f"Сумма должна быть положительной, получено: {amount}"
            )

    def _validate_currency(self, currency: str, label: str) -> None:
        """Проверяет, что код валюты есть в списке поддерживаемых."""
        if currency not in config.VALID_CURRENCIES:
            raise ValidationError(
                f"Неизвестный код валюты: {currency}. "
                f"Доступные: {', '.join(config.VALID_CURRENCIES)}"
            )

    def _calculate(self, amount: float, rate: float) -> float:
        """Выполняет конвертацию с финансовой точностью.

        Использует Decimal для избежания ошибок плавающей точки.
        Округление: ROUND_HALF_UP (бухгалтерское).
        """
        amount_decimal = Decimal(str(amount))
        rate_decimal = Decimal(str(rate))
        precision = Decimal(config.DECIMAL_PLACES)

        result = (amount_decimal * rate_decimal).quantize(
            precision, rounding=ROUND_HALF_UP
        )
        return float(result)
