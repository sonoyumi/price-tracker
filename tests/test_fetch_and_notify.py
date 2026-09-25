import httpx
import pytest

from price_tracker.fetch import Fetcher, FetchError
from price_tracker.models import Alert, Product
from price_tracker.notify import NotifyError, TelegramNotifier


class FakeTime:
    def __init__(self):
        self.now = 0.0
        self.sleeps: list[float] = []

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds

    def clock(self) -> float:
        return self.now


def make_fetcher(handler, fake: FakeTime, delay: float = 2.0) -> Fetcher:
    client = httpx.Client(transport=httpx.MockTransport(handler))
    return Fetcher("test-agent", delay=delay, retries=2, client=client, sleep=fake.sleep, clock=fake.clock)


def test_retries_on_server_error_then_succeeds():
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(503) if len(calls) < 3 else httpx.Response(200, text="ok")

    fake = FakeTime()
    assert make_fetcher(handler, fake).get("https://shop.test/a") == "ok"
    assert len(calls) == 3
    assert calls[0].headers["User-Agent"] == "test-agent"
    assert 2 in fake.sleeps and 4 in fake.sleeps  # exponential backoff


def test_client_error_is_not_retried():
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(404)

    with pytest.raises(FetchError, match="HTTP 404"):
        make_fetcher(handler, FakeTime()).get("https://shop.test/a")
    assert len(calls) == 1


def test_network_errors_give_up_after_retries():
    def handler(request):
        raise httpx.ConnectError("down", request=request)

    with pytest.raises(FetchError, match="after 3 attempts"):
        make_fetcher(handler, FakeTime()).get("https://shop.test/a")


def test_pause_between_requests_to_the_same_site_only():
    fake = FakeTime()
    fetcher = make_fetcher(lambda r: httpx.Response(200, text="x"), fake, delay=2.0)
    fetcher.get("https://shop.test/a")
    fetcher.get("https://other.test/a")  # another site: no pause
    assert fake.sleeps == []
    fetcher.get("https://shop.test/b")  # same site right after: wait
    assert fake.sleeps == [2.0]


PRODUCT = Product(id="k", name="Kettle <XL>", url="https://shop.test/k?a=1&b=2")


def test_telegram_message_is_html_escaped():
    sent = {}

    def handler(request):
        sent["body"] = request.content.decode()
        return httpx.Response(200, json={"ok": True})

    notifier = TelegramNotifier("123:SECRET", "42", client=httpx.Client(transport=httpx.MockTransport(handler)))
    notifier.send([Alert(PRODUCT, "price_down", "📉 Kettle <XL>: 10 → 8")])
    assert "Kettle+%26lt%3BXL%26gt%3B" in sent["body"]  # &lt;XL&gt; after form encoding
    assert "a%3D1%26amp%3Bb%3D2" in sent["body"]


def test_telegram_error_does_not_leak_token():
    def handler(request):
        return httpx.Response(400, json={"ok": False, "description": "Bad Request: chat not found"})

    notifier = TelegramNotifier("123:SECRET", "42", client=httpx.Client(transport=httpx.MockTransport(handler)))
    with pytest.raises(NotifyError) as info:
        notifier.send([Alert(PRODUCT, "price_up", "up")])
    assert "chat not found" in str(info.value) and "SECRET" not in str(info.value)


def test_nothing_is_sent_without_alerts():
    def handler(request):  # pragma: no cover - must not be called
        raise AssertionError("no request expected")

    TelegramNotifier("t", "1", client=httpx.Client(transport=httpx.MockTransport(handler))).send([])
