import sys
import pathlib

# Ensure the local pandas stub is imported before any test runs.
sys.modules.pop("pandas", None)
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import pandas as pd  # noqa: F401
