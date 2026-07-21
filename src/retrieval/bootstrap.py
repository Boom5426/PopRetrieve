"""Bootstrap confidence intervals for retrieval metrics and scalar statistics.

``bootstrap_ci`` (ported from ``gidflow.metrics.ranking``) resamples QUERIES for a
retrieval metric; ``bootstrap_stat`` is a generic resampler over a 1-D sample used
for e.g. per-KO Hit@1 CIs in the Frangieh analysis.
"""
from __future__ import annotations

from typing import Callable, Sequence

import numpy as np

from .evaluation import retrieval_metrics


def bootstrap_ci(scores: np.ndarray, true_pos: np.ndarray, metric: str = "hit@10",
                 n_boot: int = 1000, seed: int = 0) -> tuple[float, float, float]:
    """Return (point, lo95, hi95) for a retrieval metric via query resampling."""
    rng = np.random.default_rng(seed)
    Q = len(true_pos)
    point = retrieval_metrics(scores, true_pos)[metric]
    vals = []
    for _ in range(n_boot):
        idx = rng.integers(0, Q, Q)
        vals.append(retrieval_metrics(scores[idx], true_pos[idx])[metric])
    lo, hi = np.percentile(vals, [2.5, 97.5])
    return float(point), float(lo), float(hi)


def bootstrap_stat(sample: Sequence[float], stat: Callable[[np.ndarray], float] = np.mean,
                   n_boot: int = 1000, seed: int = 0) -> tuple[float, float, float]:
    """Return (point, lo95, hi95) for ``stat`` over a 1-D sample via resampling."""
    x = np.asarray(sample, dtype=float)
    x = x[np.isfinite(x)]
    rng = np.random.default_rng(seed)
    if len(x) == 0:
        return float("nan"), float("nan"), float("nan")
    point = float(stat(x))
    vals = [float(stat(x[rng.integers(0, len(x), len(x))])) for _ in range(n_boot)]
    lo, hi = np.percentile(vals, [2.5, 97.5])
    return point, float(lo), float(hi)
