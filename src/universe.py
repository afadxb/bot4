"""Universe loading utilities."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from .config import settings


def load_universe() -> Sequence[str]:
    """Load the universe of symbols according to configuration.

    Currently ``static`` and ``file`` sources read ``settings.universe_file``.
    The ``ibkr`` option is stubbed for future expansion.
    """

    source = settings.universe_source.lower()
    file_path = Path(settings.universe_file)

    if source in {"static", "file"}:
        if not file_path.exists():
            raise FileNotFoundError(file_path)
        return [line.strip() for line in file_path.read_text().splitlines()[1:] if line.strip()]

    if source == "ibkr":  # pragma: no cover - requires IBKR
        raise NotImplementedError("IBKR universe source not implemented")

    raise ValueError(f"Unknown universe source: {settings.universe_source}")
