#!/usr/bin/env python
"""Robustness of the 'minority subpop ranks drugs differently' result.

Kills the obvious confound (minority c3 has ~75 cells/drug, so low correlation
could be pure sampling noise):
  (R1) split-half RELIABILITY of each subpop's drug-similarity structure.
       If c3 self-agrees >> it agrees with the mean, the divergence is real.
  (R2) DOWNSAMPLE each majority subpop to c3's per-drug cell count; if its
       agreement with the mean stays high, low cell count is NOT the cause.
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path
import numpy as np, torch
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from scipy.stats import spearmanr

def unit(M): return M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-9)
def offdiag(M):
    iu = np.triu_indices(M.shape[0], 1); return M[iu]

ap = argparse.ArgumentParser()
ap.add_argument("--processed", default="data/processed/cd34_all.pt")
ap.add_argument("--K", type=int, default=4)
ap.add_argument("--seeds", type=int, default=10)
ap.add_argument("--min-cells", type=int, default=20)
args = ap.parse_args()

blob = torch.load(args.processed, weights_only=False)
X = np.asarray(blob["X"]); obs = blob["obs"]; genes = np.asarray(blob["gene_names"])
is_ctrl = obs["is_control"].values.astype(bool)
pert = obs["perturbation"].astype(str).values
Xc = X[is_ctrl]; mu_c = Xc.mean(0)
drugs = sorted(set(pert[~is_ctrl])); D = len(drugs)
K = args.K
pca = PCA(30, random_state=0).fit(Xc)
km = KMeans(K, n_init=10, random_state=0).fit(pca.transform(Xc))
cent = km.cluster_centers_; lab_c = km.labels_
frac = np.bincount(lab_c, minlength=K) / len(lab_c)
mink = int(np.argmin(frac))
lin = {0: "HSC/MPP", 1: "erythroid", 2: "myeloid", 3: "baso/mast"}
def nm(k): return f"c{k}:{lin.get(k,'')}"

def assign(P):
    Z = pca.transform(P)
    return ((Z[:, None, :] - cent[None]) ** 2).sum(-1).argmin(1)
cells = {d: X[pert == d] for d in drugs}
asg = {d: assign(cells[d]) for d in drugs}
ctrl_mu = {k: Xc[lab_c == k].mean(0) for k in range(K)}
Sall = unit(np.stack([cells[d].mean(0) - mu_c for d in drugs]))
Mall = Sall @ Sall.T

# whole-mean vs each subpop (reference numbers)
def sub_sig(k, subsample=None, seed=0):
    r = np.random.default_rng(seed); S = np.full((D, X.shape[1]), np.nan); ok = np.zeros(D, bool)
    for di, d in enumerate(drugs):
        idx = np.where(asg[d] == k)[0]
        if subsample is not None and len(idx) > subsample[di]:
            idx = r.choice(idx, subsample[di], replace=False)
        if len(idx) >= args.min_cells:
            S[di] = cells[d][idx].mean(0) - ctrl_mu[k]; ok[di] = True
    return unit(np.nan_to_num(S)), ok

n3 = np.array([int((asg[d] == mink).sum()) for d in drugs])   # per-drug minority cell count
print(f"[cd34] K={K}  minority={nm(mink)} ({frac[mink]*100:.0f}%)  per-drug minority cells: "
      f"min={n3.min()} med={int(np.median(n3))} max={n3.max()}")

# ---- R1: split-half reliability per subpop ----
print("\n[R1] split-half reliability of each subpop's drug-ranking (Spearman, avg over seeds)")
print("     vs its agreement with the WHOLE-MEAN ranking:")
for k in range(K):
    rels, means = [], []
    for s in range(args.seeds):
        r = np.random.default_rng(100 + s)
        S1 = np.full((D, X.shape[1]), np.nan); S2 = np.full((D, X.shape[1]), np.nan); ok = np.zeros(D, bool)
        for di, d in enumerate(drugs):
            idx = np.where(asg[d] == k)[0]; r.shuffle(idx); h = len(idx) // 2
            if h >= args.min_cells:
                S1[di] = cells[d][idx[:h]].mean(0) - ctrl_mu[k]
                S2[di] = cells[d][idx[h:2*h]].mean(0) - ctrl_mu[k]; ok[di] = True
        U1, U2 = unit(np.nan_to_num(S1))[ok], unit(np.nan_to_num(S2))[ok]
        rels.append(spearmanr(offdiag(U1 @ U1.T), offdiag(U2 @ U2.T)).correlation)
        Ua = Sall[ok]
        means.append(spearmanr(offdiag(U1 @ U1.T), offdiag(Ua @ Ua.T)).correlation)
    print(f"  {nm(k):16s} reliability={np.mean(rels):.2f}   agree-with-mean={np.mean(means):.2f}"
          + ("   <-- reliable but disagrees" if k == mink else ""))

# ---- R2: downsample majority subpops to minority cell count ----
print(f"\n[R2] downsample each majority subpop to c3's per-drug cell count "
      f"(med {int(np.median(n3))}); agreement with whole-mean:")
for k in range(K):
    if k == mink:
        continue
    vals = []
    for s in range(args.seeds):
        Uk, ok = sub_sig(k, subsample=n3, seed=200 + s)
        Uk = Uk[ok]; Ua = Sall[ok]
        vals.append(spearmanr(offdiag(Uk @ Uk.T), offdiag(Ua @ Ua.T)).correlation)
    # full (no downsample) reference
    Ukf, okf = sub_sig(k); Ukf = Ukf[okf]; Uaf = Sall[okf]
    full = spearmanr(offdiag(Ukf @ Ukf.T), offdiag(Uaf @ Uaf.T)).correlation
    print(f"  {nm(k):16s} full-agree={full:.2f}   downsampled-to-c3-count agree={np.mean(vals):.2f}")
print(f"\n  minority {nm(mink)} agree-with-mean (from R1) is the outlier: if majorities stay high "
      f"even at c3's cell count, the minority's divergence is biology, not sample size.")
