"""End-to-end: real CLI, real SQLite, fake shop behind httpx.MockTransport."""

import csv
from pathlib import Path

import httpx
import pytest

from price_tracker.cli import EXIT_USER_ERROR, parse_interval, run
from price_tracker.fetch import Fetcher

BOOK_PAGE = (Path(__file__).parent / "fixtures" / "books_product.html").read_text(encoding="utf-8")

PRODUCTS = """
[[product]]
id = "attic"
name = "A Light in the Attic"
url = "https://shop.test/attic"
price_selector = "p.price_color"
stock_selector = "p.instock"
target_price = 45.0

[[product]]
id = "gone"
name = "Removed product"
url = "https://shop.test/gone"
price_selector = "p.price_color"
"""


class FakeShop:
    def __init__(self):
        self.price = "£51.77"
        self.stock = "In stock (22 available)"

    def handler(self, request: httpx.Request) -> httpx.Response:
        if request.url.path == "/gone":
            return httpx.Response(404)
        html = BOOK_PAGE.replace("£51.77", self.price).replace("In stock (22 available)", self.stock)
        return httpx.Response(200, text=html)

    def fetcher(self) -> Fetcher:
        client = httpx.Client(transport=httpx.MockTransport(self.handler))
        return Fetcher("test", delay=0, retries=0, client=client, sleep=lambda s: None)


@pytest.fixture
def env(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # no real .env, so alerts go to the console only
    for name in ("BOT_TOKEN", "CHAT_ID"):
        monkeypatch.delenv(name, raising=False)
    (tmp_path / "products.toml").write_text(PRODUCTS, encoding="utf-8")
    return tmp_path


def test_check_detects_drop_target_and_stock(env, capsys):
    shop = FakeShop()
    assert run(["check"], fetcher=shop.fetcher()) == 0
    first = capsys.readouterr().out
    assert "51.77" in first and "ошибка: HTTP 404" in first  # one broken product does not stop the rest

    shop.price, shop.stock = "£44.00", "Out of stock"
    assert run(["check"], fetcher=shop.fetcher()) == 0
    second = capsys.readouterr().out
    assert "📉 A Light in the Attic: 51.77 → 44.00 (-15.0%)" in second
    assert "🎯" in second and "⛔" in second


def test_history_and_export(env, capsys):
    shop = FakeShop()
    run(["check"], fetcher=shop.fetcher())
    shop.price = "£49.00"
    run(["check"], fetcher=shop.fetcher())
    capsys.readouterr()

    assert run(["history", "attic"]) == 0
    lines = capsys.readouterr().out.strip().splitlines()
    assert "49.00" in lines[0] and "51.77" in lines[1]  # newest first

    assert run(["export", "-o", "out.csv"]) == 0
    with open(env / "out.csv", encoding="utf-8-sig", newline="") as file:
        rows = list(csv.reader(file, delimiter=";"))
    assert rows[0] == ["product_id", "checked_at", "price", "in_stock", "error"]
    assert len(rows) == 5  # header + 2 checks x 2 products


def test_unknown_product_history(env, capsys):
    assert run(["history", "nope"]) == EXIT_USER_ERROR


def test_missing_config_is_a_user_error(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert run(["check"]) == EXIT_USER_ERROR
    assert "products.example.toml" in capsys.readouterr().err


@pytest.mark.parametrize(("text", "seconds"), [("30m", 1800), ("3h", 10800), ("1d", 86400)])
def test_parse_interval(text, seconds):
    assert parse_interval(text) == seconds


@pytest.mark.parametrize("text", ["5m", "10", "fast"])
def test_bad_or_too_short_interval(text):
    with pytest.raises(ValueError):
        parse_interval(text)
