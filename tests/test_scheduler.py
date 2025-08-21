import sys, pathlib; sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from scheduler import Scheduler
from config import settings


def test_scheduler_fallback_timezone():
    sched = Scheduler(tz="Mars/Phobos")
    assert str(sched.tz) == "UTC"


def test_scheduler_runs_on_4h_close_once():
    tz = ZoneInfo("America/New_York")
    sched = Scheduler(tz="America/New_York")
    dt = datetime(2024, 1, 1, 14, 0, tzinfo=tz)
    assert sched.should_run_primary(dt) is True
    # Same timestamp should not trigger again
    assert sched.should_run_primary(dt) is False
    # Non-boundary hour should not trigger
    dt2 = datetime(2024, 1, 1, 15, 0, tzinfo=tz)
    assert sched.should_run_primary(dt2) is False


def test_scheduler_next_run_interval():
    tz = ZoneInfo("America/New_York")
    sched = Scheduler(tz="America/New_York")
    now = datetime(2024, 1, 1, 10, 0, tzinfo=tz)
    expected = now + timedelta(minutes=settings.run_interval_min)
    assert sched.next_run(now) == expected
