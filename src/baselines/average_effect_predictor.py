"""Average-effect predictor (predict-then-rank baseline).

The simplest forward perturbation predictor and the canonical *majority-biased* control:
a drug's predicted response is its AVERAGE differential-expression effect pooled across the
training contexts, ignoring the query's subpopulation structure entirely. Formally, for
drug ``d`` the predicted signature is::

    hat_delta_d = mean_over_training_contexts( mean(treated_{c,d}) - mean(control_c) )

Because it collapses to a single per-drug signature, it can only ever reproduce a mean
match — so pairing it with JUDGE's distributional decision layer cannot manufacture
subpopulation coverage the predictor never modeled. That is the point: exp09 shows the
*predictor* is the ceiling for a mean+R² retrieval, and JUDGE's gains over a mean retrieval
on top of the SAME predictor are bounded, isolating where the retrieval layer helps vs
where the predictor does.

Interface: ``fit(dataset)`` caches per-drug average signatures; ``predict(drug, context)``
returns the predicted mean-delta signature (genes,). ``predict_population`` turns that
signature into a population so the predictor can also be scored by distributional
retrieval, not only mean/R²: by default it applies the signature to the query context's
real control cells (see ``baselines.population_synthesis``), which shifts every cell by the
same vector and therefore preserves the control population's structure while inducing zero
response divergence between subpopulations.
"""
from __future__ import annotations

from typing import Optional

import numpy as np

from baselines.population_synthesis import check_mode, synth_from_cells, synth_gaussian


class AverageEffectPredictor:
    name = "average_effect"

    def __init__(self, spread_scale: float = 1.0, seed: int = 0):
        self.spread_scale = spread_scale
        self.seed = seed
        self._sig: dict[str, np.ndarray] = {}
        self._resid_std: Optional[np.ndarray] = None
        self._genes: Optional[int] = None

    def fit(self, dataset, drugs: Optional[list] = None,
            contexts: Optional[list] = None) -> "AverageEffectPredictor":
        """Cache each drug's context-averaged mean-delta signature from a ``Dataset``."""
        ctxs = contexts if contexts is not None else list(dataset.contexts)
        ctrl_mean = {c: dataset.control_mean(c) for c in ctxs}
        pool = dataset.pert[~dataset.is_control]
        all_drugs = drugs if drugs is not None else sorted(set(pool.tolist()))
        self._genes = dataset.X.shape[1]
        resid_accum = []
        for d in all_drugs:
            deltas = []
            for c in ctxs:
                rows = dataset.treated_rows(c, d)
                if len(rows) >= 2:
                    tm = dataset.X[rows].mean(0)
                    deltas.append(tm - ctrl_mean[c])
            if deltas:
                sig = np.mean(deltas, axis=0)
                self._sig[d] = sig.astype(np.float32)
                # residual spread: within-context cell scatter around the treated mean
                for c in ctxs:
                    rows = dataset.treated_rows(c, d)
                    if len(rows) >= 3:
                        resid_accum.append(dataset.X[rows] - dataset.X[rows].mean(0))
        if resid_accum:
            R = np.vstack(resid_accum)
            self._resid_std = R.std(0).astype(np.float32)
        else:
            self._resid_std = np.ones(self._genes, dtype=np.float32)
        return self

    def predict(self, drug: str, context=None, **_) -> np.ndarray:
        """Predicted mean-delta signature for ``drug`` (context-independent by design)."""
        if drug not in self._sig:
            return np.zeros(self._genes, dtype=np.float32)
        return self._sig[drug]

    def predict_population(self, drug: str, control_mean: Optional[np.ndarray] = None,
                           n_cells: int = 200, context=None, seed: Optional[int] = None,
                           control_cells: Optional[np.ndarray] = None,
                           synth: str = "cells") -> np.ndarray:
        """Synthesize a predicted response population for ``drug``.

        ``synth='cells'`` (default) applies the drug's single mean-delta signature to the
        query context's REAL control cells, one cell at a time. That is what this model
        class does: an average-effect predictor shifts every cell by the same vector. The
        predicted population therefore inherits the control population's structure exactly
        and induces no response divergence between subpopulations.

        ``synth='gaussian'`` is the legacy synthesizer (see population_synthesis).
        """
        check_mode(synth, control_mean, control_cells)
        rng = np.random.default_rng(self.seed if seed is None else seed)
        delta = self.predict(drug, context)
        if synth == "cells":
            return synth_from_cells(control_cells, delta, n_cells, rng)
        return synth_gaussian(control_mean, delta, self._resid_std, n_cells,
                              self.spread_scale, rng)

    def known_drugs(self) -> list:
        return list(self._sig)
