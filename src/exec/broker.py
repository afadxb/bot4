"""Broker interface stubs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from loguru import logger
from tenacity import retry, stop_after_attempt, wait_fixed


@dataclass
class Order:
    symbol: str
    qty: int
    side: str
    price: float


class Broker:
    """Abstract broker."""

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    def place_order(self, order: Order) -> Any:  # pragma: no cover - simple
        raise NotImplementedError


class IBKRBroker(Broker):
    """Stub implementation of a broker using IBKR.

    The real implementation would use ``ib_insync``. The stub simply logs the
    order and returns a dummy identifier.
    """

    def place_order(self, order: Order) -> str:  # pragma: no cover - trivial
        logger.info("Placing order", order=order)
        return "ORDER123"
