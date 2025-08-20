"""Market regime detection."""

from __future__ import annotations

from typing import Literal

import pandas as pd

from ..config import settings


def detect_regime(spy_df_4h: pd.DataFrame, vix: float) -> Literal["TR", "RG", "RO"]:
    """Detect market regime using SPY 4H data and VIX.

    Args:
        spy_df_4h: 4H bars for SPY with ``close``, ``sma50``, ``sma200`` and
            optionally ``adx`` columns.
        vix: Current VIX value.

    Returns:
        Regime label: ``"TR"`` (trending), ``"RG"`` (ranging) or ``"RO"`` (risk-off).
    """

    last = spy_df_4h.iloc[-1]
    sma50 = last["sma50"]
    sma200 = last["sma200"]
    close = last["close"]
    adx = last.get("adx", 0.0)

    # Risk-off if price < 200SMA or VIX >= RO threshold
    if close < sma200 or vix >= settings.regime_vix_ro:
        return "RO"

    # Trending regime
    if close > sma50 > sma200 and adx >= settings.adx_trend and vix < settings.regime_vix_tr:
        return "TR"

    # Ranging regime: flat SMA50 slope, low ADX and mid-range VIX
    if len(spy_df_4h) >= 20:
        slope = abs(spy_df_4h["sma50"].iloc[-1] - spy_df_4h["sma50"].iloc[-20]) / (
            20 * spy_df_4h["sma50"].iloc[-20]
        )
    else:
        slope = 1.0
    if slope < 0.0005 and adx < settings.adx_trend and 18 <= vix < settings.regime_vix_ro:
        return "RG"

    return "TR"
