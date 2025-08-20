import sys, pathlib; sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from datetime import datetime
from zoneinfo import ZoneInfo

from scheduler import Scheduler


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
