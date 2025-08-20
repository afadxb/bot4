"""Order helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from .broker import Order


@dataclass
class BracketOrder:
    entry: Order
    stop: Order
    pt1: Order
    pt2: Order


def build_bracket(symbol: str, qty: int, entry_price: float, stop_price: float, pt1: float, pt2: float) -> BracketOrder:
    """Create a simple bracket order."""

    entry = Order(symbol=symbol, qty=qty, side="BUY", price=entry_price)
    stop = Order(symbol=symbol, qty=qty, side="SELL", price=stop_price)
    pt1_o = Order(symbol=symbol, qty=qty // 2, side="SELL", price=pt1)
    pt2_o = Order(symbol=symbol, qty=qty - qty // 2, side="SELL", price=pt2)
    return BracketOrder(entry=entry, stop=stop, pt1=pt1_o, pt2=pt2_o)
