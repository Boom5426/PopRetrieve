#!/usr/bin/env python

"""Subsampling power analysis: energy distance vs mean_cosine at various n.

Bootstrap diagnostic: how much noise is in the energy distance estimate
at n=120 (exp12's setting) vs n=400 (exp08's setting)?

Output: <repo>/results/upgrade/subsample_power_results.csv
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
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

import numpy as np
import torch
import pandas as pd
from retrieval.metrics import energy_distance, _tensor

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def compute_energy(X, Y, device=DEVICE):
    with torch.no_grad():
        Xt = torch.as_tensor(X, dtype=torch.float32, device=device)
        Yt = torch.as_tensor(Y, dtype=torch.float32, device=device)
        return float(energy_distance(Xt, Yt))

def compute_mean_cosine(P, Q, ctrl):
    sig_P = P.mean(0) - ctrl
    sig_Q = Q.mean(0) - ctrl
    na, nb = np.linalg.norm(sig_P), np.linalg.norm(sig_Q)
    if na < 1e-12 or nb < 1e-12:
        return 0.0
    return float(sig_P @ sig_Q / (na * nb))

# ---------------------------------------------------------------------------
# 1. Load data, pick drugs
# ---------------------------------------------------------------------------

print("Loading SciPlex3...")
from data.load_sciplex3 import load_sciplex3
data = load_sciplex3()
meta = data.obs if hasattr(data, 'obs') else data.meta
expr = data.X if hasattr(data, 'X') else data.expr

k562_mask = meta['cell_line'] == 'K562'
k562_meta = meta[k562_mask]

drug_counts = k562_meta['perturbation'].value_counts()
ctrl_names = {'control', 'Control', 'Vehicle', 'DMSO', 'vehicle'}

# Pick drugs (each has 480 cells)
drugs = [d for d in drug_counts.index if d not in ctrl_names and drug_counts[d] >= 200]
target_drug = drugs[0]
target_drug2 = drugs[1]
distractor_drugs = drugs[2:5]

print(f"Drug 1 (query/self): {target_drug} ({drug_counts[target_drug]} cells)")
print(f"Drug 2 (candidate): {target_drug2} ({drug_counts[target_drug2]} cells)")
print(f"Distractors: {distractor_drugs}")

def get_expr(drug_name):
    mask = k562_mask & (meta['perturbation'] == drug_name)
    e = expr[mask.values] if hasattr(mask, 'values') else expr[mask]
    if hasattr(e, 'toarray'):
        e = e.toarray()
    return np.asarray(e, dtype=np.float32)

drug1_expr = get_expr(target_drug)
drug2_expr = get_expr(target_drug2)
dist_exprs = [get_expr(d) for d in distractor_drugs]

# Control
ctrl_mask = k562_mask & meta['perturbation'].isin(ctrl_names)
ctrl_expr = expr[ctrl_mask.values]
if hasattr(ctrl_expr, 'toarray'):
    ctrl_expr = ctrl_expr.toarray()
ctrl_expr = np.asarray(ctrl_expr, dtype=np.float32)
ctrl_mean = ctrl_expr.mean(0)
print(f"Drug1: {drug1_expr.shape}, Drug2: {drug2_expr.shape}, Ctrl: {ctrl_expr.shape}")

# ---------------------------------------------------------------------------
# 2. Same-drug self-distance bootstrap
# ---------------------------------------------------------------------------

print("\n" + "="*60)
print("PART 1: Same-drug self-distance bootstrap (estimator variance)")
print("="*60)

n_values = [30, 60, 120, 200, 300, 480]
n_boot = 50
rng = np.random.default_rng(42)

# Split drug1 into two halves
perm = rng.permutation(len(drug1_expr))
half = len(drug1_expr) // 2
pop_A = drug1_expr[perm[:half]]  # 240 cells
pop_B = drug1_expr[perm[half:]]  # 240 cells
print(f"Pop A: {pop_A.shape}, Pop B: {pop_B.shape}")

rows = []

for n in n_values:
    if n > len(pop_A) or n > len(pop_B):
        print(f"  n={n}: skipping (not enough cells in half, max={len(pop_A)})")
        continue
    
    energy_vals = []
    cosine_vals = []
    
    for b in range(n_boot):
        idx_a = rng.choice(len(pop_A), n, replace=False)
        idx_b = rng.choice(len(pop_B), n, replace=False)
        sub_A = pop_A[idx_a]
        sub_B = pop_B[idx_b]
        energy_vals.append(compute_energy(sub_A, sub_B))
        cosine_vals.append(compute_mean_cosine(sub_A, sub_B, ctrl_mean))
    
    energy_vals = np.array(energy_vals)
    cosine_vals = np.array(cosine_vals)
    e_mean, e_std = energy_vals.mean(), energy_vals.std()
    c_mean, c_std = cosine_vals.mean(), cosine_vals.std()
    e_cv = e_std / abs(e_mean) if abs(e_mean) > 1e-12 else float('inf')
    c_cv = c_std / abs(c_mean) if abs(c_mean) > 1e-12 else float('inf')
    
    rows.append({'test': 'same_drug_self', 'drug': target_drug, 'n_cells': n,
                 'metric': 'energy_distance', 'mean': e_mean, 'std': e_std,
                 'cv': e_cv, 'min': energy_vals.min(), 'max': energy_vals.max()})
    rows.append({'test': 'same_drug_self', 'drug': target_drug, 'n_cells': n,
                 'metric': 'mean_cosine', 'mean': c_mean, 'std': c_std,
                 'cv': c_cv, 'min': cosine_vals.min(), 'max': cosine_vals.max()})
    
    print(f"  n={n:4d}: energy CV={e_cv:.4f} (mean={e_mean:.4f}, std={e_std:.4f}) | "
          f"cosine CV={c_cv:.4f} (mean={c_mean:.4f}, std={c_std:.4f})")


# ---------------------------------------------------------------------------
# 3. Cross-drug distance bootstrap
# ---------------------------------------------------------------------------

print("\n" + "="*60)
print("PART 2: Cross-drug distance bootstrap (drug A vs drug B)")
print("="*60)

for n in n_values:
    if n > len(drug1_expr) or n > len(drug2_expr):
        print(f"  n={n}: skipping")
        continue
    
    energy_vals = []
    cosine_vals = []
    for b in range(n_boot):
        idx_a = rng.choice(len(drug1_expr), n, replace=False)
        idx_b = rng.choice(len(drug2_expr), n, replace=False)
        sub_A = drug1_expr[idx_a]
        sub_B = drug2_expr[idx_b]
        energy_vals.append(compute_energy(sub_A, sub_B))
        cosine_vals.append(compute_mean_cosine(sub_A, sub_B, ctrl_mean))
    
    energy_vals = np.array(energy_vals)
    cosine_vals = np.array(cosine_vals)
    e_mean, e_std = energy_vals.mean(), energy_vals.std()
    c_mean, c_std = cosine_vals.mean(), cosine_vals.std()
    e_cv = e_std / abs(e_mean) if abs(e_mean) > 1e-12 else float('inf')
    c_cv = c_std / abs(c_mean) if abs(c_mean) > 1e-12 else float('inf')
    
    rows.append({'test': 'cross_drug', 'drug': f"{target_drug}_vs_{target_drug2}",
                 'n_cells': n, 'metric': 'energy_distance', 'mean': e_mean,
                 'std': e_std, 'cv': e_cv, 'min': energy_vals.min(), 'max': energy_vals.max()})
    rows.append({'test': 'cross_drug', 'drug': f"{target_drug}_vs_{target_drug2}",
                 'n_cells': n, 'metric': 'mean_cosine', 'mean': c_mean,
                 'std': c_std, 'cv': c_cv, 'min': cosine_vals.min(), 'max': cosine_vals.max()})
    
    print(f"  n={n:4d}: energy CV={e_cv:.4f} (mean={e_mean:.4f}, std={e_std:.4f}) | "
          f"cosine CV={c_cv:.4f} (mean={c_mean:.4f}, std={c_std:.4f})")


# ---------------------------------------------------------------------------
# 4. Ranking stability
# ---------------------------------------------------------------------------

print("\n" + "="*60)
print("PART 3: Ranking stability (drug B top-1 among 5 candidates)")
print("="*60)

all_cands = [drug2_expr] + dist_exprs + [ctrl_expr[:480]]
cand_names = [target_drug2] + distractor_drugs + ['control']
print(f"Query: {target_drug}, Candidates: {cand_names}")
print(f"Candidate sizes: {[len(c) for c in all_cands]}")

for n in n_values:
    if n > len(drug1_expr) or any(n > len(cc) for cc in all_cands):
        print(f"  n={n}: skipping")
        continue
    
    top1_energy_counts = {name: 0 for name in cand_names}
    top1_cosine_counts = {name: 0 for name in cand_names}
    
    for b in range(n_boot):
        idx_q = rng.choice(len(drug1_expr), n, replace=False)
        query = drug1_expr[idx_q]
        
        energy_scores = {}
        cosine_scores = {}
        for cname, cand_full in zip(cand_names, all_cands):
            idx_c = rng.choice(len(cand_full), n, replace=False)
            cand = cand_full[idx_c]
            energy_scores[cname] = -compute_energy(query, cand)
            cosine_scores[cname] = compute_mean_cosine(query, cand, ctrl_mean)
        
        e_top1 = max(energy_scores, key=energy_scores.get)
        c_top1 = max(cosine_scores, key=cosine_scores.get)
        top1_energy_counts[e_top1] += 1
        top1_cosine_counts[c_top1] += 1
    
    e_fracs = {k: v/n_boot for k, v in top1_energy_counts.items()}
    c_fracs = {k: v/n_boot for k, v in top1_cosine_counts.items()}
    
    e_winner = max(e_fracs, key=e_fracs.get)
    c_winner = max(c_fracs, key=c_fracs.get)
    
    rows.append({'test': 'ranking_stability', 'drug': f"query={target_drug}",
                 'n_cells': n, 'metric': 'energy_top1_stability',
                 'mean': e_fracs[e_winner], 'std': 0, 'cv': 1 - e_fracs[e_winner],
                 'min': 0, 'max': 0})
    rows.append({'test': 'ranking_stability', 'drug': f"query={target_drug}",
                 'n_cells': n, 'metric': 'cosine_top1_stability',
                 'mean': c_fracs[c_winner], 'std': 0, 'cv': 1 - c_fracs[c_winner],
                 'min': 0, 'max': 0})
    
    print(f"  n={n:4d}: energy top1 stability={e_fracs[e_winner]:.2f} (winner={e_winner})")
    print(f"          cosine top1 stability={c_fracs[c_winner]:.2f} (winner={c_winner})")
    print(f"          energy: {e_fracs}")
    print(f"          cosine: {c_fracs}")

# ---------------------------------------------------------------------------
# 5. Save
# ---------------------------------------------------------------------------

import os
out_dir = RESULTS_AUDIT
os.makedirs(out_dir, exist_ok=True)
df = pd.DataFrame(rows)
out_path = os.path.join(out_dir, "subsample_power_results.csv")
df.to_csv(out_path, index=False)
print(f"\nSaved {len(df)} rows to {out_path}")

# Summary
print("\n" + "="*60)
print("SUMMARY")
print("="*60)
for test in ['same_drug_self', 'cross_drug']:
    print(f"\n{test}:")
    sub = df[df.test == test]
    for _, r in sub.iterrows():
        print(f"  n={int(r.n_cells):4d} {r.metric:20s} CV={r.cv:.4f} mean={r['mean']:.6f} std={r['std']:.6f}")

print("\nRanking stability:")
sub = df[df.test == 'ranking_stability']
for _, r in sub.iterrows():
    print(f"  n={int(r.n_cells):4d} {r.metric:25s} stability={r['mean']:.2f}")

print("\nCODE PATH: exp08 uses max_cells=None (all 400 cells), exp12 uses max_cand_cells=120")

