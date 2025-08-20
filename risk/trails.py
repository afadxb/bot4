"""Trailing stop helpers (stubs)."""

from __future__ import annotations


def chandelier_exit(high_series, atr_series, mult: float):  # pragma: no cover - stub
    """Return chandelier exit level."""
    return high_series.max() - mult * atr_series.iloc[-1]
