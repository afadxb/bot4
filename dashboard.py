"""Streamlit dashboard for monitoring bot operations.

Implements placeholders for the production-oriented dashboard blueprint.
"""

from __future__ import annotations

import datetime as dt

import pandas as pd
import streamlit as st


def main() -> None:
    """Render the Streamlit dashboard."""
    st.set_page_config(page_title="Bot Dashboard", layout="wide")
    st.title("Bot Dashboard")

    # A) Live status (top ribbon)
    now = dt.datetime.utcnow()
    next_close = (now + dt.timedelta(hours=4)).replace(minute=0, second=0, microsecond=0)
    countdown = next_close - now
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("Bot state", "RUNNING")
    col2.metric("Next 4H close", str(countdown).split(".")[0])
    col3.metric("Regime", "TR")
    col4.metric("FG Index", "62 · OK")
    col5.metric("Earnings guard", "0 tickers")
    col6.metric("Health", "last run 30s")

    # B) Portfolio & Risk panel
    st.header("Portfolio & Risk")
    portfolio_df = pd.DataFrame(
        columns=[
            "symbol",
            "size",
            "basis",
            "R unrealized",
            "Exit Score",
            "trail type",
            "stop distance",
            "time in trade",
        ]
    )
    st.dataframe(portfolio_df)
    st.metric("Risk usage", "0%")
    st.metric("Exposure", "0 / 0")
    st.metric("Drawdown", "0%")

    # C) Candidates (Entry engine)
    st.header("Candidates")
    candidates_df = pd.DataFrame(
        columns=[
            "symbol",
            "Entry Score",
            "Trend",
            "Momo",
            "Vol",
            "Setup",
            "sentiment adj",
            "near support",
            "limit",
            "stop",
            "R:R",
        ]
    )
    st.dataframe(candidates_df)
    st.text("Heatmap placeholder")
    st.text("Watchlist placeholder")

    # D) Exit & Scale-out monitor
    st.header("Exit & Scale-out")
    st.text("Exit score ladder placeholder")
    st.text("Action queue placeholder")

    # E) Regime & sentiment
    st.header("Regime & Sentiment")
    st.text("SPY vs SMA & ADX timeline placeholder")
    st.text("VIX band chart placeholder")
    st.text("FG history placeholder")
    st.text("News sentiment feed placeholder")

    # F) Performance & attribution
    st.header("Performance & Attribution")
    st.text("Equity curve placeholder")
    st.text("KPI tiles placeholder")
    st.text("Attribution views placeholder")
    st.text("R-distribution histogram placeholder")
    st.text("MFE/MAE violin placeholder")

    # G) Diagnostics (trust & QA)
    st.header("Diagnostics")
    st.text("Signal integrity placeholder")
    st.text("Missed opportunities placeholder")
    st.text("Data quality placeholder")


if __name__ == "__main__":  # pragma: no cover - UI entry point
    main()
