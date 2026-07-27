#!/usr/bin/env python
"""Experiment 9 — Predict-then-rank: forward predictors x retrieval decision layers.

The predict-then-rank paradigm the field actually uses: a *forward predictor* imagines each
candidate drug's response in the query context, then a *retrieval rule* ranks the imagined
responses against the observed query. This experiment factorizes those two stages so the
retrieval decision layer is isolated:

    predictors  (forward response models)          retrieval rules (decision layer)
      average_effect   context-averaged signature    mean_cosine   cosine of mean-delta signatures
      nearest_neighbor nearest-context transfer      r2            R^2 of predicted vs observed delta
      scgen            published (scGen / CPA-linear  dart_energy   -energy_distance (distributional)
                       fallback; backend stamped)     dart_coverage -mean_k energy over subpops

For each query we build a candidate library {covers-both (GT)} ∪ distractor drugs, ask the
predictor for each candidate's response population in the query context, then score every
candidate under all four retrieval rules. The money comparison: holding the PREDICTOR fixed,
does swapping a mean/R² retrieval for EvalShift's distributional retrieval move the ground-truth
drug up the ranking? Reported per (predictor, retrieval) as Drug Hit@1/5, MRR, nDCG@10, and —
versus the same predictor's mean-cosine retrieval as reference — top-1 flip, top-k overlap,
delta-rank; divergence-stratified; with wall-clock runtime.

Outputs (results/exp09_predict_then_rank/):
    summary.csv                 per (task, predictor, retrieval) retrieval metrics
    predictor_ranker_matrix.csv compact predictor x retrieval Hit@1/MRR/nDCG matrix
    per_query_scores.csv        one row per (query, candidate) x (predictor,retrieval)
    flip_vs_mean.csv            EvalShift vs mean/R² flip, overlap, Δrank (predictor held fixed)
    divergence_stratified.csv   per (predictor, retrieval, divergence stratum) Hit@1
    runtime.csv                 predictor fit + per-query predict + retrieval wall-clock
    provenance.csv              scgen backend actually used ('scgen' | 'cpa_linear')

    python src/experiments/exp09_predict_then_rank.py --n-seeds 8 --n-drugs 10
    QUICK=1 python src/experiments/exp09_predict_then_rank.py
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from data.load_sciplex3 import load_sciplex3
from data.load_frangieh import load_frangieh
from retrieval.tasks import ControlledMixtureTask, ContextMixtureTask, context_divergence_probe
from retrieval.metrics import score_energy, score_coverage
from retrieval.target_metrics import stratify_by_divergence
from utils.io import results_path, write_csv
from utils.logging import log, section

from experiments.baseline_common import query_divergence, per_query_metrics, summarize
from baselines.base import normalize_query, cosine
from baselines.average_effect_predictor import AverageEffectPredictor
from baselines.nearest_neighbor_predictor import NearestNeighborPredictor
from baselines.scgen_predictor import ScGenPredictor

OUT = "exp09_predict_then_rank"
GT = "covers-both"
RETRIEVALS = ["mean_cosine", "r2", "dart_energy", "dart_coverage"]
DART_RETRIEVALS = {"dart_energy", "dart_coverage"}
REF_RETRIEVAL = "mean_cosine"
METRIC_COLS = ["hit@1", "hit@5", "mrr", "ndcg@10", "rank"]


def _r2(pred_delta: np.ndarray, obs_delta: np.ndarray) -> float:
    """Coefficient of determination of predicted vs observed mean-delta (higher = better)."""
    p = np.asarray(pred_delta, dtype=np.float64)
    o = np.asarray(obs_delta, dtype=np.float64)
    ss_res = np.sum((o - p) ** 2)
    ss_tot = np.sum((o - o.mean()) ** 2)
    return float(1.0 - ss_res / ss_tot) if ss_tot > 1e-12 else 0.0


def _retrieval_scores(pred_pop: np.ndarray, pred_delta: np.ndarray,
                      Q: np.ndarray, q_delta: np.ndarray, q_labels, pred_labels,
                      seed: int) -> dict[str, float]:
    """All four retrieval rules for one predicted candidate response vs the query."""
    out = {}
    out["mean_cosine"] = cosine(q_delta, pred_delta)
    out["r2"] = _r2(pred_delta, q_delta)
    out["dart_energy"] = score_energy(pred_pop, Q, max_cells=300, seed=seed)
    if q_labels is not None and pred_labels is not None:
        out["dart_coverage"] = score_coverage(pred_pop, Q, pred_labels, q_labels,
                                               aggregator="mean", max_cells=300, seed=seed)
    else:
        out["dart_coverage"] = out["dart_energy"]
    return out


def _run_task(task_name, queries, predictors, rt_acc, perq_rows, metric_rows,
              n_cells=200, synth="cells", loco=False):
    """Predict-then-rank over DRUG candidates.

    Each query carries: target (observed query population), control_mean and control_cells
    (query-context control, as a mean vector and as real cells, to anchor predictions),
    gt_drug, cand_drugs (real drug names incl. gt_drug), labels (query subpop labels),
    divergence, seed. For each candidate drug the predictor imagines a response population
    in the query context; the four retrieval rules rank the imagined responses against the
    observed query.

    ``synth`` selects how a predictor turns its predicted effect into a population.
    'cells' (default) applies the effect to the query context's real control cells;
    'gaussian' is the legacy mean + iid-noise synthesizer, which is unimodal by
    construction (see baselines.population_synthesis).

    ``loco`` holds the query's own contexts out of the nearest-neighbor predictor's donor
    set, so its signature must be transferred from a context that does not compose the
    query. Without it the predictor can retrieve a signature it memorized from the very
    cells that form the query, and the reported numbers are an in-sample ceiling.
    """
    for qi, qd in enumerate(queries):
        Q = qd["target"]; ctrlm = qd["control_mean"]; div = qd["divergence"]
        ctrl_cells = qd.get("control_cells")
        drugs = qd["cand_drugs"]; gt_drug = qd["gt_drug"]
        if gt_drug not in drugs:
            continue
        gt = drugs.index(gt_drug)
        q_delta = Q.mean(0) - np.asarray(ctrlm, dtype=np.float64)
        q_labels = qd.get("labels")
        seed = qd.get("seed", 1000 + qi)
        excl = qd.get("query_contexts", ()) if loco else ()
        for predictor in predictors:
            pname = predictor.name
            known = set(predictor.known_drugs())
            scores = {rl: {} for rl in RETRIEVALS}
            t0 = time.perf_counter()
            for d in drugs:
                if d not in known:
                    # predictor never saw this drug -> worst-case scores (honest)
                    for rl in RETRIEVALS:
                        scores[rl][d] = -1e6
                    continue
                kw = dict(control_mean=ctrlm, control_cells=ctrl_cells,
                          n_cells=n_cells, seed=seed, synth=synth)
                if pname == "nearest_neighbor" and excl:
                    kw["exclude_contexts"] = excl
                if pname == "ot_map":
                    # MANDATORY leakage guard, not gated on loco. The OT map transports toward
                    # this drug's treated cells; if the query's own contexts are in the donor set
                    # it transports toward the answer. A cross-line query blends two contexts, so
                    # both are excluded. Without query_contexts we cannot guarantee no leakage and
                    # must refuse rather than silently leak.
                    qc = qd.get("query_contexts")
                    if not qc:
                        raise ValueError("ot_map needs qd['query_contexts'] to exclude the query's "
                                         "own contexts; refusing to run it with possible leakage.")
                    kw["exclude_context"] = tuple(qc)
                pop = predictor.predict_population(d, **kw)
                pdelta = pop.mean(0) - np.asarray(ctrlm, dtype=np.float64)
                plab, qlab = _split_for_coverage(pop, Q, q_labels)
                rs = _retrieval_scores(pop, pdelta, Q, q_delta, qlab, plab, seed)
                for rl in RETRIEVALS:
                    scores[rl][d] = rs[rl]
            dt = time.perf_counter() - t0
            rt_acc.setdefault(pname, []).append(dt)
            ref_vals = np.array([scores[REF_RETRIEVAL][d] for d in drugs])
            for rl in RETRIEVALS:
                vals = np.array([scores[rl][d] for d in drugs])
                pm = per_query_metrics(vals, gt, ref_vals=ref_vals)
                metric_rows.append({
                    "task": task_name, "predictor": pname, "retrieval": rl,
                    "seed": seed, "divergence": div, **pm,
                })
            for d in drugs:
                perq_rows.append({
                    "task": task_name, "predictor": pname, "candidate": d,
                    "is_gt": int(d == gt_drug), "seed": seed, "divergence": div,
                    **{rl: float(scores[rl][d]) for rl in RETRIEVALS},
                })
        if (qi + 1) % 10 == 0 or qi == len(queries) - 1:
            log(f"[exp09] {task_name} {qi+1}/{len(queries)} queries done")


def _split_for_coverage(pred_pop, Q, q_labels):
    """Assign query + predicted cells to 2 subpops by nearest of the query's two mean modes."""
    if q_labels is None:
        return None, None
    lab = np.asarray(q_labels)
    uniq = np.unique(lab)
    if len(uniq) < 2:
        return None, None
    mu_a = Q[lab == uniq[0]].mean(0)
    mu_b = Q[lab == uniq[1]].mean(0)
    def assign(X):
        da = np.linalg.norm(X - mu_a, axis=1)
        db = np.linalg.norm(X - mu_b, axis=1)
        return np.where(da < db, 0, 1)
    return assign(pred_pop), assign(Q)


