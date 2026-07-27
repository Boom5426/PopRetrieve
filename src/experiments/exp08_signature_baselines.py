#!/usr/bin/env python
"""Experiment 8 — Signature-retrieval baselines vs EvalShift (Phase-2, plan external-baselines).

Head-to-head of the incumbent *mean-signature* retrieval paradigm against EvalShift's
distributional retrieval, on the SAME queries and candidate libraries the core experiments
use. Signature/latent baselines:

    mean_cosine   — cosine of mean-delta signatures (the classic 'mean-out' incumbent; also
                    one of EvalShift's own scorers, kept here as the canonical signature method)
    cmap_cosine   — CMap-style full-signature connectivity (cosine)
    cmap_wtcs     — CMap WTCS-lite signed rank-enrichment of the query up/down tags
    pca_mean      — cosine in an unsupervised PCA latent
    pca_dist      — energy distance in the PCA latent (a cheap distributional retriever)

EvalShift distributional:

    global_energy  — -energy_distance (K=1 full-distribution)          [reference ranker]
    coverage_mean  — -mean_k energy over matched subpops
    coverage_worst — -max_k  energy over matched subpops

Tasks: controlled (SciPlex3 two-MOA mixture) + cross-line (two real cell types, same drug)
+ Frangieh (natural immune contexts). Ground truth = 'covers-both'. Per query we compute
Drug Hit@1/5, MRR, nDCG@10, median rank; and — versus EvalShift-energy as the reference — top-1
flip, top-k overlap, delta-rank. Divergence-stratified by the query's own subpop-response
cosine. Runtime captured per method.

Outputs (results/exp08_signature_baselines/):
    summary.csv                per (task, setting, method) retrieval metrics
    per_query_scores.csv       exchange format: one row per (query, candidate) x method
    flip_vs_dart.csv           per (task, setting, method) flip/overlap/Δrank vs EvalShift-energy
    divergence_stratified.csv  per (task, divergence stratum, method) Hit@1 / Hit@5
    runtime.csv                per method wall-clock (total + per-query)

    python src/experiments/exp08_signature_baselines.py --n-seeds 10 --n-drugs 12
    QUICK=1 python src/experiments/exp08_signature_baselines.py
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
from retrieval.tasks import (
    ControlledMixtureTask, ContextMixtureTask, context_divergence_probe,
)
from retrieval.target_metrics import stratify_by_divergence, divergence_bucket
from utils.io import results_path, write_csv
from utils.logging import log, section

from experiments.baseline_common import (
    dart_scores, signature_scores, per_query_metrics, query_divergence, summarize,
)
from baselines.base import normalize_query
from baselines.cmap_signature import CMapSignatureRetrieval
from baselines.pca_latent_retrieval import PCALatentRetrieval

OUT = "exp08_signature_baselines"
GT = "covers-both"
REF = "global_energy"                      # EvalShift reference ranker for flip/overlap/Δrank

DART_METHODS = ["mean_cosine", "global_energy", "coverage_mean", "coverage_worst"]
SIG_RANKERS = [CMapSignatureRetrieval("cosine"), CMapSignatureRetrieval("wtcs"),
               PCALatentRetrieval(mode="mean"), PCALatentRetrieval(mode="dist")]
SIG_METHODS = [r.name for r in SIG_RANKERS]
ALL_METHODS = DART_METHODS + SIG_METHODS
METRIC_COLS = ["hit@1", "hit@5", "mrr", "ndcg@10", "rank"]


def _score_query(q: dict, style: str, seed: int) -> tuple[dict, dict]:
    """Return (method->{name:score}, method->seconds) for one raw task dict."""
    scores, runtime = {}, {}
    t0 = time.perf_counter()
    ds = dart_scores(q, style, seed=seed)
    dt = time.perf_counter() - t0
    for m in DART_METHODS:
        scores[m] = ds[m]
    # attribute EvalShift wall-clock evenly across its scorers (single fused pass)
    for m in DART_METHODS:
        runtime[m] = dt / len(DART_METHODS)
    nq = normalize_query(q, ground_truth=GT)
    for r in SIG_RANKERS:
        t1 = time.perf_counter()
        scores[r.name] = r.score(nq)
        runtime[r.name] = time.perf_counter() - t1
    return scores, nq, runtime


def _emit(task_name, setting, alpha, seed, names, gt, scores, divergence,
          perq_rows, metric_rows, rt_acc):
    ref_vals = np.array([scores[REF][n] for n in names])
    for m in ALL_METHODS:
        vals = np.array([scores[m][n] for n in names])
        pm = per_query_metrics(vals, gt, ref_vals=ref_vals)
        metric_rows.append({
            "task": task_name, "setting": setting, "alpha": alpha, "seed": seed,
            "method": m, "divergence": divergence, **pm,
        })
    for n in names:
        perq_rows.append({
            "task": task_name, "setting": setting, "alpha": alpha, "seed": seed,
            "candidate": n, "divergence": divergence,
            **{m: float(scores[m][n]) for m in ALL_METHODS},
        })


def run_controlled(n_seeds, alphas, rt_acc, perq_rows, metric_rows,
                   lines=("K562", "A549", "MCF7"), n_total=400, n_distractors=40):
    data = load_sciplex3()
    log(data.summary())
    for line in lines:
        task = ControlledMixtureTask(data, cell_line=line, n_total=n_total)
        for alpha in alphas:
            for s in range(n_seeds):
                q = task.build(alpha, n_distractors=n_distractors, seed=1000 + s)
                scores, nq, rt = _score_query(q, "controlled", seed=1000 + s)
                names = nq.names
                gt = names.index(GT)
                div = query_divergence(nq)
                _emit("controlled", line, alpha, 1000 + s, names, gt, scores, div,
                      perq_rows, metric_rows, rt_acc)
                for m, sec in rt.items():
                    rt_acc.setdefault(m, []).append(sec)
        log(f"[exp08] controlled {line}: done ({len(alphas)}x{n_seeds} queries)")


def run_crossline(n_seeds, n_drugs, alphas, rt_acc, perq_rows, metric_rows,
                  pairs=(("K562", "A549"), ("A549", "MCF7"), ("K562", "MCF7")),
                  n_total=200, n_distractors=40):
    data = load_sciplex3()
    for maj, minor in pairs:
        pair = f"{maj}+{minor}"
        div = context_divergence_probe(data, maj, minor, min_cells=30, gate=0.9,
                                       rel_floor=0.5, seed=0, id_col="drug")
        task = ContextMixtureTask(data, maj, minor, min_cells=60)
        d_stars = task.divergent(div, n_drugs, n_total, id_col="drug")
        for alpha in alphas:
            for d_star in d_stars:
                for s in range(n_seeds):
                    q = task.build(d_star, alpha, n_total, n_distractors, 1000 + s)
                    scores, nq, rt = _score_query(q, "labeled", seed=1000 + s)
                    names = nq.names
                    gt = names.index(GT)
                    dv = query_divergence(nq)
                    _emit("crossline", pair, alpha, 1000 + s, names, gt, scores, dv,
                          perq_rows, metric_rows, rt_acc)
                    for m, sec in rt.items():
                        rt_acc.setdefault(m, []).append(sec)
        log(f"[exp08] crossline {pair}: {len(d_stars)} d* x {len(alphas)}a x {n_seeds}s done")


def run_frangieh(n_seeds, n_kos, alphas, rt_acc, perq_rows, metric_rows,
                 n_total=200, n_distractors=40):
    try:
        data = load_frangieh()
    except Exception as exc:                                   # pragma: no cover
        log(f"[exp08] frangieh unavailable ({exc}); skipping")
        return
    log(data.summary())
    maj, minor = "Control", "IFNγ"
    div = context_divergence_probe(data, maj, minor, min_cells=40, gate=0.9,
                                   rel_floor=0.5, seed=0, id_col="ko")
    task = ContextMixtureTask(data, maj, minor, min_cells=60)
    kos = task.divergent(div, n_kos, n_total, id_col="ko")
    for alpha in alphas:
        for ko in kos:
            for s in range(n_seeds):
                q = task.build(ko, alpha, n_total, n_distractors, 2000 + s)
                scores, nq, rt = _score_query(q, "labeled", seed=2000 + s)
                names = nq.names
                gt = names.index(GT)
                dv = query_divergence(nq)
                _emit("frangieh", f"{maj}+{minor}", alpha, 2000 + s, names, gt, scores, dv,
                      perq_rows, metric_rows, rt_acc)
                for m, sec in rt.items():
                    rt_acc.setdefault(m, []).append(sec)
    log(f"[exp08] frangieh {maj}+{minor}: {len(kos)} KOs done")


def run(n_seeds=10, n_drugs=12, n_kos=6, alphas=(0.5, 0.7, 0.9),
        include_frangieh=True):
    perq_rows, metric_rows, rt_acc = [], [], {}

    section("EXP08a controlled (SciPlex3 two-MOA mixture)")
    run_controlled(n_seeds, alphas, rt_acc, perq_rows, metric_rows)

    section("EXP08b cross-line (two real cell types, same drug)")
    run_crossline(n_seeds, n_drugs, alphas, rt_acc, perq_rows, metric_rows)

    if include_frangieh:
        section("EXP08c Frangieh (natural immune contexts)")
        run_frangieh(max(2, n_seeds // 2), n_kos, alphas, rt_acc, perq_rows, metric_rows)

    metrics = pd.DataFrame(metric_rows)
    perq = pd.DataFrame(perq_rows)
    write_csv(perq, results_path(OUT, "per_query_scores.csv"))

    # --- summary: retrieval metrics per (task, setting, method) ---
    summ = summarize(metrics, ["task", "setting", "method"], METRIC_COLS)
    summ = summ.rename(columns={"rank": "median_rank_proxy"})
    write_csv(summ, results_path(OUT, "summary.csv"))

    # overall per (task, method)
    overall = summarize(metrics, ["task", "method"], METRIC_COLS)
    write_csv(overall, results_path(OUT, "summary_by_task.csv"))

    # --- flip vs EvalShift-energy ---
    flip = metrics[metrics.method != REF].groupby(["task", "setting", "method"]).agg(
        top1_flip_rate=("top1_flip_vs_ref", "mean"),
        mean_topk_overlap=("topk_overlap_vs_ref", "mean"),
        mean_delta_rank=("delta_rank_vs_ref", "mean"),
        n_queries=("hit@1", "size"),
    ).reset_index()
    write_csv(flip, results_path(OUT, "flip_vs_dart.csv"))

    # --- divergence-stratified Hit@1 / Hit@5 ---
    strat_rows = []
    for m in ALL_METHODS:
        sub = metrics[metrics.method == m]
        for metric in ("hit@1", "hit@5"):
            st = stratify_by_divergence(sub, value_col=metric, group_cols=["task"])
            st["method"] = m; st["metric"] = metric
            strat_rows.append(st)
    strat = pd.concat(strat_rows, ignore_index=True)
    write_csv(strat, results_path(OUT, "divergence_stratified.csv"))

    # --- runtime ---
    rt_rows = [{"method": m, "total_seconds": float(np.sum(v)),
                "per_query_ms": float(np.mean(v) * 1e3), "n_calls": len(v)}
               for m, v in rt_acc.items()]
    write_csv(pd.DataFrame(rt_rows).sort_values("per_query_ms"),
              results_path(OUT, "runtime.csv"))

    # --- console headline ---
    section("EXP08 HEADLINE — Drug Hit@1 by method (avg over all queries)")
    h1 = metrics.groupby("method")["hit@1"].mean().reindex(ALL_METHODS)
    for m in ALL_METHODS:
        tag = "  <-- EvalShift" if m in DART_METHODS else ""
        log(f"  {m:16s} Hit@1={h1[m]:.3f}{tag}")
    log("\n[exp08] wrote summary.csv / per_query_scores.csv / flip_vs_dart.csv / "
        "divergence_stratified.csv / runtime.csv")
    return {"headline_hit1": h1.to_dict(), "n_queries": int(metrics.seed.nunique() and len(perq))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-seeds", type=int, default=10)
    ap.add_argument("--n-drugs", type=int, default=12)
    ap.add_argument("--n-kos", type=int, default=6)
    ap.add_argument("--alphas", default="0.5,0.7,0.9")
    ap.add_argument("--no-frangieh", action="store_true")
    args = ap.parse_args()
    if os.environ.get("QUICK") == "1":
        args.n_seeds, args.n_drugs, args.n_kos = 2, 3, 3
        log("== QUICK exp08 (reduced) ==")
    run(n_seeds=args.n_seeds, n_drugs=args.n_drugs, n_kos=args.n_kos,
        alphas=tuple(float(a) for a in args.alphas.split(",")),
        include_frangieh=not args.no_frangieh)


if __name__ == "__main__":
    main()
