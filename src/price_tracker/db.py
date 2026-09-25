"""Price history in SQLite (stdlib sqlite3: a CLI tool does not need async)."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from price_tracker.models import Observation

SCHEMA = """
CREATE TABLE IF NOT EXISTS observations (
    id          INTEGER PRIMARY KEY,
    product_id  TEXT    NOT NULL,
    checked_at  TEXT    NOT NULL,   -- ISO 8601, UTC
    price       REAL,
    in_stock    INTEGER,            -- 1 / 0 / NULL (unknown)
    error       TEXT
);
CREATE INDEX IF NOT EXISTS ix_observations_product ON observations (product_id, checked_at);
"""


def _row_to_observation(row: sqlite3.Row) -> Observation:
    stock = row["in_stock"]
    return Observation(
        price=row["price"],
        in_stock=None if stock is None else bool(stock),
        checked_at=datetime.fromisoformat(row["checked_at"]),
        error=row["error"],
    )


class History:
    def __init__(self, path: Path | str) -> None:
        if str(path) != ":memory:":
            Path(path).parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(path)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(SCHEMA)

    def close(self) -> None:
        self._conn.close()

    def save(self, product_id: str, observation: Observation) -> None:
        checked_at = observation.checked_at or datetime.now(UTC)
        stock = None if observation.in_stock is None else int(observation.in_stock)
        with self._conn:
            self._conn.execute(
                "INSERT INTO observations (product_id, checked_at, price, in_stock, error) VALUES (?, ?, ?, ?, ?)",
                (product_id, checked_at.astimezone(UTC).isoformat(), observation.price, stock, observation.error),
            )

    def last_ok(self, product_id: str) -> Observation | None:
        """The latest successful observation: errors are skipped so one failed check does not reset comparisons."""
        row = self._conn.execute(
            "SELECT * FROM observations WHERE product_id = ? AND error IS NULL "
            "ORDER BY checked_at DESC, id DESC LIMIT 1",
            (product_id,),
        ).fetchone()
        return _row_to_observation(row) if row else None

    def history(self, product_id: str, limit: int = 20) -> list[Observation]:
        rows = self._conn.execute(
            "SELECT * FROM observations WHERE product_id = ? ORDER BY checked_at DESC, id DESC LIMIT ?",
            (product_id, limit),
        ).fetchall()
        return [_row_to_observation(r) for r in rows]

    def all_rows(self) -> list[sqlite3.Row]:
        return self._conn.execute("SELECT * FROM observations ORDER BY checked_at, id").fetchall()
