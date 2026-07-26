#!/usr/bin/env python

"""Diagnostic: delta-vs-raw energy distance asymmetry on SciPlex3 K562.

Step 1 of the delta-vs-raw audit:
  (a) 10 drugs, pairwise energy distance on raw vs delta cells
  (b) Spearman rank correlation between the two distance matrices
  (c) Hit@1 on controlled mixture task with raw vs delta energy scoring
"""

# --- repo-root path resolution (added for public release; replaces hardcoded /data/boom/JUDGE) ---
from pathlib import Path as _P
REPO = _P(__file__).resolve().parents[2]
SRC = str(REPO / "src")
RESULTS_AUDIT = str(REPO / "results" / "upgrade")
DATA_PROC = str(REPO / "data" / "processed")
DATA_ANNO = str(REPO / "data" / "annotation")
# ------------------------------------------------------------------------------------------------
import sys, os
sys.path.insert(0, SRC)
os.chdir(str(REPO))

import numpy as np
import pandas as pd
import torch
from scipy.stats import spearmanr
from itertools import combinations

from data.load_sciplex3 import load_sciplex3
from retrieval.metrics import energy_distance, _tensor, _subsample
from retrieval.tasks import ControlledMixtureTask

CELL_LINE = "K562"
N_DRUGS = 10
MAX_CELLS = 500   # match the default in score_energy
SEED = 42
OUT_DIR = RESULTS_AUDIT
os.makedirs(OUT_DIR, exist_ok=True)

# ---- helpers ----

def energy_dist_raw(P, Q, max_cells=MAX_CELLS, seed=0):
    """Energy distance on raw cells (current implementation)."""
    P = _subsample(P, max_cells, seed)
    Q = _subsample(Q, max_cells, seed + 1)
    with torch.no_grad():
        return float(energy_distance(_tensor(P), _tensor(Q)))

def energy_dist_delta(P, Q, ctrl_mean, max_cells=MAX_CELLS, seed=0):
    """Energy distance on delta cells (each cell minus control mean)."""
    P = _subsample(P, max_cells, seed)
    Q = _subsample(Q, max_cells, seed + 1)
    P_delta = P - ctrl_mean
    Q_delta = Q - ctrl_mean
    with torch.no_grad():
        return float(energy_distance(_tensor(P_delta), _tensor(Q_delta)))

# ---- load data ----
print("Loading SciPlex3...")
data = load_sciplex3()
obs = data.obs
X = data.X

# Filter K562 treated cells
mask = (obs["cell_line"] == CELL_LINE) & (~data.is_control)
drugs_all = data.pert[mask]
unique_drugs, counts = np.unique(drugs_all, return_counts=True)

# Pick top 10 drugs by cell count (>100 cells each)
eligible = [(d, c) for d, c in zip(unique_drugs, counts) if c >= 100]
eligible.sort(key=lambda x: -x[1])
selected = [d for d, _ in eligible[:N_DRUGS]]
print(f"Selected {len(selected)} drugs: {selected}")
print(f"Cell counts: {[c for _, c in eligible[:N_DRUGS]]}")

# Control mean for K562
ctrl_rows = data.control_rows(CELL_LINE)
ctrl_mean = X[ctrl_rows].mean(0).astype(np.float32)
print(f"K562 control cells: {len(ctrl_rows)}")

# ---- (a) Pairwise distances ----
print("\n=== Pairwise Energy Distances ===")
drug_cells = {}
for d in selected:
    rows = np.flatnonzero(mask & (data.pert == d))
    drug_cells[d] = X[rows].astype(np.float32)
    print(f"  {d}: {len(rows)} cells")

pairs = list(combinations(range(N_DRUGS), 2))
raw_dists = np.zeros((N_DRUGS, N_DRUGS))
delta_dists = np.zeros((N_DRUGS, N_DRUGS))

for i, j in pairs:
    d_i, d_j = selected[i], selected[j]
    P, Q = drug_cells[d_i], drug_cells[d_j]
    
    raw_d = energy_dist_raw(P, Q, seed=SEED)
    delta_d = energy_dist_delta(P, Q, ctrl_mean, seed=SEED)
    
    raw_dists[i, j] = raw_d
    raw_dists[j, i] = raw_d
    delta_dists[i, j] = delta_d
    delta_dists[j, i] = delta_d

# ---- (b) Rank correlation ----
raw_vec = raw_dists[np.triu_indices(N_DRUGS, k=1)]
delta_vec = delta_dists[np.triu_indices(N_DRUGS, k=1)]
rho, pval = spearmanr(raw_vec, delta_vec)
print(f"\nSpearman rank correlation (raw vs delta): rho = {rho:.6f}, p = {pval:.2e}")
print(f"Pearson correlation: {np.corrcoef(raw_vec, delta_vec)[0,1]:.6f}")
print(f"Raw energy distances: mean={raw_vec.mean():.4f}, std={raw_vec.std():.4f}")
print(f"Delta energy distances: mean={delta_vec.mean():.4f}, std={delta_vec.std():.4f}")
print(f"Ratio raw/delta (mean): {raw_vec.mean() / delta_vec.mean():.4f}")

