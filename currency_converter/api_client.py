"""HTTP-клиент для взаимодействия с ExchangeRate-API."""

from typing import Any

import requests
from requests.exceptions import ConnectionError, HTTPError, Timeout

from currency_converter import config
from currency_converter.exceptions import NetworkError


class ExchangeRateClient:
    """HTTP-клиент для получения актуальных курсов валют.

    Attributes:
        base_url: Базовый URL API без плейсхолдера.
        timeout: Таймаут запроса в секундах.
    """

    def __init__(
        self,
        base_url: str = config.API_URL,
        timeout: int = config.TIMEOUT,
    ) -> None:
        # Убираем плейсхолдер из URL, подставляем валюту в методе
        self.base_url = base_url.replace("/{base_currency}", "")
        self.timeout = timeout

    def get_exchange_rate(self, base_currency: str, target_currency: str) -> float:
        """Получает курс целевой валюты относительно базовой.

        Args:
            base_currency: Код исходной валюты ISO 4217 (например, 'USD').
            target_currency: Код целевой валюты ISO 4217 (например, 'RUB').

        Returns:
            Курс обмена (float).

        Raises:
            NetworkError: При сетевой ошибке, не-200 статусе или отсутствии
                курса в ответе API.
        """
        url = f"{self.base_url}/{base_currency}"

        try:
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
        except ConnectionError as exc:
            raise NetworkError(f"Не удалось подключиться к API: {exc}") from exc
        except Timeout as exc:
            raise NetworkError(
                f"Превышен таймаут запроса ({self.timeout} сек): {exc}"
            ) from exc
        except HTTPError as exc:
            raise NetworkError(
                f"API вернул ошибку HTTP {response.status_code}",
                status_code=response.status_code,
            ) from exc

        data: dict[str, Any] = response.json()

        if data.get("result") != "success":
            raise NetworkError(
                f"API вернул ошибку: {data.get('error-type', 'Unknown')}"
            )

        rates: dict[str, float] = data.get("rates", {})
        rate = rates.get(target_currency)

        if rate is None:
            raise NetworkError(
                f"Курс для валюты {target_currency} не найден в ответе API"
            )

        return float(rate)
