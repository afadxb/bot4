"""Entry scoring logic."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple

import pandas as pd

from ..config import settings


@dataclass
class EntryComponents:
    trend: float = 0.0
    momentum: float = 0.0
    volume: float = 0.0
    setup: float = 0.0
    penalties: float = 0.0
    notes: Dict[str, Any] = field(default_factory=dict)


REGIME_MULT = {
    "TR": {"trend": 1.15, "momentum": 1.10, "volume": 1.0, "setup": 0.90},
    "RG": {"trend": 0.85, "momentum": 0.95, "volume": 1.0, "setup": 1.20},
    "RO": {"trend": 0.90, "momentum": 0.85, "volume": 0.90, "setup": 0.80},
}


def _apply_sentiment(score: float, daily_rsi: float, sentiment: Dict[str, Any], regime: str) -> float:
    fg = sentiment.get("fg")
    news = sentiment.get("news", "neutral")

    if fg is not None:
        if fg < settings.sentiment_fg_block:
            return 0.0
        if 25 <= fg <= 45:
            score -= 5
        if fg > 80 and daily_rsi > settings.sentiment_overheat_rsi:
            score -= 5
    if news == "pos":
        score += settings.news_sent_pos_bonus
    elif news == "neg":
        if regime == "RO":
            return 0.0
        score -= settings.news_sent_neg_penalty
    return score


def compute_entry_score(
    daily: pd.DataFrame, h4: pd.DataFrame, regime: str, sentiment: Dict[str, Any]
) -> Tuple[float, EntryComponents]:
    """Compute the final entry score.

    Args:
        daily: Daily timeframe data (must contain latest and previous row).
        h4: 4H timeframe data (latest and previous row).
        regime: Regime label from :func:`regime.detect_regime`.
        sentiment: Dict with ``fg`` (Fear & Greed int) and ``news`` sentiment.

    Returns:
        Tuple of final score and component breakdown.
    """

    comp = EntryComponents()
    d0 = daily.iloc[-1]
    d1 = daily.iloc[-2] if len(daily) > 1 else d0
    h0 = h4.iloc[-1]
    h1 = h4.iloc[-2] if len(h4) > 1 else h0

    # Trend
    if d0["close"] > d0["sma200"]:
        comp.trend += 12
    if d0["close"] > d0["sma50"]:
        comp.trend += 10
    if d0["sma50"] > d0["sma200"]:
        comp.trend += 10
    if d0.get("supertrend", 1) > 0:
        comp.trend += 8
    if h0.get("supertrend", 1) > 0:
        comp.trend += 5

    # Momentum
    rsi = d0.get("rsi", 0)
    if 55 <= rsi <= 70:
        comp.momentum += 10
    if rsi > 75:
        comp.penalties -= 5
    if d0.get("macd_line", 0) > d0.get("macd_signal", 0):
        comp.momentum += 8
    if d0.get("macd_hist", 0) > 0 and d0.get("macd_hist", 0) > d1.get("macd_hist", 0):
        comp.momentum += 6
    if h0.get("rsi", 0) > 55 and h0.get("rsi", 0) > h1.get("rsi", 0):
        comp.momentum += 6

    # Volume
    avg_vol = d0.get("avg_vol", 0)
    vol = d0.get("session_vol", 0)
    if avg_vol >= 1_000_000:
        comp.volume += 5
    if vol >= 1.2 * avg_vol > 0:
        comp.volume += 6
    if d0.get("obv_slope", 0) > 0:
        comp.volume += 4

    # Setup / Location
    if d0.get("pullback", False):
        comp.setup += 6
    if d0.get("bb_pos", 0) >= 0.5:
        comp.setup += 4

    # Penalties
    if d0.get("extended", False):
        comp.penalties -= 6
    if d0.get("gap_up", False):
        comp.penalties -= 3

    # Apply regime multipliers
    mult = REGIME_MULT.get(regime, REGIME_MULT["TR"])
    comp.trend *= mult["trend"]
    comp.momentum *= mult["momentum"]
    comp.volume *= mult["volume"]
    comp.setup *= mult["setup"]

    score = comp.trend + comp.momentum + comp.volume + comp.setup
    score = min(100.0, score)
    score += comp.penalties
    score = max(0.0, score)

    score = _apply_sentiment(score, rsi, sentiment, regime)
    score = max(0.0, min(100.0, score))
    return score, comp
