#!/usr/bin/env python

"""End-to-end fix validation: cell-level coverage replaces mean-based coverage in exp12.

Runs exp12 setting A (leave-drug-out) on A549 with:
  - Original mean-based minority_state_coverage
  - Fixed cell-level minority_state_coverage (NN-based)
  - Both evaluated for DART_energy-selected vs mean_cosine-selected drugs

Output: fix_validation.csv with per-query comparison
"""

# --- repo-root path resolution (added for public release; replaces hardcoded /data/boom/JUDGE) ---
from pathlib import Path as _P
REPO = _P(__file__).resolve().parents[2]
SRC = str(REPO / "src")
RESULTS_AUDIT = str(REPO / "results" / "upgrade")
DATA_PROC = str(REPO / "data" / "processed")
DATA_ANNO = str(REPO / "data" / "annotation")
# ------------------------------------------------------------------------------------------------
import sys, os, time
import numpy as np
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(SRC)))

from data.load_sciplex3 import load_sciplex3
from retrieval.metrics import score_energy, score_mean_cosine
from sklearn.cluster import KMeans
from scipy.spatial.distance import cdist

print("Loading SciPlex3...")
ds = load_sciplex3()
print(f"  cells={ds.X.shape[0]}, genes={ds.X.shape[1]}")

# ── helpers ──
def kmeans_states(X, k=2, seed=0):
    k = min(k, max(1, len(X) - 1))
    if k < 2:
        return np.zeros(len(X), dtype=int)
    km = KMeans(n_clusters=k, n_init=3, random_state=seed, max_iter=100).fit(X)
    return km.labels_

def mean_based_coverage(P, query_X, query_states, minority_state):
    """Original exp12 metric: cos(cand_mean, minority_mean)."""
    mino_mean = query_X[query_states == minority_state].mean(0)
    p_mean = P.mean(0)
    cos = float(np.dot(p_mean, mino_mean) / (np.linalg.norm(p_mean) * np.linalg.norm(mino_mean) + 1e-12))
    return (cos + 1) / 2

def cell_level_coverage(P, query_X, query_states, minority_state):
    """Fixed metric: fraction of minority cells with NN in P within median distance."""
    mino_cells = query_X[query_states == minority_state]
    if len(mino_cells) < 2 or len(P) < 2:
        return 0.5
    # Compute distances from minority cells to all P cells
    D = cdist(mino_cells, P, metric='euclidean')
    nn_dists = D.min(axis=1)
    # Threshold: median of ALL query cells to P distances
    all_D = cdist(query_X, P, metric='euclidean')
    threshold = np.median(all_D.min(axis=1))
    if threshold < 1e-12:
        return 1.0
    return float(np.mean(nn_dists <= threshold))

# ── load drug annotation for MoA evaluation ──
ann_path = str(_P(DATA_ANNO) / "drug_annotation_master.csv")
ann = pd.read_csv(ann_path)
drug2moa = dict(zip(ann.drug_name, ann.moa_class))

# ── run exp12-style leave-drug-out ──
ctx = "A549"
all_drugs = sorted(set(np.asarray(ds.obs["perturbation"])[(ds.obs["cell_line"] == ctx) & (~ds.obs["is_control"].astype(bool))].tolist()))
ctrl_rows = np.flatnonzero((ds.obs["cell_line"] == ctx).to_numpy() & ds.obs["is_control"].astype(bool).to_numpy())
ctrl_mean = ds.X[ctrl_rows].mean(0).astype(np.float64)

n_drugs = 20
n_seeds = 3
max_cells = 150
rows = []

print(f"Running leave-drug-out: {ctx}, {n_drugs} drugs, {n_seeds} seeds")
t0 = time.time()

