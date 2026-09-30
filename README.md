# 🏷️ Price Tracker

<p>
  <a href="https://github.com/sonoyumi/price-tracker/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/sonoyumi/price-tracker/actions/workflows/ci.yml/badge.svg"></a>
  <img alt="Python" src="https://img.shields.io/badge/python-3.11%2B-blue?logo=python&logoColor=white">
  <img alt="httpx" src="https://img.shields.io/badge/httpx-BeautifulSoup-4B8BBE">
  <img alt="SQLite" src="https://img.shields.io/badge/SQLite-history-003B57?logo=sqlite&logoColor=white">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-green">
</p>

**🇬🇧 [English](#en)** · **🇮🇹 [Italiano](#it)** · **🇺🇦 [Українська](#uk)** · **🇷🇺 [Русский](#ru)**

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
[![LinkedIn](https://img.shields.io/badge/LinkedIn-profile-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/vladyslav-shokun/)

> 💼 Need to watch competitors' prices? Get in touch.

### License

MIT, see [LICENSE](LICENSE).

---

<a name="it"></a>

## 🇮🇹 Italiano

**[🇬🇧 English](#en)** · **🇮🇹 Italiano** · **[🇺🇦 Українська](#uk)** · **[🇷🇺 Русский](#ru)**

Uno strumento da riga di comando che tiene d'occhio i prezzi dei prodotti su qualsiasi sito, conserva lo storico
dei prezzi in SQLite e invia avvisi su Telegram quando un prezzo scende, sale, raggiunge il tuo obiettivo
o quando un prodotto va esaurito o torna disponibile.

### Funzionalità

- **Qualsiasi sito:** un selettore CSS per prodotto, oppure nessun selettore se il negozio pubblica
  i dati schema.org (JSON-LD o `itemprop="price"`), come fa la maggior parte dei negozi online per i motori di ricerca.
- **Capisce i prezzi reali:** `£51.77`, `1 240,00 €`, `$1,234.50`, `1.234,50`.
- **Avvisi:** prezzo in calo / in aumento con percentuale, prezzo obiettivo raggiunto, di nuovo disponibile, esaurito.
  Il primo controllo è silenzioso (non c'è nulla con cui confrontare) e l'avviso sull'obiettivo arriva una sola volta, non a ogni controllo.
- **Storico:** ogni controllo viene salvato in SQLite; `history` lo mostra, `export` lo salva in CSV per Excel.
- **Educato per impostazione predefinita:** User-Agent proprio, pausa tra le richieste allo stesso sito, nuovi tentativi con
  backoff esponenziale su `429`/`5xx`, intervallo minimo di 10 minuti in modalità `watch`.
- **Robusto:** una pagina rotta (404, layout cambiato) viene segnalata e salvata come errore senza fermare
  gli altri prodotti; un controllo fallito non azzera mai il confronto dei prezzi.
- **Sicuro:** l'HTML nei messaggi Telegram viene sottoposto a escaping, il token del bot non compare mai negli errori né nei log.

### Esempio

Con [books.toscrape.com](https://books.toscrape.com), un sito creato apposta per esercitarsi con lo scraping:

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

Quando qualcosa cambia, gli avvisi vengono stampati e inviati su Telegram:

```
📉 A Light in the Attic: 51.77 → 44.00 (-15.0%)
🎯 A Light in the Attic: цена 44.00 достигла цели 45.00
⛔ A Light in the Attic: закончился
```

> L'output del programma è in russo: colonne Prodotto / Prezzo / Prima / Disponibilità / Stato;
> gli avvisi dicono "il prezzo 44.00 ha raggiunto l'obiettivo 45.00" ed "esaurito".

### Comandi

| Comando | Cosa fa |
|---|---|
| `price-tracker check` | Controlla tutti i prodotti una volta |
| `price-tracker watch --every 3h` | Controlla secondo una pianificazione fino all'arresto (`30m`, `3h`, `1d`; minimo `10m`) |
| `price-tracker history <id> [-n 20]` | Storico dei prezzi di un prodotto, dal più recente |
| `price-tracker export -o prices.csv` | Tutto lo storico in CSV (si apre in Excel) |

Opzioni: `--config products.toml`, `--db data/prices.db`.

### Configurazione

`products.toml`:

```toml
[[product]]
id = "light-in-the-attic"            # usato nei comandi
name = "A Light in the Attic"
url = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
price_selector = "p.price_color"     # facoltativo se il negozio ha il markup schema.org
stock_selector = "p.instock.availability"   # facoltativo
target_price = 45.0                  # facoltativo
```

`.env` (facoltativo, per Telegram): `BOT_TOKEN`, `CHAT_ID`, `REQUEST_DELAY`, `USER_AGENT` — vedi `.env.example`.

### Avvio rapido

```bash
git clone https://github.com/sonoyumi/price-tracker.git
cd price-tracker
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp products.example.toml products.toml
price-tracker check
```

Test: `pytest` (57 test: parsing su pagine salvate, regole degli avvisi, nuovi tentativi e pause con un orologio finto,
un'esecuzione end-to-end della CLI su un negozio finto, Telegram tramite un'API simulata — non serve la rete).

### Struttura del progetto

```
src/price_tracker/
├── parse.py    # prezzo e disponibilità dall'HTML: selettore CSS -> JSON-LD -> itemprop
├── alerts.py   # regole: due osservazioni -> avvisi (logica pura)
├── fetch.py    # HTTP educato: User-Agent, pausa per sito, nuovi tentativi con backoff
├── db.py       # storico dei prezzi in SQLite
├── notify.py   # console e Telegram
├── tracker.py  # un ciclo di controllo
├── config.py   # products.toml e .env
└── cli.py      # check / watch / history / export
```

> Rispetta i termini d'uso e il `robots.txt` di ogni sito. Se un negozio offre un'API ufficiale, preferisci quella.

### Autore

**Vladyslav Shokun** ([@sonoyumi](https://github.com/sonoyumi)), sviluppatore Python: bot Telegram, web scraping, automazione.

[![Telegram](https://img.shields.io/badge/Telegram-write%20me-2CA5E0?logo=telegram&logoColor=white)](https://t.me/sonoyumiii)
[![Email](https://img.shields.io/badge/Email-contact-EA4335?logo=gmail&logoColor=white)](mailto:sonoyumiii@gmail.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-profile-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/vladyslav-shokun/)

> 💼 Devi tenere d'occhio i prezzi dei concorrenti? Scrivimi.

### Licenza

MIT, vedi [LICENSE](LICENSE).

---

<a name="uk"></a>

## 🇺🇦 Українська

**[🇬🇧 English](#en)** · **[🇮🇹 Italiano](#it)** · **🇺🇦 Українська** · **[🇷🇺 Русский](#ru)**

Утиліта командного рядка, яка стежить за цінами товарів на будь-яких сайтах, зберігає історію цін
у SQLite та надсилає сповіщення в Telegram, коли ціна впала, зросла, досягла вашої цілі
або товар закінчився й знову з'явився.

### Можливості

- **Будь-який сайт:** CSS-селектор на товар або взагалі без селектора, якщо магазин публікує розмітку
  schema.org (JSON-LD або `itemprop="price"`) — так робить більшість інтернет-магазинів для пошукових систем.
- **Розуміє реальні ціни:** `£51.77`, `1 240,00 €`, `$1,234.50`, `1.234,50`.
- **Сповіщення:** ціна впала / зросла з відсотком, досягнуто цільової ціни, знову в наявності, закінчився.
  Перша перевірка — без сповіщень (немає з чим порівнювати), а сповіщення про ціль приходить один раз, а не при кожній перевірці.
- **Історія:** кожна перевірка зберігається в SQLite; `history` показує її, `export` зберігає CSV для Excel.
- **Ввічливість:** власний User-Agent, пауза між запитами до одного сайту, повтори з наростаючою (експоненційною) паузою
  при `429`/`5xx`, мінімальний інтервал 10 хвилин у режимі `watch`.
- **Надійність:** одна зламана сторінка (404, змінилася верстка) позначається як помилка й зберігається,
  але не зупиняє решту товарів; невдала перевірка ніколи не збиває порівняння цін.
- **Безпека:** HTML у повідомленнях Telegram екранується, токен бота не потрапляє в помилки й логи.

### Приклад

На [books.toscrape.com](https://books.toscrape.com) — сайті, створеному для практики парсингу:

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

Коли щось змінюється, сповіщення виводяться в консоль і надсилаються в Telegram:

```
📉 A Light in the Attic: 51.77 → 44.00 (-15.0%)
🎯 A Light in the Attic: цена 44.00 достигла цели 45.00
⛔ A Light in the Attic: закончился
```

> Програма виводить текст російською: колонки Товар / Ціна / Було / Наявність / Статус;
> сповіщення: «ціна 44.00 досягла цілі 45.00» і «закінчився».

### Команди

| Команда | Що робить |
|---|---|
| `price-tracker check` | Перевірити всі товари один раз |
| `price-tracker watch --every 3h` | Перевіряти за розкладом до зупинки (`30m`, `3h`, `1d`; мінімум `10m`) |
| `price-tracker history <id> [-n 20]` | Історія ціни товару, нові зверху |
| `price-tracker export -o prices.csv` | Уся історія в CSV (відкривається в Excel) |

Опції: `--config products.toml`, `--db data/prices.db`.

### Налаштування

`products.toml`:

```toml
[[product]]
id = "light-in-the-attic"            # використовується в командах
name = "A Light in the Attic"
url = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
price_selector = "p.price_color"     # необов'язково, якщо в магазину є розмітка schema.org
stock_selector = "p.instock.availability"   # необов'язково
target_price = 45.0                  # необов'язково
```

`.env` (необов'язково, для Telegram): `BOT_TOKEN`, `CHAT_ID`, `REQUEST_DELAY`, `USER_AGENT` — див. `.env.example`.

### Швидкий старт

```bash
git clone https://github.com/sonoyumi/price-tracker.git
cd price-tracker
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp products.example.toml products.toml
price-tracker check
```

Тести: `pytest` (57 тестів: розбір збережених сторінок, правила сповіщень, повтори й паузи з підробленим годинником,
наскрізний запуск CLI на підробленому магазині, Telegram через заглушку API — мережа не потрібна).

### Структура проєкту

```
src/price_tracker/
├── parse.py    # ціна й наявність з HTML: CSS-селектор -> JSON-LD -> itemprop
├── alerts.py   # правила: два спостереження -> сповіщення (чиста логіка)
├── fetch.py    # ввічливий HTTP: User-Agent, пауза на сайт, повтори з backoff
├── db.py       # історія цін у SQLite
├── notify.py   # консоль і Telegram
├── tracker.py  # один цикл перевірки
├── config.py   # products.toml і .env
└── cli.py      # check / watch / history / export
```

> Дотримуйтеся правил користування сайтів і `robots.txt`. Якщо в магазину є офіційний API — краще використовувати його.

### Автор

**Vladyslav Shokun** ([@sonoyumi](https://github.com/sonoyumi)) — Python-розробник: Telegram-боти, парсинг, автоматизація.

[![Telegram](https://img.shields.io/badge/Telegram-write%20me-2CA5E0?logo=telegram&logoColor=white)](https://t.me/sonoyumiii)
[![Email](https://img.shields.io/badge/Email-contact-EA4335?logo=gmail&logoColor=white)](mailto:sonoyumiii@gmail.com)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-profile-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/vladyslav-shokun/)

> 💼 Потрібно стежити за цінами конкурентів? Напишіть мені.

### Ліцензія

MIT — див. [LICENSE](LICENSE).

---

<a name="ru"></a>

## 🇷🇺 Русский

**[🇬🇧 English](#en)** · **[🇮🇹 Italiano](#it)** · **[🇺🇦 Українська](#uk)** · **🇷🇺 Русский**

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
[![LinkedIn](https://img.shields.io/badge/LinkedIn-profile-0A66C2?logo=linkedin&logoColor=white)](https://www.linkedin.com/in/vladyslav-shokun/)

> 💼 Нужно следить за ценами конкурентов? Напишите мне.

### Лицензия

MIT — см. [LICENSE](LICENSE).
