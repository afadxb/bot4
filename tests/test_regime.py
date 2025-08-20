import sys, pathlib; sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))
import pandas as pd

from scoring.regime import detect_regime


def make_df(close: float, sma50: float, sma200: float, adx: float, n: int = 25):
    data = {
        "close": [close] * n,
        "sma50": [sma50] * n,
        "sma200": [sma200] * n,
        "adx": [adx] * n,
    }
    df = pd.DataFrame(data)
    return df


def test_regime_trending():
    df = make_df(110, 100, 90, 25)
    assert detect_regime(df, vix=15) == "TR"


def test_regime_ranging():
    df = make_df(100, 100, 90, 10)
    # slope ~0 since sma50 constant; vix mid-range
    assert detect_regime(df, vix=20) == "RG"


def test_regime_risk_off():
    df = make_df(80, 100, 90, 25)
    assert detect_regime(df, vix=30) == "RO"
