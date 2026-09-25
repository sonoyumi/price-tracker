"""One check cycle: fetch -> extract -> compare with history -> save -> notify."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from price_tracker.alerts import compare
from price_tracker.db import History
from price_tracker.fetch import Fetcher, FetchError
from price_tracker.models import Alert, Observation, Product
from price_tracker.notify import Notifier, NotifyError
from price_tracker.parse import ParseError, extract


@dataclass
class CheckResult:
    product: Product
    current: Observation
    previous: Observation | None
    alerts: list[Alert] = field(default_factory=list)


def check_product(product: Product, fetcher: Fetcher, history: History, now: datetime | None = None) -> CheckResult:
    now = now or datetime.now(UTC)
    previous = history.last_ok(product.id)
    try:
        found = extract(fetcher.get(product.url), product)
        current = Observation(price=found.price, in_stock=found.in_stock, checked_at=now)
    except (FetchError, ParseError) as exc:
        # One broken product must not stop the others; the error is kept in the history.
        current = Observation(price=None, in_stock=None, checked_at=now, error=str(exc))
    history.save(product.id, current)
    return CheckResult(product, current, previous, compare(product, previous, current))


def check_all(
    products: list[Product], fetcher: Fetcher, history: History, notifier: Notifier
) -> tuple[list[CheckResult], str | None]:
    """Checks every product; returns the results and a notification error, if sending failed."""
    results = [check_product(p, fetcher, history) for p in products]
    alerts = [a for r in results for a in r.alerts]
    try:
        notifier.send(alerts)
    except NotifyError as exc:
        return results, str(exc)
    return results, None
