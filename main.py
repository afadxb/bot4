"""Command-line entry point for the adaptive S&P 100 bot.

The module now wires together all production components: it loads the
configured universe, pulls market data, evaluates entry and exit signals
and places orders through the broker.  Position state transitions are
tracked by :class:`bot.TradingBot`.
"""

from __future__ import annotations

from datetime import datetime
from time import sleep

from loguru import logger

from scheduler import Scheduler
from universe import load_universe
from bot import TradingBot
from data.market_data import IBKRMarketData
from exec.broker import IBKRBroker


def main() -> None:  # pragma: no cover - runtime entry
    logger.info("Starting trading bot")
    scheduler = Scheduler()
    universe = load_universe()
    logger.info("Loaded universe", count=len(universe))

    market_data = IBKRMarketData()
    broker = IBKRBroker()
    bot = TradingBot(market_data, broker)

    while True:
        now = datetime.now(tz=scheduler.tz)
        if scheduler.should_run_primary(now):
            logger.info("Running cycle", time=str(now))
            for symbol in universe:
                try:
                    bot.run_cycle(symbol)
                except Exception:
                    logger.opt(exception=True).error("Error processing symbol", symbol=symbol)
        next_run = scheduler.next_run(now)
        sleep((next_run - now).total_seconds())


if __name__ == "__main__":  # pragma: no cover
    main()
