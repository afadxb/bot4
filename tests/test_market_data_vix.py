import pandas as pd

from data.market_data import YFinanceMarketData


class DummyYFinanceMarketData(YFinanceMarketData):
    """Test double avoiding network calls."""

    def __post_init__(self) -> None:
        # Skip IB connection
        pass

    def _download(self, symbol: str, duration: str, bar_size: str) -> pd.DataFrame:
        assert symbol == "^VIX"
        assert duration == "5 D"
        assert bar_size == "1 day"
        return pd.DataFrame({"close": [16.0, 17.5]})


def test_get_vix_and_reference_symbol():
    md = DummyYFinanceMarketData()
    assert md.get_vix() == 17.5
    assert md.get_reference_symbol() == "SPY"
