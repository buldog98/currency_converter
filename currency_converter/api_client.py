"""HTTP-клиент для получения курсов валют с кэшированием."""

import time
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

import requests

from . import config
from .exceptions import APIError, NetworkError, RateLimitError


@dataclass
class CachedRates:
    """Запись кэша курсов с меткой времени."""

    rates: dict[str, Decimal]
    timestamp: float
    ttl: int = config.CACHE_TTL_SECONDS

    def is_expired(self) -> bool:
        return (time.time() - self.timestamp) >= self.ttl


class ExchangeRateClient:
    """Клиент для получения курсов валют через REST API."""

    def __init__(self) -> None:
        self._cache: dict[str, CachedRates] = {}
        self._session = requests.Session()
        self._session.headers.update({"Accept": "application/json"})

    def get_rates(self, base_currency: str) -> dict[str, Decimal]:
        """Возвращает словарь курсов относительно base_currency.

        Использует кэш при актуальных данных, иначе выполняет HTTP-запрос.
        """
        base_currency = base_currency.upper()

        # Проверка кэша
        cached = self._cache.get(base_currency)
        if cached and not cached.is_expired():
            return cached.rates

        # HTTP-запрос с retry
        rates = self._fetch_rates_with_retry(base_currency)

        # Сохранение в кэш
        self._cache[base_currency] = CachedRates(
            rates=rates,
            timestamp=time.time(),
        )
        return rates

    def _fetch_rates_with_retry(self, base_currency: str) -> dict[str, Decimal]:
        """Выполняет HTTP-запрос с повторными попытками."""
        url = config.API_BASE_URL.format(base_code=base_currency)
        last_error: Exception | None = None

        for attempt in range(1, config.MAX_RETRIES + 1):
            try:
                response = self._session.get(
                    url,
                    timeout=config.REQUEST_TIMEOUT,
                )
                return self._parse_response(response)
            except requests.exceptions.Timeout:
                last_error = NetworkError(
                    f"Timeout on attempt {attempt}/{config.MAX_RETRIES}"
                )
            except requests.exceptions.ConnectionError:
                last_error = NetworkError(
                    f"Connection error on attempt {attempt}/{config.MAX_RETRIES}"
                )
            except requests.exceptions.HTTPError as exc:
                if exc.response is not None and exc.response.status_code == 429:
                    raise RateLimitError("Rate limit exceeded") from exc
                raise NetworkError(f"HTTP error: {exc}") from exc

        # Все попытки исчерпаны
        raise last_error or NetworkError("Unknown network error")

    def _parse_response(self, response: requests.Response) -> dict[str, Decimal]:
        """Парсит JSON-ответ и извлекает курсы."""
        response.raise_for_status()
        data: dict[str, Any] = response.json()

        match data.get("result"):
            case "success":
                raw_rates: dict[str, float] = data["rates"]
                return {code: Decimal(str(rate)) for code, rate in raw_rates.items()}
            case "error":
                error_type = data.get("error-type", "unknown")
                raise APIError(error_type)
            case _:
                raise APIError("unexpected-response")
