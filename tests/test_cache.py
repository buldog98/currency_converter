"""Unit-тесты модуля кэширования (api_client.py — класс CachedRates)."""

import time

from currency_converter.api_client import CachedRates


class TestCachedRates:
    """Тесты класса CachedRates."""

    def test_cache_hit(self):
        """Проверка получения актуальной записи."""
        from decimal import Decimal

        rates = {"USD": Decimal("1.0"), "RUB": Decimal("92.5")}
        cache = CachedRates(rates=rates, timestamp=time.time(), ttl=900)
        assert cache.is_expired() is False

    def test_cache_expired(self):
        """Проверка устаревания записи."""
        from decimal import Decimal

        rates = {"USD": Decimal("1.0")}
        # Создаём запись с timestamp в прошлом
        cache = CachedRates(
            rates=rates, timestamp=time.time() - 1000, ttl=900
        )
        assert cache.is_expired() is True

    def test_cache_fresh_boundary(self):
        """Проверка граничного условия TTL."""
        from decimal import Decimal

        rates = {"USD": Decimal("1.0")}
        cache = CachedRates(rates=rates, timestamp=time.time(), ttl=0)
        # Небольшая задержка, чтобы разница времени стала > 0
        time.sleep(0.01)
        assert cache.is_expired() is True


