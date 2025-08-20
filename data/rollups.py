"""Timeframe roll-up helpers."""

from __future__ import annotations

import pandas as pd


def rollup_1h_to_4h(df_1h: pd.DataFrame) -> pd.DataFrame:
    """Roll up 1H bars to 4H bars using session-aware boundaries.

    Args:
        df_1h: DataFrame indexed by timezone-aware datetimes with columns
            ``open``, ``high``, ``low``, ``close``, ``volume``.

    Returns:
        4H resampled DataFrame.
    """

    if df_1h.empty:
        raise ValueError("No data to roll up")
    df = df_1h.resample("4H", label="right", closed="right").agg(
        {
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
        }
    )
    return df.dropna()
