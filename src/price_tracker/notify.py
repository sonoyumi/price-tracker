"""Where alerts go: always the console, plus Telegram when BOT_TOKEN and CHAT_ID are set."""

from __future__ import annotations

from html import escape
from typing import Protocol

import httpx

from price_tracker.models import Alert

API_URL = "https://api.telegram.org"
MESSAGE_LIMIT = 4096


class Notifier(Protocol):
    def send(self, alerts: list[Alert]) -> None: ...


class NotifyError(RuntimeError):
    pass


class ConsoleNotifier:
    def send(self, alerts: list[Alert]) -> None:
        for alert in alerts:
            print(f"  {alert.text}")


class TelegramNotifier:
    def __init__(self, token: str, chat_id: str, client: httpx.Client | None = None) -> None:
        self._token = token
        self._chat_id = chat_id
        self._client = client or httpx.Client(timeout=15)

    def send(self, alerts: list[Alert]) -> None:
        if not alerts:
            return
        lines = [f'{escape(a.text)}\n<a href="{escape(a.product.url)}">открыть</a>' for a in alerts]
        text = "\n\n".join(lines)[:MESSAGE_LIMIT]
        try:
            response = self._client.post(
                f"{API_URL}/bot{self._token}/sendMessage",
                data={"chat_id": self._chat_id, "text": text, "parse_mode": "HTML", "disable_web_page_preview": "true"},
            )
        except httpx.HTTPError as exc:
            raise NotifyError(f"Telegram: network error {type(exc).__name__}") from None
        payload = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
        if response.status_code != 200 or not payload.get("ok"):
            # The token is part of the URL, so it is never included in the message.
            raise NotifyError(f"Telegram rejected the message: {payload.get('description', response.status_code)}")


class MultiNotifier:
    def __init__(self, *notifiers: Notifier) -> None:
        self._notifiers = notifiers

    def send(self, alerts: list[Alert]) -> None:
        for notifier in self._notifiers:
            notifier.send(alerts)
