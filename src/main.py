"""Main entry point wiring components together."""

from __future__ import annotations

from datetime import datetime

from loguru import logger

from .config import settings
from .scheduler import Scheduler
from .universe import load_universe
from .scoring import sentiment


def main() -> None:  # pragma: no cover - runtime entry
    scheduler = Scheduler()
    universe = load_universe()
    logger.info("Loaded universe", count=len(universe))
    now = datetime.now()
    if scheduler.should_run_primary(now):
        fg = sentiment.get_fear_greed()
        logger.info("Fear & Greed", value=fg)
    logger.info("Next run at", time=scheduler.next_run(now))


if __name__ == "__main__":  # pragma: no cover
    main()
