"""How a forward predictor turns a predicted *effect* into a predicted *population*.

A predict-then-rank baseline must emit a population, not just a signature, because the
distributional retrieval layer scores populations. The synthesis step is therefore
load-bearing for every distributional claim made about predicted populations, and it is
easy to get wrong in a way that silently decides the answer.

Two modes, both explicit:

``cells`` (default)
    Apply the predicted effect to the query context's REAL control cells, one cell at a
    time. This is what the scGen / CPA family actually does: encode observed cells, do
    latent arithmetic per cell, decode per cell. It is the only mode under which a
    predicted population can carry the control population's covariance, and any
    multimodality the control population has.

``gaussian`` (legacy)
    ``control_mean + delta + iid N(0, resid_std)``. The result is a single isotropic cloud
    around one point, so it is UNIMODAL BY CONSTRUCTION: it cannot express subpopulation
    structure no matter what the predictor learned. Any structure diagnostic computed on a
    ``gaussian`` population therefore measures this synthesizer and not the predictor. In
    particular, a k-means k=2 between/total variance ratio on such a cloud returns that
    statistic's null value, not evidence that the predictor collapsed anything.

    Retained ONLY so the pre-2026-07-12 numbers can be regenerated and compared side by
    side. Do not use it to make a claim about a predictor.

An additive-effect predictor (average-effect, nearest-neighbor, and the latent-arithmetic
models scGen and CPA) shifts every cell by the SAME delta. Under ``cells`` this preserves
the control population's structure exactly and induces zero response divergence between
subpopulations: the per-subpopulation response deltas are identical by construction. That
is an analytic property of the model class, not an artifact of the synthesizer, and it is
the honest form of the structure-preservation gate.
"""
from __future__ import annotations

from typing import Optional

import numpy as np

SYNTH_MODES = ("cells", "gaussian")


def resample_rows(n_available: int, n_cells: int, rng: np.random.Generator) -> np.ndarray:
    """Row indices for an n_cells draw from a pool of n_available cells.

    Sampling is without replacement whenever the pool is large enough, so a predicted
    population is not inflated with duplicate cells (duplicates add zero-distance pairs and
    bias every kernel-based distance).
    """
    if n_available <= 0:
        raise ValueError("cannot synthesize a population from an empty control pool")
    return rng.choice(n_available, n_cells, replace=n_available < n_cells)


def synth_from_cells(control_cells: np.ndarray, delta: np.ndarray, n_cells: int,
                     rng: np.random.Generator) -> np.ndarray:
    """Additive effect applied per cell to real control cells: ``x_i + delta``.

    Preserves the control population's covariance and multimodality; adds no divergence.
    """
    C = np.asarray(control_cells, dtype=np.float32)
    if C.ndim != 2:
        raise ValueError(f"control_cells must be (cells, genes), got shape {C.shape}")
    idx = resample_rows(len(C), n_cells, rng)
    return (C[idx] + np.asarray(delta, dtype=np.float32)[None, :]).astype(np.float32)


def synth_gaussian(control_mean: np.ndarray, delta: np.ndarray, resid_std: np.ndarray,
                   n_cells: int, spread_scale: float, rng: np.random.Generator) -> np.ndarray:
    """LEGACY: ``control_mean + delta + iid N(0, resid_std)``. Unimodal by construction."""
    base = np.asarray(control_mean, dtype=np.float32) + np.asarray(delta, dtype=np.float32)
    noise = rng.normal(size=(n_cells, base.shape[0])).astype(np.float32) * \
        (np.asarray(resid_std, dtype=np.float32) * spread_scale)
    return (base[None, :] + noise).astype(np.float32)


def check_mode(synth: str, control_mean: Optional[np.ndarray],
               control_cells: Optional[np.ndarray]) -> None:
    """Fail loudly when the requested synthesis mode lacks the input it requires."""
    if synth not in SYNTH_MODES:
        raise ValueError(f"synth must be one of {SYNTH_MODES}, got {synth!r}")
    if synth == "cells" and control_cells is None:
        raise ValueError(
            "synth='cells' needs the query context's real control cells "
            "(control_cells, shape (cells, genes)). Pass them, or ask for synth='gaussian' "
            "explicitly and accept that the population is unimodal by construction.")
    if synth == "gaussian" and control_mean is None:
        raise ValueError("synth='gaussian' needs control_mean (genes,)")
