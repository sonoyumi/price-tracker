from price_tracker.alerts import compare
from price_tracker.models import Observation, Product

BOOK = Product(id="b", name="Book", url="https://example.com/b", target_price=45.0)
PLAIN = Product(id="p", name="Plain", url="https://example.com/p")


def obs(price, in_stock=True, error=None):
    return Observation(price=price, in_stock=in_stock, error=error)


def kinds(alerts):
    return [a.kind for a in alerts]


def test_first_check_is_silent_unless_already_below_target():
    assert compare(PLAIN, None, obs(10)) == []
    assert compare(BOOK, None, obs(50)) == []
    assert kinds(compare(BOOK, None, obs(40))) == ["target"]


def test_price_drop_and_rise_with_percent():
    down = compare(PLAIN, obs(100), obs(80))
    assert kinds(down) == ["price_down"]
    assert "100.00 → 80.00 (-20.0%)" in down[0].text
    assert kinds(compare(PLAIN, obs(80), obs(100))) == ["price_up"]
    assert compare(PLAIN, obs(80), obs(80)) == []


def test_crossing_the_target_fires_once():
    assert kinds(compare(BOOK, obs(51.77), obs(44.99))) == ["price_down", "target"]
    assert kinds(compare(BOOK, obs(44.99), obs(43))) == ["price_down"]  # already below: no repeat


def test_stock_changes():
    assert kinds(compare(PLAIN, obs(10, in_stock=False), obs(10, in_stock=True))) == ["in_stock"]
    assert kinds(compare(PLAIN, obs(10, in_stock=True), obs(10, in_stock=False))) == ["out_of_stock"]
    assert compare(PLAIN, obs(10, in_stock=None), obs(10, in_stock=True)) == []


def test_failed_check_produces_no_alerts():
    assert compare(PLAIN, obs(10), obs(None, None, error="HTTP 503")) == []


def test_previous_failure_counts_as_no_history():
    assert compare(PLAIN, obs(None, None, error="HTTP 503"), obs(10)) == []
