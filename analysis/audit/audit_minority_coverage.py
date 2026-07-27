#!/usr/bin/env python

"""Audit: minority_state_coverage structural blind spot + cell-level alternative.

Step 1: Compare mean-based coverage (current exp12) with cell-level coverage
        on SciPlex3 controlled mixture queries (K562, HDAC vs JAK, alpha=0.7).
Step 2: Compare DART_energy-selected vs mean_cosine-selected drugs on both metrics.

Output: audit_minority_coverage.csv, audit_minority_coverage_summary.json
"""

# --- repo-root path resolution (added for public release; replaces hardcoded /data/boom/DART) ---
from pathlib import Path as _P
REPO = _P(__file__).resolve().parents[2]
SRC = str(REPO / "src")
RESULTS_AUDIT = str(REPO / "results" / "upgrade")
DATA_PROC = str(REPO / "data" / "processed")
DATA_ANNO = str(REPO / "data" / "annotation")
# ------------------------------------------------------------------------------------------------
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
# repo root = parents[2] when this file lives at <repo>/analysis/<category>/
sys.path.insert(0, SRC)

import numpy as np
import pandas as pd
from scipy.spatial.distance import cdist
from scipy.stats import spearmanr

from data.load_sciplex3 import load_sciplex3
from retrieval.tasks import ControlledMixtureTask
from retrieval.metrics import score_mean_cosine, score_energy


# ── Metrics ──────────────────────────────────────────────────────────────────

def mean_based_coverage(P, query_X, query_states, minority_state):
    """Current exp12 implementation: cos(candidate_mean, minority_mean), mapped to [0,1]."""
    mino_cells = query_X[query_states == minority_state]
    if len(mino_cells) == 0 or len(P) == 0:
        return 0.5
    mino_mean = mino_cells.mean(0)
    p_mean = P.mean(0)
    cos = float(np.dot(p_mean, mino_mean) /
                (np.linalg.norm(p_mean) * np.linalg.norm(mino_mean) + 1e-12))
    return (cos + 1) / 2


def cell_level_nn_dists(P, query_X, query_states, minority_state):
    """Compute nearest-neighbor distances from each minority query cell to P.
    Returns array of shape (n_minority,)."""
    mino_cells = query_X[query_states == minority_state]
    if len(mino_cells) == 0 or len(P) == 0:
        return np.array([])
    dists = cdist(mino_cells, P, metric='euclidean')
    return dists.min(axis=1)


