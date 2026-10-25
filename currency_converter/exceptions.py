"""Иерархия кастомных исключений проекта."""


class CurrencyError(Exception):
    """Базовое исключение для всех ошибок конвертера."""
    pass


class NetworkError(CurrencyError):
    """Ошибка сетевого взаимодействия с API."""
    pass


class ValidationError(CurrencyError):
    """Ошибка валидации пользовательского ввода."""
    pass


class ConversionError(CurrencyError):
    """Ошибка математической конвертации."""
    pass

