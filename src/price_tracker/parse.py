"""Extracting price and availability from a product page.

Order of attempts: the CSS selector from the config -> schema.org JSON-LD -> <meta itemprop="price">.
Many shops embed JSON-LD for search engines, so a product often works without any selector at all.
"""

from __future__ import annotations

import json
import re
from typing import Any

from bs4 import BeautifulSoup

from price_tracker.models import Observation, Product

_NUMBER_CHARS = re.compile(r"[^\d,.\-]")
_OUT_OF_STOCK = re.compile(r"out of stock|sold out|unavailable|нет в наличии|закончил|распродан", re.I)
_IN_STOCK = re.compile(r"in stock|available|в наличии|есть", re.I)


class ParseError(ValueError):
    pass


def parse_price(value: Any) -> float | None:
    """'£51.77', '1 240,00 €', '1,234.50', '1.234,50', 7 -> float; anything else -> None."""
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int | float):
        return float(value)
    text = _NUMBER_CHARS.sub("", str(value).replace(" ", ""))
    if not text or text in {"-", ".", ","}:
        return None
    if "," in text and "." in text:
        if text.rfind(",") > text.rfind("."):  # the separator that comes last is the decimal one
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    elif "," in text:
        whole, _, frac = text.rpartition(",")
        text = f"{whole}.{frac}" if text.count(",") == 1 and len(frac) != 3 else text.replace(",", "")
    try:
        return float(text)
    except ValueError:
        return None


def parse_stock(text: str) -> bool | None:
    if _OUT_OF_STOCK.search(text):  # checked first: "unavailable" contains "available"
        return False
    if _IN_STOCK.search(text):
        return True
    return None


def _json_ld_offers(soup: BeautifulSoup) -> list[dict]:
    offers: list[dict] = []

    def walk(node: Any) -> None:
        if isinstance(node, list):
            for item in node:
                walk(item)
        elif isinstance(node, dict):
            types = node.get("@type")
            types = types if isinstance(types, list) else [types]
            if "Product" in types and "offers" in node:
                found = node["offers"]
                offers.extend(found if isinstance(found, list) else [found])
            for key in ("@graph", "mainEntity"):
                if key in node:
                    walk(node[key])

    for script in soup.find_all("script", type="application/ld+json"):
        try:
            walk(json.loads(script.string or ""))
        except json.JSONDecodeError:
            continue
    return [o for o in offers if isinstance(o, dict)]


def extract(html: str, product: Product) -> Observation:
    soup = BeautifulSoup(html, "html.parser")
    price: float | None = None
    in_stock: bool | None = None

    if product.price_selector:
        node = soup.select_one(product.price_selector)
        if node is None:
            raise ParseError(f"price selector {product.price_selector!r} matched nothing (did the page change?)")
        price = parse_price(node.get("content") or node.get_text(" ", strip=True))

    offers = _json_ld_offers(soup)
    if price is None:
        for offer in offers:
            price = parse_price(offer.get("price") or offer.get("lowPrice"))
            if price is not None:
                break
    if price is None:
        meta = soup.select_one('[itemprop="price"]')
        if meta is not None:
            price = parse_price(meta.get("content") or meta.get_text(strip=True))
    if price is None:
        raise ParseError("price not found: set price_selector for this product")

    if product.stock_selector:
        node = soup.select_one(product.stock_selector)
        in_stock = parse_stock(node.get_text(" ", strip=True)) if node is not None else False
    else:
        for offer in offers:
            availability = str(offer.get("availability", ""))
            if availability:
                in_stock = "InStock" in availability or "PreOrder" in availability
                break
    return Observation(price=price, in_stock=in_stock)
