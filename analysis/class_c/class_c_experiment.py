#!/usr/bin/env python3

# =============================================================================
# SUPERSEDED. DO NOT USE THE NUMBERS THIS SCRIPT PRODUCES.
#
# `retrieval.metrics.score_energy` returns MINUS the energy distance, i.e. a
# SIMILARITY (higher = more similar). This script ranks it ASCENDING
# (rankdata(e_scores) / argmin(dart_scores)) under the comment "lowest energy =
# top pick", so JUDGE's rank-1 candidate is the population FARTHEST from the
# query. The mean-cosine baseline in the same script is ranked correctly
# (argmax). JUDGE is ranked backwards and its incumbent is not.
#
# The inversion selects large-response candidates (energy distance tracks
# candidate magnitude at rho = +0.79), and large response predicts potency, so
# it manufactures an apparent +0.52 JUDGE-vs-potency correlation. The true value
# is -0.52.
#
# This script also pools all four doses (the rest of the paper uses 10 uM) and
# pools GDSC1 with GDSC2 (different platforms, not a common AUC scale).
#
# Use analysis/class_c/class_c_magnitude_control_v2.py. See CORRECTIONS.md R14.
# =============================================================================


"""
Class C Semi-Real Viability Oracle Experiment
JUDGE energy vs mean_cosine ranking evaluated against GDSC AUC/IC50.
"""

# --- repo-root path resolution (added for public release; replaces hardcoded /data/boom/JUDGE) ---
from pathlib import Path as _P
REPO = _P(__file__).resolve().parents[2]
SRC = str(REPO / "src")
RESULTS_AUDIT = str(REPO / "results" / "upgrade")
DATA_PROC = str(REPO / "data" / "processed")
DATA_ANNO = str(REPO / "data" / "annotation")
# ------------------------------------------------------------------------------------------------
import sys
sys.path.insert(0, SRC)

import numpy as np
import pandas as pd
import json
from scipy import stats
from itertools import combinations

# --- Load match table ---
match_df = pd.read_csv(str(_P(RESULTS_AUDIT) / 'drug_match_table.csv'))

# Deduplicate: S-Ruxolitinib and Ruxolitinib both map to same GDSC drug.
# Keep only one (Ruxolitinib, drop S-Ruxolitinib)
match_df = match_df[match_df['sp_drug'] != 'S-Ruxolitinib (INCB018424)'].copy()
print(f"After dedup: {match_df['sp_drug'].nunique()} unique SP drugs")
for ln in ['A549', 'K562', 'MCF7']:
    sub = match_df[match_df['cell_line'] == ln]
    print(f"  {ln}: {sub['sp_drug'].nunique()} drugs")

# --- Load SciPlex3 data ---
from data.load_sciplex3 import load_sciplex3
ds = load_sciplex3()
print(f"\nSciPlex3: {ds.X.shape}, cell lines: {ds.obs['cell_line'].unique()}")

# --- Load scoring functions ---
from retrieval.metrics import score_energy, score_mean_cosine

# --- Build per-cell-line experiment ---
SEED = 42
np.random.seed(SEED)

all_results = []

