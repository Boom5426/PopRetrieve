#!/usr/bin/env python
"""Exp09 structure diagnostics — what do predicted candidate populations actually contain?

This experiment supplies Gate 1 of the two-gate criterion ("structure must be preserved
before a distributional scorer can exploit it"). It compares PREDICTED candidate response
populations against the REAL ones a distributional scorer wins on.

Two things were wrong with the pre-2026-07-12 version of this experiment, and both are
fixed here. They matter because Gate 1 is the paper's mechanistic explanation for its
central negative result, so it must not be an artifact of our own code.

1. THE SYNTHESIZER DECIDED THE ANSWER. Every predictor emitted its population as
   ``control_mean + delta + iid Gaussian noise``, which is unimodal by construction. A
   k-means k=2 between/total variance ratio on such a cloud returns that statistic's NULL
   VALUE (~0.009 at these dimensions), not evidence that the predictor collapsed anything.
   The old "~5x lower subpopulation-variance ratio than real data" therefore measured our
   wrapper. Populations are now synthesized by applying the predicted effect to the query
   context's REAL control cells (``synth='cells'``, see baselines.population_synthesis).
   ``--synth both`` reruns the legacy path side by side so the change is auditable.

2. THE REAL REFERENCE WAS NOT LIKE-FOR-LIKE. "Real" was a single-context treated
   population, while the predicted population was anchored on the query's BLENDED control.
   The candidate population a distributional scorer actually ranks is the alpha-blended
   treated population across both contexts ("covers-both" in exp01-exp08), so that is now
   the reference (``real_blend``). The old single-context reference is kept as
   ``real_single`` for continuity.

THE QUANTITY THAT ACTUALLY DECIDES GATE 1 is not baseline structure but INDUCED RESPONSE
DIVERGENCE: do the query's two subpopulations respond in *different directions*? With
per-subpopulation matched controls,

    d_k = mean(treated cells of subpop k) - mean(control cells of subpop k)
    induced_response_cosine = cos(d_0, d_1)

Real data: cosine well below 1 (that divergence is the whole premise of PopRetrieve).
Any additive-effect predictor (average-effect, nearest-neighbor, and the latent-arithmetic
models scGen and CPA) adds the SAME delta to every cell, so d_0 = d_1 exactly and the
cosine is 1.000 by construction. That is an analytic property of the model class, it is not
a defect of the synthesizer, and it is the honest form of Gate 1: these predictors can
preserve baseline structure yet still offer a distributional scorer nothing to exploit,
because they induce no differential response.

Outputs:
    results/exp09_structure_diagnostics/exp09_structure_diagnostics.csv
    results/exp09_structure_diagnostics/exp09_structure_diagnostics_summary.csv
    results/exp09_structure_diagnostics/gate1_response_divergence.csv
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist
from scipy.stats import entropy, spearmanr
from sklearn.cluster import KMeans

from data.load_sciplex3 import load_sciplex3
from retrieval.tasks import ContextMixtureTask
from retrieval.metrics import score_mean_cosine, score_energy
from baselines.average_effect_predictor import AverageEffectPredictor
from baselines.nearest_neighbor_predictor import NearestNeighborPredictor
from baselines.scgen_predictor import make_scgen_predictor
from utils.io import results_path, write_csv
from utils.logging import log, section

OUT = "exp09_structure_diagnostics"
N_CELLS = 200
ALPHA = 0.7                      # query composition: majority / minority context mix
PAIRS = [("K562", "A549"), ("A549", "MCF7"), ("K562", "MCF7")]


# ── diagnostics ──────────────────────────────────────────────────────────────

def _subpop_variance_ratio(X: np.ndarray, k: int = 2) -> float:
    """Between-cluster / total sum-of-squares from k-means (0 = no structure, 1 = perfect).

    NOTE its null value: on a unimodal isotropic cloud this does NOT go to 0, because
    k-means always splits something. Compare against ``real_blend``, never against 0.
    """
    if len(X) < k + 1:
        return float("nan")
    km = KMeans(n_clusters=k, n_init=3, random_state=0, max_iter=50).fit(X)
    mu = X.mean(axis=0)
    sst = float(np.sum((X - mu) ** 2))
    if sst < 1e-12:
        return 0.0
    ssw = sum(float(np.sum((X[km.labels_ == c] - X[km.labels_ == c].mean(axis=0)) ** 2))
              for c in range(k))
    return float((sst - ssw) / sst)


def _split_half_stability(X: np.ndarray, reps: int = 10, seed: int = 0) -> float:
    """Mean cosine between centroids of random half-splits."""
    rng = np.random.default_rng(seed)
    n = len(X)
    if n < 4:
        return float("nan")
    cosines = []
    for _ in range(reps):
        idx = rng.permutation(n)
        m1, m2 = X[idx[: n // 2]].mean(0), X[idx[n // 2:]].mean(0)
        d = np.linalg.norm(m1) * np.linalg.norm(m2)
        cosines.append(1.0 if d < 1e-12 else float(np.dot(m1, m2) / d))
    return float(np.mean(cosines))


def _response_diversity(X: np.ndarray, seed: int = 0) -> float:
    """IQR of pairwise cosine distances among cells (higher = more diverse)."""
    if len(X) < 3:
        return float("nan")
    if len(X) > 100:
        rng = np.random.default_rng(seed)
        X = X[rng.choice(len(X), 100, replace=False)]
    dists = pdist(X, metric="cosine")
    return float(np.percentile(dists, 75) - np.percentile(dists, 25))


def _isotropy_index(X: np.ndarray, n_components: int = 20) -> float:
    """Normalized entropy of PCA explained-variance ratios. High = isotropic."""
    from sklearn.decomposition import PCA
    nc = min(n_components, min(X.shape) - 1)
    if nc < 2:
        return float("nan")
    ev = PCA(n_components=nc, random_state=0).fit(X).explained_variance_ratio_
    ev = ev / ev.sum()
    return float(entropy(ev) / np.log(nc))


def _cos(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float("nan") if na < 1e-12 or nb < 1e-12 else float(a @ b / (na * nb))


def _induced_response_cosine(X: np.ndarray, labels: np.ndarray,
                             ctrl_by_label: dict) -> float:
    """cos(d_0, d_1) where d_k = mean(subpop k) - mean(matched control of subpop k).

    THE Gate-1 quantity. Exactly 1.0 for any predictor that adds one delta to every cell.
    """
    uniq = [u for u in np.unique(labels) if u in ctrl_by_label]
    if len(uniq) < 2:
        return float("nan")
    deltas = []
    for u in uniq[:2]:
        rows = X[labels == u]
        if len(rows) < 2:
            return float("nan")
        deltas.append(rows.mean(0) - np.asarray(ctrl_by_label[u], dtype=np.float64))
    return _cos(deltas[0], deltas[1])


def _compute_diagnostics(X: np.ndarray, seed: int = 0) -> dict:
    return {
        "subpop_variance_ratio": _subpop_variance_ratio(X),
        "split_half_stability": _split_half_stability(X, seed=seed),
        "response_diversity": _response_diversity(X, seed=seed),
        "isotropy_index": _isotropy_index(X),
        "n_cells": len(X),
    }


def _score_disagreement(pops: dict, ctrl: np.ndarray, query_pop: np.ndarray,
                        seed: int = 0) -> float:
    """Spearman rho between mean_cosine and energy rankings across candidates."""
    names = list(pops)
    if len(names) < 3:
        return float("nan")
    mc = [score_mean_cosine(pops[n], query_pop, control_P=ctrl, control_Q=ctrl) for n in names]
    en = [score_energy(pops[n], query_pop, max_cells=min(200, N_CELLS), seed=seed) for n in names]
    rho, _ = spearmanr(mc, en)
    return float(rho)


# ── population builders (matched composition) ────────────────────────────────

def _blend(data, ctx_maj, ctx_min, rows_maj, rows_min, n_total, alpha, rng):
    """Alpha-mixture of two contexts' cells, with the context label carried per cell."""
    n_maj = int(round(alpha * n_total))
    n_min = n_total - n_maj
    if len(rows_maj) == 0 or len(rows_min) == 0:
        return None, None
    i_maj = rng.choice(rows_maj, n_maj, replace=len(rows_maj) < n_maj)
    i_min = rng.choice(rows_min, n_min, replace=len(rows_min) < n_min)
    X = np.vstack([data.X[i_maj], data.X[i_min]]).astype(np.float32)
    lab = np.array([ctx_maj] * n_maj + [ctx_min] * n_min)
    return X, lab


