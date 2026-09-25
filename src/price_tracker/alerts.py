"""Rules that turn two consecutive observations into alerts. Pure logic, no I/O."""

from __future__ import annotations

from price_tracker.models import Alert, Observation, Product


def fmt_price(value: float) -> str:
    return f"{value:,.2f}".replace(",", " ")


def compare(product: Product, previous: Observation | None, current: Observation) -> list[Alert]:
    if not current.ok:
        return []
    assert current.price is not None
    alerts: list[Alert] = []
    price, target = current.price, product.target_price

    if previous is None or not previous.ok:
        if target is not None and price <= target:
            alerts.append(
                Alert(
                    product, "target", f"🎯 {product.name}: {fmt_price(price)} — уже не дороже цели {fmt_price(target)}"
                )
            )
        return alerts

    assert previous.price is not None
    old = previous.price
    if price != old:
        change = (price - old) / old * 100 if old else 0.0
        kind, arrow = ("price_down", "📉") if price < old else ("price_up", "📈")
        alerts.append(
            Alert(product, kind, f"{arrow} {product.name}: {fmt_price(old)} → {fmt_price(price)} ({change:+.1f}%)")
        )
    if target is not None and price <= target < old:
        alerts.append(
            Alert(product, "target", f"🎯 {product.name}: цена {fmt_price(price)} достигла цели {fmt_price(target)}")
        )

    if previous.in_stock is False and current.in_stock is True:
        alerts.append(Alert(product, "in_stock", f"✅ {product.name}: снова в наличии"))
    elif previous.in_stock is True and current.in_stock is False:
        alerts.append(Alert(product, "out_of_stock", f"⛔ {product.name}: закончился"))
    return alerts
