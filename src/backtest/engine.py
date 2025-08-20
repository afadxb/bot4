"""Backtest engine stub."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BacktestResult:
    trades: int = 0
    cagr: float = 0.0
    max_dd: float = 0.0


def run_backtest() -> BacktestResult:  # pragma: no cover - placeholder
    return BacktestResult()


if __name__ == "__main__":  # pragma: no cover
    print(run_backtest())
