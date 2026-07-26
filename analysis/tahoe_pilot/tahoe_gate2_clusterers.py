"""Gate 2, re-run with the SAME clusterer panel the manuscript reports.

WHY THIS EXISTS
---------------
The first Gate 2 pass scored the unsupervised arm with k-means only and got a ceiling-minus-
unsupervised gap of 0.181, which was then compared with the manuscript's tissue gap of 0.117.
That comparison is not like for like, and it fails in exactly the way the manuscript warns
about: the tissue number's unsupervised arm is the BEST of four methods, and it is Leiden that
achieves it. The manuscript is explicit that the method families behave differently there:

    "Centroid-based methods collapse (k-means 0.638, Gaussian mixtures 0.620) where the
     graph-based method partly survives (Leiden 0.780), which is the signature of a dominant
     variance direction that is not the drug-response axis."

Scoring Tahoe with k-means alone therefore suppresses the unsupervised arm and inflates the gap.
This script re-scores the IDENTICAL drug pairs, with the identical seed and cell sampling, under
the full panel, and reports the gap against the best unsupervised method, which is the quantity
the manuscript actually reports.

All methods are given best-permutation label matching for free, as in the manuscript.

Numbers only. Run: python tahoe_gate2_clusterers.py --h5ad <path> --pairs <gate2_per_pair.csv> --out <dir>
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.sparse as sp
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.mixture import GaussianMixture
from sklearn.model_selection import StratifiedKFold

SEED = 0
N_PCA = 50          # Leiden and GMM are run in PCA space, as standard single-cell practice
GATE2_CELLS_PER_ARM = 300


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def bpa(true, pred):
    """Best-permutation accuracy for a two-way split; label matching is free."""
    a = (true == pred).mean()
    return float(max(a, 1.0 - a))


def leiden_two_way(Z, seed=SEED):
    """Leiden, with the resolution tuned DOWN until it returns two communities.

    Leiden does not take k. Reporting a many-community partition against a two-class label
    would score the method on a task it was not asked to do, so the resolution is lowered until
    exactly two communities are returned, and the two largest are used if it never reaches two.
    """
    import scanpy as sc
    from anndata import AnnData

    ad = AnnData(Z)
    sc.pp.neighbors(ad, n_neighbors=15, use_rep="X", random_state=seed)
    best = None
    for res in (1.0, 0.5, 0.25, 0.1, 0.05, 0.02, 0.01):
        sc.tl.leiden(ad, resolution=res, random_state=seed, key_added="l",
                     flavor="igraph", n_iterations=2, directed=False)
        lab = ad.obs["l"].astype(int).to_numpy()
        k = len(np.unique(lab))
        if best is None or abs(k - 2) < abs(best[1] - 2):
            best = (lab, k)
        if k == 2:
            return lab
    lab, k = best
    top2 = pd.Series(lab).value_counts().index[:2]
    return np.where(lab == top2[0], 0, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--h5ad", required=True)
    ap.add_argument("--pairs", required=True, help="gate2_per_pair.csv from the first pass")
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=0, help="0 = all pairs")
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)

    import anndata as ad_io
    log(f"reading {a.h5ad}")
    ann = ad_io.read_h5ad(a.h5ad)
    X = ann.X
    if not sp.isspmatrix_csr(X):
        X = sp.csr_matrix(X)
    X = X.astype(np.float32)
    obs = ann.obs[["cell_name", "drug"]].astype(str).reset_index(drop=True)
    log(f"X {X.shape}")

    pairs = pd.read_csv(a.pairs)
    if a.limit:
        pairs = pairs.sample(a.limit, random_state=SEED).reset_index(drop=True)
    log(f"{len(pairs)} pairs to re-score")

    rng = np.random.default_rng(SEED)
    rows = []
    for i, r in pairs.iterrows():
        line, da, db = r.cell_line, r.drug_a, r.drug_b
        ia = np.flatnonzero(((obs.cell_name == line) & (obs.drug == da)).to_numpy())
        ib = np.flatnonzero(((obs.cell_name == line) & (obs.drug == db)).to_numpy())
        n = min(len(ia), len(ib), GATE2_CELLS_PER_ARM)
        if n < 50:
            continue
        # NOTE: this re-draws the sample rather than reusing the first pass's exact cells (the
        # first pass did not persist indices). Same seed and same rule, so it is a matched
        # protocol, not the identical draw; the k-means column below is recomputed here rather
        # than copied so that every number in this table comes from one sampling.
        ia = rng.choice(ia, size=n, replace=False)
        ib = rng.choice(ib, size=n, replace=False)
        Z = np.asarray(sp.vstack([X[ia], X[ib]]).todense(), dtype=np.float64)
        y = np.r_[np.zeros(n, int), np.ones(n, int)]

        oof = np.empty_like(y)
        for tr, te in StratifiedKFold(5, shuffle=True, random_state=SEED).split(Z, y):
            oof[te] = LogisticRegression(max_iter=2000, C=1.0).fit(Z[tr], y[tr]).predict(Z[te])
        ceiling = bpa(y, oof)

        P = PCA(n_components=min(N_PCA, Z.shape[0] - 1, Z.shape[1]),
                random_state=SEED).fit_transform(Z)
        acc = {
            "kmeans_full": bpa(y, KMeans(2, n_init=10, random_state=SEED).fit_predict(Z)),
            "kmeans_pca": bpa(y, KMeans(2, n_init=10, random_state=SEED).fit_predict(P)),
            "gmm_pca": bpa(y, GaussianMixture(2, random_state=SEED, n_init=3).fit_predict(P)),
            "leiden_pca": bpa(y, leiden_two_way(P)),
        }
        best = max(acc.values())
        rows.append({"cell_line": line, "drug_a": da, "drug_b": db, "n_per_arm": int(n),
                     "supervised_ceiling": ceiling, **acc,
                     "best_unsupervised": best, "gap_vs_best": ceiling - best,
                     "gap_vs_kmeans": ceiling - acc["kmeans_full"]})
        if (i + 1) % 50 == 0:
            log(f"  {i + 1}/{len(pairs)} pairs")

    df = pd.DataFrame(rows)
    df.to_csv(out / "gate2_clusterer_panel.csv", index=False)

    s = {"n_pairs": len(df), "n_lines": int(df.cell_line.nunique()), "seed": SEED}
    for c in ["supervised_ceiling", "kmeans_full", "kmeans_pca", "gmm_pca", "leiden_pca",
              "best_unsupervised", "gap_vs_best", "gap_vs_kmeans"]:
        s[c] = {"median": float(df[c].median()), "q25": float(df[c].quantile(.25)),
                "q75": float(df[c].quantile(.75)), "mean": float(df[c].mean())}
    s["frac_gap_vs_best_gt_0.05"] = float((df.gap_vs_best > 0.05).mean())
    s["frac_gap_vs_best_gt_0.10"] = float((df.gap_vs_best > 0.10).mean())
    pl = df.groupby("cell_line").gap_vs_best.median()
    s["lines_with_median_gap_gt_0.05"] = int((pl > 0.05).sum())
    s["n_lines_total"] = int(len(pl))
    (out / "gate2_clusterer_summary.json").write_text(json.dumps(s, indent=2))
    print("\n===== GATE 2, FULL CLUSTERER PANEL =====")
    print(json.dumps(s, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