for seed in range(n_seeds):
    rng = np.random.default_rng(seed)
    held = rng.choice(all_drugs, min(n_drugs, len(all_drugs)), replace=False)
    
    for hi, hd in enumerate(held):
        # Query = held-out drug's cells
        qrows = np.flatnonzero(
            (ds.obs["cell_line"] == ctx).to_numpy() & 
            (ds.obs["perturbation"] == hd).to_numpy() &
            (~ds.obs["is_control"].astype(bool).to_numpy())
        )
        if len(qrows) < 20:
            continue
        if len(qrows) > 200:
            qrows = rng.choice(qrows, 200, replace=False)
        qX = ds.X[qrows].astype(np.float32)
        qs = kmeans_states(qX, k=2, seed=seed)
        minority = int(np.argmin(np.bincount(qs)))
        
        # Library = all other drugs
        library = [d for d in all_drugs if d != hd]
        cand_pops = {}
        for d in library:
            drows = np.flatnonzero(
                (ds.obs["cell_line"] == ctx).to_numpy() & 
                (ds.obs["perturbation"] == d).to_numpy() &
                (~ds.obs["is_control"].astype(bool).to_numpy())
            )
            if len(drows) < 10:
                continue
            if len(drows) > max_cells:
                drows = rng.choice(drows, max_cells, replace=False)
            cand_pops[d] = ds.X[drows].astype(np.float32)
        
        if len(cand_pops) < 5:
            continue
        
        names = list(cand_pops.keys())
        
        # Score with both methods
        mc = min(150, len(qX))
        energy_scores = np.array([score_energy(cand_pops[n], qX, max_cells=mc, seed=seed) for n in names])
        cosine_scores = np.array([score_mean_cosine(cand_pops[n], qX, control_P=ctrl_mean, control_Q=ctrl_mean) for n in names])
        
        dart_pick = names[int(np.argmax(energy_scores))]
        mean_pick = names[int(np.argmax(cosine_scores))]
        
        # Evaluate both picks under both coverage metrics
        for pick_method, pick_drug in [("DART_energy", dart_pick), ("mean_cosine", mean_pick)]:
            P = cand_pops[pick_drug]
            mb_cov = mean_based_coverage(P, qX, qs, minority)
            cl_cov = cell_level_coverage(P, qX, qs, minority)
            
            # MoA match: does the picked drug share MoA with the hidden drug?
            hd_moa = drug2moa.get(hd)
            pick_moa = drug2moa.get(pick_drug)
            moa_match = 1 if (hd_moa and pick_moa and hd_moa == pick_moa) else 0
            
            rows.append({
                "seed": seed, "held_drug": hd, "pick_method": pick_method,
                "picked_drug": pick_drug, "same_drug": int(pick_drug == hd),
                "mean_based_coverage": mb_cov, "cell_level_coverage": cl_cov,
                "moa_match": moa_match,
                "dart_pick": dart_pick, "mean_pick": mean_pick,
                "picks_differ": int(dart_pick != mean_pick),
            })
        
        if (hi + 1) % 5 == 0:
            print(f"  seed={seed} drug {hi+1}/{len(held)} done ({time.time()-t0:.0f}s)")

df = pd.DataFrame(rows)
outpath = str(_P(RESULTS_AUDIT) / "fix_validation.csv")
df.to_csv(outpath, index=False)
print(f"\nSaved {len(df)} rows to {outpath}")

# ── analysis ──
print("\n" + "="*60)
print("FIX VALIDATION ANALYSIS")
print("="*60)

dart_rows = df[df.pick_method == "DART_energy"]
mean_rows = df[df.pick_method == "mean_cosine"]

# Pair by (seed, held_drug)
merged = dart_rows.merge(mean_rows, on=["seed", "held_drug"], suffixes=("_dart", "_mean"))

# Mean-based coverage gap
mb_gap = merged.mean_based_coverage_dart.values - merged.mean_based_coverage_mean.values
print(f"\nMean-based coverage (original metric):")
print(f"  JUDGE mean: {dart_rows.mean_based_coverage.mean():.4f}")
print(f"  Mean mean: {mean_rows.mean_based_coverage.mean():.4f}")
print(f"  Gap (JUDGE - mean): {mb_gap.mean():.4f} (median {np.median(mb_gap):.4f})")
print(f"  JUDGE wins: {(mb_gap > 0).mean():.1%}")

# Cell-level coverage gap
cl_gap = merged.cell_level_coverage_dart.values - merged.cell_level_coverage_mean.values
print(f"\nCell-level coverage (FIXED metric):")
print(f"  JUDGE mean: {dart_rows.cell_level_coverage.mean():.4f}")
print(f"  Mean mean: {mean_rows.cell_level_coverage.mean():.4f}")
print(f"  Gap (JUDGE - mean): {cl_gap.mean():.4f} (median {np.median(cl_gap):.4f})")
print(f"  JUDGE wins: {(cl_gap > 0).mean():.1%}")

# MoA match
print(f"\nMoA match rate:")
print(f"  JUDGE: {dart_rows.moa_match.mean():.3f}")
print(f"  Mean: {mean_rows.moa_match.mean():.3f}")

# Rank disagreement
print(f"\nPicks differ: {merged.picks_differ_dart.mean():.1%}")
print(f"Total queries: {len(merged)}")

# Wilcoxon test on cell-level gap
from scipy.stats import wilcoxon
if len(cl_gap) > 10:
    stat, p = wilcoxon(cl_gap)
    print(f"\nWilcoxon signed-rank on cell-level gap: stat={stat:.1f}, p={p:.4f}")