# ---------------------------------------------------------------------------
# Query builders (reuse the package tasks; expose predictor-friendly fields)
# ---------------------------------------------------------------------------


def _crossline_queries(data, n_seeds, n_drugs, alphas,
                       pairs=(("K562", "A549"), ("A549", "MCF7"), ("K562", "MCF7")),
                       n_total=200, n_distractors=30):
    """Cross-line heterogeneous queries whose candidates are REAL drugs.

    For a divergent drug d* shared by two cell lines, the query is d*'s response mixed across
    the two lines (heterogeneous). Candidate drugs = {d*} ∪ {other shared drugs}; the GT is
    d*. The predictor must imagine each candidate drug's response in the query's blended
    control — it has no access to the within-query line structure, which is exactly the point.
    """
    out = []
    for maj, minor in pairs:
        div = context_divergence_probe(data, maj, minor, min_cells=30, gate=0.9,
                                       rel_floor=0.5, seed=0, id_col="drug")
        task = ContextMixtureTask(data, maj, minor, min_cells=60)
        d_stars = task.divergent(div, n_drugs, n_total, id_col="drug")
        # candidate pool of real drugs shared across the two lines
        shared = [d for d in task.shared]
        for alpha in alphas:
            for d_star in d_stars:
                # candidate drugs: GT + up to n_distractors other shared drugs
                others = [d for d in shared if d != d_star]
                for s in range(n_seeds):
                    r = np.random.default_rng(7000 + s)
                    r.shuffle(others)
                    cand_drugs = [d_star] + others[:n_distractors]
                    q = task.build(d_star, alpha, n_total, n_distractors, 1000 + s)
                    nq = normalize_query(q, ground_truth=GT)
                    out.append({
                        "target": nq.Q, "control_mean": q["ctrl_T"],
                        "control_cells": _blend_control_cells(
                            data, maj, minor, alpha, n_total, 1000 + s),
                        "query_contexts": (maj, minor),
                        "cand_drugs": cand_drugs, "gt_drug": d_star,
                        "labels": nq.labels_Q, "divergence": query_divergence(nq),
                        "seed": 1000 + s, "setting": f"{maj}+{minor}", "alpha": alpha,
                    })
    return out


