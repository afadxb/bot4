"""Lightweight pandas substitute used primarily for unit tests.

The project historically shipped a very small subset of :mod:`pandas` to keep
the test environment minimal.  During runtime however, third party libraries
such as ``yfinance`` expect the full pandas API which the stub cannot
provide.  To reconcile both use cases this module now attempts to import the
real pandas package when available and the code is not executed under
``pytest``.  When the import succeeds the module's globals are populated with
the real objects and the stub definitions are skipped.  When the import fails
or tests are running, a tiny in-house implementation offering just enough
features for the tests is used instead.
"""

from __future__ import annotations

import os
import sys
import importlib.machinery
import importlib.util
from typing import Any, Dict, Iterable, List, Optional, Union, Callable


# -- runtime shim ---------------------------------------------------------

if "PYTEST_CURRENT_TEST" not in os.environ and "pytest" not in sys.modules:  # pragma: no cover - delegation
    for path in sys.path[1:]:
        spec = importlib.machinery.PathFinder.find_spec("pandas", [path])
        if spec and spec.origin and spec.origin != __file__:
            module = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            try:
                spec.loader.exec_module(module)  # type: ignore[arg-type]
            except Exception:  # pragma: no cover - fall back to stub
                continue
            else:
                globals().update(module.__dict__)
                sys.modules[__name__] = module
                break


if "DataFrame" not in globals():

    class Series(list):
        """Very small subset of :class:`pandas.Series`."""

        @property
        def iloc(self) -> "Series":  # pragma: no cover - trivial
            return self

        # -- basic analytics -------------------------------------------------
        def rolling(self, window: int) -> "Series._Rolling":
            return Series._Rolling(self, window)

        class _Rolling:
            def __init__(self, series: "Series", window: int):
                self.series = series
                self.window = window

            def mean(self) -> "Series":
                data = self.series
                w = self.window
                result = []
                for i in range(len(data)):
                    start = max(0, i + 1 - w)
                    window_vals = data[start : i + 1]
                    result.append(sum(window_vals) / len(window_vals))
                return Series(result)

        def diff(self, periods: int = 1) -> "Series":
            result: List[Any] = []
            for i in range(len(self)):
                if i < periods:
                    result.append(0)
                else:
                    result.append(self[i] - self[i - periods])
            return Series(result)


    class DataFrame:
        """Very small subset of :class:`pandas.DataFrame`."""

        def __init__(
            self,
            data: Optional[Dict[str, Iterable[Any]]] = None,
            columns: Optional[Iterable[str]] = None,
            **_: Any,
        ):
            """Construct a minimal ``DataFrame``.

            Parameters
            ----------
            data:
                Mapping of column names to iterables. If omitted, an empty
                ``DataFrame`` is created.
            columns:
                Optional explicit column order. When provided, missing columns
                default to empty lists. Additional keyword arguments are accepted
                for API compatibility but ignored. This mirrors the behaviour of
                the real pandas constructor sufficiently for our tests and
                dashboard code.
            """

            if data is None:
                data = {}

            if columns is None:
                columns = list(data.keys())
            else:
                # Ensure all referenced columns exist in ``data``
                data = {col: list(data.get(col, [])) for col in columns}

            self._data = {k: list(v) for k, v in data.items()}
            self.columns = list(self._data.keys())
            rows = zip(*self._data.values())
            self._rows: List[Dict[str, Any]] = [dict(zip(self.columns, r)) for r in rows]

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

        def __getitem__(self, key: Union[str, List[str]]) -> Union[Series, "DataFrame"]:
            if isinstance(key, list):
                data = {col: self._data[col] for col in key}
                return DataFrame(data, columns=key)
            return Series(self._data[key])

        def __setitem__(self, key: str, value: Iterable[Any]) -> None:
            values = list(value) if isinstance(value, Iterable) and not isinstance(value, str) else [value] * len(self)
            self._data[key] = values
            if key not in self.columns:
                self.columns.append(key)
            for idx in range(len(values)):
                if idx < len(self._rows):
                    self._rows[idx][key] = values[idx]
                else:
                    self._rows.append({key: values[idx]})

        # Convenience for tests expecting DataFrame with dropna/resample
        def dropna(self) -> "DataFrame":  # pragma: no cover - trivial
            return self

        def resample(self, *args: Any, **kwargs: Any):  # pragma: no cover - unused
            raise NotImplementedError("resample not supported in stub")

        # -- additional helpers ----------------------------------------------
        def rename(
            self,
            *,
            columns: Optional[Union[Dict[str, str], Callable[[str], str]]] = None,
            inplace: bool = False,
        ) -> "DataFrame":
            if columns is None:
                return self

            if callable(columns):
                mapping = {col: columns(col) for col in self.columns}
            else:
                mapping = {col: columns.get(col, col) for col in self.columns}

            new_data = {mapping[col]: vals for col, vals in self._data.items()}
            if inplace:
                self._data = new_data
                self.columns = list(new_data.keys())
                rows = zip(*self._data.values())
                self._rows = [dict(zip(self.columns, r)) for r in rows]
                return self
            return DataFrame(new_data)

        def tail(self, n: int) -> "DataFrame":
            if n <= 0:
                return DataFrame({col: [] for col in self.columns}, columns=self.columns)
            new_data = {col: vals[-n:] for col, vals in self._data.items()}
            return DataFrame(new_data, columns=self.columns)
