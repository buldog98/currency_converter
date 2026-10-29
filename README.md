
# Currency Converter

Консольное приложение для конвертации валют с актуальными курсами через REST API.

## Возможности
- Конвертация между 10+ валютами (коды ISO 4217)
- Актуальные курсы через ExchangeRate-API
- Финансовая точность вычислений (`decimal.Decimal`)
- In-memory кэширование курсов с TTL (15 минут)
- Обработка сетевых ошибок и невалидного ввода (Fail-Fast)

## Требования
- Python 3.14+
- pip

## Установка и запуск

1. Клонируйте репозиторий:
```bash
git clone <url-репозитория>
cd currency_converter
2. Создайте и активируйте виртуальное окружение:
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
3. source .venv/bin/activate Установите зависимости:
pip install -r requirements.txt
4. Запустите конвертацию (пример: 100 USD в RUB):
python -m currency_converter 100 USD RUB
Тестирование
Запуск unit-тестов:
python -m pytest tests/ -v
