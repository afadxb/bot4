import pandas as pd


def test_empty_dataframe_columns():
    df = pd.DataFrame(columns=["a", "b"])
    assert list(df.columns) == ["a", "b"]
    assert len(df) == 0


def test_dataframe_missing_columns_default_empty_lists():
    df = pd.DataFrame({"a": [1, 2]}, columns=["a", "b"])
    assert list(df.columns) == ["a", "b"]
    assert df["a"] == [1, 2]
    assert df["b"] == []
