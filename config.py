"""Configuration management for the bot."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _getenv(name: str, default):
    """Read environment variable ``name`` and cast to ``type(default)``.

    ``bool`` values are handled explicitly so that any of ``1``, ``true``,
    ``yes`` or ``on`` (case-insensitive) evaluate to ``True`` while all other
    values fall back to ``False``.  This makes it possible to toggle features
    such as debug logging via environment variables without surprising
    behaviour from ``bool("false")`` evaluating truthy.
    """

    value = os.getenv(name)
    if value is None:
        return default
    if isinstance(default, bool):
        return value.lower() in {"1", "true", "yes", "on"}
    return type(default)(value)


@dataclass(frozen=True)
class Settings:
    ib_host: str = _getenv("IB_HOST", "127.0.0.1")
    ib_port: int = _getenv("IB_PORT", 7497)
    ib_client_id: int = _getenv("IB_CLIENT_ID", 42)
    ib_account_id: str | None = os.getenv("IB_ACCOUNT_ID")

    universe_source: str = _getenv("UNIVERSE_SOURCE", "static")
    universe_file: str = _getenv("UNIVERSE_FILE", "sp100.csv")
    primary_tf: str = _getenv("PRIMARY_TF", "4H")
    run_interval_min: int = _getenv("RUN_INTERVAL_MIN", 60)

    risk_per_trade: float = _getenv("RISK_PER_TRADE", 0.01)
    max_positions: int = _getenv("MAX_POSITIONS", 5)
    portfolio_pct: float = _getenv("PORTFOLIO_PCT", 0.1)

    entry_threshold: int = _getenv("ENTRY_THRESHOLD", 70)
    watch_threshold: int = _getenv("WATCH_THRESHOLD", 55)

    pt1_r_mult: float = _getenv("PT1_R_MULT", 1.5)
    pt2_r_mult: float = _getenv("PT2_R_MULT", 2.0)
    atr_trail_mult_strong: float = _getenv("ATR_TRAIL_MULT_STRONG", 2.5)
    chandelier_mult: float = _getenv("CHANDELIER_MULT", 3.0)

    regime_vix_tr: float = _getenv("REGIME_VIX_TR", 22.0)
    regime_vix_ro: float = _getenv("REGIME_VIX_RO", 26.0)
    adx_trend: float = _getenv("ADX_TREND", 20.0)

    # Indicator parameters
    rsi_window: int = _getenv("RSI_WINDOW", 14)
    supertrend_period: int = _getenv("SUPER_TREND_PERIOD", 10)
    supertrend_mult: float = _getenv("SUPER_TREND_MULT", 3.0)
    sma_fast: int = _getenv("SMA_FAST", 50)
    sma_slow: int = _getenv("SMA_SLOW", 200)
    sma_exit: int = _getenv("SMA_EXIT", 20)
    macd_fast: int = _getenv("MACD_FAST", 12)
    macd_slow: int = _getenv("MACD_SLOW", 26)
    macd_signal: int = _getenv("MACD_SIGNAL", 9)

    sentiment_fg_block: int = _getenv("SENTIMENT_FG_BLOCK", 25)
    sentiment_overheat_rsi: int = _getenv("SENTIMENT_OVERHEAT_RSI", 70)
    news_sent_pos_bonus: int = _getenv("NEWS_SENT_POS_BONUS", 3)
    news_sent_neg_penalty: int = _getenv("NEWS_SENT_NEG_PENALTY", 5)

    earnings_policy: str = _getenv("EARNINGS_POLICY", "BLOCK_NEW")

    db_url: str = _getenv("DB_URL", "sqlite:///./bot.db")
    timezone: str = _getenv("TIMEZONE", "America/New_York")

    # Misc
    debug: bool = _getenv("DEBUG", False)


settings = Settings()
