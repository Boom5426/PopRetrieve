"""PCA-latent retrieval baseline.

A representation-learning stand-in between raw-signature CMap retrieval and JUDGE's full
distributional distances: project cells into a low-dimensional PCA latent (fit on the
available control / query cells, so it is a purely *unsupervised* linear embedding), then
retrieve with one of two kernels:

    mode='mean'  — cosine of the mean latent-delta vectors (a latent-space CMap; still a
                   mean-based, subpopulation-blind score).
    mode='dist'  — a distributional distance IN the latent space: the (negated) energy
                   distance between the candidate and query latent point clouds. This keeps
                   distributional information but at a fraction of the ambient dimension —
                   a cheap distributional retriever to bracket JUDGE against.

The PCA basis is fit once per query on a control anchor (query control cells if available,
else the pooled candidate+query cells), then reused for every candidate so scores are
comparable.  ``n_components`` is clipped to the feasible rank.
"""
from __future__ import annotations

import numpy as np
from sklearn.decomposition import PCA

from .base import Candidate, NormalizedQuery, cosine


def _energy_distance_np(X: np.ndarray, Y: np.ndarray, max_cells: int = 400,
                        seed: int = 0) -> float:
    """Numpy energy distance E = 2E|X-Y| - E|X-X'| - E|Y-Y'| (lower = closer).

    Subsampled for tractability; pure numpy so the baseline carries no torch dependency
    (the ambient-space JUDGE energy uses the torch/CUDA kernel — this is the latent bracket).
    """
    rng = np.random.default_rng(seed)
    def sub(A, s):
        return A if len(A) <= max_cells else A[np.random.default_rng(s).choice(len(A), max_cells, replace=False)]
    X, Y = sub(X, seed), sub(Y, seed + 1)
    if len(X) < 2 or len(Y) < 2:
        return 1e6
    from scipy.spatial.distance import cdist
    dxy = cdist(X, Y).mean(); dxx = cdist(X, X).mean(); dyy = cdist(Y, Y).mean()
    return float(2 * dxy - dxx - dyy)


class PCALatentRetrieval:
    """Retrieve in a PCA latent fit on a per-query control/pooled anchor."""

    def __init__(self, n_components: int = 30, mode: str = "mean",
                 max_cells: int = 400, seed: int = 0):
        if mode not in ("mean", "dist"):
            raise ValueError("mode must be 'mean' or 'dist'")
        self.n_components = n_components
        self.mode = mode
        self.max_cells = max_cells
        self.seed = seed
        self.name = f"pca_{mode}"

    def _fit_basis(self, nq: NormalizedQuery) -> PCA:
        # Anchor the basis on the query cells + a sample of candidate cells so the latent
        # spans the response directions; unsupervised (no ground-truth leakage).
        parts = [np.asarray(nq.Q, dtype=np.float64)]
        for c in nq.candidates:
            parts.append(np.asarray(c.X, dtype=np.float64))
        pool = np.vstack(parts)
        if len(pool) > 4000:
            pool = pool[np.random.default_rng(self.seed).choice(len(pool), 4000, replace=False)]
        k = int(min(self.n_components, pool.shape[1], max(2, min(pool.shape) - 1)))
        pca = PCA(n_components=k, random_state=self.seed)
        pca.fit(pool)
        return pca

    def score(self, nq: NormalizedQuery, **_) -> dict[str, float]:
        pca = self._fit_basis(nq)
        Qz = pca.transform(np.asarray(nq.Q, dtype=np.float64))
        cQ = None
        if nq.control_Q is not None:
            cQ = pca.transform(np.asarray(nq.control_Q, dtype=np.float64)[None, :])[0]
        q_mean = Qz.mean(0) - (cQ if cQ is not None else 0.0)
        out = {}
        for c in nq.candidates:
            Pz = pca.transform(np.asarray(c.X, dtype=np.float64))
            if self.mode == "mean":
                cP = None
                if c.control is not None:
                    cP = pca.transform(np.asarray(c.control, dtype=np.float64)[None, :])[0]
                p_mean = Pz.mean(0) - (cP if cP is not None else 0.0)
                out[c.name] = cosine(q_mean, p_mean)
            else:  # dist
                out[c.name] = -_energy_distance_np(Pz, Qz, self.max_cells, self.seed)
        return out


def pca_latent_scores(nq: NormalizedQuery, n_components: int = 30, mode: str = "mean",
                      max_cells: int = 400, seed: int = 0) -> dict[str, float]:
    return PCALatentRetrieval(n_components=n_components, mode=mode,
                              max_cells=max_cells, seed=seed).score(nq)
