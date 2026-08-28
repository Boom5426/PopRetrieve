#!/usr/bin/env python
"""Experiment 11 — HIR-Bench: Heterogeneous Inverse Retrieval Benchmark.

Drives the full benchmark grid over (alpha, conflict_level, cells_per_subpop,
noise_sigma, library_size, information_condition).  Produces 7 CSV files
covering three layers: method-independent difficulty, method performance,
and theoretical boundary validation.

Usage:
    python src/experiments/exp11_hir_benchmark.py [--quick] [--n-seeds N] [--grid G]
"""
from __future__ import annotations

import argparse
import itertools
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from benchmarks.heterogeneous_retrieval_benchmark import generate_hir_cell
from benchmarks.oracle_utility import (
    welfare_mean, welfare_worst, welfare_cvar,
    oracle_population_optimal, oracle_mean_optimal, oracle_flip_risk,
    oracle_utility_gap, decision_regret, WELFARE_FUNCTIONS,
)
from benchmarks.preference_conflict import (
    topk_disagreement, weighted_kendall_conflict, standard_kendall_conflict,
    response_cosine,
)
from benchmarks.theory_boundary import compute_boundary
from benchmarks.predictability import extract_features

from retrieval.metrics import (
    score_mean_cosine, score_mean_l2, score_energy,
    score_mmd_rbf, score_sliced_wasserstein, score_coverage,
)
from retrieval.evaluation import retrieval_metrics
from utils.io import results_path, write_csv
from utils.logging import log, section

OUT = "exp11_hir_benchmark"


# ── method registry ──────────────────────────────────────────────────────────

def _assign_labels(X, query_X, query_labels):
    """Assign subpop labels to candidate cells by nearest query centroid."""
    unique_labels = np.unique(query_labels)
    centroids = np.array([query_X[query_labels == l].mean(0) for l in unique_labels])
    # Cosine distances
    X_norm = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-12)
    C_norm = centroids / (np.linalg.norm(centroids, axis=1, keepdims=True) + 1e-12)
    sims = X_norm @ C_norm.T
    assigned = unique_labels[sims.argmax(axis=1)]
    return assigned


def _score_method(method_name, P, Q, query_labels, ctrl=None, seed=0):
    """Score candidate P against query Q using the named method.  Higher = better."""
    mc = min(300, len(P), len(Q))
    if method_name == "mean_cosine":
        return score_mean_cosine(P, Q, control_P=ctrl, control_Q=ctrl)
    elif method_name == "mean_l2":
        return score_mean_l2(P, Q)
    elif method_name == "cmap_signature_match":
        return score_mean_cosine(P, Q, control_P=ctrl, control_Q=ctrl)
    elif method_name == "cmap_signature_reverse":
        return -score_mean_cosine(P, Q, control_P=ctrl, control_Q=ctrl)
    elif method_name == "DART_energy":
        return score_energy(P, Q, max_cells=mc, seed=seed)
    elif method_name == "DART_mmd":
        return score_mmd_rbf(P, Q, max_cells=mc, seed=seed)
    elif method_name == "DART_sliced_wasserstein":
        return score_sliced_wasserstein(P, Q, max_cells=mc, seed=seed)
    elif method_name == "DART_coverage_mean":
        labels_P = _assign_labels(P, Q, query_labels)
        return score_coverage(P, Q, labels_P, query_labels, aggregator="mean",
                               max_cells=mc, seed=seed)
    elif method_name == "DART_coverage_worst":
        labels_P = _assign_labels(P, Q, query_labels)
        return score_coverage(P, Q, labels_P, query_labels, aggregator="worst",
                               max_cells=mc, seed=seed)
    else:
        raise ValueError(f"Unknown method: {method_name}")


METHOD_FAMILY = {
    "mean_cosine": "mean_signature",
    "mean_l2": "mean_signature",
    "cmap_signature_match": "cmap_signature",
    "cmap_signature_reverse": "cmap_signature",
    "DART_energy": "DART_distributional",
    "DART_mmd": "DART_distributional",
    "DART_sliced_wasserstein": "DART_distributional",
    "DART_coverage_mean": "DART_coverage",
    "DART_coverage_worst": "DART_coverage",
}

ALL_METHODS = list(METHOD_FAMILY.keys())


# ── grid definition ──────────────────────────────────────────────────────────

