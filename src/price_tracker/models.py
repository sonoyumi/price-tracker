"""Data classes shared by all modules."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Product:
    id: str
    name: str
    url: str
    price_selector: str | None = None  # CSS selector; None -> schema.org / meta tags
    stock_selector: str | None = None
    target_price: float | None = None  # alert when the price drops to this level or below


@dataclass(frozen=True)
class Observation:
    """One check of one product. `error` is set when the page could not be fetched or parsed."""

    price: float | None
    in_stock: bool | None
    checked_at: datetime | None = None
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.error is None and self.price is not None


@dataclass(frozen=True)
class Alert:
    product: Product
    kind: str  # price_down | price_up | target | in_stock | out_of_stock
    text: str
