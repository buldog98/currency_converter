"""Точка входа в приложение. CLI-интерфейс на базе argparse."""

import argparse
import sys

from .api_client import ExchangeRateClient
from .converter import CurrencyConverter
from .exceptions import CurrencyError


def create_parser() -> argparse.ArgumentParser:
    """Создаёт парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(
        description="Конвертер валют с актуальными курсами (REST API)."
    )
    parser.add_argument(
        "amount",
        type=float,
        help="Сумма для конвертации (положительное число).",
    )
    parser.add_argument(
        "from_currency",
        type=str,
        help="Исходная валюта (ISO 4217, например USD).",
    )
    parser.add_argument(
        "to_currency",
        type=str,
        help="Целевая валюта (ISO 4217, например RUB).",
    )
    return parser


def format_result(result: dict) -> str:
    """Форматирует словарь результата в читаемую строку."""
    return (
        f"{result['amount']} {result['from']} = "
        f"{result['result']} {result['to']} "
        f"(по курсу {result['rate']})"
    )


def main() -> None:
    """Точка входа: парсинг аргументов, запуск конвертации, вывод."""
    parser = create_parser()
    args = parser.parse_args()

    # Инициализация графа зависимостей (DI)
    client = ExchangeRateClient()
    converter = CurrencyConverter(client)

    try:
        result = converter.convert(
            amount=args.amount,
            from_currency=args.from_currency,
            to_currency=args.to_currency,
        )
        print(format_result(result))
    except CurrencyError as exc:
        print(f"Error: {exc.message}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Unexpected error: {exc}", file=sys.stderr)
        sys.exit(2)
    except KeyboardInterrupt:
        print("\nОперация отменена пользователем.", file=sys.stderr)
        sys.exit(130)


if __name__ == "__main__":
    main()