# Save pairwise results
pair_records = []
for i, j in pairs:
    pair_records.append({
        "drug_i": selected[i], "drug_j": selected[j],
        "energy_raw": raw_dists[i, j], "energy_delta": delta_dists[i, j],
        "ratio": raw_dists[i, j] / max(delta_dists[i, j], 1e-12)
    })
df_pairs = pd.DataFrame(pair_records)
df_pairs.to_csv(f"{OUT_DIR}/step1_pairwise_distances.csv", index=False)
print(f"\nPairwise distances saved to {OUT_DIR}/step1_pairwise_distances.csv")

# ---- (c) Controlled mixture Hit@1 ----
print("\n=== Controlled Mixture Task: Raw vs Delta Energy ===")

def score_raw_energy(P, Q, max_cells=MAX_CELLS, seed=0, **_):
    return -energy_dist_raw(P, Q, max_cells=max_cells, seed=seed)

def score_delta_energy(P, Q, ctrl, max_cells=MAX_CELLS, seed=0, **_):
    return -energy_dist_delta(P, Q, ctrl, max_cells=max_cells, seed=seed)

hit1_raw_list = []
hit1_delta_list = []
alphas_test = [0.5, 0.7, 0.9]
n_seeds = 20

for alpha in alphas_test:
    raw_hits = 0
    delta_hits = 0
    for s in range(n_seeds):
        task = ControlledMixtureTask(data, cell_line=CELL_LINE, seed=s)
        q = task.build(alpha=alpha, n_distractors=40, seed=s)
        
        target = q["target"]
        ctrl = q["pseudo_control"]
        cands = q["candidates"]
        gt = q["ground_truth"]  # "covers-both"
        
        # Score all candidates with raw energy
        scores_raw = {}
        scores_delta = {}
        for name, C in cands.items():
            scores_raw[name] = score_raw_energy(target, C, seed=s)
            scores_delta[name] = score_delta_energy(
                target - ctrl, C - ctrl, ctrl=np.zeros_like(ctrl),
                seed=s)
        
        # Hit@1 = is top-ranked candidate the ground truth?
        best_raw = max(scores_raw, key=scores_raw.get)
        best_delta = max(scores_delta, key=scores_delta.get)
        
        if best_raw == gt:
            raw_hits += 1
        if best_delta == gt:
            delta_hits += 1
    
    h1_raw = raw_hits / n_seeds
    h1_delta = delta_hits / n_seeds
    hit1_raw_list.append(h1_raw)
    hit1_delta_list.append(h1_delta)
    print(f"  alpha={alpha:.1f}: Hit@1 raw={h1_raw:.3f}, delta={h1_delta:.3f}")

mean_raw = np.mean(hit1_raw_list)
mean_delta = np.mean(hit1_delta_list)
print(f"\n  Mean Hit@1: raw={mean_raw:.4f}, delta={mean_delta:.4f}")

# ---- Summary ----
print("\n" + "="*60)
print("STEP 1 SUMMARY")
print("="*60)
print(f"Spearman rho (raw vs delta distance): {rho:.6f}")
print(f"p-value: {pval:.2e}")
print(f"Mean raw energy dist: {raw_vec.mean():.4f}")
print(f"Mean delta energy dist: {delta_vec.mean():.4f}")
print(f"Ratio (raw/delta): {raw_vec.mean()/delta_vec.mean():.2f}x")
print(f"Hit@1 raw energy (mean across alphas): {mean_raw:.4f}")
print(f"Hit@1 delta energy (mean across alphas): {mean_delta:.4f}")
if rho < 0.95:
    print("CONFIRMED: raw and delta energy rankings differ substantially")
    print("  -> The asymmetry is a real source of signal distortion")
else:
    print("Rankings are similar; asymmetry effect is minor")

# Save summary
summary = {
    "spearman_rho": rho, "spearman_p": pval,
    "mean_raw_dist": raw_vec.mean(), "mean_delta_dist": delta_vec.mean(),
    "ratio_raw_over_delta": raw_vec.mean() / delta_vec.mean(),
    "hit1_raw_alpha05": hit1_raw_list[0], "hit1_raw_alpha07": hit1_raw_list[1],
    "hit1_raw_alpha09": hit1_raw_list[2],
    "hit1_delta_alpha05": hit1_delta_list[0], "hit1_delta_alpha07": hit1_delta_list[1],
    "hit1_delta_alpha09": hit1_delta_list[2],
    "hit1_raw_mean": mean_raw, "hit1_delta_mean": mean_delta,
}
pd.DataFrame([summary]).to_csv(f"{OUT_DIR}/step1_summary.csv", index=False)
print(f"\nSummary saved to {OUT_DIR}/step1_summary.csv")

