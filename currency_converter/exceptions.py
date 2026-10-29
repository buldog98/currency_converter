"""Иерархия доменных исключений конвертера валют."""


class CurrencyError(Exception):
    """Базовое исключение для всех ошибок конвертера."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class ValidationError(CurrencyError):
    """Ошибка валидации входных данных (неверный код валюты, отрицательная сумма)."""


class NetworkError(CurrencyError):
    """Ошибка сетевого взаимодействия с API."""


class RateLimitError(CurrencyError):
    """Превышен лимит запросов к API (HTTP 429)."""


class APIError(CurrencyError):
    """API вернул логическую ошибку (unsupported-code, invalid-code и т.д.)."""

    def __init__(self, error_type: str) -> None:
        self.error_type = error_type
        super().__init__(f"API error: {error_type}")


class ConversionError(CurrencyError):
    """Ошибка математической конвертации (отсутствие курса в ответе)."""
