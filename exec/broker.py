"""Broker interface stubs.

The module now includes a minimal :class:`IBKRBroker` that connects to an
Interactive Brokers TWS or Gateway instance via :mod:`ib_insync`.  The broker
is intentionally lightweight – it is not meant to expose the full richness of
the IBKR API but rather just enough functionality for the trading bot to place
orders and query account equity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from loguru import logger
from tenacity import retry, stop_after_attempt, wait_fixed

from config import settings

try:  # pragma: no cover - requires ib_insync at runtime
    from ib_insync import IB, Stock, MarketOrder, LimitOrder
except Exception:  # pragma: no cover - fallback for environments without ib_insync
    IB = Stock = MarketOrder = LimitOrder = None  # type: ignore


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

    def get_balance(self) -> float:  # pragma: no cover - simple
        raise NotImplementedError


class IBKRBroker(Broker):
    """Tiny wrapper around ``ib_insync.IB``.

    The broker lazily connects on instantiation using credentials from
    :mod:`config.settings`.  Only the functionality required by the bot is
    implemented: placing simple market/limit orders and fetching the account's
    net liquidation value for position sizing.
    """

    ib: IB = field(default_factory=IB)  # type: ignore[misc]

    def __post_init__(self) -> None:  # pragma: no cover - network
        if IB is None:
            raise RuntimeError("ib_insync is required for IBKRBroker")
        logger.info(
            "Connecting to IBKR", host=settings.ib_host, port=settings.ib_port, client=settings.ib_client_id
        )
        self.ib.connect(settings.ib_host, settings.ib_port, clientId=settings.ib_client_id)
        self.account_id = settings.ib_account_id
        logger.debug("IBKR connection established")

    def place_order(self, order: Order) -> str:  # pragma: no cover - network
        action = order.side.upper()
        contract = Stock(order.symbol, "SMART", "USD")
        if order.price:
            ib_order = LimitOrder(action, order.qty, order.price)
            logger.debug("Submitting limit order", symbol=order.symbol, qty=order.qty, price=order.price)
        else:
            ib_order = MarketOrder(action, order.qty)
            logger.debug("Submitting market order", symbol=order.symbol, qty=order.qty)
        trade = self.ib.placeOrder(contract, ib_order)
        logger.info("Placed order", symbol=order.symbol, qty=order.qty, side=order.side)
        return str(trade.order.orderId)

    def get_balance(self) -> float:  # pragma: no cover - network
        summary = self.ib.accountSummary()
        for row in summary:
            if row.tag == "NetLiquidation" and (
                not getattr(self, "account_id", None) or row.account == self.account_id
            ):
                try:
                    value = float(row.value)
                    logger.debug("Retrieved account balance", value=value)
                    return value
                except ValueError:
                    continue
        return 0.0
