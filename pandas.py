"""Minimal pandas stub for unit tests.

This stub implements only the features required by the unit tests in this
kata: ``DataFrame`` construction from a dict of lists, basic ``iloc`` access
and column selection returning ``Series`` objects. It is *not* a drop-in
replacement for pandas.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List


class Series(list):
    """Very small subset of :class:`pandas.Series`."""

    @property
    def iloc(self) -> "Series":  # pragma: no cover - trivial
        return self


class DataFrame:
    """Very small subset of :class:`pandas.DataFrame`."""

    def __init__(self, data: Dict[str, Iterable[Any]]):
        self._data = {k: list(v) for k, v in data.items()}
        rows = zip(*self._data.values())
        self._rows: List[Dict[str, Any]] = [dict(zip(self._data.keys(), r)) for r in rows]

    class _ILoc:
        def __init__(self, rows: List[Dict[str, Any]]):
            self.rows = rows

        def __getitem__(self, idx: int) -> Dict[str, Any]:
            return self.rows[idx]

    @property
    def iloc(self) -> "DataFrame._ILoc":  # pragma: no cover - trivial
        return DataFrame._ILoc(self._rows)

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self._rows)

    def __getitem__(self, col: str) -> Series:
        return Series(self._data[col])

    # Convenience for tests expecting DataFrame with dropna/resample
    def dropna(self) -> "DataFrame":  # pragma: no cover - trivial
        return self

    def resample(self, *args: Any, **kwargs: Any):  # pragma: no cover - unused
        raise NotImplementedError("resample not supported in stub")
