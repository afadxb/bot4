"""Earnings schedule stubs."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol


class EarningsProvider(Protocol):
    def next_earnings(self, symbol: str) -> datetime | None: ...


class StubEarningsProvider:
    """Default provider that returns ``None`` for all symbols."""

    def next_earnings(self, symbol: str) -> datetime | None:  # pragma: no cover - trivial
        return None
