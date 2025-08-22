"""Market data interfaces."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import pandas as pd

from loguru import logger
from config import settings

try:  # pragma: no cover - requires ib_insync at runtime
    from ib_insync import IB, Stock, util
except Exception:  # pragma: no cover - fallback when ib_insync missing
    IB = Stock = util = None  # type: ignore
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
    """Retrieve historical bars from Interactive Brokers.

    A connection is established on initialisation using credentials from
    :mod:`config.settings`.  Only a subset of the API is exercised so the
    implementation remains intentionally small.  The returned frames include
    a collection of commonly used indicators so the scoring modules can
    operate on the data directly.
    """

    # ``ib_insync`` is an optional dependency.  When it is not installed the
    # imported ``IB`` symbol above will be ``None``.  Using ``IB`` directly as a
    # ``default_factory`` would cause a ``TypeError`` during dataclass
    # instantiation because ``None`` is not callable.  To keep the class usable
    # in environments without ``ib_insync`` (the test-suite, documentation
    # builds, etc.) we store ``None`` by default and lazily create the ``IB``
    # client in :meth:`__post_init__` when the real library is available.
    ib: IB | None = None

    def __post_init__(self) -> None:  # pragma: no cover - network
        if IB is None:
            # ``ib_insync`` is missing – signal to callers that this provider
            # cannot be used rather than failing with a ``TypeError`` from the
            # dataclass machinery.
            raise ImportError("ib_insync is required for IBKRMarketData")

        # When ``ib`` wasn't supplied, create a new client instance now.
        if self.ib is None:
            self.ib = IB()

        # Establish the API connection using configured credentials unless we
        # were given a pre-connected instance.
        if not self.ib.isConnected():
            self.ib.connect(
                settings.ib_host, settings.ib_port, clientId=settings.ib_client_id
            )

    def close(self) -> None:  # pragma: no cover - network
        """Disconnect from the IBKR API if connected."""
        if self.ib and self.ib.isConnected():
            self.ib.disconnect()

    # Support usage as a context manager to guarantee disconnection.
    def __enter__(self) -> "IBKRMarketData":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    # -- internal helpers -------------------------------------------------
    def _download(self, symbol: str, duration: str, bar_size: str) -> pd.DataFrame:
        logger.debug("Downloading bars", symbol=symbol, duration=duration, bar_size=bar_size)
        contract = Stock(symbol, "SMART", "USD")
        bars = self.ib.reqHistoricalData(
            contract,
            endDateTime="",
            durationStr=duration,
            barSizeSetting=bar_size,
            whatToShow="TRADES",
            useRTH=True,
        )
        df = util.df(bars)
        df = df.rename(columns=str.lower)
        df = df[["open", "high", "low", "close", "volume"]]
        return df.dropna()

    def get_bars(self, symbol: str, tf: str, lookback: int) -> pd.DataFrame:
        """Fetch price bars and compute indicators for ``symbol``.

        Parameters mirror those of the previous stub implementation so the
        rest of the application remains unchanged.
        """

        logger.debug("Fetching bars", symbol=symbol, timeframe=tf, lookback=lookback)
        if tf == "D":
            df = self._download(symbol, f"{lookback + settings.sma_slow} D", "1 day")
            df["sma50"] = sma(df["close"], settings.sma_fast)
            df["sma200"] = sma(df["close"], settings.sma_slow)
            df["supertrend"] = supertrend(
                df,
                period=settings.supertrend_period,
                multiplier=settings.supertrend_mult,
            )
            df["rsi"] = rsi(df["close"], window=settings.rsi_window)
            macd_line, macd_signal, macd_hist = macd(
                df["close"],
                fast=settings.macd_fast,
                slow=settings.macd_slow,
                signal=settings.macd_signal,
            )
            df["macd_line"] = macd_line
            df["macd_signal"] = macd_signal
            df["macd_hist"] = macd_hist
            df["avg_vol"] = df["volume"].rolling(settings.sma_exit).mean()
            df["session_vol"] = df["volume"]
            df["obv_slope"] = obv(df["close"], df["volume"]).diff()
            lband, _, hband = bbands(df["close"], window=settings.sma_exit)
            df["bb_pos"] = (df["close"] - lband) / (hband - lband)
            df["pullback"] = False
            df["extended"] = False
            df["gap_up"] = False
            return df.tail(lookback)
        if tf == "1H":
            df = self._download(symbol, "60 D", "1 hour")
            df["supertrend"] = supertrend(
                df,
                period=settings.supertrend_period,
                multiplier=settings.supertrend_mult,
            )
            macd_line, macd_signal, _ = macd(
                df["close"],
                fast=settings.macd_fast,
                slow=settings.macd_slow,
                signal=settings.macd_signal,
            )
            df["macd_line"] = macd_line
            df["macd_signal"] = macd_signal
            return df.tail(lookback)
        if tf == "4H":
            df_1h = self._download(symbol, "60 D", "1 hour")
            df = rollup_1h_to_4h(df_1h)
            df["supertrend"] = supertrend(
                df,
                period=settings.supertrend_period,
                multiplier=settings.supertrend_mult,
            )
            df["rsi"] = rsi(df["close"], window=settings.rsi_window)
            macd_line, macd_signal, _ = macd(
                df["close"],
                fast=settings.macd_fast,
                slow=settings.macd_slow,
                signal=settings.macd_signal,
            )
            df["macd_line"] = macd_line
            df["macd_signal"] = macd_signal
            df["sma20"] = sma(df["close"], settings.sma_exit)
            df["bearish_pattern"] = False
            return df.tail(lookback)
        logger.debug("Unsupported timeframe", timeframe=tf)
        raise NotImplementedError

    def get_last_close(self, symbol: str) -> float:
        df = self.get_bars(symbol, "D", 1)
        return float(df["close"].iloc[-1])

    def get_vix(self) -> float:
        """Return the latest VIX value.

        The VIX is retrieved as the last closing price of the CBOE Volatility
        Index.  Only a single day of data is required so a short download
        window keeps the request lightweight.
        """

        df = self._download("VIX", "5 D", "1 day")
        return float(df["close"].iloc[-1])

    def get_reference_symbol(self) -> str:
        """Symbol used as the market reference for regime detection.

        ``SPY`` – the S&P 500 ETF – acts as a broad market benchmark and is
        used by the scoring modules when assessing overall market regime.
        """

        return "SPY"


@dataclass
class YFinanceMarketData(IBKRMarketData):
    """Retrieve historical bars from Yahoo Finance.

    This implementation reuses the indicator calculations from
    :class:`IBKRMarketData` but sources the raw OHLCV data from the public
    Yahoo Finance API via the :mod:`yfinance` package.  No network connection
    is established at initialisation time which keeps the class lightweight
    and easy to stub in tests.
    """

    def __post_init__(self) -> None:  # pragma: no cover - trivial
        # The Yahoo Finance backend does not require persistent connections,
        # so initialisation is effectively a no-op.
        pass

    # -- internal helpers -------------------------------------------------
    def _download(self, symbol: str, duration: str, bar_size: str) -> pd.DataFrame:
        """Download historical bars using :mod:`yfinance`.

        Parameters mirror the signature of :meth:`IBKRMarketData._download` to
        keep the rest of the application unchanged.  The ``duration`` string is
        converted to the ``period`` parameter expected by ``yfinance`` and the
        ``bar_size`` is mapped to the corresponding ``interval``.
        """

        logger.debug("Downloading bars", symbol=symbol, duration=duration, bar_size=bar_size)
        import yfinance as yf  # Imported lazily to keep dependency optional

        period = duration.lower().replace(" ", "")  # e.g. "5 D" -> "5d"
        interval_map = {"1 day": "1d", "1 hour": "1h"}
        interval = interval_map.get(bar_size, "1d")
        df = yf.download(symbol, period=period, interval=interval, progress=False)
        df = df.rename(columns=str.lower)
        df = df[["open", "high", "low", "close", "volume"]]
        return df.dropna()

    def get_vix(self) -> float:
        """Return the latest VIX value using the ``^VIX`` ticker."""

        df = self._download("^VIX", "5 D", "1 day")
        return float(df["close"].iloc[-1])
