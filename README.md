# price-tracker

Короткое описание: что делает проект и зачем.

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env   # заполнить своими значениями
price-tracker           # или: python -m price_tracker
```

## Тесты и линтер

```bash
pytest
ruff check .
```

## Структура

```
src/price_tracker/   код
tests/              тесты
```
