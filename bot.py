from __future__ import annotations

"""Simple trading loop wiring market data, scoring and execution.

The :class:`TradingBot` ties together the market data provider, scoring
modules and broker to demonstrate how a full cycle of entry and exit might
be orchestrated.  It is intentionally lightweight and uses the stub
implementations provided elsewhere in the project.
"""

from dataclasses import dataclass, field
from typing import Dict

from exec.broker import Broker, Order
from exec.orders import build_bracket
from exec.state import PositionState, next_state
from data.market_data import MarketData
from scoring.entry_scoring import compute_entry_score
from scoring.exit_scoring import compute_exit_score


@dataclass
class TradingBot:
    """Coordinator that pulls data, evaluates signals and places orders."""

    market_data: MarketData
    broker: Broker
    regime: str = "TR"
    positions: Dict[str, PositionState] = field(default_factory=dict)

    def run_cycle(self, symbol: str) -> None:
        """Run one evaluation cycle for ``symbol``.

        The method checks whether a new position should be opened or an
        existing one should be closed based on scoring modules.  It
        maintains a simple state machine per symbol.
        """

        state = self.positions.get(symbol, PositionState.INIT)
        if state is PositionState.INIT:
            self._attempt_entry(symbol)
        elif state in {PositionState.FILLED, PositionState.MANAGED}:
            self._check_exit(symbol)

    # -- internal helpers -------------------------------------------------

    def _attempt_entry(self, symbol: str) -> None:
        daily = self.market_data.get_bars(symbol, "D", 2)
        h4 = self.market_data.get_bars(symbol, "4H", 2)
        score, _ = compute_entry_score(daily, h4, self.regime, {"fg": 50})
        if score < 90:
            return
        price = float(daily["close"].iloc[-1])
        bracket = build_bracket(
            symbol,
            qty=100,
            entry_price=price,
            stop_price=price * 0.95,
            pt1=price * 1.02,
            pt2=price * 1.05,
        )
        for order in (bracket.entry, bracket.stop, bracket.pt1, bracket.pt2):
            self.broker.place_order(order)
        self.positions[symbol] = next_state(PositionState.INIT, filled=True)

    def _check_exit(self, symbol: str) -> None:
        h4 = self.market_data.get_bars(symbol, "4H", 2)
        d1 = self.market_data.get_bars(symbol, "D", 1)
        h1 = self.market_data.get_bars(symbol, "1H", 2)
        comp = compute_exit_score(h4, d1, h1)
        if comp.total < 15:
            return
        price = float(d1["close"].iloc[-1])
        exit_order = Order(symbol=symbol, qty=100, side="SELL", price=price)
        self.broker.place_order(exit_order)
        self.positions[symbol] = next_state(PositionState.MANAGED, exited=True)
