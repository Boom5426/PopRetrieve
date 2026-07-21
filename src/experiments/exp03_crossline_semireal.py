#!/usr/bin/env python
"""Experiment 3 — Cross-cell-line semi-real positive anchor (plan §8-Exp3, FINDINGS §9).

The two divergent response modes are now two REAL cell types (e.g. K562 vs A549)
responding to the SAME drug — a realistic model of a heterogeneous sample, with ZERO
new data. First a model-free divergence probe (does the same drug push two lines in
near-orthogonal directions, clearing the 0.9 gate, above the within-line reliability
floor?), then the mixture retrieval over many divergent d* drugs, swept over alpha.
Retains per-query score vectors for exp07.

    python src/experiments/exp03_crossline_semireal.py --n-seeds 10 --n-drugs 15
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from experiments.common import FINDINGS, verdict            # noqa: E402
from data.load_sciplex3 import load_sciplex3                 # noqa: E402
from retrieval.tasks import ContextMixtureTask, context_divergence_probe  # noqa: E402
from retrieval.rankers import score_labeled, SCORERS         # noqa: E402
from retrieval.evaluation import hit_at_1                    # noqa: E402
from utils.io import results_path, write_csv                 # noqa: E402
from utils.logging import log, section                      # noqa: E402

OUT = "exp03_crossline_semireal"
PAIRS = [("K562", "A549"), ("A549", "MCF7"), ("K562", "MCF7")]


def run(n_seeds=10, n_drugs=15, alphas=(0.5, 0.6, 0.7, 0.8, 0.9), n_total=200,
        n_distractors=40, processed=None):
    data = load_sciplex3(processed)
    log(data.summary())
    div_rows, mix_rows, perq_rows = [], [], []
    headline = {}
    for maj, minor in PAIRS:
        pair = f"{maj}+{minor}"
        div = context_divergence_probe(data, maj, minor, min_cells=30, gate=0.9,
                                       rel_floor=0.5, seed=0, id_col="drug")
        div = div.copy()
        div["pair"] = pair
        div_rows.append(div)
        rel = div[div["reliable"]]
        log(f"[exp03] {pair}: reliable drugs={len(rel)} "
            f"cross_cos median={rel['cross_cos'].median():.2f} "
            f"clear-gate={int((rel['cross_cos'] < 0.9).sum())}/{len(rel)}")

        task = ContextMixtureTask(data, maj, minor, min_cells=60)
        d_stars = task.divergent(div, n_drugs, n_total, id_col="drug")
        log(f"         d* drugs ({len(d_stars)}): {', '.join(d_stars[:6])}...")

        per_scorer_hits = {s: [] for s in SCORERS}
        for alpha in alphas:
            hit = {s: [] for s in SCORERS}
            for d_star in d_stars:
                for s in range(n_seeds):
                    q = task.build(d_star, alpha, n_total, n_distractors, 1000 + s)
                    sc = score_labeled(q)
                    names = list(q["cands"])
                    gt = names.index("covers-both")
                    for scorer in SCORERS:
                        vals = np.array([sc[scorer][n] for n in names])
                        hit[scorer].append(hit_at_1(vals, gt))
                    for n in names:
                        perq_rows.append({
                            "dataset": "crossline", "pair": pair, "d_star": d_star,
                            "alpha": alpha, "seed": 1000 + s, "candidate": n,
                            **{scorer: float(sc[scorer][n]) for scorer in SCORERS},
                        })
            row = {"pair": pair, "alpha": alpha}
            for scorer in SCORERS:
                row[f"{scorer}_hit@1"] = float(np.mean(hit[scorer]))
                per_scorer_hits[scorer].extend(hit[scorer])
            mix_rows.append(row)
            log(f"  alpha={alpha:.2f} | " +
                "  ".join(f"{s}={row[f'{s}_hit@1']:.2f}" for s in SCORERS))
        headline[pair] = {s: float(np.mean(per_scorer_hits[s])) for s in SCORERS}

    write_csv(pd.concat(div_rows, ignore_index=True), results_path(OUT, "crossline_divergence.csv"))
    write_csv(pd.DataFrame(mix_rows), results_path(OUT, "crossline_retrieval.csv"))
    write_csv(pd.DataFrame(perq_rows), results_path(OUT, "per_query_scores.csv"))

    section("EXP03 HEADLINE (avg Hit@1 of covers-both over alpha) vs FINDINGS §9")
    checks = []
    for maj, minor in PAIRS:
        pair = f"{maj}+{minor}"
        log(f"  {pair}: " + "  ".join(f"{s}={headline[pair][s]:.2f}" for s in SCORERS))
        for s in SCORERS:
            if pair in FINDINGS["exp03_crossline"]:
                checks.append(verdict(f"{pair}/{s}", headline[pair][s],
                                      FINDINGS["exp03_crossline"][pair][s]))
    return {"headline": headline, "checks": checks}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-seeds", type=int, default=10)
    ap.add_argument("--n-drugs", type=int, default=15)
    ap.add_argument("--alphas", default="0.5,0.6,0.7,0.8,0.9")
    ap.add_argument("--n-total", type=int, default=200)
    ap.add_argument("--n-distractors", type=int, default=40)
    ap.add_argument("--processed", default=None)
    args = ap.parse_args()
    run(n_seeds=args.n_seeds, n_drugs=args.n_drugs,
        alphas=tuple(float(a) for a in args.alphas.split(",")),
        n_total=args.n_total, n_distractors=args.n_distractors, processed=args.processed)


if __name__ == "__main__":
    main()
