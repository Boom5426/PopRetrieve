#!/usr/bin/env python
"""Explore CD34+ natural heterogeneity to design the real-source money experiment.

- cluster DMSO control into K natural subpopulations (k-means on PCA), name by markers
- per-drug mean-delta signatures + pairwise cosine (find mean-CONFUSABLE drug pairs)
- per-drug per-subpop effect magnitude (find drugs with subpop-SPECIFIC / heterogeneous effects)
- go/no-go: does a mean-confusable pair have DIVERGENT subpop-effect profiles?
  (that gap is exactly what mean-matching misses and distribution-aware scoring catches)
"""
from __future__ import annotations
import numpy as np, torch, pandas as pd
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

blob = torch.load("data/processed/cd34_all.pt", weights_only=False)
X = np.asarray(blob["X"]); obs = blob["obs"]; genes = np.asarray(blob["gene_names"])
is_ctrl = obs["is_control"].values.astype(bool)
pert = obs["perturbation"].astype(str).values
Xc = X[is_ctrl]
drugs = sorted(set(pert[~is_ctrl]))
print(f"control cells={Xc.shape[0]}  genes={X.shape[1]}  drugs={len(drugs)}")
cnt = pd.Series(pert[~is_ctrl]).value_counts()
print(f"treated cells/drug: min={cnt.min()} med={int(cnt.median())} max={cnt.max()}")

# ---- natural subpops of the control (unsupervised) ----
pca = PCA(n_components=30, random_state=0).fit(Xc)
Zc = pca.transform(Xc)
print("\n[subpops] silhouette by K:")
for K in [2, 3, 4, 5, 6]:
    km = KMeans(K, n_init=10, random_state=0).fit(Zc)
    sil = silhouette_score(Zc, km.labels_, sample_size=2000, random_state=0)
    print(f"  K={K}  sil={sil:.3f}  sizes={list(np.bincount(km.labels_))}")

K = 4
km = KMeans(K, n_init=10, random_state=0).fit(Zc)
lab = km.labels_
cent = np.stack([Zc[lab == k].mean(0) for k in range(K)])
mu_all = Xc.mean(0)
print(f"\n[subpops] K={K} markers (top genes vs global control mean):")
for k in range(K):
    d = Xc[lab == k].mean(0) - mu_all
    top = np.argsort(-d)[:12]
    print(f"  c{k} (n={int((lab==k).sum())}): " + ", ".join(genes[top]))

# ---- per-drug mean-delta signatures + confusability ----
sig = np.stack([X[pert == d].mean(0) - mu_all for d in drugs])
Sn = sig / (np.linalg.norm(sig, axis=1, keepdims=True) + 1e-9)
C = Sn @ Sn.T
iu = np.triu_indices(len(drugs), 1)
order = np.argsort(-C[iu])
print("\n[confusable] most mean-similar drug PAIRS (cosine of mean-delta):")
for t in order[:12]:
    i, j = iu[0][t], iu[1][t]
    print(f"  {drugs[i]:16s} ~ {drugs[j]:16s}  cos={C[i,j]:.3f}")

# ---- per-drug per-subpop effect magnitude ----
def subpop_effect(d):
    Xt = X[pert == d]; Zt = pca.transform(Xt)
    a = ((Zt[:, None, :] - cent[None]) ** 2).sum(-1).argmin(1)
    eff = []
    for k in range(K):
        if (a == k).sum() >= 5:
            eff.append(float(np.linalg.norm(Xt[a == k].mean(0) - Xc[lab == k].mean(0))))
        else:
            eff.append(np.nan)
    return np.array(eff)

E = np.stack([subpop_effect(d) for d in drugs])                 # [D,K]
het = np.nanstd(E, axis=1) / (np.nanmean(E, axis=1) + 1e-9)     # effect heterogeneity across subpops
print("\n[heterogeneous drugs] largest across-subpop effect variation (std/mean):")
for i in np.argsort(-het)[:10]:
    print(f"  {drugs[i]:16s} het={het[i]:.2f}  per-subpop|Δ|={np.round(E[i],2)}")

# ---- go/no-go: mean-confusable but subpop-divergent ----
En = E / (np.nanmean(E, axis=1, keepdims=True) + 1e-9)          # normalize each drug's profile
print("\n[GO/NO-GO] mean-confusable pairs ranked by SUBPOP-profile divergence:")
cand = []
for t in order[:40]:                                            # top-40 mean-similar pairs
    i, j = iu[0][t], iu[1][t]
    prof_div = np.nanmean(np.abs(En[i] - En[j]))                # how differently they hit subpops
    cand.append((prof_div, C[i, j], i, j))
for prof_div, cos, i, j in sorted(cand, reverse=True)[:10]:
    print(f"  {drugs[i]:16s} ~ {drugs[j]:16s}  meancos={cos:.3f}  subpop_div={prof_div:.2f}")
    print(f"       {drugs[i]:16s} per-subpop|Δ|={np.round(E[i],2)}")
    print(f"       {drugs[j]:16s} per-subpop|Δ|={np.round(E[j],2)}")
