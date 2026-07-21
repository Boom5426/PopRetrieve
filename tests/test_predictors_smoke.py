"""Smoke tests for the predict-then-rank predictors (average-effect + nearest-neighbor).

Builds a tiny synthetic ``Dataset`` (2 contexts, a few drugs, real controls) and checks:
  * fit caches per-drug signatures; predict returns finite (genes,) vectors;
  * the predicted signature correlates with the TRUE planted drug effect;
  * predict_population returns (n_cells, genes) with non-zero spread;
  * nearest-neighbor picks the context whose control is closest.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np
import pandas as pd

from data.population import Dataset
from baselines.average_effect_predictor import AverageEffectPredictor
from baselines.nearest_neighbor_predictor import NearestNeighborPredictor

G = 60


def _synth_dataset(seed=0):
    rng = np.random.default_rng(seed)
    drugs = ["drugA", "drugB", "drugC"]
    contexts = ["ctxA", "ctxB"]
    ctrl_base = {"ctxA": rng.normal(size=G), "ctxB": rng.normal(size=G) + 2.0}
    drug_effect = {d: rng.normal(size=G) for d in drugs}
    rows = []
    Xparts = []
    for c in contexts:
        # controls
        Xc = ctrl_base[c][None, :] + rng.normal(size=(40, G)) * 0.3
        Xparts.append(Xc)
        for _ in range(40):
            rows.append({"perturbation": "control", "cell_line": c, "is_control": True})
        for d in drugs:
            Xt = ctrl_base[c][None, :] + drug_effect[d][None, :] + rng.normal(size=(30, G)) * 0.3
            Xparts.append(Xt)
            for _ in range(30):
                rows.append({"perturbation": d, "cell_line": c, "is_control": False})
    X = np.vstack(Xparts).astype(np.float32)
    obs = pd.DataFrame(rows)
    ds = Dataset(X=X, obs=obs, gene_names=[f"g{i}" for i in range(G)],
                 context_col="cell_line", pert_col="perturbation", name="synth")
    return ds, drug_effect, ctrl_base


def test_average_effect_fit_predict_shapes():
    ds, eff, _ = _synth_dataset()
    pred = AverageEffectPredictor().fit(ds)
    sig = pred.predict("drugA")
    assert sig.shape == (G,) and np.all(np.isfinite(sig))
    # predicted signature correlates with the planted effect
    r = np.corrcoef(sig, eff["drugA"])[0, 1]
    assert r > 0.8, r


def test_average_effect_population_spread():
    ds, _, ctrl = _synth_dataset()
    pred = AverageEffectPredictor().fit(ds)
    cells = ds.X[ds.control_rows("ctxA")]
    P = pred.predict_population("drugB", control_cells=cells, n_cells=100)
    assert P.shape == (100, G)
    assert P.std(0).mean() > 0.0
    # legacy synthesizer still available, and still produces a population
    Pg = pred.predict_population("drugB", control_mean=ctrl["ctxA"], n_cells=100,
                                 synth="gaussian")
    assert Pg.shape == (100, G) and Pg.std(0).mean() > 0.0


def test_synth_cells_requires_control_cells():
    """The structure-preserving path must fail loudly, never fall back to the mean."""
    ds, _, ctrl = _synth_dataset()
    pred = AverageEffectPredictor().fit(ds)
    for P in (pred, NearestNeighborPredictor().fit(ds)):
        try:
            P.predict_population("drugB", control_mean=ctrl["ctxA"], n_cells=10)
        except ValueError as exc:
            assert "control_cells" in str(exc)
        else:
            raise AssertionError(f"{P.name}: synth='cells' silently accepted a mean vector")


def test_gaussian_synth_is_unimodal_and_cells_synth_is_not():
    """Why the synthesizer choice is load-bearing for any structure claim.

    A bimodal control population must stay bimodal after an additive effect is applied to
    its cells, and must be flattened to one isotropic blob by the legacy synthesizer. This
    pins the reason the old 'predictors collapse subpopulation structure' number measured
    the wrapper rather than the predictor.
    """
    from sklearn.cluster import KMeans

    def var_ratio(X, k=2):
        km = KMeans(n_clusters=k, n_init=3, random_state=0).fit(X)
        mu = X.mean(0)
        sst = float(np.sum((X - mu) ** 2))
        ssw = sum(float(np.sum((X[km.labels_ == c] - X[km.labels_ == c].mean(0)) ** 2))
                  for c in range(k))
        return (sst - ssw) / sst

    rng = np.random.default_rng(0)
    # explicitly bimodal control population: two well-separated modes
    bimodal = np.vstack([rng.normal(size=(60, G)) * 0.3,
                         rng.normal(size=(60, G)) * 0.3 + 6.0]).astype(np.float32)
    ds, _, _ = _synth_dataset()
    pred = AverageEffectPredictor().fit(ds)

    P_cells = pred.predict_population("drugB", control_cells=bimodal, n_cells=120)
    P_gauss = pred.predict_population("drugB", control_mean=bimodal.mean(0), n_cells=120,
                                      synth="gaussian")
    assert var_ratio(P_cells) > 0.5, "cells-synth destroyed the control's bimodality"
    assert var_ratio(P_gauss) < 0.2, "gaussian-synth should be unimodal by construction"


def test_additive_predictors_induce_zero_response_divergence():
    """Gate 1, in its analytic form.

    An additive-effect predictor shifts every cell by the same delta, so two subpopulations
    of the predicted population have IDENTICAL response deltas against their own matched
    controls: cos(d_0, d_1) == 1 exactly. There is therefore no differential structure for a
    distributional scorer to exploit, regardless of how much baseline structure survives.
    """
    rng = np.random.default_rng(1)
    ds, _, _ = _synth_dataset()
    pred = AverageEffectPredictor().fit(ds)

    ctrl_0 = rng.normal(size=(50, G)).astype(np.float32) * 0.3
    ctrl_1 = (rng.normal(size=(50, G)) * 0.3 + 6.0).astype(np.float32)
    cells = np.vstack([ctrl_0, ctrl_1])
    lab = np.array([0] * 50 + [1] * 50)

    delta = pred.predict("drugB")
    P = cells + delta[None, :]                       # what synth='cells' does, per cell
    d0 = P[lab == 0].mean(0) - ctrl_0.mean(0)
    d1 = P[lab == 1].mean(0) - ctrl_1.mean(0)
    cos = float(d0 @ d1 / (np.linalg.norm(d0) * np.linalg.norm(d1)))
    assert abs(cos - 1.0) < 1e-5, f"additive predictor induced divergence: cos={cos}"


def test_nn_predict_shapes_and_corr():
    ds, eff, _ = _synth_dataset()
    pred = NearestNeighborPredictor().fit(ds)
    sig = pred.predict("drugC", context=ds.control_mean("ctxA"))
    assert sig.shape == (G,) and np.all(np.isfinite(sig))
    r = np.corrcoef(sig, eff["drugC"])[0, 1]
    assert r > 0.8, r


def test_nn_picks_nearest_context():
    ds, eff, ctrl = _synth_dataset()
    pred = NearestNeighborPredictor().fit(ds)
    # anchor exactly on ctxB control -> nearest context should be ctxB
    c_star = pred._nearest_context(ctrl["ctxB"])
    assert c_star == "ctxB"
    # with ctxB excluded, must transfer from ctxA
    c_star2 = pred._nearest_context(ctrl["ctxB"], exclude="ctxB")
    assert c_star2 == "ctxA"


def test_both_predictors_known_drugs():
    ds, _, _ = _synth_dataset()
    for P in (AverageEffectPredictor().fit(ds), NearestNeighborPredictor().fit(ds)):
        assert set(P.known_drugs()) == {"drugA", "drugB", "drugC"}


def test_nn_nearest_context_returns_none_when_all_excluded():
    """Degenerate single-context dataset with that context excluded -> None, never the
    excluded context itself (regression for the leave-one-context-out leak fix)."""
    ds, _, ctrl = _synth_dataset()
    pred = NearestNeighborPredictor().fit(ds, contexts=["ctxA"])
    assert pred._nearest_context(ctrl["ctxA"], exclude="ctxA") is None


def test_nn_predict_fallback_excludes_held_out_context():
    """When the nearest context lacks the drug, the fallback average must not include the
    excluded context's signature (airtight cross-context transfer)."""
    ds, _, ctrl = _synth_dataset()
    pred = NearestNeighborPredictor().fit(ds)
    # Force the fallback path: drug present only in ctxB, query anchored+excluding ctxB.
    pred._delta = {k: v for k, v in pred._delta.items()
                   if not (k[0] == "ctxA" and k[1] == "drugB")}
    sig = pred.predict("drugB", context=ctrl["ctxB"], exclude_context="ctxB")
    # ctxB is the only remaining context with drugB -> fallback has nothing to average,
    # so it must return zeros, NOT the excluded ctxB signature.
    assert np.allclose(sig, 0.0), "fallback leaked the excluded context's signature"
