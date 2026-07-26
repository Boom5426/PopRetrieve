"""Gate 3 recomputed on DISJOINT cell sets, plus a partition-robustness check.

WHY
---
The first pass asked whether the mean-signature similarity of two drugs ranks the similarity of
their G2M-compartment responses. That statistic has a mechanical component and should not be
reported without one: the mean signature is taken over ALL cells, so it CONTAINS the G2M cells
(about 26% of them here). Part of any correlation is therefore arithmetic rather than biology.
The manuscript's tissue statistic (rho = +0.878, Fig. 5f) has the same structure, so this is a
correction that applies to the existing result too, not only to the new one.

The clean version uses disjoint cell sets: does the MAJORITY compartment's response similarity
rank the MINORITY compartment's response similarity, when the two are computed from cells that
share no members? That is also the sharper statement of Gate 3: if the bulk already tells you
what the minority does, resolving the minority buys nothing.

  x = cos( delta_G1(A),  delta_G1(B)  )     majority, G1 cells only
  y = cos( delta_G2M(A), delta_G2M(B) )     minority, G2M cells only

Each delta is referred to its own phase-matched control, so the baseline phase signature cancels
and what is compared is response, not identity.

SECOND CHECK: is the answer an artefact of using cell cycle as the partition? Cell cycle is one
axis and it is marker-derived. We therefore repeat the whole thing with a partition that is not
cell cycle and not derived from marker genes: k-means (k=2) fitted on the CONTROL cells of each
line, with treated cells assigned to the nearest control centroid. The partition is then defined
entirely by untreated cell state and is fixed before any treated cell is seen, so it cannot be
tuned to the response it is used to measure.

Numbers only; no plots. Run: python tahoe_gate3_disjoint.py --h5ad <path> --out <dir>
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
from scipy.stats import spearmanr
from sklearn.cluster import KMeans

SEED = 0
CONTROL_DRUG = "DMSO_TF"
MIN_CELLS_SUBPOP = 50
MIN_DRUGS_PER_LINE = 10


def log(m):
    print(f"[{time.strftime('%H:%M:%S')}] {m}", flush=True)


def group_means(X, keys):
    cat = pd.Categorical(keys)
    codes = cat.codes
    if (codes < 0).any():
        raise ValueError("unmapped group key")
    n = len(cat.categories)
    counts = np.bincount(codes, minlength=n).astype(np.float64)
    ind = sp.csr_matrix((np.ones(len(codes), np.float32), (codes, np.arange(len(codes)))),
                        shape=(n, X.shape[0]))
    return cat.categories, np.asarray((ind @ X).todense(), np.float64) / counts[:, None], counts.astype(int)


def pairwise_cosine(M):
    nrm = np.linalg.norm(M, axis=1, keepdims=True)
    nrm[nrm == 0] = np.nan
    Mn = M / nrm
    return Mn @ Mn.T


def gate3_for_partition(X, obs, part: pd.Series, label: str, out: Path):
    """part: per-cell label in {'A','B'} (A = majority), aligned to obs rows."""
    keep = part.isin(["A", "B"]).to_numpy()
    idx = np.flatnonzero(keep)
    o = obs.iloc[idx]
    p = part.iloc[idx]
    cats, means, counts = group_means(X[idx], o.cell_name + "||" + o.drug + "||" + p)
    pos = {k: i for i, k in enumerate(cats)}

    lines = sorted(o.cell_name.unique())
    drugs = sorted(d for d in o.drug.unique() if d != CONTROL_DRUG)
    rows, pair_rows = [], []
    rng = np.random.default_rng(SEED)
    for line in lines:
        dA, dB, ok = {}, {}, []
        for d in drugs:
            ks = {s: f"{line}||{d}||{s}" for s in ("A", "B")}
            cs = {s: f"{line}||{CONTROL_DRUG}||{s}" for s in ("A", "B")}
            if not all(k in pos for k in list(ks.values()) + list(cs.values())):
                continue
            if min(counts[pos[k]] for k in list(ks.values()) + list(cs.values())) < MIN_CELLS_SUBPOP:
                continue
            dA[d] = means[pos[ks["A"]]] - means[pos[cs["A"]]]
            dB[d] = means[pos[ks["B"]]] - means[pos[cs["B"]]]
            ok.append(d)
        if len(ok) < MIN_DRUGS_PER_LINE:
            continue
        SA = pairwise_cosine(np.vstack([dA[d] for d in ok]))
        SB = pairwise_cosine(np.vstack([dB[d] for d in ok]))
        iu = np.triu_indices(len(ok), k=1)
        x, y = SA[iu], SB[iu]
        m = np.isfinite(x) & np.isfinite(y)
        if m.sum() < 50:
            continue
        rho, pv = spearmanr(x[m], y[m])
        rows.append({"cell_line": line, "partition": label, "n_drugs": len(ok),
                     "n_pairs": int(m.sum()), "spearman_rho": float(rho), "p_value": float(pv)})
        sel = rng.choice(np.flatnonzero(m), size=min(100, int(m.sum())), replace=False)
        for s in sel:
            pair_rows.append({"cell_line": line, "partition": label,
                              "drug_a": ok[iu[0][s]], "drug_b": ok[iu[1][s]],
                              "cos_majority_response": float(x[s]),
                              "cos_minority_response": float(y[s])})
    df = pd.DataFrame(rows)
    df.to_csv(out / f"gate3_disjoint_{label}.csv", index=False)
    pd.DataFrame(pair_rows).to_csv(out / f"gate3_disjoint_{label}_pairs.csv", index=False)
    log(f"{label}: {len(df)} lines | median rho {df.spearman_rho.median():.3f}")
    return df


def control_state_partition(X, obs, rng) -> pd.Series:
    """k-means k=2 fitted on each line's CONTROL cells; treated cells assigned to nearest centroid.

    The partition is a property of untreated cell state only. It is fixed before any treated cell
    is looked at, so it cannot be tuned to the response it is later used to measure. 'A' is the
    larger control cluster.
    """
    part = pd.Series(["none"] * len(obs), index=obs.index, dtype=object)
    for line in sorted(obs.cell_name.unique()):
        ctl = np.flatnonzero(((obs.cell_name == line) & (obs.drug == CONTROL_DRUG)).to_numpy())
        trt = np.flatnonzero(((obs.cell_name == line) & (obs.drug != CONTROL_DRUG)).to_numpy())
        if len(ctl) < 2 * MIN_CELLS_SUBPOP:
            continue
        Zc = np.asarray(X[ctl].todense(), np.float32)
        km = KMeans(2, n_init=10, random_state=SEED).fit(Zc)
        lab = km.labels_
        big = 0 if (lab == 0).sum() >= (lab == 1).sum() else 1
        name = {big: "A", 1 - big: "B"}
        part.iloc[ctl] = [name[l] for l in lab]
        # assign treated cells in chunks to bound memory
        for s in range(0, len(trt), 200_000):
            sl = trt[s:s + 200_000]
            Zt = np.asarray(X[sl].todense(), np.float32)
            a = np.argmin(((Zt[:, None, :] - km.cluster_centers_[None]) ** 2).sum(-1), axis=1) \
                if False else km.predict(Zt)
            part.iloc[sl] = [name[l] for l in a]
    return part


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--h5ad", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--skip-state-partition", action="store_true")
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)

    import anndata as ad
    log(f"reading {a.h5ad}")
    ann = ad.read_h5ad(a.h5ad)
    X = ann.X
    if not sp.isspmatrix_csr(X):
        X = sp.csr_matrix(X)
    X = X.astype(np.float32)
    obs = ann.obs[["cell_name", "drug", "phase"]].astype(str).reset_index(drop=True)
    log(f"X {X.shape} nnz={X.nnz:,}")

    res = {}
    # partition 1: cell cycle, majority G1 vs minority G2M
    ph = obs.phase.map({"G1": "A", "G2M": "B"}).fillna("none")
    d1 = gate3_for_partition(X, obs, ph, "cellcycle_G1_vs_G2M", out)
    res["cellcycle"] = {"n_lines": len(d1), "median_rho": float(d1.spearman_rho.median()),
                        "min_rho": float(d1.spearman_rho.min()),
                        "max_rho": float(d1.spearman_rho.max()),
                        "lines_below_0.5": int((d1.spearman_rho < 0.5).sum())}

    if not a.skip_state_partition:
        log("building control-state partition (k-means on control cells per line)")
        rng = np.random.default_rng(SEED)
        st = control_state_partition(X, obs, rng)
        log(f"control-state partition sizes: {st.value_counts().to_dict()}")
        d2 = gate3_for_partition(X, obs, st, "controlstate_k2", out)
        res["controlstate"] = {"n_lines": len(d2), "median_rho": float(d2.spearman_rho.median()),
                               "min_rho": float(d2.spearman_rho.min()),
                               "max_rho": float(d2.spearman_rho.max()),
                               "lines_below_0.5": int((d2.spearman_rho < 0.5).sum())}

    (out / "gate3_disjoint_summary.json").write_text(json.dumps(res, indent=2))
    print("\n===== GATE 3, DISJOINT CELL SETS =====")
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
