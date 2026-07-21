"""Path resolution + small IO helpers for the DART repo.

DART is a standalone repository; the package root IS the repo root. Processed tensors
are read from ``<repo>/data`` (large, git-ignored — see data/README.md). Set the
``DIDR_DATA_ROOT`` env var to point elsewhere (on the original dev machine a
``data -> ../data`` symlink makes this resolve to the shared data tree).
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pandas as pd

PKG_ROOT = Path(__file__).resolve().parents[2]          # DART/  (repo root == package root)
REPO_ROOT = PKG_ROOT                                     # standalone repo
DATA_ROOT = Path(os.environ.get("DIDR_DATA_ROOT", PKG_ROOT / "data"))
RESULTS_ROOT = PKG_ROOT / "results"


def data_path(*parts: str) -> Path:
    return DATA_ROOT.joinpath(*parts)


def results_path(*parts: str) -> Path:
    return RESULTS_ROOT.joinpath(*parts)


def write_csv(df: pd.DataFrame, path: str | Path) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    return path


def load_config(path: str | Path) -> dict[str, Any]:
    """Load a YAML experiment config; falls back to an empty dict if absent."""
    path = Path(path)
    if not path.exists():
        return {}
    import yaml
    with open(path) as fh:
        return yaml.safe_load(fh) or {}