QUICK_GRID = {
    "alpha": [0.5, 0.85],
    "conflict_level": [0.0, 0.5, 1.0],
    "cells_per_subpop": [15, 60],
    "noise_sigma": [0.5],
    "library_size": [20, 100],
    "info_cond": ["observed", "predicted_mean"],
    "n_subpops": [2],
    "dim": [50],
}

FULL_GRID = {
    "alpha": [0.50, 0.70, 0.85, 0.95],
    "conflict_level": np.linspace(0, 1, 7).tolist(),
    "cells_per_subpop": [15, 60],
    "noise_sigma": [0.3, 0.8],
    "library_size": [20, 100],
    "info_cond": ["observed", "predicted_mean", "predicted_structure"],
    "n_subpops": [2],
    "dim": [50],
}


def _make_grid(grid_spec, n_seeds):
    """Generate all (params, seed) tuples."""
    keys = sorted(grid_spec.keys())
    combos = list(itertools.product(*(grid_spec[k] for k in keys)))
    cells = []
    for combo in combos:
        params = dict(zip(keys, combo))
        for s in range(n_seeds):
            cells.append((params, s))
    return cells


# ── main loop ────────────────────────────────────────────────────────────────

def run(quick: bool = False, n_seeds: int = None, grid_size: int = None,
        skip_method_perf: bool = False):
    grid_spec = QUICK_GRID if quick else FULL_GRID
    if n_seeds is None:
        n_seeds = 3 if quick else 20
    if grid_size is not None:
        # Override conflict_level granularity
        grid_spec = dict(grid_spec)
        grid_spec["conflict_level"] = np.linspace(0, 1, grid_size).tolist()

    cells = _make_grid(grid_spec, n_seeds)
    n_total = len(cells)
    section(f"HIR-BENCH ({'QUICK' if quick else 'FULL'}) — {n_total} cells")

    welfare_types = ["mean", "worst"]

    rows_independent = []   # method-independent difficulty
    rows_performance = []   # per-method results
    rows_boundary = []      # theoretical boundary
    rows_dominance = []     # method dominance
    rows_sanity = []        # sanity checks
    rows_uncertainty = []   # uncertainty bands

    t0 = time.time()
    for ci, (params, seed) in enumerate(cells):
        if ci > 0 and ci % max(1, n_total // 10) == 0:
            elapsed = time.time() - t0
            rate = ci / elapsed
            log(f"  [{ci}/{n_total}] {rate:.1f} cells/s, ETA {(n_total - ci) / rate:.0f}s")

        grid_id = f"a{params['alpha']:.2f}_c{params['conflict_level']:.2f}_" \
                  f"n{params['cells_per_subpop']}_s{params['noise_sigma']}_" \
                  f"L{params['library_size']}_I{params['info_cond']}"

        cell = generate_hir_cell(
            n_subpops=params["n_subpops"],
            dim=params["dim"],
            library_size=params["library_size"],
            majority_fraction=params["alpha"],
            conflict_level=params["conflict_level"],
            cells_per_subpop=params["cells_per_subpop"],
            noise_sigma=params["noise_sigma"],
            information_condition=params["info_cond"],
            seed=seed,
        )

        # ── method-independent layer ──
        td = topk_disagreement(cell)
        wkc = weighted_kendall_conflict(cell)
        skc = standard_kendall_conflict(cell)
        rc = response_cosine(cell)
        boundary = compute_boundary(cell)

        # Genuinely observable features: computed from the candidate populations and the
        # query only, never from the utility matrix. These are what the predictability claim
        # actually requires; the topk/kendall/response_cosine features below are functions of
        # cell.utility_matrix, i.e. of the same oracle that defines the label.
        obs_feats = extract_features(cell)

        for wt in welfare_types:
            pop_opt, pop_val = oracle_population_optimal(cell, welfare=wt)
            mean_opt, mean_val = oracle_mean_optimal(cell)
            flip = oracle_flip_risk(cell, welfare=wt)
            ugap = oracle_utility_gap(cell, welfare=wt)
            alpha_star = boundary["alpha_star"] if boundary and not boundary.get("no_conflict") else float("nan")
            bm = params["alpha"] - alpha_star if not np.isnan(alpha_star) else float("nan")

            row_ind = {
                "grid_id": grid_id, "seed": seed,
                "n_subpops": params["n_subpops"], "dim": params["dim"],
                "library_size": params["library_size"],
                "cells_per_subpop": params["cells_per_subpop"],
                "noise_sigma": params["noise_sigma"],
                "alpha": params["alpha"], "conflict_level": params["conflict_level"],
                "information_condition": params["info_cond"],
                # oracle-derived (functions of cell.utility_matrix, like the label)
                "topk_disagreement": td, "weighted_kendall_conflict": wkc,
                "standard_kendall_conflict": skc, "response_cosine": rc,
                # observable at query time (functions of the populations only)
                **obs_feats,
                "welfare_type": wt,
                "oracle_population_optimal_drug": pop_opt,
                "oracle_mean_optimal_drug": mean_opt,
                "oracle_flip_risk": flip,
                "oracle_utility_gap": ugap,
                "theoretical_alpha_star": alpha_star,
                "theoretical_boundary_margin": bm,
            }
            rows_independent.append(row_ind)

            # ── method performance layer ──
            # This loop is the benchmark's entire cost: 9 methods x up to 100 candidates x
            # an O(n^2 d) population distance, per grid cell. On the FULL grid (13,440
            # instances) it does not finish in a reasonable time, which is why the FULL
            # predictability number was previously produced by an out-of-tree "lean runner"
            # that skipped it, and why the artifact committed under results/ was a QUICK
            # 144-instance run reporting AUC 0.5 while the manuscript quoted 0.640.
            #
            # The method-INDEPENDENT layer above (oracle labels + conflict features +
            # observable features) is all the predictability layer needs. skip_method_perf
            # makes that runnable in-tree on the FULL grid, so the number in the paper and
            # the CSV in results/ come from the same committed script.
            if skip_method_perf:
                continue
            ctrl = cell.query_X.mean(axis=0)  # pseudo-control for CMap

            for method in ALL_METHODS:
                scores = []
                for d_id in cell.drug_ids:
                    P = cell.candidate_populations[d_id]
                    s = _score_method(method, P, cell.query_X, cell.query_labels,
                                       ctrl=ctrl, seed=seed)
                    scores.append(s)
                scores = np.array(scores)
                top1_idx = int(np.argmax(scores))
                selected_drug = cell.drug_ids[top1_idx]
                hit1 = int(selected_drug == pop_opt)

                # Hit@5
                top5_idx = np.argsort(-scores)[:5]
                hit5 = int(pop_opt in [cell.drug_ids[j] for j in top5_idx])

                # MRR
                pop_opt_idx = cell.drug_ids.index(pop_opt)
                rank = int(np.where(np.argsort(-scores) == pop_opt_idx)[0][0]) + 1
                mrr = 1.0 / rank

                # nDCG@10
                top10_idx = np.argsort(-scores)[:10]
                dcg = sum(1.0 / np.log2(pos + 2) for pos, j in enumerate(top10_idx)
                          if cell.drug_ids[j] == pop_opt)
                ndcg = dcg  # ideal DCG = 1/log2(2) = 1.0 for single relevant

                # Regret
                regret = decision_regret(cell, selected_drug, welfare=wt)

                row_perf = {
                    "grid_id": grid_id, "seed": seed,
                    "method": method, "method_family": METHOD_FAMILY[method],
                    "welfare_type": wt,
                    "information_condition": params["info_cond"],
                    "alpha": params["alpha"], "conflict_level": params["conflict_level"],
                    "cells_per_subpop": params["cells_per_subpop"],
                    "noise_sigma": params["noise_sigma"],
                    "library_size": params["library_size"],
                    "selected_top1_drug": selected_drug,
                    "oracle_population_optimal_drug": pop_opt,
                    "hit_at_1": hit1, "hit_at_5": hit5,
                    "mrr": mrr, "ndcg": ndcg,
                    "decision_regret": regret,
                    "rank": rank,
                }
                rows_performance.append(row_perf)

        # ── theoretical boundary layer ──
        if boundary and not boundary.get("no_conflict", False):
            rows_boundary.append({
                "grid_id": grid_id, "seed": seed,
                "A": boundary["A"], "B": boundary["B"],
                "alpha_star": boundary["alpha_star"],
                "d_M": boundary["d_M"], "d_C": boundary["d_C"],
                "actual_alpha": params["alpha"],
                "observed_flip": oracle_flip_risk(cell, welfare="worst"),
                "information_condition": params["info_cond"],
            })

    elapsed = time.time() - t0
    log(f"  Grid complete: {n_total} cells in {elapsed:.1f}s ({n_total / elapsed:.1f} cells/s)")

    # ── sanity checks ──
    df_ind = pd.DataFrame(rows_independent)
    df_perf = pd.DataFrame(rows_performance)
    df_bound = pd.DataFrame(rows_boundary)

    # Sanity 1: no-conflict → flip_risk ≤ 0.05
    noconf = df_ind[df_ind.conflict_level == 0.0]
    s1_rate = noconf.oracle_flip_risk.mean() if len(noconf) > 0 else 0
    rows_sanity.append({"check": "no_conflict_flip_rate", "value": s1_rate,
                         "threshold": 0.05, "pass": int(s1_rate <= 0.05)})

    # Sanity 2: boundary error
    if len(df_bound) > 0:
        # Empirical: at what alpha does flip first appear?
        err = abs(df_bound.alpha_star - df_bound.actual_alpha).median()
        rows_sanity.append({"check": "median_boundary_margin", "value": err,
                             "threshold": 1.0, "pass": 1})

    # Sanity 3: predicted_mean → PopRetrieve ≈ mean (Δhit@1 ≤ 0.05).
    # Needs the method-performance layer; it is absent when that loop is skipped.
    if not skip_method_perf:
        pm = df_perf[df_perf.information_condition == "predicted_mean"]
        if len(pm) > 0:
            mean_hit = pm[pm.method == "mean_cosine"].hit_at_1.mean()
            energy_hit = pm[pm.method == "DART_energy"].hit_at_1.mean()
            delta = abs(energy_hit - mean_hit)
            rows_sanity.append({"check": "predicted_mean_dart_eq_mean", "value": delta,
                                "threshold": 0.10, "pass": int(delta <= 0.10)})

    # ── method dominance ──
    for wt in (welfare_types if not skip_method_perf else ()):
        for info in df_perf.information_condition.unique():
            sub = df_perf[(df_perf.welfare_type == wt) & (df_perf.information_condition == info)]
            if len(sub) == 0:
                continue
            agg = sub.groupby("method").agg(
                hit_at_1=("hit_at_1", "mean"),
                mrr=("mrr", "mean"),
                ndcg=("ndcg", "mean"),
                regret=("decision_regret", "mean"),
            ).reset_index()
            for metric in ["hit_at_1", "mrr", "ndcg"]:
                best = agg.loc[agg[metric].idxmax()]
                rows_dominance.append({
                    "welfare_type": wt, "information_condition": info,
                    "metric": metric,
                    "best_method": best["method"], "best_value": best[metric],
                })
            # regret: lower is better
            best_r = agg.loc[agg["regret"].idxmin()]
            rows_dominance.append({
                "welfare_type": wt, "information_condition": info,
                "metric": "decision_regret",
                "best_method": best_r["method"], "best_value": best_r["regret"],
            })

    # ── uncertainty bands (bootstrap over seeds) ──
    for wt in (welfare_types if not skip_method_perf else ()):
        for method in ALL_METHODS:
            for info in df_perf.information_condition.unique():
                sub = df_perf[(df_perf.welfare_type == wt) &
                              (df_perf.method == method) &
                              (df_perf.information_condition == info)]
                if len(sub) < 3:
                    continue
                hit_vals = sub.hit_at_1.values
                rows_uncertainty.append({
                    "welfare_type": wt, "method": method, "information_condition": info,
                    "hit_at_1_mean": hit_vals.mean(),
                    "hit_at_1_std": hit_vals.std(),
                    "hit_at_1_ci_lo": np.percentile(hit_vals, 2.5),
                    "hit_at_1_ci_hi": np.percentile(hit_vals, 97.5),
                    "n_cells": len(sub),
                })

    # ── write CSVs ──
    write_csv(df_ind, results_path(OUT, "phase_grid_method_independent.csv"))
    if skip_method_perf:
        # Do NOT overwrite the method-performance tables with empty ones: a downstream
        # consumer reading a zero-row CSV would silently produce nothing, or worse, an
        # apparently valid summary over no data. Leave the existing artifacts in place and
        # say so.
        log("  [skip_method_perf] method-performance / dominance / uncertainty tables NOT "
            "written; existing artifacts left untouched.")
    else:
        write_csv(df_perf, results_path(OUT, "phase_grid_method_performance.csv"))
        write_csv(pd.DataFrame(rows_dominance), results_path(OUT, "method_dominance.csv"))
        write_csv(pd.DataFrame(rows_uncertainty), results_path(OUT, "uncertainty_band.csv"))
    if len(df_bound) > 0:
        write_csv(df_bound, results_path(OUT, "theoretical_boundary.csv"))
    write_csv(pd.DataFrame(rows_sanity), results_path(OUT, "sanity_checks.csv"))

    section("SANITY CHECKS")
    for sc in rows_sanity:
        log(f"  {'PASS' if sc['pass'] else 'FAIL'}: {sc['check']} = {sc['value']:.4f} "
            f"(threshold {sc['threshold']})")

    section("METHOD DOMINANCE")
    for md in rows_dominance:
        log(f"  [{md['welfare_type']}|{md['information_condition']}] "
            f"{md['metric']}: {md['best_method']} = {md['best_value']:.4f}")

    # ── predictability layer ──
    # Run BOTH feature sets. The paper's claim ("failure is predictable from observable
    # features") is only supported by the OBSERVABLE row. The ORACLE row is a circular upper
    # bound: its features and its label are both functions of cell.utility_matrix. Reporting
    # only the oracle row would commit, inside this paper, the exact error the paper audits.
    #
    # This layer must not be swallowed. It used to sit under a bare `except Exception` that
    # logged one line and shipped every other CSV, so a silent failure looked like success.
    from benchmarks.predictability import (
        ORACLE_FEATURES, OBSERVABLE_FEATURES, predictability_auc,
    )
    section("PREDICTABILITY")
    pred_rows = []
    for fs_name, fs in (("observable", OBSERVABLE_FEATURES), ("oracle_derived", ORACLE_FEATURES)):
        r = predictability_auc(df_ind, df_perf, feature_cols=fs)
        note = ("what a retrieval method can see at query time; this is the feature set the "
                "predictability claim requires"
                if fs_name == "observable" else
                "CIRCULAR upper bound: these features and the label are both functions of "
                "cell.utility_matrix")
        log(f"  [{fs_name}] pooled AUC = {r['auc']:.4f}  "
            f"per-fold mean = {r['auc_fold_mean']:.4f} "
            f"[{r['auc_fold_lo']:.3f}, {r['auc_fold_hi']:.3f}] over {r['n_folds']} folds")
        log(f"             majority-class baseline = {r['majority_baseline']:.4f}; "
            f"effective independent units = {r.get('n_effective_units', float('nan'))} "
            f"(rows = {r['n_positive'] + r['n_negative']})")
        log(f"             {note}")
        for feat, imp in r["feature_importances"].items():
            log(f"               {feat}: {imp:+.4f}")
        pred_rows.append({
            "target": "oracle_flip_risk", "feature_set": fs_name,
            "auc": r["auc"], "auc_fold_mean": r["auc_fold_mean"],
            "auc_fold_lo": r["auc_fold_lo"], "auc_fold_hi": r["auc_fold_hi"],
            "n_folds": r["n_folds"], "majority_baseline": r["majority_baseline"],
            "n_effective_units": r.get("n_effective_units"),
            "n_positive": r["n_positive"], "n_negative": r["n_negative"],
            "grouping": "+".join(r["group_cols"]), "note": note,
            **{f"importance_{k}": v for k, v in r["feature_importances"].items()},
        })
    write_csv(pd.DataFrame(pred_rows), results_path(OUT, "phase_grid_predictability.csv"))

    return df_ind, df_perf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true",
                    help="Use QUICK grid (small, fast)")
    ap.add_argument("--n-seeds", type=int, default=None)
    ap.add_argument("--skip-method-perf", action="store_true",
                    help="skip the per-method retrieval-scoring loop (the benchmark's whole "
                         "cost). The method-independent layer and the predictability layer "
                         "still run, which is what the FULL-grid predictability number "
                         "needs; the method-performance CSVs are left untouched.")
    ap.add_argument("--grid", type=int, default=None,
                    help="Number of conflict_level points")
    args = ap.parse_args()

    quick = args.quick or os.environ.get("QUICK") == "1"
    run(quick=quick, n_seeds=args.n_seeds, grid_size=args.grid,
        skip_method_perf=args.skip_method_perf)


if __name__ == "__main__":
    main()
