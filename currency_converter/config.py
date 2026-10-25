"""Константы проекта Currency Converter."""

# URL ExchangeRate-API (базовая версия без ключа)
API_URL: str = "https://open.er-api.com/v6/latest/{base_currency}"

# Таймаут HTTP-запроса в секундах
TIMEOUT: int = 5

# Список поддерживаемых валют (ISO 4217)
# tuple используется вместо list для защиты от случайной модификации
VALID_CURRENCIES: tuple[str, ...] = (
    "USD", "EUR", "RUB", "GBP", "JPY", "CNY",
    "KZT", "BYN", "UAH", "CHF", "CAD", "AUD",
)

# Точность округления для финансовых расчётов
DECIMAL_PLACES: str = "0.01"

