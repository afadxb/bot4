"""Market data interfaces."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import pandas as pd
try:  # pragma: no cover - optional dependency
    import yfinance as yf
except Exception:  # pragma: no cover - graceful fallback
    yf = None

from .indicators import (
    bbands,
    macd,
    obv,
    rsi,
    sma,
    supertrend,
)
from .rollups import rollup_1h_to_4h


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
    that can be replaced with a fully featured provider.  Rather than raising
    ``NotImplementedError`` this stub fetches data from ``yfinance`` as a
    lightweight fallback so the rest of the bot can operate in a demo mode.
    The returned frames include a handful of commonly used indicator columns
    which keeps the scoring modules functional.
    """

    def _download(self, symbol: str, interval: str, period: str) -> pd.DataFrame:
        if yf is None:
            raise RuntimeError("yfinance is required for the IBKRMarketData stub")
        df = yf.download(symbol, interval=interval, period=period, progress=False)
        df = df.rename(columns=str.lower)
        df = df[["open", "high", "low", "close", "volume"]]
        return df.dropna()

    def get_bars(self, symbol: str, tf: str, lookback: int) -> pd.DataFrame:
        if tf == "D":
            # fetch extra history to compute long moving averages
            df = self._download(symbol, "1d", f"{lookback + 200}d")
            df["sma50"] = sma(df["close"], 50)
            df["sma200"] = sma(df["close"], 200)
            df["supertrend"] = supertrend(df)
            df["rsi"] = rsi(df["close"])
            macd_line, macd_signal, macd_hist = macd(df["close"])
            df["macd_line"] = macd_line
            df["macd_signal"] = macd_signal
            df["macd_hist"] = macd_hist
            df["avg_vol"] = df["volume"].rolling(20).mean()
            df["session_vol"] = df["volume"]
            df["obv_slope"] = obv(df["close"], df["volume"]).diff()
            lband, _, hband = bbands(df["close"])
            df["bb_pos"] = (df["close"] - lband) / (hband - lband)
            df["pullback"] = False
            df["extended"] = False
            df["gap_up"] = False
            return df.tail(lookback)
        if tf == "1H":
            df = self._download(symbol, "1h", "60d")
            df["supertrend"] = supertrend(df)
            macd_line, macd_signal, _ = macd(df["close"])
            df["macd_line"] = macd_line
            df["macd_signal"] = macd_signal
            return df.tail(lookback)
        if tf == "4H":
            df_1h = self._download(symbol, "1h", "60d")
            df = rollup_1h_to_4h(df_1h)
            df["supertrend"] = supertrend(df)
            df["rsi"] = rsi(df["close"])
            macd_line, macd_signal, _ = macd(df["close"])
            df["macd_line"] = macd_line
            df["macd_signal"] = macd_signal
            df["sma20"] = sma(df["close"], 20)
            df["bearish_pattern"] = False
            return df.tail(lookback)
        raise NotImplementedError

    def get_last_close(self, symbol: str) -> float:
        df = self.get_bars(symbol, "D", 1)
        return float(df["close"].iloc[-1])

    def get_vix(self) -> float:  # pragma: no cover - stub
        raise NotImplementedError

    def get_reference_symbol(self) -> str:  # pragma: no cover - stub
        return "SPY"
