"""Nearest-neighbor predictor (predict-then-rank baseline).

A context-aware forward predictor that, unlike the average-effect model, DOES respect which
biological context the query lives in: to predict drug ``d`` in a query context, it transfers
``d``'s response from the training context whose CONTROL state is nearest (cosine) to the
query context's control state. Formally::

    c* = argmin_c  cosine_distance( control_mean(c_query), control_mean(c_train) )
    hat_delta_d = mean(treated_{c*, d}) - mean(control_{c*})

This is the k=1 instance-based analogue of transfer-learning perturbation predictors: it can
capture context-specific response magnitude/direction where the neighbor context is
informative, but — like any single-context predictor — it still emits ONE signature per
(drug, query), so it too is blind to *within-query* subpopulation divergence. exp09
contrasts mean/R² vs PopRetrieve retrieval on top of it.

Interface mirrors ``AverageEffectPredictor``: ``fit(dataset)`` then ``predict(drug, context)``
where ``context`` supplies the query control mean used to pick the neighbor.
"""
from __future__ import annotations

from typing import Optional

import numpy as np

from baselines.population_synthesis import check_mode, synth_from_cells, synth_gaussian


def _cos_dist(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na < 1e-12 or nb < 1e-12:
        return 1.0
    return 1.0 - float(a @ b / (na * nb))


class NearestNeighborPredictor:
    name = "nearest_neighbor"

    def __init__(self, spread_scale: float = 1.0, seed: int = 0):
        self.spread_scale = spread_scale
        self.seed = seed
        self._delta: dict[tuple, np.ndarray] = {}     # (context, drug) -> signature
        self._ctrl: dict[str, np.ndarray] = {}        # context -> control mean
        self._contexts: list = []
        self._resid_std: Optional[np.ndarray] = None
        self._genes: Optional[int] = None

    def fit(self, dataset, drugs: Optional[list] = None,
            contexts: Optional[list] = None) -> "NearestNeighborPredictor":
        ctxs = contexts if contexts is not None else list(dataset.contexts)
        self._contexts = list(ctxs)
        self._genes = dataset.X.shape[1]
        self._ctrl = {c: dataset.control_mean(c).astype(np.float32) for c in ctxs}
        pool = dataset.pert[~dataset.is_control]
        all_drugs = drugs if drugs is not None else sorted(set(pool.tolist()))
        resid_accum = []
        for c in ctxs:
            for d in all_drugs:
                rows = dataset.treated_rows(c, d)
                if len(rows) >= 2:
                    self._delta[(c, d)] = (dataset.X[rows].mean(0) - self._ctrl[c]).astype(np.float32)
                    if len(rows) >= 3:
                        resid_accum.append(dataset.X[rows] - dataset.X[rows].mean(0))
        self._resid_std = (np.vstack(resid_accum).std(0).astype(np.float32)
                           if resid_accum else np.ones(self._genes, dtype=np.float32))
        return self

    @staticmethod
    def _excluded(exclude_context, exclude_contexts) -> frozenset:
        """Normalize the two exclusion arguments into one set of held-out contexts."""
        out = set()
        if exclude_context is not None:
            out.add(exclude_context)
        if exclude_contexts:
            out.update(exclude_contexts)
        return frozenset(out)

    def _nearest_context(self, query_control: np.ndarray, excluded=frozenset(),
                         exclude: Optional[str] = None) -> Optional[str]:
        """Nearest training context by control-state cosine distance.

        Returns None when every candidate context is excluded, so callers can detect the
        degenerate case rather than silently receiving an excluded context. Never returns a
        context in ``excluded`` / ``exclude``.
        """
        excluded = self._excluded(exclude, excluded)
        qc = np.asarray(query_control, dtype=np.float32)
        best, bestd = None, np.inf
        for c in self._contexts:
            if c in excluded:
                continue
            d = _cos_dist(qc, self._ctrl[c])
            if d < bestd:
                best, bestd = c, d
        return best

    def predict(self, drug: str, context=None, exclude_context: Optional[str] = None,
                exclude_contexts=None, **_) -> np.ndarray:
        """Predicted signature for ``drug`` transferred from the nearest training context.

        ``context`` must be the query control MEAN vector (genes,). ``exclude_context`` /
        ``exclude_contexts`` hold the query's own context(s) out of the donor set to force
        genuine cross-context transfer. A heterogeneous query is composed of MORE THAN ONE
        context, so all of them must be excluded for the transfer to be out-of-sample;
        pass them together via ``exclude_contexts``.
        """
        excluded = self._excluded(exclude_context, exclude_contexts)

        def _fallback() -> np.ndarray:
            sigs = [self._delta[(c, drug)] for c in self._contexts
                    if c not in excluded and (c, drug) in self._delta]
            return (np.mean(sigs, axis=0).astype(np.float32) if sigs
                    else np.zeros(self._genes, np.float32))

        if context is None:
            return _fallback()
        c_star = self._nearest_context(context, excluded=excluded)
        if c_star is not None and (c_star, drug) in self._delta:
            return self._delta[(c_star, drug)]
        return _fallback()

    def predict_population(self, drug: str, control_mean: Optional[np.ndarray] = None,
                           n_cells: int = 200, context=None,
                           exclude_context: Optional[str] = None,
                           exclude_contexts=None,
                           seed: Optional[int] = None,
                           control_cells: Optional[np.ndarray] = None,
                           synth: str = "cells") -> np.ndarray:
        """Transfer ``drug``'s signature from the nearest training context, then synthesize.

        ``synth='cells'`` (default) applies the transferred signature to the query context's
        REAL control cells. The transferred signature is a single vector, so every cell is
        shifted identically: the control population's structure is preserved and no response
        divergence between subpopulations is induced. ``synth='gaussian'`` is the legacy
        synthesizer (see population_synthesis).
        """
        check_mode(synth, control_mean, control_cells)
        rng = np.random.default_rng(self.seed if seed is None else seed)
        anchor = context
        if anchor is None:
            anchor = control_mean if control_mean is not None else \
                np.asarray(control_cells, dtype=np.float32).mean(0)
        delta = self.predict(drug, context=anchor, exclude_context=exclude_context,
                             exclude_contexts=exclude_contexts)
        if synth == "cells":
            return synth_from_cells(control_cells, delta, n_cells, rng)
        return synth_gaussian(control_mean, delta, self._resid_std, n_cells,
                              self.spread_scale, rng)

    def known_drugs(self) -> list:
        return sorted({d for (_, d) in self._delta})
