#!/usr/bin/env python
"""Experiment 11 — Synthetic phase diagram: when is distributional retrieval necessary?

DART's central claim is a *divergence-gated* boundary: when a query population is internally
homogeneous, mean-signature retrieval is already optimal and DART's distributional scorers
buy nothing; as the population's two modes diverge, mean-signature retrieval degrades (the
mean washes out the minority mode) while distributional retrieval holds. This experiment maps
that boundary as a 2-D phase diagram over a fully controlled synthetic sweep, so the phase
transition is visible as a surface rather than argued from a handful of real datasets.

Two control axes (both use the repo's ``build_divergence_query``, which shifts the minority
subpopulation by ``lam * (mu_B - mu_A)``):
    lambda (divergence)  0 -> two subpops identical (homogeneous); >=1 -> orthogonal modes
    alpha  (mixture)     fraction of the majority mode (0.5 = balanced, 0.9 = majority-dominated)

At each (lambda, alpha) cell we build many seeded queries and score the ground-truth candidate
('covers-both', the only candidate that reproduces BOTH modes) against distractors under:
    mean_cosine     mean-delta cosine (the signature/CMap incumbent)
    global_energy   DART energy-distance retrieval (distributional)
    coverage_worst  DART worst-subpop coverage (the divergence-gated scorer)

The phase-diagram source is the per-cell Hit@1 (and MRR) for each scorer, plus the DART
advantage ``global_energy - mean_cosine`` whose sign flips across the boundary. No figure is
drawn here (per the phase constraint); the CSVs are the plot-ready source.

Outputs (results/exp11_synthetic_phase_diagram/):
    phase_diagram_source.csv    per (lambda, alpha, scorer) Hit@1, Hit@5, MRR, mean_rank
    dart_advantage_grid.csv     per (lambda, alpha) energy-vs-mean and coverage-vs-mean Δ Hit@1
    boundary_contour.csv        per alpha, the lambda* where DART advantage crosses +0.05
    divergence_calibration.csv  realized subpop cosine vs lambda (axis calibration)
    per_query_scores.csv        one row per (lambda, alpha, seed, candidate) x scorer

    python src/experiments/exp11_synthetic_phase_diagram.py --n-seeds 12 --grid 9
    QUICK=1 python src/experiments/exp11_synthetic_phase_diagram.py
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
from retrieval.tasks import ControlledMixtureTask, build_divergence_query
from retrieval.metrics import score_mean_cosine, score_energy, score_coverage
from retrieval.evaluation import rank_of
from utils.io import results_path, write_csv
from utils.logging import log, section

OUT = "exp11_synthetic_phase_diagram"
GT = "covers-both"
SCORERS = ["mean_cosine", "global_energy", "coverage_worst"]
ADV_THRESH = 0.05


def _score_candidates(q, subpop_cos, seed):
    """Score every candidate under the three scorers; return dict scorer->{name:score}."""
    target = q["target"]; tlab = q["target_labels"]; ctrl = q["pseudo_control"]
    cands = q["candidates"]
    names = list(cands)
    out = {s: {} for s in SCORERS}
    for name in names:
        P = cands[name]
        # subpop labels for the candidate: split by nearest of the target's two modes
        plab = _assign_modes(P, target, tlab)
        out["mean_cosine"][name] = score_mean_cosine(P, target, control_P=ctrl, control_Q=ctrl)
        out["global_energy"][name] = score_energy(P, target, max_cells=300, seed=seed)
        out["coverage_worst"][name] = score_coverage(P, target, plab, tlab,
                                                      aggregator="worst", max_cells=300, seed=seed)
    return out, names


def _assign_modes(P, target, tlab):
    """Assign candidate cells to the target's two modes by nearest centroid."""
    tlab = np.asarray(tlab)
    uniq = np.unique(tlab)
    if len(uniq) < 2:
        return np.zeros(len(P), int)
    mu0 = target[tlab == uniq[0]].mean(0)
    mu1 = target[tlab == uniq[1]].mean(0)
    d0 = np.linalg.norm(P - mu0, axis=1)
    d1 = np.linalg.norm(P - mu1, axis=1)
    return np.where(d0 < d1, 0, 1)


