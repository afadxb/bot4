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


def test_dataframe_rename_tail_and_selection():
    df = pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]})
    df = df.rename(columns=str.lower)
    assert list(df.columns) == ["a", "b"]
    tail = df.tail(2)
    assert tail["a"] == [2, 3]
    subset = df[["a"]]
    assert list(subset.columns) == ["a"]


def test_series_rolling_diff_and_assignment():
    df = pd.DataFrame({"a": [1, 2, 3, 4], "b": [10, 20, 30, 40]})
    df["c"] = df["a"].rolling(2).mean()
    assert df["c"] == [1.0, 1.5, 2.5, 3.5]
    diff = df["b"].diff()
    assert diff == [0, 10, 10, 10]