for cell_line in ['A549', 'K562', 'MCF7']:
    print(f"\n{'='*60}")
    print(f"Cell line: {cell_line}")
    print(f"{'='*60}")
    
    # Get matched drugs for this cell line
    line_matches = match_df[match_df['cell_line'] == cell_line].copy()
    matched_drugs = sorted(line_matches['sp_drug'].unique())
    n_drugs = len(matched_drugs)
    print(f"Matched drugs: {n_drugs}")
    
    if n_drugs < 8:
        print(f"SKIP: fewer than 8 matched drugs")
        continue
    
    # Get viability lookup: sp_drug -> AUC
    via_lookup = dict(zip(line_matches['sp_drug'], line_matches['AUC']))
    ic50_lookup = dict(zip(line_matches['sp_drug'], line_matches['LN_IC50']))
    
    # Get expression data for this cell line
    line_mask = ds.obs['cell_line'] == cell_line
    control_mask = line_mask & ds.obs['is_control']
    
    # Pre-extract treated cell populations for each matched drug
    drug_cells = {}
    for drug in matched_drugs:
        drug_mask = line_mask & (ds.obs['perturbation'] == drug) & (~ds.obs['is_control'])
        n_cells = drug_mask.sum()
        if n_cells >= 10:  # need enough cells for distributional scoring
            drug_cells[drug] = ds.X[drug_mask.values].toarray() if hasattr(ds.X, 'toarray') else ds.X[drug_mask.values]
    
    # Filter to drugs with enough cells
    valid_drugs = sorted(drug_cells.keys())
    print(f"Drugs with >= 10 treated cells: {len(valid_drugs)}/{n_drugs}")
    
    if len(valid_drugs) < 8:
        print(f"SKIP: fewer than 8 valid drugs after cell count filter")
        continue
    
    # Leave-one-out retrieval
    for qi, query_drug in enumerate(valid_drugs):
        candidate_drugs = [d for d in valid_drugs if d != query_drug]
        n_cand = len(candidate_drugs)
        
        query_cells = drug_cells[query_drug]
        
        # Score each candidate against query
        dart_scores = []
        mean_scores = []
        cand_aucs = []
        cand_ic50s = []
        
        for cand_drug in candidate_drugs:
            cand_cells = drug_cells[cand_drug]
            
            # JUDGE energy score (lower = more similar distributions)
            e_score = score_energy(query_cells, cand_cells, max_cells=500, seed=SEED)
            # Mean cosine score (higher = more similar means)
            m_score = score_mean_cosine(query_cells, cand_cells)
            
            dart_scores.append(e_score)
            mean_scores.append(m_score)
            cand_aucs.append(via_lookup[cand_drug])
            cand_ic50s.append(ic50_lookup[cand_drug])
        
        dart_scores = np.array(dart_scores)
        mean_scores = np.array(mean_scores)
        cand_aucs = np.array(cand_aucs)
        cand_ic50s = np.array(cand_ic50s)
        
        # Rank by JUDGE (lower energy = more similar = rank 1)
        dart_ranks = stats.rankdata(dart_scores, method='average')
        # Rank by mean cosine (higher = more similar = rank 1, so negate)
        mean_ranks = stats.rankdata(-mean_scores, method='average')
        # Potency rank: lower AUC = more potent = rank 1
        potency_ranks = stats.rankdata(cand_aucs, method='average')
        
        # Spearman: correlation between JUDGE rank and potency rank
        # Positive = JUDGE's most-similar also tends to be most-potent
        dart_spearman, dart_pval = stats.spearmanr(dart_ranks, potency_ranks)
        mean_spearman, mean_pval = stats.spearmanr(mean_ranks, potency_ranks)
        
        # Top-1 picks
        dart_top1_idx = np.argmin(dart_scores)  # lowest energy = top pick
        mean_top1_idx = np.argmax(mean_scores)  # highest cosine = top pick
        
        dart_top1_drug = candidate_drugs[dart_top1_idx]
        mean_top1_drug = candidate_drugs[mean_top1_idx]
        dart_top1_auc = cand_aucs[dart_top1_idx]
        mean_top1_auc = cand_aucs[mean_top1_idx]
        
        # Most potent candidate (lowest AUC)
        most_potent_idx = np.argmin(cand_aucs)
        most_potent_drug = candidate_drugs[most_potent_idx]
        
        # Hit@1: did top-1 pick = most potent?
        dart_hit1 = 1 if dart_top1_idx == most_potent_idx else 0
        mean_hit1 = 1 if mean_top1_idx == most_potent_idx else 0
        
        # Hit@3
        dart_top3_idxs = set(np.argsort(dart_scores)[:3])
        mean_top3_idxs = set(np.argsort(-mean_scores)[:3])
        dart_hit3 = 1 if most_potent_idx in dart_top3_idxs else 0
        mean_hit3 = 1 if most_potent_idx in mean_top3_idxs else 0
        
        all_results.append({
            'cell_line': cell_line,
            'query_drug': query_drug,
            'query_auc': via_lookup[query_drug],
            'query_ic50': ic50_lookup[query_drug],
            'n_candidates': n_cand,
            'dart_top1_drug': dart_top1_drug,
            'dart_top1_auc': dart_top1_auc,
            'mean_top1_drug': mean_top1_drug,
            'mean_top1_auc': mean_top1_auc,
            'most_potent_drug': most_potent_drug,
            'most_potent_auc': cand_aucs[most_potent_idx],
            'dart_spearman_rho': dart_spearman,
            'dart_spearman_p': dart_pval,
            'mean_spearman_rho': mean_spearman,
            'mean_spearman_p': mean_pval,
            'dart_hit1': dart_hit1,
            'mean_hit1': mean_hit1,
            'dart_hit3': dart_hit3,
            'mean_hit3': mean_hit3,
        })
        
        if qi % 10 == 0:
            print(f"  query {qi+1}/{len(valid_drugs)}: {query_drug}")

