#!/usr/bin/env python
"""Real natural-heterogeneity drug retrieval on CD34+ primary HSPCs (NOTHING constructed).

The heterogeneity is the intrinsic progenitor structure of primary CD34+ cells
(HSC/MPP, erythroid, myeloid, basophil-mast), found unsupervised on the DMSO control.
Self-retrieval: each real drug's held-out treated population is the query; rank all
36 drugs (by their DISJOINT held-out halves) to retrieve the true drug. Compare
mean-matching vs distribution-aware (global energy, natural-subpop coverage).

    python scripts/eval_cd34_retrieval.py --n-seeds 8 --K 4
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path
import numpy as np, torch, pandas as pd
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gidflow.losses.distribution import energy_distance          # noqa: E402
from gidflow.metrics.ranking import retrieval_metrics            # noqa: E402

DEV = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return 0.0 if na < 1e-9 or nb < 1e-9 else float(a @ b / (na * nb))


def edist(a, b, cap, rng):
    if len(a) < 3 or len(b) < 3:
        return 1e6
    if len(a) > cap:
        a = a[rng.choice(len(a), cap, replace=False)]
    if len(b) > cap:
        b = b[rng.choice(len(b), cap, replace=False)]
    with torch.no_grad():
        return float(energy_distance(torch.as_tensor(a, device=DEV),
                                     torch.as_tensor(b, device=DEV)))


SC = ["mean_cosine", "global_energy", "coverage_mean", "coverage_worst"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--processed", default="data/processed/cd34_all.pt")
    ap.add_argument("--K", type=int, default=4)
    ap.add_argument("--n-seeds", type=int, default=8)
    ap.add_argument("--cap", type=int, default=160)
    ap.add_argument("--out", default="results/subflow/cd34_retrieval.csv")
    args = ap.parse_args()

    blob = torch.load(args.processed, weights_only=False)
    X = np.asarray(blob["X"]); obs = blob["obs"]; genes = np.asarray(blob["gene_names"])
    is_ctrl = obs["is_control"].values.astype(bool)
    pert = obs["perturbation"].astype(str).values
    Xc = X[is_ctrl]; mu_c = Xc.mean(0)
    drugs = sorted(set(pert[~is_ctrl]))
    D = len(drugs)
    print(f"[cd34] control={Xc.shape[0]} drugs={D} genes={X.shape[1]}")

    # ---- natural subpops (unsupervised, control-only) ----
    K = args.K
    pca = PCA(30, random_state=0).fit(Xc)
    km = KMeans(K, n_init=10, random_state=0).fit(pca.transform(Xc))
    cent = km.cluster_centers_
    lab_c = km.labels_

    def assign(P):
        Z = pca.transform(P)
        return ((Z[:, None, :] - cent[None]) ** 2).sum(-1).argmin(1)

    frac = np.bincount(lab_c, minlength=K) / len(lab_c)
    print(f"[cd34] K={K} subpop fractions: {np.round(frac,3)}  (minority={frac.min():.3f})")

    pool = {d: X[pert == d] for d in drugs}
    # precompute per-drug subpop assignment once (fixed cells)
    passign = {d: assign(pool[d]) for d in drugs}
    cassign = lab_c

    def split_idx(n, seed):
        r = np.random.default_rng(seed)
        idx = r.permutation(n); h = n // 2
        return idx[:h], idx[h:]

    rows = []
    for seed in range(args.n_seeds):
        rng = np.random.default_rng(1000 + seed)
        # split every drug into disjoint halves A (query source) / B (candidate)
        A, B, Aa, Ba = {}, {}, {}, {}
        for d in drugs:
            ia, ib = split_idx(len(pool[d]), 7000 + seed)
            A[d], B[d] = pool[d][ia], pool[d][ib]
            Aa[d], Ba[d] = passign[d][ia], passign[d][ib]
        # candidate signatures/pools = B halves (fixed within seed)
        cand_sig = {d: B[d].mean(0) - mu_c for d in drugs}
        for qi, dq in enumerate(drugs):
            target = A[dq]; tat = Aa[dq]
            tgt_sig = target.mean(0) - mu_c
            sc = {s: np.zeros(D) for s in SC}
            for ci, dc in enumerate(drugs):
                sc["mean_cosine"][ci] = cos(tgt_sig, cand_sig[dc])
                sc["global_energy"][ci] = -edist(B[dc], target, args.cap, rng)
                es = []
                for k in range(K):
                    tk = target[tat == k]; pk = B[dc][Ba[dc] == k]
                    if len(tk) >= 3 and len(pk) >= 3:
                        es.append(edist(pk, tk, args.cap, rng))
                sc["coverage_mean"][ci] = -np.mean(es) if es else -1e6
                sc["coverage_worst"][ci] = -np.max(es) if es else -1e6
            for s in SC:
                m = retrieval_metrics(sc[s][None], np.array([qi]))
                order = np.argsort(-sc[s]); rank = int(np.where(order == qi)[0][0]) + 1
                rows.append({"seed": seed, "query": dq, "scorer": s,
                             "hit@1": m["hit@1"], "hit@3": float(rank <= 3),
                             "mrr": 1.0 / rank, "rank": rank})
        print(f"  seed {seed} done", flush=True)

    df = pd.DataFrame(rows)
    out = Path(args.out); out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"\n[cd34] wrote {out}  (self-retrieval over {D} real drugs, {args.n_seeds} seeds)")
    print(f"{'scorer':16s} {'Hit@1':>7s} {'Hit@3':>7s} {'MRR':>7s} {'medRank':>8s}")
    agg = {}
    for s in SC:
        d = df[df.scorer == s]
        agg[s] = (d['hit@1'].mean(), d['hit@3'].mean(), d['mrr'].mean(), d['rank'].median())
        print(f"{s:16s} {agg[s][0]:7.3f} {agg[s][1]:7.3f} {agg[s][2]:7.3f} {agg[s][3]:8.1f}")
    print(f"(random baseline Hit@1={1/D:.3f})")

    # ---- minority-subpop panel: is the responsive minority invisible to the mean? ----
    print("\n[minority] per-drug effect magnitude: whole-mean vs each natural subpop")
    mink = int(np.argmin(frac))
    mean_eff, sub_eff = [], []
    for d in drugs:
        P = pool[d]; a = passign[d]
        mean_eff.append(np.linalg.norm(P.mean(0) - mu_c))
        pk = P[a == mink]
        sub_eff.append(np.linalg.norm(pk.mean(0) - Xc[cassign == mink].mean(0)) if len(pk) >= 5 else np.nan)
    mean_eff, sub_eff = np.array(mean_eff), np.array(sub_eff)
    from scipy.stats import spearmanr
    rho = spearmanr(mean_eff, sub_eff, nan_policy="omit").correlation
    top_mean = drugs[int(np.argmax(mean_eff))]
    top_min = drugs[int(np.nanargmax(sub_eff))]
    print(f"  minority subpop = c{mink} ({frac[mink]*100:.1f}% of cells)")
    print(f"  Spearman(mean-effect rank, minority-effect rank) = {rho:.3f}")
    print(f"  top drug by WHOLE-MEAN effect   : {top_mean}")
    print(f"  top drug by MINORITY(c{mink}) effect: {top_min}")
    print("  -> if these differ / rho is low, a mean-based ranker misses the drug that "
          "most affects the responsive minority.")


if __name__ == "__main__":
    main()
