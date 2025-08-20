"""Internal hourly scheduler."""

from __future__ import annotations

from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from loguru import logger

from config import settings

FOUR_HOUR_BOUNDARIES = [time(10), time(14), time(18), time(22)]


class Scheduler:
    """Simple scheduler that decides when to run primary logic."""

    def __init__(self, tz: str | ZoneInfo = settings.timezone) -> None:
        try:
            self.tz = ZoneInfo(str(tz))
        except ZoneInfoNotFoundError:
            logger.warning("Timezone %s not found; falling back to UTC", tz)
            self.tz = ZoneInfo("UTC")
        self.last_primary: datetime | None = None

    def is_primary_time(self, now: datetime) -> bool:
        now_local = now.astimezone(self.tz)
        if now_local.minute != 0:
            return False
        return any(now_local.time().hour == t.hour for t in FOUR_HOUR_BOUNDARIES)

    def should_run_primary(self, now: datetime) -> bool:
        """Return True if the primary 4H tasks should run at ``now``.

        The method ensures that each 4H boundary triggers at most once.
        """

        if not self.is_primary_time(now):
            return False
        if self.last_primary and now <= self.last_primary:
            return False
        self.last_primary = now
        logger.debug("Primary task scheduled", time=str(now))
        return True

    def next_run(self, now: datetime) -> datetime:
        """Return the next time the hourly loop should wake up."""
        return now + timedelta(minutes=settings.run_interval_min)
