"""Minimal stub of loguru.logger.

This project avoids pulling in the real :mod:`loguru` dependency to keep the
test environment light-weight.  The previous stub exposed the ``logger`` API
but discarded all messages which made it difficult to understand what the bot
was doing at runtime.  For local debugging we implement a very small logger
that prints structured messages to ``stdout``.
"""

from __future__ import annotations

from datetime import datetime


class _Logger:
    """Very small subset of the :mod:`loguru` logger API.

    Each log method accepts positional arguments which are simply joined with a
    space.  Keyword arguments are rendered in ``key=value`` form.  The output
    is prefixed with a timestamp and the log level to aid debugging.
    """

    def _log(self, level: str, *args, **kwargs) -> None:
        ts = datetime.now().isoformat(timespec="seconds")
        parts = [str(a) for a in args]
        parts.extend(f"{k}={v}" for k, v in kwargs.items())
        message = " ".join(parts)
        print(f"[{ts}] {level}: {message}")

    def info(self, *args, **kwargs) -> None:
        self._log("INFO", *args, **kwargs)

    def debug(self, *args, **kwargs) -> None:
        self._log("DEBUG", *args, **kwargs)

    def warning(self, *args, **kwargs) -> None:
        self._log("WARNING", *args, **kwargs)

    def error(self, *args, **kwargs) -> None:
        self._log("ERROR", *args, **kwargs)


logger = _Logger()


__all__ = ["logger"]
