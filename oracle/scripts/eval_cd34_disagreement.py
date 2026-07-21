#!/usr/bin/env python
"""Do NATURAL progenitor subpopulations of CD34+ rank drugs differently?

Construction-free test of the thesis on real heterogeneity: if distinct natural
subpopulations (HSC / erythroid / myeloid / baso-mast) induce DIFFERENT drug
orderings, then any single mean-based ranking (which the population mean forces)
is wrong for at least one subpopulation — the mechanism behind "population-in,
mean-out". Per-subpop per-drug mean-delta signatures; compare drug-similarity
structure and nearest-drug across subpops and vs the whole-population mean.

    python scripts/eval_cd34_disagreement.py --K 4
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path
import numpy as np, torch, pandas as pd
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]


def unit(M):
    return M / (np.linalg.norm(M, axis=1, keepdims=True) + 1e-9)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed", default="data/processed/cd34_all.pt")
    ap.add_argument("--K", type=int, default=4)
    ap.add_argument("--min-cells", type=int, default=25)
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
    names = {}
    marker_lineage = {"HBB": "erythroid", "HBD": "erythroid", "KLF1": "erythroid",
                      "MPO": "myeloid", "ELANE": "myeloid", "PRTN3": "myeloid",
                      "SPINK2": "HSC/MPP", "AVP": "HSC/MPP", "FAM30A": "HSC/MPP",
                      "CLC": "baso/mast", "HDC": "baso/mast", "CPA3": "baso/mast"}
    for k in range(K):
        d = Xc[lab_c == k].mean(0) - mu_c
        top = [genes[i] for i in np.argsort(-d)[:15]]
        lin = next((marker_lineage[g] for g in top if g in marker_lineage), f"c{k}")
        names[k] = f"c{k}:{lin}"
    print(f"[cd34] K={K} subpops: " + "  ".join(f"{names[k]}({frac[k]*100:.0f}%)" for k in range(K)))

    def assign(P):
        Z = pca.transform(P)
        return ((Z[:, None, :] - cent[None]) ** 2).sum(-1).argmin(1)

    passign = {d: assign(X[pert == d]) for d in drugs}

    # per-subpop per-drug signature (direction), and whole-mean signature
    ctrl_sub_mu = {k: Xc[lab_c == k].mean(0) for k in range(K)}
    Sig = {k: np.full((D, X.shape[1]), np.nan) for k in range(K)}
    Sall = np.zeros((D, X.shape[1]))
    ok = {k: np.zeros(D, bool) for k in range(K)}
    for di, d in enumerate(drugs):
        P = X[pert == d]; a = passign[d]
        Sall[di] = P.mean(0) - mu_c
        for k in range(K):
            if (a == k).sum() >= args.min_cells:
                Sig[k][di] = P[a == k].mean(0) - ctrl_sub_mu[k]
                ok[k][di] = True

    Un = {k: unit(np.nan_to_num(Sig[k])) for k in range(K)}
    Ua = unit(Sall)

    # (1) cross-subpop agreement of the drug-drug similarity structure
    print("\n[1] agreement of drug-similarity structure across subpops (Spearman of off-diag cosines):")
    print("     " + " ".join(f"{names[l][:10]:>11s}" for l in range(K)))
    for k in range(K):
        rowvals = []
        for l in range(K):
            valid = ok[k] & ok[l]
            Mk = (Un[k][valid] @ Un[k][valid].T)
            Ml = (Un[l][valid] @ Un[l][valid].T)
            iu = np.triu_indices(valid.sum(), 1)
            rho = spearmanr(Mk[iu], Ml[iu]).correlation
            rowvals.append(rho)
        print(f"  {names[k][:10]:>10s} " + " ".join(f"{v:11.2f}" for v in rowvals))

    # (2) each subpop's drug-ranking vs the WHOLE-MEAN ranking
    print("\n[2] does each subpop agree with the WHOLE-MEAN drug ordering?")
    for k in range(K):
        valid = ok[k]
        Mk = Un[k][valid] @ Un[k][valid].T
        Ma = Ua[valid] @ Ua[valid].T
        iu = np.triu_indices(valid.sum(), 1)
        rho = spearmanr(Mk[iu], Ma[iu]).correlation
        print(f"  {names[k]:22s} vs mean: Spearman={rho:.2f}  (n_drugs={valid.sum()})")

    # (3) nearest-drug flips: for each drug, top-match under mean vs under minority subpop
    mink = int(np.argmin(frac))
    print(f"\n[3] nearest-drug substitution (mean vs minority {names[mink]}):")
    Ma = Ua @ Ua.T; np.fill_diagonal(Ma, -9)
    Mm = Un[mink] @ Un[mink].T; np.fill_diagonal(Mm, -9)
    flips = 0; examples = []
    for di, d in enumerate(drugs):
        if not ok[mink][di]:
            continue
        nn_mean = int(np.argmax(Ma[di]))
        cand = np.where(ok[mink])[0]
        nn_min = int(cand[np.argmax(Mm[di][cand])])
        if nn_mean != nn_min:
            flips += 1
            examples.append((d, drugs[nn_mean], drugs[nn_min]))
    nvalid = int(ok[mink].sum())
    print(f"  {flips}/{nvalid} drugs get a DIFFERENT nearest drug on the minority vs the mean")
    for d, a, b in examples[:8]:
        print(f"     {d:16s}  mean->{a:16s}  minority->{b}")

    # (4) headline number
    valid_all = np.ones(D, bool)
    for k in range(K):
        valid_all &= ok[k]
    print(f"\n[summary] {valid_all.sum()}/{D} drugs measurable in all {K} subpops.")
    Ms = []
    for k in range(K):
        Mk = Un[k][valid_all] @ Un[k][valid_all].T
        Ms.append(Mk[np.triu_indices(valid_all.sum(), 1)])
    rhos = [spearmanr(Ms[k], Ms[l]).correlation for k in range(K) for l in range(k + 1, K)]
    print(f"  mean pairwise cross-subpop drug-ranking Spearman = {np.mean(rhos):.2f} "
          f"(range {np.min(rhos):.2f}..{np.max(rhos):.2f})")
    print("  low/moderate => natural subpops genuinely rank drugs differently => a single "
          "mean-based ranking cannot serve all subpopulations.")


if __name__ == "__main__":
    main()
