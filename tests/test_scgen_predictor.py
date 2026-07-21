"""Smoke test for the published-predictor wrapper (scGen + CPA-linear fallback).

Always exercises the CPA-linear fallback (deterministic, dependency-light) so the test is
green regardless of whether the scvi-tools/scGen training stack is installed. If scGen IS
importable the factory prefers it at run time; that path is exercised in exp09, not here.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np
import pandas as pd

from data.population import Dataset
from baselines.scgen_predictor import ScGenPredictor, make_scgen_predictor

G = 60


def _synth_dataset(seed=0):
    rng = np.random.default_rng(seed)
    drugs = ["drugA", "drugB", "drugC"]
    contexts = ["ctxA", "ctxB"]
    ctrl_base = {"ctxA": rng.normal(size=G), "ctxB": rng.normal(size=G) + 2.0}
    drug_effect = {d: rng.normal(size=G) for d in drugs}
    Xparts, rows = [], []
    for c in contexts:
        Xparts.append(ctrl_base[c][None, :] + rng.normal(size=(40, G)) * 0.3)
        rows += [{"perturbation": "control", "cell_line": c, "is_control": True}] * 40
        for d in drugs:
            Xparts.append(ctrl_base[c][None, :] + drug_effect[d][None, :] + rng.normal(size=(30, G)) * 0.3)
            rows += [{"perturbation": d, "cell_line": c, "is_control": False}] * 30
    ds = Dataset(X=np.vstack(Xparts).astype(np.float32), obs=pd.DataFrame(rows),
                 gene_names=[f"g{i}" for i in range(G)], context_col="cell_line",
                 pert_col="perturbation", name="synth")
    return ds, drug_effect, ctrl_base


def test_fallback_backend_label():
    P = ScGenPredictor(force_fallback=True)
    assert P.backend == "cpa_linear"


def test_fallback_predict_correlates():
    ds, eff, ctrl = _synth_dataset()
    P = ScGenPredictor(force_fallback=True, n_latent=20).fit(ds)
    sig = P.predict("drugA", control_mean=ctrl["ctxA"])
    assert sig.shape == (G,) and np.all(np.isfinite(sig))
    assert np.corrcoef(sig, eff["drugA"])[0, 1] > 0.7


def test_fallback_population_shape_and_spread():
    ds, _, ctrl = _synth_dataset()
    P = ScGenPredictor(force_fallback=True).fit(ds)
    cells = ds.X[ds.control_rows("ctxA")]
    pop = P.predict_population("drugB", control_cells=cells, n_cells=80)
    assert pop.shape == (80, G) and pop.std(0).mean() > 0.0
    pop_g = P.predict_population("drugB", control_mean=ctrl["ctxA"], n_cells=80,
                                 synth="gaussian")
    assert pop_g.shape == (80, G) and pop_g.std(0).mean() > 0.0


def test_latent_arithmetic_is_per_cell():
    """The CPA-linear path must encode/shift/decode EACH control cell, not just the mean.

    If the latent delta were applied to one mean vector and the population re-inflated with
    iid noise, every predicted population would be a single isotropic blob and the exp09
    structure diagnostics would be measuring the synthesizer. Two clearly separated groups
    of control cells must therefore still be separated after prediction.
    """
    ds, _, _ = _synth_dataset()
    P = ScGenPredictor(force_fallback=True, n_latent=20).fit(ds)
    a = ds.X[ds.control_rows("ctxA")]
    b = ds.X[ds.control_rows("ctxB")]          # ctxB controls sit +2.0 away from ctxA
    pop_a = P.predict_population("drugB", control_cells=a, n_cells=40, seed=0)
    pop_b = P.predict_population("drugB", control_cells=b, n_cells=40, seed=0)
    # the two decoded populations must stay apart: the predictor did not collapse them
    sep = np.linalg.norm(pop_a.mean(0) - pop_b.mean(0))
    within = 0.5 * (pop_a.std(0).mean() + pop_b.std(0).mean())
    assert sep > within, f"latent path collapsed distinct controls (sep={sep}, within={within})"


def test_factory_returns_backend_attr():
    impl = make_scgen_predictor(force_fallback=True)
    assert impl.backend == "cpa_linear"
    assert hasattr(impl, "fit") and hasattr(impl, "predict")
