import sys, pathlib; sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
import pandas as pd

from src.scoring.entry_scoring import compute_entry_score


def build_daily(rsi=60, macd_hist=1.0):
    data = {
        "close": [100, 110],
        "sma50": [95, 100],
        "sma200": [90, 90],
        "supertrend": [1, 1],
        "rsi": [55, rsi],
        "macd_line": [0, 1],
        "macd_signal": [0, 0],
        "macd_hist": [0.5, macd_hist],
        "avg_vol": [1_500_000, 1_500_000],
        "session_vol": [1_000_000, 2_000_000],
        "obv_slope": [1, 1],
        "pullback": [True, True],
        "bb_pos": [0.6, 0.6],
        "extended": [False, False],
        "gap_up": [False, False],
    }
    return pd.DataFrame(data)


def build_h4():
    data = {
        "supertrend": [1, 1],
        "rsi": [50, 60],
    }
    return pd.DataFrame(data)


def test_entry_full_score_tr():
    daily = build_daily()
    h4 = build_h4()
    score, comp = compute_entry_score(daily, h4, "TR", {"fg": 50, "news": "neutral"})
    assert score == 100
    assert comp.trend > 0 and comp.momentum > 0


def test_entry_sentiment_penalty():
    daily = build_daily()
    h4 = build_h4()
    score, _ = compute_entry_score(daily, h4, "TR", {"fg": 30})
    assert score == 95  # -5 penalty for mid FG


def test_entry_regime_multiplier_rg():
    daily = build_daily()
    h4 = build_h4()
    score, _ = compute_entry_score(daily, h4, "RG", {"fg": 50})
    assert round(score, 2) == 93.75


def test_entry_fg_block():
    daily = build_daily()
    h4 = build_h4()
    score, _ = compute_entry_score(daily, h4, "TR", {"fg": 10})
    assert score == 0
