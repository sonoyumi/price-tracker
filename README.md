# 🏷️ Price Tracker

<p>
  <a href="https://github.com/sonoyumi/price-tracker/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/sonoyumi/price-tracker/actions/workflows/ci.yml/badge.svg"></a>
  <img alt="Python" src="https://img.shields.io/badge/python-3.11%2B-blue?logo=python&logoColor=white">
  <img alt="httpx" src="https://img.shields.io/badge/httpx-BeautifulSoup-4B8BBE">
  <img alt="SQLite" src="https://img.shields.io/badge/SQLite-history-003B57?logo=sqlite&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-green">
</p>

**🇬🇧 [English](#en)** · **🇷🇺 [Русский](#ru)**

---

<a name="en"></a>

## 🇬🇧 English

A command-line tool that watches product prices on any website, keeps the price history
in SQLite and sends alerts to Telegram when a price drops, rises, reaches your target
or when a product goes out of stock or comes back.

### Features

- **Any website:** a CSS selector per product, or no selector at all when the shop publishes
  schema.org data (JSON-LD or `itemprop="price"`), which most online shops do for search engines.
- **Understands real-world prices:** `£51.77`, `1 240,00 €`, `$1,234.50`, `1.234,50`.
- **Alerts:** price down / up with percent, target price reached, back in stock, out of stock.
  The first check is silent (nothing to compare with), and a target alert fires once, not on every check.
- **History:** every check is stored in SQLite; `history` shows it, `export` saves CSV for Excel.
- **Polite by default:** own User-Agent, pause between requests to the same site, retries with
  exponential backoff on `429`/`5xx`, minimum interval of 10 minutes in `watch` mode.
- **Robust:** one broken page (404, changed layout) is reported and stored as an error without stopping
  the other products; a failed check never resets price comparisons.
- **Safe:** HTML in Telegram messages is escaped, the bot token never appears in errors or logs.

### Example

Using [books.toscrape.com](https://books.toscrape.com), a website made for scraping practice:

```bash
cp products.example.toml products.toml
price-tracker check
```

```
Товар                 Цена   Было   Наличие    Статус
--------------------  -----  -----  ---------  ------
A Light in the Attic  51.77  51.77  в наличии  ок
Tipping the Velvet    53.74  53.74  в наличии  ок
```

When something changes, alerts are printed and sent to Telegram:

```
📉 A Light in the Attic: 51.77 → 44.00 (-15.0%)
🎯 A Light in the Attic: цена 44.00 достигла цели 45.00
⛔ A Light in the Attic: закончился
```

### Commands

| Command | What it does |
|---|---|
| `price-tracker check` | Check all products once |
| `price-tracker watch --every 3h` | Check on a schedule until stopped (`30m`, `3h`, `1d`; minimum `10m`) |
| `price-tracker history <id> [-n 20]` | Price history of one product, newest first |
| `price-tracker export -o prices.csv` | Whole history to CSV (opens in Excel) |

Options: `--config products.toml`, `--db data/prices.db`.

### Configuration

`products.toml`:

```toml
[[product]]
id = "light-in-the-attic"            # used in commands
name = "A Light in the Attic"
url = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
price_selector = "p.price_color"     # optional if the shop has schema.org markup
stock_selector = "p.instock.availability"   # optional
target_price = 45.0                  # optional
```

`.env` (optional, for Telegram): `BOT_TOKEN`, `CHAT_ID`, `REQUEST_DELAY`, `USER_AGENT` — see `.env.example`.

### Quick start

```bash
git clone https://github.com/sonoyumi/price-tracker.git
cd price-tracker
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp products.example.toml products.toml
price-tracker check
```

Tests: `pytest` (57 tests: parsing on saved pages, alert rules, retries and pauses with a fake clock,
an end-to-end CLI run against a fake shop, Telegram via a mocked API — no network needed).

### Project structure

```
src/price_tracker/
├── parse.py    # price and stock from HTML: CSS selector -> JSON-LD -> itemprop
├── alerts.py   # rules: two observations -> alerts (pure logic)
├── fetch.py    # polite HTTP: User-Agent, per-site pause, retries with backoff
├── db.py       # price history in SQLite
├── notify.py   # console and Telegram
├── tracker.py  # one check cycle
├── config.py   # products.toml and .env
└── cli.py      # check / watch / history / export
```

> Respect each website's terms of use and `robots.txt`. If a shop offers an official API, prefer it.

### Author

**Vladyslav Shokun** ([@sonoyumi](https://github.com/sonoyumi)), Python developer: Telegram bots, web scraping, automation.

[![Telegram](https://img.shields.io/badge/Telegram-write%20me-2CA5E0?logo=telegram&logoColor=white)](https://t.me/sonoyumiii)
[![Email](https://img.shields.io/badge/Email-contact-EA4335?logo=gmail&logoColor=white)](mailto:sonoyumiii@gmail.com)

> 💼 Need to watch competitors' prices? Get in touch.

### License

MIT, see [LICENSE](LICENSE).

---

<a name="ru"></a>

## 🇷🇺 Русский

**[🇬🇧 English](#en)** · **🇷🇺 Русский**

Утилита командной строки, которая следит за ценами товаров на любых сайтах, хранит историю цен
в SQLite и присылает алерты в Telegram, когда цена упала, выросла, достигла вашей цели
или товар закончился и снова появился.

### Возможности

- **Любой сайт:** CSS-селектор на товар или вообще без селектора, если магазин публикует разметку
  schema.org (JSON-LD или `itemprop="price"`) — так делает большинство интернет-магазинов для поисковиков.
- **Понимает реальные цены:** `£51.77`, `1 240,00 €`, `$1,234.50`, `1.234,50`.
- **Алерты:** цена упала / выросла с процентом, достигнута целевая цена, снова в наличии, закончился.
  Первая проверка без алертов (не с чем сравнивать), алерт о цели приходит один раз, а не при каждой проверке.
- **История:** каждая проверка сохраняется в SQLite; `history` показывает её, `export` сохраняет CSV для Excel.
- **Вежливость:** свой User-Agent, пауза между запросами к одному сайту, повторы с нарастающей паузой
  при `429`/`5xx`, минимальный интервал 10 минут в режиме `watch`.
- **Надёжность:** одна сломанная страница (404, сменилась вёрстка) отмечается ошибкой и сохраняется,
  но не останавливает остальные товары; неудачная проверка не сбивает сравнение цен.
- **Безопасность:** HTML в сообщениях Telegram экранируется, токен бота не попадает в ошибки и логи.

### Пример

На [books.toscrape.com](https://books.toscrape.com) — сайте, созданном для практики парсинга:

```bash
cp products.example.toml products.toml
price-tracker check
```

Вывод и алерты — как в английском разделе выше.

### Команды

| Команда | Что делает |
|---|---|
| `price-tracker check` | Проверить все товары один раз |
| `price-tracker watch --every 3h` | Проверять по расписанию до остановки (`30m`, `3h`, `1d`; минимум `10m`) |
| `price-tracker history <id> [-n 20]` | История цены товара, новые сверху |
| `price-tracker export -o prices.csv` | Вся история в CSV (открывается в Excel) |

Опции: `--config products.toml`, `--db data/prices.db`.

### Настройка

Список товаров — `products.toml` (пример и описание полей — в `products.example.toml`).
Telegram (необязательно) — `.env`: `BOT_TOKEN`, `CHAT_ID`, `REQUEST_DELAY`, `USER_AGENT` (см. `.env.example`).

### Быстрый старт

```bash
git clone https://github.com/sonoyumi/price-tracker.git
cd price-tracker
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp products.example.toml products.toml
price-tracker check
```

Тесты: `pytest` (57 тестов: разбор сохранённых страниц, правила алертов, повторы и паузы с поддельными часами,
сквозной запуск CLI на поддельном магазине, Telegram через заглушку API — сеть не нужна).

### Структура проекта

```
src/price_tracker/
├── parse.py    # цена и наличие из HTML: CSS-селектор -> JSON-LD -> itemprop
├── alerts.py   # правила: два наблюдения -> алерты (чистая логика)
├── fetch.py    # вежливый HTTP: User-Agent, пауза на сайт, повторы
├── db.py       # история цен в SQLite
├── notify.py   # консоль и Telegram
├── tracker.py  # один цикл проверки
├── config.py   # products.toml и .env
└── cli.py      # check / watch / history / export
```

> Соблюдайте правила сайтов и `robots.txt`. Если у магазина есть официальный API — лучше использовать его.

### Автор

**Vladyslav Shokun** ([@sonoyumi](https://github.com/sonoyumi)) — Python-разработчик: Telegram-боты, парсинг, автоматизация.

[![Telegram](https://img.shields.io/badge/Telegram-write%20me-2CA5E0?logo=telegram&logoColor=white)](https://t.me/sonoyumiii)
[![Email](https://img.shields.io/badge/Email-contact-EA4335?logo=gmail&logoColor=white)](mailto:sonoyumiii@gmail.com)

> 💼 Нужно следить за ценами конкурентов? Напишите мне.

### Лицензия

MIT — см. [LICENSE](LICENSE).
