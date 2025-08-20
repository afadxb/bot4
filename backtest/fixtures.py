"""Synthetic data fixtures for tests."""

from __future__ import annotations

from typing import Iterator

import pandas as pd


def synthetic_prices(start: float, steps: int) -> Iterator[pd.Timestamp]:  # pragma: no cover - example
    for i in range(steps):
        yield pd.Timestamp("2024-01-01") + pd.Timedelta(hours=i)
