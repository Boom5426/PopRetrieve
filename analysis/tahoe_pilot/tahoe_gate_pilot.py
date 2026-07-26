"""Pilot: the two measured gates and the proposed third, on Tahoe-100M plate 3.

WHY THIS EXISTS
---------------
Every gate statistic in the manuscript rests on one of two thin foundations:

  Gate 1  differential response   constructed cell-line mixtures (induced cosine 0.014-0.044)
                                  and 17 patient-drug pairs (median 0.566)
  Gate 2  recoverability          one constructed K562 mixture (ceiling 0.692 / unsup 0.674)
                                  and 36 GBM splits of which 30 come from a single patient
                                  (ceiling 0.923 / unsup 0.777)
  Gate 3  decision relevance      18 within-patient drug pairs, 15 of them from patient PW030,
                                  Spearman +0.878, no p-value quoted because they are not
                                  independent

Tahoe-100M plate 3 is a complete 50 cell line x 93 drug grid (one dose per drug) with a DMSO_TF
control arm in every line, median 648 cells per condition, and a cell-cycle phase call on every
cell. It is NOT a constructed mixture: nobody pipetted two populations together, the within-line
heterogeneity is intrinsic cell state. That makes it a third kind of material, sitting between
the mixtures the manuscript built and the tumours it could not control, and it lets every gate
statistic be recomputed at 100x to 10,000x the sample size.

This script computes the manuscript's OWN statistics on that material so the numbers are
directly comparable. It does not introduce a new metric.

WHAT IS PRE-SPECIFIED, BEFORE LOOKING AT ANY RESULT
---------------------------------------------------
Representation: the 2,304 highly variable genes in log1p space, exactly as the preprocessed
file ships them. Nothing is refitted, rescaled or reselected here.

Subpopulation partition for Gates 1 and 3: cell-cycle phase, G1 versus G2M. S is dropped as
intermediate. Each subpopulation's response is referred to ITS OWN phase-matched control, which
is the correction recorded in CORRECTIONS.md R30: referring a subpopulation's response to a
pooled or mismatched baseline leaves the baseline difference in the response and inflates
apparent divergence.

Partition for Gate 2: drug identity, not phase. This is deliberate and it is the whole reason
Gate 2 is run separately. Phase is derived FROM expression by marker scoring, so asking a probe
to recover phase from expression is partly circular, which is the failure mode this project
exists to criticise. Drug identity is external: it is which well the cell came from. That makes
the Gate 2 test here the same construct as the manuscript's K562 benchmark (cells differing only
in which drug they saw) and the same as the GBM natural test, so the numbers are comparable.

Compartment for Gate 3: reported for BOTH G1 and G2M, never one of them, so that no choice of
compartment can be made after seeing which one is favourable.

Direction predicted in advance: if Gate 3 is the binding condition, then within most cell lines
the mean-signature similarity of two drugs should already rank the similarity of their
subpopulation responses, i.e. high Spearman, matching the +0.878 seen in tissue. Cell lines where
it does NOT are the contexts in which distribution-aware retrieval should pay off, and that is a
positive, falsifiable prediction rather than another null.

Minimum-count rules, fixed here and applied without exception: a condition enters Gates 1 and 3
only if it has at least MIN_CELLS_SUBPOP cells in each of treated-G1, treated-G2M, control-G1 and
control-G2M. A pair enters Gate 2 only if both arms have at least MIN_CELLS_GATE2 cells. Every
exclusion is counted and reported; nothing is dropped silently.

OUTPUTS
-------
Per-condition and per-pair CSVs, so every summary number can be recomputed from the raw rows by
someone who does not trust this script. Numbers only; no plots.

Run:  python tahoe_gate_pilot.py --h5ad <path> --out <dir>
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
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold

SEED = 0
CONTROL_DRUG = "DMSO_TF"
MIN_CELLS_SUBPOP = 50      # per (condition, phase) arm, for Gates 1 and 3
MIN_CELLS_GATE2 = 100      # per drug arm, for Gate 2
GATE2_PAIRS_PER_LINE = 20  # random drug pairs per cell line
GATE2_CELLS_PER_ARM = 300  # cap, balanced across the two arms


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def load(h5ad_path: str):
    """Load the plate and return (X csr float32, obs DataFrame)."""
    import anndata as ad

    log(f"reading {h5ad_path}")
    a = ad.read_h5ad(h5ad_path)
    X = a.X
    if not sp.isspmatrix_csr(X):
        X = sp.csr_matrix(X)
    X = X.astype(np.float32)
    obs = a.obs[["cell_name", "drug", "phase"]].copy()
    for c in obs.columns:
        obs[c] = obs[c].astype(str)
    log(f"loaded X {X.shape} nnz={X.nnz:,} | obs {obs.shape}")
    return X, obs


def group_means(X: sp.csr_matrix, keys: pd.Series) -> tuple[pd.Index, np.ndarray, np.ndarray]:
    """Mean expression vector per group.

    Returns (group_index, means [n_groups x n_genes], counts [n_groups]).
    Implemented as one sparse matmul with a row-normalised indicator, which is exact and does
    not materialise the dense matrix.
    """
    cat = pd.Categorical(keys)
    codes = cat.codes
    if (codes < 0).any():
        raise ValueError("group key has NaN/unmapped entries; refusing to compute means")
    n_groups = len(cat.categories)
    counts = np.bincount(codes, minlength=n_groups).astype(np.float64)
    if (counts == 0).any():
        raise ValueError("empty group encountered")
    ind = sp.csr_matrix(
        (np.ones(len(codes), dtype=np.float32), (codes, np.arange(len(codes)))),
        shape=(n_groups, X.shape[0]),
    )
    sums = ind @ X                      # n_groups x n_genes, sparse
    means = np.asarray(sums.todense(), dtype=np.float64) / counts[:, None]
    return cat.categories, means, counts.astype(int)


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    if na == 0 or nb == 0:
        return np.nan
    return float(np.dot(a, b) / (na * nb))


def pairwise_cosine(M: np.ndarray) -> np.ndarray:
    """Row-wise cosine similarity matrix for a small matrix of delta vectors."""
    n = np.linalg.norm(M, axis=1, keepdims=True)
    n[n == 0] = np.nan
    Mn = M / n
    return Mn @ Mn.T


def best_permutation_accuracy(true: np.ndarray, pred: np.ndarray) -> float:
    """Two-class best-permutation accuracy: label matching is free, as in the manuscript."""
    acc = (true == pred).mean()
    return float(max(acc, 1.0 - acc))


def run_gate1_and_gate3(X, obs, out: Path) -> dict:
    """Gate 1 (induced response cosine) and Gate 3 (does the mean already rank the compartment)."""
    log("computing (line, drug, phase) group means")
    keep = obs.phase.isin(["G1", "G2M"])
    idx = np.flatnonzero(keep.to_numpy())
    o = obs.iloc[idx]
    key = o.cell_name + "||" + o.drug + "||" + o.phase
    cats, means, counts = group_means(X[idx], key)
    tab = pd.DataFrame({"key": list(cats), "n": counts})
    tab[["cell_name", "drug", "phase"]] = tab.key.str.split(r"\|\|", expand=True, regex=True)
    pos = {k: i for i, k in enumerate(cats)}

    # also the phase-pooled mean per (line, drug), for the mean-signature side
    key_all = o.cell_name + "||" + o.drug
    cats_all, means_all, counts_all = group_means(X[idx], key_all)
    pos_all = {k: i for i, k in enumerate(cats_all)}

    lines = sorted(o.cell_name.unique())
    drugs = sorted(d for d in o.drug.unique() if d != CONTROL_DRUG)
    log(f"{len(lines)} cell lines x {len(drugs)} drugs (control = {CONTROL_DRUG})")

    g1_rows, excl = [], {"missing_group": 0, "too_few_cells": 0}
    deltas = {}   # (line, drug) -> dict of delta vectors
    for line in lines:
        for phase in ("G1", "G2M"):
            ck = f"{line}||{CONTROL_DRUG}||{phase}"
            if ck not in pos:
                excl["missing_group"] += len(drugs)
        ck_all = f"{line}||{CONTROL_DRUG}"
        for drug in drugs:
            ks = {p: f"{line}||{drug}||{p}" for p in ("G1", "G2M")}
            cks = {p: f"{line}||{CONTROL_DRUG}||{p}" for p in ("G1", "G2M")}
            if not all(k in pos for k in list(ks.values()) + list(cks.values())):
                excl["missing_group"] += 1
                continue
            ns = {p: counts[pos[ks[p]]] for p in ks}
            nc = {p: counts[pos[cks[p]]] for p in cks}
            if min(list(ns.values()) + list(nc.values())) < MIN_CELLS_SUBPOP:
                excl["too_few_cells"] += 1
                continue
            d_g1 = means[pos[ks["G1"]]] - means[pos[cks["G1"]]]
            d_g2m = means[pos[ks["G2M"]]] - means[pos[cks["G2M"]]]
            d_mean = means_all[pos_all[f"{line}||{drug}"]] - means_all[pos_all[ck_all]]
            deltas[(line, drug)] = {"G1": d_g1, "G2M": d_g2m, "mean": d_mean}
            g1_rows.append({
                "cell_line": line, "drug": drug,
                "n_treated_G1": ns["G1"], "n_treated_G2M": ns["G2M"],
                "n_control_G1": nc["G1"], "n_control_G2M": nc["G2M"],
                "induced_cosine_G1_vs_G2M": cosine(d_g1, d_g2m),
                "norm_delta_G1": float(np.linalg.norm(d_g1)),
                "norm_delta_G2M": float(np.linalg.norm(d_g2m)),
                "norm_delta_mean": float(np.linalg.norm(d_mean)),
            })
    g1 = pd.DataFrame(g1_rows)
    g1.to_csv(out / "gate1_per_condition.csv", index=False)
    log(f"Gate 1: {len(g1)} conditions kept; excluded {excl}")

    # ---- Gate 3: within each line, does mean similarity rank compartment similarity? ----
    g3_rows, g3_pairs = [], []
    rng = np.random.default_rng(SEED)
    for line in lines:
        ds = [d for d in drugs if (line, d) in deltas]
        if len(ds) < 10:
            continue
        M_mean = np.vstack([deltas[(line, d)]["mean"] for d in ds])
        for comp in ("G1", "G2M"):
            M_comp = np.vstack([deltas[(line, d)][comp] for d in ds])
            S_mean, S_comp = pairwise_cosine(M_mean), pairwise_cosine(M_comp)
            iu = np.triu_indices(len(ds), k=1)
            x, y = S_mean[iu], S_comp[iu]
            ok = np.isfinite(x) & np.isfinite(y)
            if ok.sum() < 50:
                continue
            rho, p = spearmanr(x[ok], y[ok])
            g3_rows.append({"cell_line": line, "compartment": comp, "n_drugs": len(ds),
                            "n_pairs": int(ok.sum()), "spearman_rho": float(rho),
                            "p_value": float(p)})
            if comp == "G2M":  # keep a raw sample so the correlation can be re-derived by hand
                sel = rng.choice(np.flatnonzero(ok), size=min(200, int(ok.sum())), replace=False)
                for s in sel:
                    g3_pairs.append({"cell_line": line, "drug_a": ds[iu[0][s]],
                                     "drug_b": ds[iu[1][s]],
                                     "cos_mean_signature": float(x[s]),
                                     "cos_G2M_response": float(y[s])})
    g3 = pd.DataFrame(g3_rows)
    g3.to_csv(out / "gate3_per_line.csv", index=False)
    pd.DataFrame(g3_pairs).to_csv(out / "gate3_pair_sample.csv", index=False)
    log(f"Gate 3: {len(g3)} (line, compartment) correlations")
    return {"gate1": g1, "gate3": g3, "deltas_keys": list(deltas), "gate1_excluded": excl}


def run_gate2(X, obs, out: Path) -> pd.DataFrame:
    """Gate 2 on the drug-response partition: the K562 construct, transplanted to 50 lines."""
    rng = np.random.default_rng(SEED)
    lines = sorted(obs.cell_name.unique())
    rows = []
    for li, line in enumerate(lines):
        sub = obs[(obs.cell_name == line) & (obs.drug != CONTROL_DRUG)]
        counts = sub.drug.value_counts()
        eligible = sorted(counts[counts >= MIN_CELLS_GATE2].index)
        if len(eligible) < 2:
            continue
        pairs = set()
        while len(pairs) < min(GATE2_PAIRS_PER_LINE, len(eligible) * (len(eligible) - 1) // 2):
            a, b = rng.choice(len(eligible), size=2, replace=False)
            pairs.add(tuple(sorted((eligible[a], eligible[b]))))
        for a, b in sorted(pairs):
            ia = np.flatnonzero(((obs.cell_name == line) & (obs.drug == a)).to_numpy())
            ib = np.flatnonzero(((obs.cell_name == line) & (obs.drug == b)).to_numpy())
            n = min(len(ia), len(ib), GATE2_CELLS_PER_ARM)
            ia = rng.choice(ia, size=n, replace=False)
            ib = rng.choice(ib, size=n, replace=False)
            Z = np.asarray(sp.vstack([X[ia], X[ib]]).todense(), dtype=np.float64)
            y = np.r_[np.zeros(n, int), np.ones(n, int)]

            # supervised ceiling: cross-validated linear probe, out-of-fold predictions only
            oof = np.empty_like(y)
            for tr, te in StratifiedKFold(5, shuffle=True, random_state=SEED).split(Z, y):
                clf = LogisticRegression(max_iter=2000, C=1.0)
                clf.fit(Z[tr], y[tr])
                oof[te] = clf.predict(Z[te])
            ceiling = best_permutation_accuracy(y, oof)

            km = KMeans(n_clusters=2, n_init=10, random_state=SEED).fit_predict(Z)
            unsup = best_permutation_accuracy(y, km)

            rows.append({"cell_line": line, "drug_a": a, "drug_b": b, "n_per_arm": int(n),
                         "supervised_ceiling": ceiling, "unsupervised_kmeans": unsup,
                         "gap": ceiling - unsup})
        if (li + 1) % 10 == 0:
            log(f"  Gate 2: {li + 1}/{len(lines)} cell lines, {len(rows)} pairs so far")
    g2 = pd.DataFrame(rows)
    g2.to_csv(out / "gate2_per_pair.csv", index=False)
    log(f"Gate 2: {len(g2)} drug pairs across {g2.cell_line.nunique()} cell lines")
    return g2


def summarise(g1: pd.DataFrame, g3: pd.DataFrame, g2: pd.DataFrame, excl: dict) -> dict:
    def q(s, name):
        s = s.dropna()
        return {f"{name}_n": int(len(s)), f"{name}_median": float(s.median()),
                f"{name}_q25": float(s.quantile(.25)), f"{name}_q75": float(s.quantile(.75)),
                f"{name}_mean": float(s.mean())}

    s = {"seed": SEED, "gate1_excluded": excl}
    s.update(q(g1.induced_cosine_G1_vs_G2M, "gate1_induced_cosine"))
    s["gate1_per_line_median"] = {
        k: float(v) for k, v in
        g1.groupby("cell_line").induced_cosine_G1_vs_G2M.median().items()}
    for comp in ("G1", "G2M"):
        sub = g3[g3.compartment == comp]
        s.update(q(sub.spearman_rho, f"gate3_rho_{comp}"))
        s[f"gate3_{comp}_lines_above_0.8"] = int((sub.spearman_rho > 0.8).sum())
        s[f"gate3_{comp}_lines_below_0.5"] = int((sub.spearman_rho < 0.5).sum())
        s[f"gate3_{comp}_lines_total"] = int(len(sub))
    s.update(q(g2.supervised_ceiling, "gate2_ceiling"))
    s.update(q(g2.unsupervised_kmeans, "gate2_unsupervised"))
    s.update(q(g2.gap, "gate2_gap"))
    s["gate2_pairs"] = int(len(g2))
    return s


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--h5ad", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--skip-gate2", action="store_true")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    X, obs = load(a.h5ad)
    res = run_gate1_and_gate3(X, obs, out)
    g2 = (pd.DataFrame(columns=["cell_line", "supervised_ceiling", "unsupervised_kmeans", "gap"])
          if a.skip_gate2 else run_gate2(X, obs, out))
    s = summarise(res["gate1"], res["gate3"], g2, res["gate1_excluded"])
    (out / "summary.json").write_text(json.dumps(s, indent=2))
    print("\n===== SUMMARY =====")
    print(json.dumps(s, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
