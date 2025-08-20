"""Sentiment stubs."""

from __future__ import annotations

from typing import Literal


def get_fear_greed() -> int:
    """Return the Fear & Greed index value.

    The default implementation returns 50 to represent neutral sentiment. In a
    real deployment this would call an external API.
    """

    return 50


def get_news_sentiment(symbol: str) -> Literal["pos", "neg", "neutral"]:
    """Return ticker specific news sentiment.

    Always returns ``"neutral"`` in this stub implementation.
    """

    return "neutral"
