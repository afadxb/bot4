import sys, pathlib; sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
from src.risk.stops import near_support


def test_near_support_by_atr():
    assert near_support(price=101, support=100, atr=2)  # within 0.5*ATR (1)


def test_near_support_by_percent():
    assert near_support(price=100.4, support=100, atr=0.1)  # within 0.5%


def test_not_near_support():
    assert not near_support(price=106, support=100, atr=2)
