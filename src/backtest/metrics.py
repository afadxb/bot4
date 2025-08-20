"""Metrics helpers for backtests."""

from __future__ import annotations

from typing import Iterable

import numpy as np


def sharpe(returns: Iterable[float]) -> float:
    arr = np.array(list(returns))
    if arr.std() == 0:
        return 0.0
    return arr.mean() / arr.std()
