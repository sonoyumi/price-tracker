"""Polite page fetching: timeouts, retries, and a pause between requests to the same site."""

from __future__ import annotations

import time
from collections.abc import Callable
from urllib.parse import urlsplit

import httpx

RETRY_STATUSES = {429, 500, 502, 503, 504}


class FetchError(RuntimeError):
    pass


class Fetcher:
    def __init__(
        self,
        user_agent: str,
        delay: float = 2.0,
        retries: int = 2,
        client: httpx.Client | None = None,
        sleep: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._client = client or httpx.Client(timeout=20, follow_redirects=True)
        self._client.headers["User-Agent"] = user_agent
        self._delay = delay
        self._retries = retries
        self._sleep = sleep
        self._clock = clock
        self._last_request: dict[str, float] = {}  # host -> time of the last request

    def close(self) -> None:
        self._client.close()

    def _wait_for_host(self, host: str) -> None:
        last = self._last_request.get(host)
        if last is not None:
            remaining = self._delay - (self._clock() - last)
            if remaining > 0:
                self._sleep(remaining)
        self._last_request[host] = self._clock()

    def get(self, url: str) -> str:
        host = urlsplit(url).netloc
        error = "unknown error"
        for attempt in range(self._retries + 1):
            if attempt:
                self._sleep(2**attempt)  # 2 s, 4 s ...
            self._wait_for_host(host)
            try:
                response = self._client.get(url)
            except httpx.HTTPError as exc:
                error = f"network error: {type(exc).__name__}"
                continue
            if response.status_code in RETRY_STATUSES:
                error = f"HTTP {response.status_code}"
                continue
            if response.status_code >= 400:
                raise FetchError(f"HTTP {response.status_code}")
            return response.text
        raise FetchError(f"{error} (after {self._retries + 1} attempts)")
