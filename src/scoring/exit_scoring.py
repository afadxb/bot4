"""Exit scoring logic."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass
class ExitComponents:
    h4_supertrend_flip: int = 0
    h4_macd_cross: int = 0
    h4_close_lt_20sma: int = 0
    h4_rsi_lt_50: int = 0
    h4_bearish_pattern: int = 0
    d1_close_lt_50sma: int = 0
    d1_vol_spike: int = 0
    d1_trendline_break: int = 0
    h1_accel_confirmation: int = 0
    total: int = 0


def compute_exit_score(h4: pd.DataFrame, d1: pd.DataFrame, h1: pd.DataFrame) -> ExitComponents:
    """Compute exit score using multi-timeframe signals."""

    comp = ExitComponents()

    h0 = h4.iloc[-1]
    h1_prev = h4.iloc[-2] if len(h4) > 1 else h0

    if h0.get("supertrend", 1) < 0 and h1_prev.get("supertrend", 1) > 0:
        comp.h4_supertrend_flip = 3
    if h0.get("macd_line", 0) < h0.get("macd_signal", 0) and h1_prev.get("macd_line", 0) >= h1_prev.get("macd_signal", 0):
        comp.h4_macd_cross = 2
    if h0.get("close", 0) < h0.get("sma20", 0):
        comp.h4_close_lt_20sma = 1
    if h0.get("rsi", 100) < 50 and h1_prev.get("rsi", 100) >= 50:
        comp.h4_rsi_lt_50 = 1
    if h0.get("bearish_pattern", False):
        comp.h4_bearish_pattern = 1

    d0 = d1.iloc[-1]
    if d0.get("close", 0) < d0.get("sma50", 0):
        comp.d1_close_lt_50sma = 2
    if d0.get("volume", 0) > 1.5 * d0.get("avg_vol", 0) > 0:
        comp.d1_vol_spike = 2
    if d0.get("trendline_break", False):
        comp.d1_trendline_break = 2

    if len(h1) >= 2:
        h1_curr = h1.iloc[-1]
        h1_prev = h1.iloc[-2]
        st_flip = h1_curr.get("supertrend", 1) < 0 and h1_prev.get("supertrend", 1) > 0
        macd_cross = h1_curr.get("macd_line", 0) < h1_curr.get("macd_signal", 0) and h1_prev.get(
            "macd_line", 0
        ) >= h1_prev.get("macd_signal", 0)
        if st_flip and macd_cross:
            comp.h1_accel_confirmation = 1

    comp.total = (
        comp.h4_supertrend_flip
        + comp.h4_macd_cross
        + comp.h4_close_lt_20sma
        + comp.h4_rsi_lt_50
        + comp.h4_bearish_pattern
        + comp.d1_close_lt_50sma
        + comp.d1_vol_spike
        + comp.d1_trendline_break
        + comp.h1_accel_confirmation
    )
    return comp
