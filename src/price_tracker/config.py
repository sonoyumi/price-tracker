"""Product list (products.toml) and settings (.env)."""

from __future__ import annotations

import os
import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

from price_tracker.models import Product

_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class Settings:
    bot_token: str = field(repr=False)  # never shown in logs
    chat_id: str
    user_agent: str
    request_delay: float  # seconds between requests to the same site

    @property
    def telegram_enabled(self) -> bool:
        return bool(self.bot_token and self.chat_id)


def load_settings(env_file: Path | None = None) -> Settings:
    load_dotenv(env_file or Path.cwd() / ".env")  # only the .env of the current folder, never a parent's
    try:
        delay = float(os.getenv("REQUEST_DELAY", "").strip() or 2)
    except ValueError:
        raise ConfigError("REQUEST_DELAY must be a number of seconds") from None
    return Settings(
        bot_token=os.getenv("BOT_TOKEN", "").strip(),
        chat_id=os.getenv("CHAT_ID", "").strip(),
        user_agent=os.getenv("USER_AGENT", "").strip()
        or "price-tracker/0.1 (+https://github.com/sonoyumi/price-tracker)",
        request_delay=max(delay, 0.0),
    )


def load_products(path: Path) -> list[Product]:
    if not path.exists():
        raise ConfigError(f"{path} not found: copy products.example.toml to products.toml")
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"{path}: {exc}") from None

    items = data.get("product", [])
    if not items:
        raise ConfigError(f"{path}: add at least one [[product]] section")

    products: list[Product] = []
    seen: set[str] = set()
    for i, item in enumerate(items, start=1):
        where = f"{path.name}, product #{i}"
        for key in ("id", "name", "url"):
            if not str(item.get(key, "")).strip():
                raise ConfigError(f"{where}: '{key}' is required")
        pid = str(item["id"])
        if not _ID_RE.match(pid):
            raise ConfigError(f"{where}: id {pid!r} must be lowercase latin letters, digits, '-' or '_'")
        if pid in seen:
            raise ConfigError(f"{where}: duplicate id {pid!r}")
        if not str(item["url"]).startswith(("http://", "https://")):
            raise ConfigError(f"{where}: url must start with http:// or https://")
        target = item.get("target_price")
        if target is not None and (not isinstance(target, int | float) or target <= 0):
            raise ConfigError(f"{where}: target_price must be a positive number")
        seen.add(pid)
        products.append(
            Product(
                id=pid,
                name=str(item["name"]),
                url=str(item["url"]),
                price_selector=item.get("price_selector") or None,
                stock_selector=item.get("stock_selector") or None,
                target_price=float(target) if target is not None else None,
            )
        )
    return products
