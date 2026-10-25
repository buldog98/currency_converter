"""Иерархия кастомных исключений проекта."""


class CurrencyError(Exception):
    """Базовое исключение для всех ошибок конвертера."""


class NetworkError(CurrencyError):
    """Ошибка сетевого взаимодействия с API."""


class ValidationError(CurrencyError):
    """Ошибка валидации пользовательского ввода."""


class ConversionError(CurrencyError):
    """Ошибка математической конвертации."""
