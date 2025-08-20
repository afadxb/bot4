"""Stop and support utilities."""

from __future__ import annotations


def near_support(price: float, support: float, atr: float) -> bool:
    """Return True if ``price`` is within 0.5*ATR or 0.5% above ``support``."""

    if support <= 0:
        raise ValueError("support must be positive")
    cond1 = price <= support + 0.5 * atr
    cond2 = price / support <= 1.005
    return bool(cond1 or cond2)
