import sys, pathlib; sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

import pandas as pd

from main import TradingBot
from exec.broker import Broker, Order
from exec.state import PositionState


class FakeMarketData:
    def __init__(self):
        self.calls = []
        self.exit_ready = False

    def get_bars(self, symbol: str, tf: str, lookback: int) -> pd.DataFrame:
        self.calls.append((symbol, tf, lookback))
        if tf == "D" and lookback == 2:
            data = {
                "close": [100, 110],
                "sma50": [95, 100],
                "sma200": [90, 90],
                "supertrend": [1, 1],
                "rsi": [55, 60],
                "macd_line": [0, 1],
                "macd_signal": [0, 0],
                "macd_hist": [0.5, 1.0],
                "avg_vol": [1_500_000, 1_500_000],
                "session_vol": [1_000_000, 2_000_000],
                "obv_slope": [1, 1],
                "pullback": [True, True],
                "bb_pos": [0.6, 0.6],
                "extended": [False, False],
                "gap_up": [False, False],
            }
            return pd.DataFrame(data)
        if tf == "4H" and lookback == 2:
            if not self.exit_ready:
                data = {
                    "supertrend": [1, 1],
                    "rsi": [50, 60],
                }
                return pd.DataFrame(data)
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
        if tf == "D" and lookback == 1:
            data = {
                "close": [110],
                "sma50": [115],
                "volume": [2_000_000],
                "avg_vol": [1_000_000],
                "trendline_break": [True],
            }
            return pd.DataFrame(data)
        if tf == "1H" and lookback == 2:
            data = {
                "supertrend": [1, -1],
                "macd_line": [1, -1],
                "macd_signal": [0, 0],
            }
            return pd.DataFrame(data)
        raise ValueError((tf, lookback))

    def get_last_close(self, symbol: str) -> float:  # pragma: no cover - not used
        return 0.0

    def get_vix(self) -> float:  # pragma: no cover - not used
        return 0.0

    def get_reference_symbol(self) -> str:  # pragma: no cover - not used
        return "SPY"


class MockBroker(Broker):
    def __init__(self):
        self.orders = []

    def place_order(self, order: Order) -> str:
        self.orders.append(order)
        return str(len(self.orders))

    def get_balance(self) -> float:
        return 10_000.0


def test_bot_entry_and_exit_cycle():
    md = FakeMarketData()
    broker = MockBroker()
    bot = TradingBot(md, broker)

    bot.run_cycle("AAPL")
    assert ("AAPL", "D", 2) in md.calls and ("AAPL", "4H", 2) in md.calls
    assert len(broker.orders) == 4  # entry + bracket
    assert broker.orders[0].qty == 9

    md.exit_ready = True
    bot.run_cycle("AAPL")
    assert ("AAPL", "1H", 2) in md.calls
    assert len(broker.orders) == 5  # plus exit order
    assert broker.orders[-1].qty == 9
    assert bot.positions["AAPL"] == PositionState.EXITED

    bot.run_cycle("AAPL")
    assert len(broker.orders) == 5