def _blend_control_cells(data, maj, minor, alpha, n_total, seed):
    """The query context's REAL control cells, mixed at the query's own alpha.

    This is what a predictor must be anchored on to emit a population that could carry any
    structure at all. The mean of these cells is (up to sampling) q['ctrl_T'].
    """
    rng = np.random.default_rng(seed)
    cr_maj, cr_min = data.control_rows(maj), data.control_rows(minor)
    n_maj = int(round(alpha * n_total))
    n_min = n_total - n_maj
    i_maj = rng.choice(cr_maj, n_maj, replace=len(cr_maj) < n_maj)
    i_min = rng.choice(cr_min, n_min, replace=len(cr_min) < n_min)
    return np.vstack([data.X[i_maj], data.X[i_min]]).astype(np.float32)


def run(n_seeds=8, n_drugs=10, alphas=(0.5, 0.7, 0.9), lines=("K562", "A549", "MCF7"),
        include_crossline=True, force_fallback=False, synth="cells", loco=False,
        nonadditive=False, epochs=100):
    section("EXP09 — predict-then-rank (predictor x retrieval)")
    data = load_sciplex3()
    log(data.summary())
    log(f"[exp09] population synthesis = {synth!r}; leave-one-context-out = {loco}")

    # --- fit predictors once on the full dataset ---
    pool = [AverageEffectPredictor(), NearestNeighborPredictor(),
            ScGenPredictor(force_fallback=force_fallback)]

    if nonadditive:
        # The falsification test for Gate 1. The three predictors above are ALL additive by
        # construction, so they can only ever demonstrate the algebra. These three are not, and
        # they decide the framework: if a predictor that genuinely induces differential response
        # still yields no distributional advantage, the two-gate account is wrong.
        #
        # They live behind a flag because they need scgen 2.1.1 / cpa-tools 0.8.1, which pin an
        # older scvi-tools and therefore a separate environment (see analysis/predictors/README).
        # Nothing else in this experiment changes: same queries, same libraries, same scorers.
        from baselines.nonadditive_predictors import (
            RealScGenPredictor, RealCPAPredictor, OTMapPredictor)
        pool += [RealScGenPredictor(n_epochs=epochs), RealCPAPredictor(n_epochs=epochs),
                 OTMapPredictor()]
        log(f"[exp09] NON-ADDITIVE predictors enabled (published scGen, published CPA, OT map)")

    predictors = []
    fit_rt = {}
    for P in pool:
        t0 = time.perf_counter()
        P.fit(data)
        fit_rt[P.name] = time.perf_counter() - t0
        predictors.append(P)
        log(f"[exp09] fitted {P.name}"
            + (f" (backend={getattr(P,'backend','')})" if hasattr(P, "backend") else "")
            + f" in {fit_rt[P.name]:.1f}s")
    scgen_backend = getattr([p for p in predictors if p.name == "scgen"][0], "backend", "unknown")

    perq_rows, metric_rows, rt_acc = [], [], {}

    section("EXP09 cross-line predict-then-rank (real-drug candidates)")
    qs = _crossline_queries(data, n_seeds, n_drugs, alphas)
    log(f"[exp09] built {len(qs)} cross-line queries")
    _run_task("crossline", qs, predictors, rt_acc, perq_rows, metric_rows,
              synth=synth, loco=loco)

    metrics = pd.DataFrame(metric_rows)
    perq = pd.DataFrame(perq_rows)
    write_csv(perq, results_path(OUT, "per_query_scores.csv"))

    # --- summary per (task, predictor, retrieval) ---
    summ = summarize(metrics, ["task", "predictor", "retrieval"], METRIC_COLS)
    summ = summ.rename(columns={"rank": "mean_rank"})
    write_csv(summ, results_path(OUT, "summary.csv"))

    # --- compact predictor x retrieval matrix (Hit@1 / MRR / nDCG averaged over tasks) ---
    mat = metrics.groupby(["predictor", "retrieval"]).agg(
        hit1=("hit@1", "mean"), hit5=("hit@5", "mean"),
        mrr=("mrr", "mean"), ndcg=("ndcg@10", "mean"), n=("hit@1", "size"),
    ).reset_index()
    write_csv(mat, results_path(OUT, "predictor_ranker_matrix.csv"))

    # --- EvalShift vs mean/R2 flip (predictor held fixed) ---
    flip = metrics[metrics.retrieval.isin(DART_RETRIEVALS)].groupby(
        ["task", "predictor", "retrieval"]).agg(
        top1_flip_rate=("top1_flip_vs_ref", "mean"),
        mean_topk_overlap=("topk_overlap_vs_ref", "mean"),
        mean_delta_rank=("delta_rank_vs_ref", "mean"),
        n_queries=("hit@1", "size"),
    ).reset_index()
    write_csv(flip, results_path(OUT, "flip_vs_mean.csv"))

    # --- divergence-stratified Hit@1 ---
    strat_rows = []
    for (pname, rl), sub in metrics.groupby(["predictor", "retrieval"]):
        st = stratify_by_divergence(sub, value_col="hit@1")
        st["predictor"] = pname; st["retrieval"] = rl
        strat_rows.append(st)
    write_csv(pd.concat(strat_rows, ignore_index=True),
              results_path(OUT, "divergence_stratified.csv"))

    # --- runtime ---
    rt_rows = []
    for p in predictors:
        calls = rt_acc.get(p.name, [1e-9])
        rt_rows.append({"predictor": p.name, "fit_seconds": fit_rt[p.name],
                        "per_query_ms": float(np.mean(calls) * 1e3), "n_queries": len(calls)})
    write_csv(pd.DataFrame(rt_rows), results_path(OUT, "runtime.csv"))

    # --- provenance ---
    write_csv(pd.DataFrame([{"predictor": "scgen", "backend": scgen_backend,
                             "synth": synth, "leave_one_context_out": bool(loco),
                             "note": "cpa_linear = in-repo linear-latent fallback; "
                                     "scgen = real scvi-tools VAE. synth='cells' applies the "
                                     "predicted effect to real control cells; 'gaussian' is "
                                     "the legacy unimodal synthesizer. loco=False means the "
                                     "nearest-neighbor donor set still contains the query's "
                                     "own contexts, i.e. an in-sample ceiling."}]),
              results_path(OUT, "provenance.csv"))

    # --- console headline ---
    section("EXP09 HEADLINE — Drug Hit@1 by (predictor x retrieval)")
    piv = metrics.groupby(["predictor", "retrieval"])["hit@1"].mean().unstack("retrieval")
    piv = piv.reindex(columns=RETRIEVALS)
    log(piv.round(3).to_string())
    log(f"\n[exp09] scgen backend = {scgen_backend}")
    log("[exp09] key question: within each predictor row, does dart_energy/coverage beat "
        "mean_cosine/r2?")
    for pname in piv.index:
        best_sig = max(piv.loc[pname, "mean_cosine"], piv.loc[pname, "r2"])
        best_dart = max(piv.loc[pname, "dart_energy"], piv.loc[pname, "dart_coverage"])
        log(f"  {pname:16s} best signature={best_sig:.3f}  best EvalShift={best_dart:.3f}  "
            f"Δ={best_dart - best_sig:+.3f}")
    return {"matrix": piv.to_dict(), "scgen_backend": scgen_backend}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-seeds", type=int, default=8)
    ap.add_argument("--n-drugs", type=int, default=10)
    ap.add_argument("--alphas", default="0.5,0.7,0.9")
    ap.add_argument("--lines", default="K562,A549,MCF7")
    ap.add_argument("--force-fallback", action="store_true",
                    help="skip scGen import probe, use CPA-linear fallback directly")
    ap.add_argument("--synth", choices=["cells", "gaussian"], default="cells",
                    help="how a predictor turns its predicted effect into a population; "
                         "'gaussian' is the legacy unimodal synthesizer, kept for comparison")
    ap.add_argument("--loco", action="store_true",
                    help="hold the query's own contexts out of the nearest-neighbor donor "
                         "set (genuine cross-context transfer); without it exp09 is an "
                         "in-sample ceiling")
    args = ap.parse_args()
    if os.environ.get("QUICK") == "1":
        args.n_seeds = 2
        args.lines = "K562,A549"
        log("== QUICK exp09 (reduced) ==")
    run(n_seeds=args.n_seeds, n_drugs=args.n_drugs,
        alphas=tuple(float(a) for a in args.alphas.split(",")),
        lines=tuple(args.lines.split(",")), force_fallback=args.force_fallback,
        synth=args.synth, loco=args.loco)


if __name__ == "__main__":
    main()
