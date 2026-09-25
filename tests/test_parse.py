from pathlib import Path

import pytest

from price_tracker.models import Product
from price_tracker.parse import ParseError, extract, parse_price, parse_stock

FIXTURES = Path(__file__).parent / "fixtures"


def page(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def product(**kwargs) -> Product:
    return Product(id="p", name="P", url="https://example.com/p", **kwargs)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("£51.77", 51.77),
        ("1 240,00 €", 1240.0),
        ("1 249,90 ₴", 1249.9),
        ("$1,234.50", 1234.5),
        ("1.234,50", 1234.5),
        ("1,234", 1234.0),
        ("39", 39.0),
        (19.5, 19.5),
        ("по запросу", None),
        ("", None),
        (None, None),
    ],
)
def test_parse_price(raw, expected):
    assert parse_price(raw) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("In stock (22 available)", True),
        ("В наличии", True),
        ("Out of stock", False),
        ("Currently unavailable", False),
        ("Нет в наличии", False),
        ("Call us", None),
    ],
)
def test_parse_stock(text, expected):
    assert parse_stock(text) is expected


def test_css_selectors_on_books_page():
    found = extract(page("books_product.html"), product(price_selector="p.price_color", stock_selector="p.instock"))
    assert found.price == 51.77
    assert found.in_stock is True


def test_missing_stock_element_means_out_of_stock():
    found = extract(page("books_product.html"), product(price_selector="p.price_color", stock_selector=".nope"))
    assert found.in_stock is False


def test_json_ld_graph_without_any_selector():
    found = extract(page("shop_jsonld.html"), product())
    assert found.price == 1249.9
    assert found.in_stock is False  # schema.org/OutOfStock


def test_selector_wins_over_json_ld():
    found = extract(page("shop_jsonld.html"), product(price_selector="span.price"))
    assert found.price == 1249.9


def test_meta_itemprop_price():
    assert extract(page("shop_meta.html"), product()).price == 39.99


def test_selector_that_matches_nothing_is_a_clear_error():
    with pytest.raises(ParseError, match="did the page change"):
        extract(page("books_product.html"), product(price_selector=".price-new"))


def test_page_without_price():
    with pytest.raises(ParseError, match="price not found"):
        extract("<html><body>Hello</body></html>", product())
