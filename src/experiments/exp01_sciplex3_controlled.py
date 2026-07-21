#!/usr/bin/env python
"""Experiment 1 — SciPlex3 controlled retrieval (plan §8-Exp1, reproduces FINDINGS §3).

Build a heterogeneous query as an alpha/(1-alpha) mixture of two orthogonal MOA
response modes (HDAC vs JAK) with KNOWN subpopulation labels; ground truth = the
covers-both drug. Rank a held-out candidate library by four scorers and report Hit@1
of covers-both, swept over alpha, per cell line. Retains the full per-query candidate
score vectors for exp07 (ranking flip).

    python src/experiments/exp01_sciplex3_controlled.py --n-seeds 20
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # put src/ on sys.path

import numpy as np
import pandas as pd

from experiments.common import FINDINGS, verdict          # noqa: E402
from data.load_sciplex3 import load_sciplex3               # noqa: E402
from retrieval.tasks import ControlledMixtureTask          # noqa: E402
from retrieval.rankers import score_controlled, SCORERS    # noqa: E402
from retrieval.evaluation import hit_at_1, rank_of         # noqa: E402
from utils.io import results_path, write_csv               # noqa: E402
from utils.logging import log, section                     # noqa: E402

OUT = "exp01_sciplex3_controlled"


def run(n_seeds=20, alphas=(0.5, 0.6, 0.7, 0.8, 0.9), n_total=400, n_distractors=40,
        lines=("K562", "A549", "MCF7"), processed=None):
    data = load_sciplex3(processed)
    log(data.summary())
    summary_rows, perq_rows = [], []
    headline = {}
    for line in lines:
        task = ControlledMixtureTask(data, cell_line=line, n_total=n_total)
        log(f"[exp01] {line}: HDAC={len(task.rows_a)} JAK={len(task.rows_b)} "
            f"distractors={len(task.distractor_rows)}")
        per_scorer_hits = {s: [] for s in SCORERS}
        for alpha in alphas:
            hit = {s: [] for s in SCORERS}
            rnk = {s: [] for s in SCORERS}
            for s in range(n_seeds):
                q = task.build(alpha, n_distractors=n_distractors, seed=1000 + s)
                sc = score_controlled(q)
                names = list(q["candidates"])
                gt = names.index("covers-both")
                for scorer in SCORERS:
                    vals = np.array([sc[scorer][n] for n in names])
                    hit[scorer].append(hit_at_1(vals, gt))
                    rnk[scorer].append(rank_of(vals, gt))
                for n in names:
                    perq_rows.append({
                        "cell_line": line, "alpha": alpha, "seed": 1000 + s,
                        "candidate": n,
                        **{scorer: float(sc[scorer][n]) for scorer in SCORERS},
                    })
            row = {"cell_line": line, "alpha": alpha}
            for scorer in SCORERS:
                row[f"{scorer}_hit@1"] = float(np.mean(hit[scorer]))
                row[f"{scorer}_rank_med"] = float(np.median(rnk[scorer]))
                per_scorer_hits[scorer].extend(hit[scorer])
            summary_rows.append(row)
            log(f"  alpha={alpha:.2f} | " + "  ".join(
                f"{s}={row[f'{s}_hit@1']:.2f}" for s in SCORERS))
        headline[line] = {s: float(np.mean(per_scorer_hits[s])) for s in SCORERS}

    summary = pd.DataFrame(summary_rows)
    perq = pd.DataFrame(perq_rows)
    write_csv(summary, results_path(OUT, "metrics_summary.csv"))
    write_csv(perq, results_path(OUT, "per_query_scores.csv"))

    section("EXP01 HEADLINE (avg Hit@1 of covers-both over alpha) vs FINDINGS §3")
    checks = []
    for line in lines:
        log(f"  {line}: " + "  ".join(f"{s}={headline[line][s]:.2f}" for s in SCORERS))
        for s in SCORERS:
            if line in FINDINGS["exp01_controlled"]:
                checks.append(verdict(f"{line}/{s}", headline[line][s],
                                      FINDINGS["exp01_controlled"][line][s]))
    return {"headline": headline, "checks": checks}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-seeds", type=int, default=20)
    ap.add_argument("--alphas", default="0.5,0.6,0.7,0.8,0.9")
    ap.add_argument("--n-total", type=int, default=400)
    ap.add_argument("--n-distractors", type=int, default=40)
    ap.add_argument("--lines", default="K562,A549,MCF7")
    ap.add_argument("--processed", default=None)
    args = ap.parse_args()
    run(n_seeds=args.n_seeds, alphas=tuple(float(a) for a in args.alphas.split(",")),
        n_total=args.n_total, n_distractors=args.n_distractors,
        lines=tuple(args.lines.split(",")), processed=args.processed)


if __name__ == "__main__":
    main()
