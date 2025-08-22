"""Command-line entry point for the adaptive S&P 100 bot.

The module now wires together all production components: it loads the
configured universe, pulls market data, evaluates entry and exit signals
and places orders through the broker.  Position state transitions are
tracked by :class:`TradingBot`.
"""

from __future__ import annotations

from datetime import datetime
from time import sleep
from dataclasses import dataclass, field
from typing import Dict

from loguru import logger

from scheduler import Scheduler
from universe import load_universe
from data.market_data import MarketData, YFinanceMarketData
from exec.broker import Broker, Order, IBKRBroker
from exec.orders import build_bracket
from exec.state import PositionState, next_state
from scoring.entry_scoring import compute_entry_score
from scoring.exit_scoring import compute_exit_score
from config import settings


@dataclass
class TradingBot:
    """Coordinator that pulls data, evaluates signals and places orders."""

    market_data: MarketData
    broker: Broker
    regime: str = "TR"
    positions: Dict[str, PositionState] = field(default_factory=dict)
    position_sizes: Dict[str, int] = field(default_factory=dict)
    portfolio_pct: float = settings.portfolio_pct

    def run_cycle(self, symbol: str) -> None:
        """Run one evaluation cycle for ``symbol``.

        The method checks whether a new position should be opened or an
        existing one should be closed based on scoring modules.  It
        maintains a simple state machine per symbol.
        """

        state = self.positions.get(symbol, PositionState.INIT)
        logger.debug("Run cycle", symbol=symbol, state=state)
        if state is PositionState.INIT:
            self._attempt_entry(symbol)
        elif state in {PositionState.FILLED, PositionState.MANAGED}:
            self._check_exit(symbol)

    # -- internal helpers -------------------------------------------------

    def _attempt_entry(self, symbol: str) -> None:
        daily = self.market_data.get_bars(symbol, "D", 2)
        h4 = self.market_data.get_bars(symbol, "4H", 2)
        score, _ = compute_entry_score(daily, h4, self.regime, {"fg": 50})
        logger.debug("Entry score computed", symbol=symbol, score=score)
        if score < 90:
            logger.debug("Entry score below threshold", symbol=symbol)
            return
        if symbol in self.positions and self.positions[symbol] is not PositionState.EXITED:
            logger.debug("Symbol already in positions", symbol=symbol)
            return
        price = float(daily["close"].iloc[-1])
        equity = getattr(self.broker, "get_balance", lambda: 0.0)()
        allocation = equity * self.portfolio_pct
        qty = int(allocation / price)
        logger.debug(
            "Position sizing", symbol=symbol, price=price, equity=equity, allocation=allocation, qty=qty
        )
        if qty <= 0:
            logger.debug("Quantity not positive", symbol=symbol)
            return
        bracket = build_bracket(
            symbol,
            qty=qty,
            entry_price=price,
            stop_price=price * 0.95,
            pt1=price * 1.02,
            pt2=price * 1.05,
        )
        logger.debug(
            "Placing bracket orders",
            symbol=symbol,
            entry=bracket.entry.price,
            stop=bracket.stop.price,
            pt1=bracket.pt1.price,
            pt2=bracket.pt2.price,
        )
        for order in (bracket.entry, bracket.stop, bracket.pt1, bracket.pt2):
            self.broker.place_order(order)
        self.positions[symbol] = next_state(PositionState.INIT, filled=True)
        self.position_sizes[symbol] = qty

    def _check_exit(self, symbol: str) -> None:
        h4 = self.market_data.get_bars(symbol, "4H", 2)
        d1 = self.market_data.get_bars(symbol, "D", 1)
        h1 = self.market_data.get_bars(symbol, "1H", 2)
        comp = compute_exit_score(h4, d1, h1)
        logger.debug("Exit score computed", symbol=symbol, score=comp.total)
        if comp.total < 15:
            logger.debug("Exit score below threshold", symbol=symbol)
            return
        price = float(d1["close"].iloc[-1])
        qty = self.position_sizes.get(symbol, 0)
        logger.debug("Exit sizing", symbol=symbol, price=price, qty=qty)
        if qty <= 0:
            logger.debug("No position to exit", symbol=symbol)
            return
        exit_order = Order(symbol=symbol, qty=qty, side="SELL", price=price)
        self.broker.place_order(exit_order)
        self.positions[symbol] = next_state(PositionState.MANAGED, exited=True)
        self.position_sizes.pop(symbol, None)


def main() -> None:  # pragma: no cover - runtime entry
    logger.info("Starting trading bot")
    scheduler = Scheduler()
    universe = load_universe()
    logger.info("Loaded universe", count=len(universe))

    market_data = YFinanceMarketData()
    broker = IBKRBroker()
    bot = TradingBot(market_data, broker)

    while True:
        now = datetime.now(tz=scheduler.tz)
        logger.debug("Main loop tick", time=str(now))
        if scheduler.should_run_primary(now):
            logger.info("Running cycle", time=str(now))
            for symbol in universe:
                try:
                    bot.run_cycle(symbol)
                except Exception:
                    logger.opt(exception=True).error("Error processing symbol", symbol=symbol)
        else:
            logger.debug("Primary cycle skipped", time=str(now))
        next_run = scheduler.next_run(now)
        logger.debug("Sleeping", until=str(next_run))
        sleep((next_run - now).total_seconds())


if __name__ == "__main__":  # pragma: no cover
    main()
