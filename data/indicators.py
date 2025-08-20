"""Indicator helper functions built on pandas/ta."""

from __future__ import annotations

import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD, ADXIndicator, SuperTrend
from ta.volatility import AverageTrueRange, BollingerBands


def sma(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window).mean()


def ema(series: pd.Series, window: int) -> pd.Series:
    return series.ewm(span=window, adjust=False).mean()


def atr(df: pd.DataFrame, window: int) -> pd.Series:
    ind = AverageTrueRange(high=df["high"], low=df["low"], close=df["close"], window=window)
    return ind.average_true_range()


def rsi(series: pd.Series, window: int = 14) -> pd.Series:
    return RSIIndicator(close=series, window=window).rsi()


def macd(series: pd.Series) -> tuple[pd.Series, pd.Series, pd.Series]:
    ind = MACD(close=series)
    return ind.macd(), ind.macd_signal(), ind.macd_diff()


def supertrend(df: pd.DataFrame, period: int = 10, multiplier: float = 3.0) -> pd.Series:
    ind = SuperTrend(high=df["high"], low=df["low"], close=df["close"], period=period, multiplier=multiplier)
    return ind.super_trend_direction()


def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    return (volume.where(close >= close.shift(), -volume).fillna(0)).cumsum()


def bbands(series: pd.Series, window: int = 20) -> tuple[pd.Series, pd.Series, pd.Series]:
    ind = BollingerBands(close=series, window=window)
    return ind.bollinger_lband(), ind.bollinger_mavg(), ind.bollinger_hband()


def adx(df: pd.DataFrame, window: int = 14) -> pd.Series:
    ind = ADXIndicator(high=df["high"], low=df["low"], close=df["close"], window=window)
    return ind.adx()