def _assign_to_modes(X, mu_a, mu_b, lab_a, lab_b):
    """Nearest-centroid subpop assignment, exactly as the retrieval layer does at score time."""
    da = np.linalg.norm(X - mu_a, axis=1)
    db = np.linalg.norm(X - mu_b, axis=1)
    return np.where(da < db, lab_a, lab_b)


# ── main ─────────────────────────────────────────────────────────────────────

def run(n_seeds: int = 8, n_drugs: int = 10, synth_modes=("cells", "gaussian")):
    section("EXP09 STRUCTURE DIAGNOSTICS — predicted vs real candidate populations")
    data = load_sciplex3()
    log(data.summary())
    log(f"synthesis modes under test: {list(synth_modes)}")

    avg = AverageEffectPredictor(seed=0).fit(data)
    nn = NearestNeighborPredictor(seed=0).fit(data)
    sg = make_scgen_predictor(force_fallback=False)
    sg.fit(data)
    log(f"[diag] predictors fitted: avg, nn, scgen(backend={sg.backend})")
    predictors = {"average_effect": avg, "nearest_neighbor": nn, "scgen": sg}

    rows, gate1_rows = [], []

    for ctx_maj, ctx_min in PAIRS:
        pair = f"{ctx_maj}+{ctx_min}"
        ctrl_maj = data.control_mean(ctx_maj)
        ctrl_min = data.control_mean(ctx_min)
        ctrl_blend = ALPHA * ctrl_maj + (1 - ALPHA) * ctrl_min
        ctrl_by_ctx = {ctx_maj: ctrl_maj, ctx_min: ctrl_min}
        cr_maj, cr_min = data.control_rows(ctx_maj), data.control_rows(ctx_min)

        # Drugs shared by both contexts (a candidate must exist in both to be blendable).
        # ContextMixtureTask.shared already computes this; do NOT rescan every treated cell.
        task = ContextMixtureTask(data, ctx_maj=ctx_maj, ctx_min=ctx_min)
        drugs = [d for d in sorted(task.shared)
                 if len(data.treated_rows(ctx_maj, d)) >= 10
                 and len(data.treated_rows(ctx_min, d)) >= 10][:n_drugs]
        log(f"[diag] pair {pair}: {len(drugs)} drugs with >=10 cells in both contexts")

        for drug in drugs:
            for seed in range(n_seeds):
                rng = np.random.default_rng(10_000 + seed)

                # blended CONTROL cells for the query context (what a predictor is anchored on)
                ctrl_cells, ctrl_lab = _blend(data, ctx_maj, ctx_min, cr_maj, cr_min,
                                              N_CELLS, ALPHA, rng)
                if ctrl_cells is None:
                    continue

                # REAL candidate population, matched composition ("covers-both")
                real_blend, real_lab = _blend(
                    data, ctx_maj, ctx_min,
                    data.treated_rows(ctx_maj, drug), data.treated_rows(ctx_min, drug),
                    N_CELLS, ALPHA, rng)
                if real_blend is None:
                    continue

                # old single-context reference, kept for continuity
                real_single = data.X[data.treated_rows(ctx_min, drug)][:N_CELLS]

                base = {"pair": pair, "drug": drug, "seed": seed}
                for tag, X in (("real_blend", real_blend), ("real_single", real_single)):
                    r = _compute_diagnostics(X, seed=seed)
                    r.update(base, source=tag, predictor=tag, synth="real")
                    rows.append(r)

                # Gate-1 quantity on the real candidate, using true context labels
                gate1_rows.append({**base, "predictor": "real_blend", "synth": "real",
                                   "induced_response_cosine": _induced_response_cosine(
                                       real_blend, real_lab, ctrl_by_ctx)})

                # centroids of the real candidate's two subpops, for nearest-mode assignment
                mu_a = real_blend[real_lab == ctx_maj].mean(0)
                mu_b = real_blend[real_lab == ctx_min].mean(0)

                for synth in synth_modes:
                    pred_pops = {}
                    for pname, pred in predictors.items():
                        kw = dict(n_cells=N_CELLS, seed=seed, synth=synth,
                                  control_mean=ctrl_blend, control_cells=ctrl_cells)
                        if pname == "nearest_neighbor":
                            kw.update(context=ctrl_min, exclude_context=ctx_min)
                        pp = pred.predict_population(drug, **kw)
                        d = _compute_diagnostics(pp, seed=seed)
                        d.update(base, source="predicted", predictor=pname, synth=synth)
                        rows.append(d)
                        pred_pops[pname] = pp

                        # Gate-1 quantity on the predicted candidate. Cells are assigned to
                        # subpopulations the way the retrieval layer does it (nearest mode),
                        # because a scorer has no oracle labels for a candidate.
                        plab = _assign_to_modes(pp, mu_a, mu_b, ctx_maj, ctx_min)
                        gate1_rows.append({**base, "predictor": pname, "synth": synth,
                                           "induced_response_cosine": _induced_response_cosine(
                                               pp, plab, ctrl_by_ctx)})

                    pred_pops["real_blend"] = real_blend
                    if len(pred_pops) >= 3:
                        for src, src_pop in pred_pops.items():
                            lib = {k: v for k, v in pred_pops.items() if k != src}
                            sd = _score_disagreement(lib, ctrl_blend, src_pop, seed=seed)
                            for r in rows:
                                if (r["seed"] == seed and r["drug"] == drug and r["pair"] == pair
                                        and r["predictor"] == src
                                        and r["synth"] in (synth, "real")):
                                    r["score_disagreement"] = sd
                                    break

    df = pd.DataFrame(rows)
    write_csv(df, results_path(OUT, "exp09_structure_diagnostics.csv"))

    metrics = ["subpop_variance_ratio", "split_half_stability", "response_diversity",
               "isotropy_index", "score_disagreement"]
    summ = df.groupby(["synth", "predictor"])[metrics].agg(["mean", "std"]).reset_index()
    summ.columns = ["synth", "predictor"] + [f"{m}_{s}" for m, s in summ.columns[2:]]
    write_csv(summ, results_path(OUT, "exp09_structure_diagnostics_summary.csv"))

    g1 = pd.DataFrame(gate1_rows)
    g1s = (g1.groupby(["synth", "predictor"])["induced_response_cosine"]
           .agg(["mean", "std", "median", "count"]).reset_index())
    write_csv(g1, results_path(OUT, "gate1_response_divergence.csv"))
    write_csv(g1s, results_path(OUT, "gate1_response_divergence_summary.csv"))

    section("BASELINE STRUCTURE (subpop_variance_ratio), by synthesis mode")
    log(summ[["synth", "predictor", "subpop_variance_ratio_mean",
              "subpop_variance_ratio_std"]].round(4).to_string(index=False))

    section("GATE 1 — INDUCED RESPONSE DIVERGENCE  cos(d_maj, d_min)")
    log("  1.000 = every cell got the same delta, so the two subpopulations respond")
    log("  identically and a distributional scorer has nothing differential to exploit.")
    log(g1s.round(4).to_string(index=False))

    ref = df[(df.predictor == "real_blend")].subpop_variance_ratio.mean()
    section("INTERPRETATION")
    log(f"  real_blend subpop_variance_ratio = {ref:.4f}")
    for synth in synth_modes:
        p = df[(df.source == "predicted") & (df.synth == synth)].subpop_variance_ratio.mean()
        log(f"  predicted ({synth:8s}) = {p:.4f}   ratio real/pred = {ref / p if p else float('nan'):.2f}x")
    return df, g1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-seeds", type=int, default=8)
    ap.add_argument("--n-drugs", type=int, default=10)
    ap.add_argument("--synth", choices=["cells", "gaussian", "both"], default="both",
                    help="population synthesizer; 'both' reruns the legacy path for comparison")
    args = ap.parse_args()
    modes = ("cells", "gaussian") if args.synth == "both" else (args.synth,)
    run(n_seeds=args.n_seeds, n_drugs=args.n_drugs, synth_modes=modes)


if __name__ == "__main__":
    main()
