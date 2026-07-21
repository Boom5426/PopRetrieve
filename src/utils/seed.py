"""Deterministic seeding helpers.

Every experiment threads explicit integer seeds into ``numpy.random.default_rng``
so runs are byte-reproducible; ``set_seed`` additionally pins the global RNGs for
libraries (torch / sklearn) that read them (PCA/KMeans use ``random_state`` directly).
"""
from __future__ import annotations

import random

import numpy as np


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch
        torch.manual_seed(seed)
    except ImportError:  # pragma: no cover - torch always present here
        pass


def rng(seed: int) -> np.random.Generator:
    """Return an independent PCG64 generator (the reproduction workhorse)."""
    return np.random.default_rng(seed)