def cell_level_coverage(nn_dists, threshold):
    """Fraction of minority cells whose NN distance is within threshold."""
    if len(nn_dists) == 0:
        return 0.0
    return float((nn_dists <= threshold).mean())


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    t0 = time.time()
    print("Loading SciPlex3...")
    ds = load_sciplex3()
    print(f"  {ds.X.shape[0]} cells x {ds.X.shape[1]} genes, loaded in {time.time()-t0:.1f}s")

    N_SEEDS = 20
    ALPHA = 0.7
    OUT_DIR = Path(__file__).resolve().parent

    task = ControlledMixtureTask(ds, cell_line="K562", class_a="HDAC",
                                 class_b="JAK", seed=42)
    ctrl = task.pseudo_control

    all_rows = []
    rank_corrs = []
    top1_disagrees = 0
    total_queries = 0

    # Step 2 counters (across ALL 20 queries, strict wins only)
    dart_wins_cell_total = 0
    dart_wins_mean_total = 0

    for seed in range(N_SEEDS):
        print(f"\n--- Seed {seed}/{N_SEEDS} ---")
        q = task.build(alpha=ALPHA, n_distractors=40, seed=seed)
        target = q["target"]
        target_labels = q["target_labels"]
        candidates = q["candidates"]
        minority_state = 1  # class_b = JAK

        cand_names = list(candidates.keys())
        n_minority = int((target_labels == minority_state).sum())
        print(f"  {len(cand_names)} candidates, {n_minority} minority cells")

        # ── Step 1: compute both coverage metrics ──
        mean_covs = {}
        nn_dists_all = {}

        for name in cand_names:
            P = candidates[name]
            mean_covs[name] = mean_based_coverage(P, target, target_labels, minority_state)
            nn_dists_all[name] = cell_level_nn_dists(P, target, target_labels, minority_state)

        # Global threshold: 50th percentile of ALL nn-distances pooled across candidates
        pooled = np.concatenate(list(nn_dists_all.values()))
        threshold = float(np.median(pooled))

        cell_covs = {}
        for name in cand_names:
            cell_covs[name] = cell_level_coverage(nn_dists_all[name], threshold)

        # Rank correlation
        mc_arr = np.array([mean_covs[n] for n in cand_names])
        cc_arr = np.array([cell_covs[n] for n in cand_names])
        rho, _ = spearmanr(mc_arr, cc_arr)
        if np.isnan(rho):
            rho = 0.0
        rank_corrs.append(rho)

        # Top-1 comparison (coverage metrics only)
        top1_mean = cand_names[int(np.argmax(mc_arr))]
        top1_cell = cand_names[int(np.argmax(cc_arr))]
        disagree = (top1_mean != top1_cell)
        if disagree:
            top1_disagrees += 1
        total_queries += 1

        print(f"  Spearman rho={rho:.4f}, top-1 {'DISAGREE' if disagree else 'agree'}")
        for kc in ["covers-both", "majority-only", "minority-only"]:
            if kc in mean_covs:
                print(f"    {kc}: mean_cov={mean_covs[kc]:.4f}, cell_cov={cell_covs[kc]:.4f}")

        # ── Step 2: DART_energy vs mean_cosine drug selection ──
        mc_limit = min(300, min(len(candidates[n]) for n in cand_names), len(target))
        energy_scores = {}
        cosine_scores = {}

        for name in cand_names:
            P = candidates[name]
            energy_scores[name] = score_energy(P, target, max_cells=mc_limit, seed=seed)
            cosine_scores[name] = score_mean_cosine(P, target, control_P=ctrl, control_Q=ctrl)

        dart_top1 = max(energy_scores, key=energy_scores.get)
        mean_sel_top1 = max(cosine_scores, key=cosine_scores.get)

        # Strict-win comparison across ALL queries
        if dart_top1 != mean_sel_top1:
            if cell_covs[dart_top1] > cell_covs[mean_sel_top1]:
                dart_wins_cell_total += 1
            if mean_covs[dart_top1] > mean_covs[mean_sel_top1]:
                dart_wins_mean_total += 1
            print(f"  EvalShift selects: {dart_top1}, mean_cosine selects: {mean_sel_top1}")
            print(f"    EvalShift-sel  cell_cov={cell_covs[dart_top1]:.4f}  mean_cov={mean_covs[dart_top1]:.4f}")
            print(f"    Mean-sel  cell_cov={cell_covs[mean_sel_top1]:.4f}  mean_cov={mean_covs[mean_sel_top1]:.4f}")
        else:
            print(f"  EvalShift and mean_cosine agree: {dart_top1}")
        # (ties: same drug, coverage identical, neither strict win)

        # Per-candidate rows for CSV
        for name in cand_names:
            ctype = "key" if name in ("covers-both", "majority-only", "minority-only") else "distractor"
            all_rows.append({
                "seed": seed,
                "candidate": name,
                "candidate_type": ctype,
                "mean_based_coverage": round(mean_covs[name], 6),
                "cell_level_coverage": round(cell_covs[name], 6),
                "energy_score": round(energy_scores[name], 6),
                "cosine_score": round(cosine_scores[name], 6),
                "nn_threshold": round(threshold, 6),
                "n_minority_cells": n_minority,
            })

    # ── Summary ──────────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    mean_rho = float(np.mean(rank_corrs))
    frac_disagree = top1_disagrees / total_queries
    dart_cell_frac = dart_wins_cell_total / total_queries
    dart_mean_frac = dart_wins_mean_total / total_queries

    print(f"Step 1:")
    print(f"  Mean Spearman rho (mean-based vs cell-level): {mean_rho:.4f}")
    print(f"  Per-seed rhos: {[round(r,3) for r in rank_corrs]}")
    print(f"  Fraction top-1 disagree: {frac_disagree:.4f} ({top1_disagrees}/{total_queries})")
    print(f"\nStep 2 (over all {total_queries} queries):")
    print(f"  EvalShift wins cell-level: {dart_wins_cell_total}/{total_queries} = {dart_cell_frac:.4f}")
    print(f"  EvalShift wins mean-based: {dart_wins_mean_total}/{total_queries} = {dart_mean_frac:.4f}")

    blind_spot = (mean_rho < 0.7) or (frac_disagree > 0.3)
    print(f"\nConfirmed blind spot: {blind_spot}")
    print(f"  (rho < 0.7? {mean_rho < 0.7}  |  disagree > 30%? {frac_disagree > 0.3})")

    # Save CSV
    df = pd.DataFrame(all_rows)
    csv_path = OUT_DIR / "audit_minority_coverage.csv"
    df.to_csv(csv_path, index=False)
    print(f"\nSaved {len(df)} rows to {csv_path}")

    # Save summary JSON
    summary = {
        "step1_rank_correlation_mean_vs_cell": round(mean_rho, 6),
        "step1_fraction_rankings_disagree": round(frac_disagree, 6),
        "step1_per_seed_rho": [round(r, 4) for r in rank_corrs],
        "step2_dart_wins_cell_level": round(dart_cell_frac, 6),
        "step2_dart_wins_mean_based": round(dart_mean_frac, 6),
        "step2_n_total_queries": total_queries,
        "step2_n_dart_wins_cell": dart_wins_cell_total,
        "step2_n_dart_wins_mean": dart_wins_mean_total,
        "confirmed_blind_spot": blind_spot,
    }
    json_path = OUT_DIR / "audit_minority_coverage_summary.json"
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Saved summary to {json_path}")
    print(f"\nTotal runtime: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    main()