# --- Aggregate results ---
res_df = pd.DataFrame(all_results)
res_df.to_csv(str(_P(RESULTS_AUDIT) / 'class_c_viability.csv'), index=False)
print(f"\nSaved class_c_viability.csv: {len(res_df)} queries")

# --- Summary statistics ---
print(f"\n{'='*60}")
print("OVERALL RESULTS")
print(f"{'='*60}")

print(f"Total queries: {len(res_df)}")
for ln in res_df['cell_line'].unique():
    sub = res_df[res_df['cell_line'] == ln]
    print(f"\n--- {ln} ({len(sub)} queries) ---")
    print(f"  JUDGE Spearman rho: median={sub['dart_spearman_rho'].median():.4f}, "
          f"mean={sub['dart_spearman_rho'].mean():.4f}")
    print(f"  Mean Spearman rho: median={sub['mean_spearman_rho'].median():.4f}, "
          f"mean={sub['mean_spearman_rho'].mean():.4f}")
    print(f"  JUDGE Hit@1: {sub['dart_hit1'].mean():.4f}")
    print(f"  Mean Hit@1: {sub['mean_hit1'].mean():.4f}")
    print(f"  JUDGE Hit@3: {sub['dart_hit3'].mean():.4f}")
    print(f"  Mean Hit@3: {sub['mean_hit3'].mean():.4f}")
    print(f"  JUDGE top1 AUC: mean={sub['dart_top1_auc'].mean():.4f}")
    print(f"  Mean top1 AUC: mean={sub['mean_top1_auc'].mean():.4f}")

# Overall
print(f"\n--- OVERALL ---")
print(f"JUDGE Spearman rho: median={res_df['dart_spearman_rho'].median():.4f}, "
      f"mean={res_df['dart_spearman_rho'].mean():.4f}")
print(f"Mean Spearman rho: median={res_df['mean_spearman_rho'].median():.4f}, "
      f"mean={res_df['mean_spearman_rho'].mean():.4f}")

# Wilcoxon signed-rank: JUDGE-top1 AUC vs Mean-top1 AUC
# Lower AUC = more potent; if JUDGE picks more potent drugs, its top1 AUC should be lower
from scipy.stats import wilcoxon
stat, p_wilcoxon = wilcoxon(res_df['dart_top1_auc'], res_df['mean_top1_auc'])
print(f"\nWilcoxon JUDGE-top1 AUC vs Mean-top1 AUC: stat={stat:.1f}, p={p_wilcoxon:.6f}")
dart_lower = (res_df['dart_top1_auc'] < res_df['mean_top1_auc']).sum()
mean_lower = (res_df['dart_top1_auc'] > res_df['mean_top1_auc']).sum()
ties = (res_df['dart_top1_auc'] == res_df['mean_top1_auc']).sum()
print(f"  JUDGE picks more potent: {dart_lower}/{len(res_df)}, Mean picks more potent: {mean_lower}/{len(res_df)}, ties: {ties}")

# Hit rates
print(f"\nDart Hit@1: {res_df['dart_hit1'].mean():.4f}")
print(f"Mean Hit@1: {res_df['mean_hit1'].mean():.4f}")
n_valid = res_df['n_candidates'].iloc[0]  # all same within cell line
for ln in res_df['cell_line'].unique():
    sub = res_df[res_df['cell_line'] == ln]
    n_c = sub['n_candidates'].iloc[0]
    random_hit1 = 1.0 / n_c
    random_hit3 = min(3.0 / n_c, 1.0)
    print(f"  {ln}: random Hit@1 = {random_hit1:.4f} (1/{n_c}), random Hit@3 = {random_hit3:.4f}")

print(f"\nDart Hit@3: {res_df['dart_hit3'].mean():.4f}")
print(f"Mean Hit@3: {res_df['mean_hit3'].mean():.4f}")

# Random baseline Hit@1 (harmonic mean across cell lines)
random_hit1_vals = []
for ln in res_df['cell_line'].unique():
    sub = res_df[res_df['cell_line'] == ln]
    n_c = sub['n_candidates'].iloc[0]
    random_hit1_vals.append(1.0 / n_c)
avg_random_hit1 = np.mean(random_hit1_vals)
print(f"\nAverage random Hit@1 baseline: {avg_random_hit1:.4f}")

