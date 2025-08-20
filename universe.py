"""Universe loading utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from loguru import logger
from config import settings


def load_universe() -> Sequence[str]:
    """Load the universe of symbols according to configuration.

    Currently ``static`` and ``file`` sources read ``settings.universe_file``.
    The ``ibkr`` option is stubbed for future expansion.
    """

    source = settings.universe_source.lower()
    file_path = Path(settings.universe_file)

    logger.debug("Loading universe", source=source, file=str(file_path))

    if source in {"static", "file"}:
        if not file_path.exists():
            raise FileNotFoundError(file_path)
        symbols = [line.strip() for line in file_path.read_text().splitlines()[1:] if line.strip()]
        logger.debug("Loaded symbols", count=len(symbols))
        return symbols

    if source == "ibkr":  # pragma: no cover - requires IBKR
        raise NotImplementedError("IBKR universe source not implemented")

    raise ValueError(f"Unknown universe source: {settings.universe_source}")
