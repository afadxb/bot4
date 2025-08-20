"""Position sizing helpers."""

from __future__ import annotations

from config import settings


def position_size(equity: float, entry: float, stop: float, risk_per_trade: float | None = None) -> int:
    """Return share quantity respecting risk per trade.

    Args:
        equity: Account equity.
        entry: Proposed entry price.
        stop: Protective stop price.
        risk_per_trade: Fractional risk per trade. Defaults to ``settings.risk_per_trade``.
    """

    risk = (equity * (risk_per_trade or settings.risk_per_trade))
    risk_per_share = entry - stop
    if risk_per_share <= 0:
        return 0
    qty = int(risk / risk_per_share)
    return max(qty, 0)