def run(n_seeds=12, grid=9, lines=("K562",), n_total=300, n_distractors=20):
    section("EXP11 — synthetic divergence x mixture phase diagram")
    data = load_sciplex3()
    log(data.summary())

    lambdas = np.round(np.linspace(0.0, 1.2, grid), 3)
    alphas = np.round(np.linspace(0.5, 0.9, max(3, grid // 2)), 3)
    log(f"[exp11] grid: {len(lambdas)} lambdas x {len(alphas)} alphas x {n_seeds} seeds "
        f"= {len(lambdas)*len(alphas)*n_seeds} queries per line, lines={lines}")

    perq_rows, cell_rows, calib_rows = [], [], []
    for line in lines:
        task = ControlledMixtureTask(data, cell_line=line, n_total=n_total)
        for lam in lambdas:
            cos_acc = []
            for alpha in alphas:
                # accumulate per-seed ranks of GT under each scorer
                gt_rank = {s: [] for s in SCORERS}
                for s in range(n_seeds):
                    seed = 5000 + s
                    q, subpop_cos = build_divergence_query(task, lam, alpha, n_total,
                                                           n_distractors, seed)
                    cos_acc.append(subpop_cos)
                    scores, names = _score_candidates(q, subpop_cos, seed)
                    gt = names.index(GT)
                    for sc in SCORERS:
                        vec = np.array([scores[sc][n] for n in names])
                        r = rank_of(vec, gt)
                        gt_rank[sc].append(r)
                        perq_rows.append({
                            "line": line, "lambda": lam, "alpha": alpha, "seed": seed,
                            "scorer": sc, "gt_rank": r, "subpop_cos": subpop_cos,
                        })
                for sc in SCORERS:
                    rr = np.array(gt_rank[sc], dtype=float)
                    cell_rows.append({
                        "line": line, "lambda": lam, "alpha": alpha, "scorer": sc,
                        "hit@1": float(np.mean(rr <= 1)), "hit@5": float(np.mean(rr <= 5)),
                        "mrr": float(np.mean(1.0 / rr)), "mean_rank": float(np.mean(rr)),
                        "n_seeds": n_seeds,
                    })
            calib_rows.append({"line": line, "lambda": lam,
                               "subpop_cos_mean": float(np.mean(cos_acc)),
                               "subpop_cos_std": float(np.std(cos_acc))})
            log(f"[exp11] {line} lambda={lam} done (subpop_cos≈{np.mean(cos_acc):.2f})")

    cells = pd.DataFrame(cell_rows)
    write_csv(pd.DataFrame(perq_rows), results_path(OUT, "per_query_scores.csv"))
    write_csv(cells, results_path(OUT, "phase_diagram_source.csv"))
    write_csv(pd.DataFrame(calib_rows), results_path(OUT, "divergence_calibration.csv"))

    # --- DART advantage grid (energy - mean, coverage - mean) per (lambda, alpha) ---
    piv = cells.pivot_table(index=["line", "lambda", "alpha"], columns="scorer",
                            values="hit@1").reset_index()
    piv["adv_energy_vs_mean"] = piv["global_energy"] - piv["mean_cosine"]
    piv["adv_coverage_vs_mean"] = piv["coverage_worst"] - piv["mean_cosine"]
    write_csv(piv, results_path(OUT, "dart_advantage_grid.csv"))

    # --- boundary contour: for each alpha, smallest lambda where adv_energy_vs_mean >= thresh ---
    bnd = []
    for (line, alpha), sub in piv.groupby(["line", "alpha"]):
        sub = sub.sort_values("lambda")
        crossed = sub[sub.adv_energy_vs_mean >= ADV_THRESH]
        lam_star = float(crossed["lambda"].iloc[0]) if len(crossed) else float("nan")
        bnd.append({"line": line, "alpha": alpha, "lambda_star": lam_star,
                    "advantage_thresh": ADV_THRESH,
                    "max_advantage": float(sub.adv_energy_vs_mean.max())})
    write_csv(pd.DataFrame(bnd), results_path(OUT, "boundary_contour.csv"))

    # --- console headline: advantage surface ---
    section("EXP11 HEADLINE — DART energy advantage over mean_cosine (Hit@1 Δ)")
    grid_view = piv.pivot_table(index="lambda", columns="alpha", values="adv_energy_vs_mean")
    log(grid_view.round(2).to_string())
    section("EXP11 — phase boundary (lambda* where energy advantage first >= +0.05)")
    log(pd.DataFrame(bnd).round(3).to_string(index=False))
    log("\n[exp11] reading: at low lambda (homogeneous) advantage≈0 (mean is fine); "
        "as lambda grows the advantage turns positive — the divergence-gated boundary.")
    return {"boundary": bnd}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-seeds", type=int, default=12)
    ap.add_argument("--grid", type=int, default=9)
    ap.add_argument("--lines", default="K562")
    args = ap.parse_args()
    if os.environ.get("QUICK") == "1":
        args.n_seeds = 4
        args.grid = 5
        log("== QUICK exp11 (reduced grid) ==")
    run(n_seeds=args.n_seeds, grid=args.grid, lines=tuple(args.lines.split(",")))


if __name__ == "__main__":
    main()
