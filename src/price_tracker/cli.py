"""Command line: price-tracker check | watch | history | export."""

from __future__ import annotations

import argparse
import csv
import re
import sys
import time
from pathlib import Path

from price_tracker import __version__
from price_tracker.alerts import fmt_price
from price_tracker.config import ConfigError, Settings, load_products, load_settings
from price_tracker.db import History
from price_tracker.fetch import Fetcher
from price_tracker.models import Product
from price_tracker.notify import ConsoleNotifier, MultiNotifier, Notifier, TelegramNotifier
from price_tracker.tracker import CheckResult, check_all

EXIT_USER_ERROR = 2
MIN_INTERVAL = 10 * 60  # never poll a shop more often than every 10 minutes
_UNITS = {"m": 60, "h": 3600, "d": 86400}


def parse_interval(text: str) -> int:
    match = re.fullmatch(r"\s*(\d+)\s*([mhd])\s*", text.lower())
    if not match:
        raise ValueError("interval looks like 30m, 3h or 1d")
    seconds = int(match.group(1)) * _UNITS[match.group(2)]
    if seconds < MIN_INTERVAL:
        raise ValueError("interval must be at least 10m: be polite to the shops")
    return seconds


def _stock(value: bool | None) -> str:
    return {True: "в наличии", False: "нет", None: "—"}[value]


def format_results(results: list[CheckResult]) -> str:
    rows = [["Товар", "Цена", "Было", "Наличие", "Статус"]]
    for r in results:
        cur, prev = r.current, r.previous
        if cur.error:
            status = f"ошибка: {cur.error}"
        else:
            status = f"{len(r.alerts)} алерт(ов)" if r.alerts else "ок"
        rows.append(
            [
                r.product.name[:40],
                fmt_price(cur.price) if cur.price is not None else "—",
                fmt_price(prev.price) if prev and prev.price is not None else "—",
                _stock(cur.in_stock),
                status,
            ]
        )
    widths = [max(len(row[i]) for row in rows) for i in range(len(rows[0]))]
    lines = ["  ".join(v.ljust(w) for v, w in zip(row, widths, strict=True)).rstrip() for row in rows]
    lines.insert(1, "  ".join("-" * w for w in widths))
    return "\n".join(lines)


def build_notifier(settings: Settings) -> Notifier:
    if settings.telegram_enabled:
        return MultiNotifier(ConsoleNotifier(), TelegramNotifier(settings.bot_token, settings.chat_id))
    return ConsoleNotifier()


def run_check(products: list[Product], fetcher: Fetcher, history: History, notifier: Notifier) -> None:
    results, notify_error = check_all(products, fetcher, history, notifier)
    print()
    print(format_results(results))
    if notify_error:
        print(f"\nВнимание: {notify_error}", file=sys.stderr)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="price-tracker", description="Track product prices and get alerts.")
    parser.add_argument("--config", type=Path, default=Path("products.toml"), help="product list (products.toml)")
    parser.add_argument("--db", type=Path, default=Path("data/prices.db"), help="history database")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check", help="check all products once")
    watch = sub.add_parser("watch", help="check on a schedule until stopped (Ctrl+C)")
    watch.add_argument("--every", default="3h", help="interval: 30m, 3h, 1d (default 3h, minimum 10m)")
    hist = sub.add_parser("history", help="price history of one product")
    hist.add_argument("product_id")
    hist.add_argument("-n", type=int, default=20, help="how many records (20)")
    export = sub.add_parser("export", help="export the whole history to CSV")
    export.add_argument("-o", "--output", type=Path, default=Path("prices.csv"))
    return parser


def _history(history: History, product_id: str, limit: int) -> int:
    rows = history.history(product_id, limit)
    if not rows:
        print(f"Нет истории для {product_id!r}", file=sys.stderr)
        return EXIT_USER_ERROR
    for o in rows:
        value = f"ошибка: {o.error}" if o.error else f"{fmt_price(o.price)}  {_stock(o.in_stock)}"
        print(f"{o.checked_at:%Y-%m-%d %H:%M}  {value}")
    return 0


def _export(history: History, output: Path) -> int:
    with output.open("w", newline="", encoding="utf-8-sig") as file:  # utf-8-sig: Excel opens it correctly
        writer = csv.writer(file, delimiter=";")
        writer.writerow(["product_id", "checked_at", "price", "in_stock", "error"])
        for row in history.all_rows():
            writer.writerow([row["product_id"], row["checked_at"], row["price"], row["in_stock"], row["error"]])
    print(f"Сохранено: {output}")
    return 0


def run(argv: list[str] | None = None, fetcher: Fetcher | None = None) -> int:
    args = build_parser().parse_args(argv)
    history = History(args.db)
    try:
        if args.command == "history":
            return _history(history, args.product_id, args.n)
        if args.command == "export":
            return _export(history, args.output)

        try:
            products = load_products(args.config)
            interval = parse_interval(args.every) if args.command == "watch" else 0
            settings = load_settings()
        except (ConfigError, ValueError) as exc:
            print(f"Ошибка: {exc}", file=sys.stderr)
            return EXIT_USER_ERROR

        fetcher = fetcher or Fetcher(settings.user_agent, delay=settings.request_delay)
        notifier = build_notifier(settings)
        try:
            if args.command == "check":
                run_check(products, fetcher, history, notifier)
                return 0
            print(f"Проверяю {len(products)} товар(ов) каждые {args.every}. Остановить: Ctrl+C")
            while True:
                run_check(products, fetcher, history, notifier)
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nОстановлено.")
            return 0
        finally:
            fetcher.close()
    finally:
        history.close()


def main() -> None:
    sys.exit(run())
