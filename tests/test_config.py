from pathlib import Path

import pytest

from price_tracker.config import ConfigError, load_products, load_settings

ROOT = Path(__file__).resolve().parents[1]


def write(tmp_path, text: str) -> Path:
    path = tmp_path / "products.toml"
    path.write_text(text, encoding="utf-8")
    return path


def test_shipped_example_is_valid():
    products = load_products(ROOT / "products.example.toml")
    assert [p.id for p in products] == ["light-in-the-attic", "tipping-the-velvet"]
    assert products[0].target_price == 45.0
    assert products[1].target_price is None


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("", "at least one"),
        ('[[product]]\nid = "a"\nname = "A"\n', "'url' is required"),
        ('[[product]]\nid = "Bad Id"\nname = "A"\nurl = "https://x"\n', "lowercase"),
        ('[[product]]\nid = "a"\nname = "A"\nurl = "ftp://x"\n', "http"),
        ('[[product]]\nid = "a"\nname = "A"\nurl = "https://x"\ntarget_price = -1\n', "positive"),
        (
            '[[product]]\nid = "a"\nname = "A"\nurl = "https://x"\n[[product]]\nid = "a"\nname = "B"\nurl = "https://y"\n',
            "duplicate",
        ),
        ("[[product]\n", "products.toml"),
    ],
)
def test_invalid_product_lists(tmp_path, text, message):
    with pytest.raises(ConfigError, match=message):
        load_products(write(tmp_path, text))


def test_missing_file_explains_what_to_do(tmp_path):
    with pytest.raises(ConfigError, match="products.example.toml"):
        load_products(tmp_path / "products.toml")


def test_settings_hide_token_and_detect_telegram(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("BOT_TOKEN", "123:SECRET")
    monkeypatch.setenv("CHAT_ID", "42")
    monkeypatch.setenv("REQUEST_DELAY", "0.5")
    settings = load_settings()
    assert settings.telegram_enabled and settings.request_delay == 0.5
    assert "SECRET" not in repr(settings)

    monkeypatch.delenv("CHAT_ID")
    assert not load_settings().telegram_enabled
