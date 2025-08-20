"""Market data interfaces."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import pandas as pd


class MarketData(Protocol):
    """Abstract market data provider."""

    def get_bars(self, symbol: str, tf: str, lookback: int) -> pd.DataFrame: ...

    def get_last_close(self, symbol: str) -> float: ...

    def get_vix(self) -> float: ...

    def get_reference_symbol(self) -> str: ...


@dataclass
class IBKRMarketData:
    """Minimal stub using IBKR via ib_insync.

    The real implementation would use ``ib_insync``. Here we provide a stub
    that can be replaced with a fully featured provider. The methods raise
    ``NotImplementedError`` to avoid accidental usage in tests.
    """

    def get_bars(self, symbol: str, tf: str, lookback: int) -> pd.DataFrame:  # pragma: no cover - stub
        raise NotImplementedError

    def get_last_close(self, symbol: str) -> float:  # pragma: no cover - stub
        raise NotImplementedError

    def get_vix(self) -> float:  # pragma: no cover - stub
        raise NotImplementedError

    def get_reference_symbol(self) -> str:  # pragma: no cover - stub
        return "SPY"
