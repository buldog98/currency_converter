"""Точка входа в приложение Currency Converter."""

import sys
from typing import Any

from currency_converter.api_client import ExchangeRateClient
from currency_converter.config import VALID_CURRENCIES
from currency_converter.converter import CurrencyConverter
from currency_converter.exceptions import CurrencyError


def format_result(data: dict[str, Any]) -> str:
    """Форматирует результат конвертации для вывода в консоль.

    Args:
        data: Словарь с результатом работы CurrencyConverter.convert().

    Returns:
        Человекочитаемая строка результата.
    """
    return (
        f"{data['amount']:.2f} {data['from_currency']} = "
        f"{data['result']:.2f} {data['to_currency']} "
        f"(курс: {data['rate']:.4f})"
    )


def get_user_input() -> tuple[float, str, str]:
    """Запрашивает у пользователя параметры конвертации.

    Returns:
        Кортеж (amount, from_currency, to_currency).

    Raises:
        ValueError: При некорректном вводе суммы.
    """
    amount = float(input("Введите сумму: ").strip())
    from_currency = input("Исходная валюта (код ISO, например USD): ").strip().upper()
    to_currency = input("Целевая валюта (код ISO, например RUB): ").strip().upper()
    return amount, from_currency, to_currency


def main() -> None:
    """Главная функция приложения."""
    print("=== Конвертер валют ===")
    print(f"Поддерживаемые валюты: {', '.join(VALID_CURRENCIES)}\n")

    client = ExchangeRateClient()
    converter = CurrencyConverter(client)

    try:
        amount, from_currency, to_currency = get_user_input()
        result = converter.convert(amount, from_currency, to_currency)
        print("\n" + format_result(result))
    except ValueError:
        print("\nОшибка: сумма должна быть числом.", file=sys.stderr)
        sys.exit(1)
    except CurrencyError as exc:
        print(f"\nОшибка конвертации: {exc}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nОперация отменена пользователем.")
        sys.exit(0)


if __name__ == "__main__":
    main()
