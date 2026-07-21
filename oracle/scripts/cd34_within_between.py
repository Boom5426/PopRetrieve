#!/usr/bin/env python
"""Definitive noise-controlled test: do well-powered natural lineages rank drugs
differently, BEYOND sampling noise?

Matched-budget within-vs-between design (the only fair comparison):
  at a fixed budget of n cells/drug/subpop,
    within[k]  = Spearman(drug-sim from sample1_k, drug-sim from sample2_k)   [disjoint]
    between[k,l]= Spearman(drug-sim from sample_k, drug-sim from sample_l)
  If between[k,l] < within[k],within[l] robustly => lineages genuinely disagree.
  If between ~= within => the apparent disagreement is just noise.
Only big subpops (fraction > thr) and drugs with >= 2n cells in each are used.
"""
from __future__ import annotations
import argparse
import numpy as np, torch
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from scipy.stats import spearmanr

def unit(M): return M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-9)
def od(M): return M[np.triu_indices(M.shape[0], 1)]

ap = argparse.ArgumentParser()
ap.add_argument("--processed", default="data/processed/cd34_all.pt")
ap.add_argument("--n", type=int, default=80, help="matched cells/drug/subpop budget")
ap.add_argument("--seeds", type=int, default=12)
ap.add_argument("--thr", type=float, default=0.2, help="min subpop fraction to include")
args = ap.parse_args()

blob = torch.load(args.processed, weights_only=False)
X = np.asarray(blob["X"]); obs = blob["obs"]; genes = np.asarray(blob["gene_names"])
is_ctrl = obs["is_control"].values.astype(bool)
pert = obs["perturbation"].astype(str).values
Xc = X[is_ctrl]; mu_c = Xc.mean(0)
drugs = sorted(set(pert[~is_ctrl])); D = len(drugs)
lin = {"HBB": "erythroid", "HBD": "erythroid", "KLF1": "erythroid", "MPO": "myeloid",
       "ELANE": "myeloid", "PRTN3": "myeloid", "SPINK2": "HSC/MPP", "AVP": "HSC/MPP",
       "CLC": "baso/mast", "HDC": "baso/mast", "CPA3": "baso/mast", "GATA2": "baso/mast"}
pca = PCA(30, random_state=0).fit(Xc)

for K in [2, 3]:
    km = KMeans(K, n_init=10, random_state=0).fit(pca.transform(Xc))
    cent = km.cluster_centers_; lab_c = km.labels_
    frac = np.bincount(lab_c, minlength=K) / len(lab_c)
    def name(k):
        d = Xc[lab_c == k].mean(0) - mu_c
        top = [genes[i] for i in np.argsort(-d)[:15]]
        return f"c{k}:" + next((lin[g] for g in top if g in lin), "?")
    def assign(P):
        Z = pca.transform(P); return ((Z[:, None, :] - cent[None]) ** 2).sum(-1).argmin(1)
    asg = {d: assign(X[pert == d]) for d in drugs}
    ctrl_mu = {k: Xc[lab_c == k].mean(0) for k in range(K)}
    big = [k for k in range(K) if frac[k] > args.thr]
    n = args.n
    # drugs usable = >= 2n cells in every big subpop
    usable = [d for d in drugs if all((asg[d] == k).sum() >= 2 * n for k in big)]
    print(f"\n===== K={K}  big subpops={[name(k) for k in big]}  "
          f"fracs={np.round(frac,2)}  n={n}/drug/subpop  usable drugs={len(usable)} =====")
    if len(usable) < 8:
        print("   too few usable drugs at this budget; skip."); continue

    within = {k: [] for k in big}; between = {}
    for s in range(args.seeds):
        r = np.random.default_rng(300 + s)
        samp = {}  # (k, half) -> [len(usable), G]
        for k in big:
            A = np.zeros((len(usable), X.shape[1])); B = np.zeros((len(usable), X.shape[1]))
            for di, d in enumerate(usable):
                idx = np.where(asg[d] == k)[0]; r.shuffle(idx)
                A[di] = X[pert == d][idx[:n]].mean(0) - ctrl_mu[k]
                B[di] = X[pert == d][idx[n:2*n]].mean(0) - ctrl_mu[k]
            samp[(k, 0)] = unit(A); samp[(k, 1)] = unit(B)
        for k in big:
            within[k].append(spearmanr(od(samp[(k,0)] @ samp[(k,0)].T),
                                       od(samp[(k,1)] @ samp[(k,1)].T)).correlation)
        for i, k in enumerate(big):
            for l in big[i+1:]:
                between.setdefault((k, l), []).append(
                    spearmanr(od(samp[(k,0)] @ samp[(k,0)].T),
                              od(samp[(l,0)] @ samp[(l,0)].T)).correlation)
    print("  within-subpop reliability (same lineage, disjoint cells):")
    for k in big:
        print(f"    {name(k):16s} within={np.mean(within[k]):.2f} ± {np.std(within[k]):.2f}")
    print("  between-subpop agreement (different lineage, matched budget):")
    for (k, l), v in between.items():
        wk, wl = np.mean(within[k]), np.mean(within[l]); b = np.mean(v)
        verdict = "DISAGREE (real)" if b < min(wk, wl) - 2*np.std(v) else "agree ~ noise floor"
        print(f"    {name(k):16s} vs {name(l):16s} between={b:.2f} ± {np.std(v):.2f}  "
              f"(within {wk:.2f}/{wl:.2f}) -> {verdict}")
