"""Minimal tenacity.retry decorator stub."""

from __future__ import annotations

from typing import Callable


def retry(*args, **kwargs):
    def decorator(fn: Callable):
        return fn
    return decorator


def stop_after_attempt(n):  # pragma: no cover - trivial
    return None


def wait_fixed(n):  # pragma: no cover - trivial
    return None
