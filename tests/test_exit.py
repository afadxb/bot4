import sys, pathlib; sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
import pandas as pd

from src.scoring.exit_scoring import compute_exit_score


def build_h4():
    data = {
        "supertrend": [1, -1],
        "macd_line": [1, -1],
        "macd_signal": [0, 0],
        "close": [105, 95],
        "sma20": [100, 100],
        "rsi": [55, 45],
        "bearish_pattern": [False, True],
    }
    return pd.DataFrame(data)


def build_d1():
    data = {
        "close": [110],
        "sma50": [115],
        "volume": [2_000_000],
        "avg_vol": [1_000_000],
        "trendline_break": [True],
    }
    return pd.DataFrame(data)


def build_h1(macd_cross=True):
    if macd_cross:
        macd_line = [1, -1]
        macd_sig = [0, 0]
    else:
        macd_line = [1, 1]
        macd_sig = [0, 0]
    data = {
        "supertrend": [1, -1],
        "macd_line": macd_line,
        "macd_signal": macd_sig,
    }
    return pd.DataFrame(data)


def test_exit_full_score_with_confirmation():
    comp = compute_exit_score(build_h4(), build_d1(), build_h1(True))
    assert comp.total == 15
    assert comp.h1_accel_confirmation == 1


def test_exit_no_confirmation_without_macd_cross():
    comp = compute_exit_score(build_h4(), build_d1(), build_h1(False))
    assert comp.h1_accel_confirmation == 0
