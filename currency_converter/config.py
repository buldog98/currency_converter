"""Константы, URL API и перечисление валют."""

from enum import StrEnum

# URL публичного API (бесплатный, без ключа)
API_BASE_URL: str = "https://open.er-api.com/v6/latest/{base_code}"

# Таймауты HTTP-запроса: (connect_timeout, read_timeout)
REQUEST_TIMEOUT: tuple[float, float] = (3.0, 10.0)

# Максимальное количество повторных попыток при сетевых ошибках
MAX_RETRIES: int = 3

# Время жизни кэша курсов в секундах (15 минут)
CACHE_TTL_SECONDS: int = 900


# Перечисление поддерживаемых валют (ISO 4217)
class Currency(StrEnum):
    USD = "USD"
    EUR = "EUR"
    RUB = "RUB"
    JPY = "JPY"
    GBP = "GBP"
    CNY = "CNY"
    KZT = "KZT"
    BYN = "BYN"
    UAH = "UAH"
    TRY = "TRY"


# Множество валидных кодов для быстрой проверки
VALID_CURRENCIES: set[str] = {c.value for c in Currency}
