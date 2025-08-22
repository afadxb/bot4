"""Pushover alert helper."""

from __future__ import annotations

import os
from typing import Optional

try:  # pragma: no cover - optional dependency
    import requests  # type: ignore
except Exception:  # pragma: no cover - fallback when requests missing
    from . import requests_stub as requests  # type: ignore


def send_pushover(message: str, title: str = "Bot Alert") -> None:
    """Send a pushover notification if credentials are available."""

    token = os.getenv("PUSHOVER_TOKEN")
    user = os.getenv("PUSHOVER_USER_KEY")
    if not token or not user:  # pragma: no cover - network side effect
        return
    requests.post("https://api.pushover.net/1/messages.json", data={"token": token, "user": user, "message": message, "title": title})
