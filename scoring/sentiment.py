"""Sentiment stubs."""

from __future__ import annotations

from typing import Literal

from loguru import logger


def get_fear_greed() -> int:
    """Return the Fear & Greed index value.

    The default implementation returns 50 to represent neutral sentiment. In a
    real deployment this would call an external API.
    """

    logger.debug("Fetching Fear & Greed index")
    return 50


def get_news_sentiment(symbol: str) -> Literal["pos", "neg", "neutral"]:
    """Return ticker specific news sentiment.

    Always returns ``"neutral"`` in this stub implementation.
    """

    logger.debug("Fetching news sentiment", symbol=symbol)
    return "neutral"
