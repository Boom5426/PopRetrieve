#!/usr/bin/env python3
"""Gate 2, rebuilt: is the subpopulation structure UNRECOVERABLE, or merely unclustered?

WHY THIS SCRIPT EXISTS
----------------------
The original Gate-2 evidence (identifiability_phase_diagram.py, exp09_structure_diagnostics.py)
tested KMeans and Gaussian mixtures only, and concluded that real subpopulations "cannot be
reliably identified". That conclusion does not follow from that evidence. Two gaps:

  1. NO NON-CENTROID METHOD. KMeans and GMM both assume compact, roughly isotropic, roughly
     equal-mass clusters. Single-cell structure routinely violates all three. Graph-based
     (Leiden) and density-based (HDBSCAN) methods are the field's actual defaults and were
     never run. "Centroid clustering failed" is not "the structure is not there".

  2. NO UPPER BOUND. Without a supervised probe there is no way to separate
        (a) the information is absent from the representation, from
        (b) the information is present and unsupervised methods cannot find it.
     These have opposite implications. Under (a) single-cell resolution cannot pay off no
     matter what a method does. Under (b) it can, and the bottleneck is the unsupervised
     ASSIGNMENT step, which is a solvable problem rather than an information ceiling.

The supervised linear probe is the CEILING: it is handed the true source labels, and its
held-out accuracy is the most any downstream method could extract from this representation
about this partition. If the ceiling is low, Gate 2 stands as an information limit. If the
ceiling is high while unsupervised recovery stays near zero, Gate 2 must be restated.

TWO METHODOLOGICAL POINTS, both of which change the answer if got wrong
----------------------------------------------------------------------
* THE REPRESENTATION MUST BE FIT INSIDE THE FOLD. PCA does not see labels, so fitting it on
  all cells cannot leak label information; but it does see the test cells' covariance, and a
  reviewer is right to object. Every supervised number here therefore fits PCA on the TRAINING
  cells only and projects the test cells through it. The unsupervised methods are given the
  easier, transductive representation (PCA on the full mixture), because that is what an
  unsupervised pipeline would actually have.

  CORRECTION. This file previously claimed the resulting bias runs AGAINST the conclusion we
  reach. It runs FOR it. The conclusion is that the GAP (ceiling minus best unsupervised) is
  SMALL, hence "informational, not algorithmic". Inflating the unsupervised arm and deflating
  the supervised arm SHRINKS the gap, which is the direction that supports the conclusion. The
  gap reported here is therefore an UNDERESTIMATE, and reading it as a conservative bound was
  an error. analysis/natural/gate2_drug_response.py recomputes the ceiling under the MATCHED
  representation (the same transductive PCA the clusterers get, which leaks no labels because
  PCA never sees them); that matched gap is the one to trust.

* ARI AND AUC ARE NOT COMPARABLE. ARI punishes a 68%-accurate binary partition far harder than
  accuracy does, so "probe ARI 0.12 versus GMM ARI 0.10" understates the gap enormously while
  "probe AUC 0.75 versus GMM ARI 0.10" compares two different quantities. We therefore convert
  every clustering to its BEST-PERMUTATION ACCURACY against the true labels, which is the same
  unit as the probe's accuracy and is generous to the clusterer (it gets the label matching for
  free, and for k>2 each cluster is assigned its majority class, which is generous again).

DESIGN
------
K562, 10 uM, HDAC-target cells versus JAK-target cells: a known bimodal mixture. Separation is
scaled by s using a transform fit ONCE on the full source populations, never on the sampled
cells (the fix identifiability_phase_diagram.py already carries). s = 1.0 is the real data.

    PYTHONPATH=src python analysis/identifiability/gate2_supervised_upper_bound.py
"""
from pathlib import Path as _P
REPO = _P(__file__).resolve().parents[2]
import sys
sys.path.insert(0, str(REPO / "src"))

import json
import time
import warnings

import numpy as np
import pandas as pd
import torch
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import adjusted_rand_score, roc_auc_score, accuracy_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

import hdbscan
import scanpy as sc
import anndata as ad

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

DATA_PROC = REPO / "data" / "processed"
OUT = REPO / "results" / "upgrade"

SEPS = [1.0, 1.5, 2.0, 3.0, 5.0, 8.0]     # real data sits at s = 1.0
BUDGETS = [50, 100, 200, 400]
SEEDS = list(range(10))
N_PCA = 30
UNSUP = ["kmeans_k2", "gmm_k2", "leiden", "hdbscan"]


def best_permutation_accuracy(y, lab):
    """Accuracy of a clustering, giving it the label matching for free.

    Each cluster is assigned its majority true class. For k=2 this is the best of the two
    permutations; for k>2 it is strictly generous (an over-partitioning method is never
    penalised for splitting a true class). HDBSCAN noise (-1) is its own cluster and is
    likewise assigned its majority class, which is generous to HDBSCAN.
    """
    acc = 0
    for c in set(lab):
        m = lab == c
        if m.sum():
            acc += np.bincount(y[m], minlength=2).max()
    return acc / len(y)


def unsupervised(X, y, seed):
    """Every unsupervised method sees the SAME transductive PCA (the easier setting)."""
    out = {}
    km = KMeans(n_clusters=2, n_init=10, random_state=seed).fit_predict(X)
    out["kmeans_k2"] = (adjusted_rand_score(y, km), best_permutation_accuracy(y, km), 2)

    gm = GaussianMixture(n_components=2, covariance_type="full", random_state=seed,
                         n_init=3).fit(X).predict(X)
    out["gmm_k2"] = (adjusted_rand_score(y, gm), best_permutation_accuracy(y, gm), 2)

    a = ad.AnnData(X.astype(np.float32))
    sc.pp.neighbors(a, n_neighbors=15, use_rep="X", random_state=seed)
    sc.tl.leiden(a, resolution=1.0, random_state=seed, flavor="igraph",
                 n_iterations=2, directed=False)
    lb = a.obs["leiden"].astype(int).values
    out["leiden"] = (adjusted_rand_score(y, lb), best_permutation_accuracy(y, lb),
                     int(len(set(lb))))

    hl = hdbscan.HDBSCAN(min_cluster_size=max(10, len(X) // 20)).fit_predict(X)
    out["hdbscan"] = (adjusted_rand_score(y, hl), best_permutation_accuracy(y, hl),
                      int(len(set(hl) - {-1})))
    return out


def _classifiers(seed):
    """A LINEAR probe alone is a lower bound on the ceiling, not the ceiling.

    If the true boundary between the two sources is nonlinear, logistic regression will
    underperform and we would mistake its limit for an information limit, which would let us
    conclude "the structure is not there" from what is really "our classifier is too weak".
    The ceiling is therefore the MAXIMUM over a linear, a kernel-free nonlinear ensemble, and
    a purely local method. If all three top out together, the ceiling is real.
    """
    return {
        "linear": LogisticRegression(max_iter=5000, C=1.0, random_state=seed),
        "forest": RandomForestClassifier(n_estimators=300, random_state=seed, n_jobs=4),
        "knn": KNeighborsClassifier(n_neighbors=15),
    }


def supervised_ceiling(Xraw, y, seed, n_pca):
    """The CEILING. PCA is fit inside the training fold; test cells are only projected."""
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    names = list(_classifiers(0))
    pred = {m: np.zeros(len(y), dtype=int) for m in names}
    prob = {m: np.zeros(len(y), dtype=float) for m in names}
    for tr, te in skf.split(Xraw, y):
        k = min(n_pca, len(tr) - 1, Xraw.shape[1])
        p = PCA(n_components=k, random_state=seed).fit(Xraw[tr])       # TRAIN ONLY
        s = StandardScaler().fit(p.transform(Xraw[tr]))
        Ztr, Zte = s.transform(p.transform(Xraw[tr])), s.transform(p.transform(Xraw[te]))
        for m, clf in _classifiers(seed).items():
            clf.fit(Ztr, y[tr])
            pred[m][te] = clf.predict(Zte)
            prob[m][te] = clf.predict_proba(Zte)[:, 1]
    out = {}
    for m in names:
        out[f"probe_{m}_acc"] = accuracy_score(y, pred[m])
        out[f"probe_{m}_auc"] = roc_auc_score(y, prob[m])
        out[f"probe_{m}_ari"] = adjusted_rand_score(y, pred[m])
    # the ceiling is the best any supervised learner achieved, per run
    out["probe_acc"] = max(out[f"probe_{m}_acc"] for m in names)
    out["probe_auc"] = max(out[f"probe_{m}_auc"] for m in names)
    out["probe_ari"] = max(out[f"probe_{m}_ari"] for m in names)
    return out


def main() -> None:
    t0 = time.time()
    d = torch.load(DATA_PROC / "sciplex3_all.pt", weights_only=False)
    X = d["X"]
    X = X.numpy() if hasattr(X, "numpy") else np.asarray(X)
    obs = d["obs"].reset_index(drop=True)

    base = ((obs["cell_line"] == "K562") & (obs["dose_value"] == 10000.0)
            & (~obs["is_control"].astype(bool)))
    tgt = obs["target"].astype(str).str.upper()
    Hidx = np.where((base & tgt.str.contains("HDAC")).values)[0]
    Jidx = np.where((base & tgt.str.contains("JAK")).values)[0]
    print(f"n_HDAC={len(Hidx)} n_JAK={len(Jidx)}", flush=True)

    XH = X[Hidx].astype(np.float64)
    XJ = X[Jidx].astype(np.float64)
    G_ALL = np.vstack([XH, XJ]).mean(0)
    CH, CJ = XH.mean(0), XJ.mean(0)

    maxn = min(len(XH), len(XJ))
    budgets = [b for b in BUDGETS if b <= maxn]
    print(f"effective budgets: {budgets} (max {maxn} per source)", flush=True)

    rows = []
    for s in SEPS:
        for n in budgets:
            for seed in SEEDS:
                rng = np.random.RandomState(1000 + seed)
                H = XH[rng.choice(len(XH), n, replace=False)] + (s - 1.0) * (CH - G_ALL)
                J = XJ[rng.choice(len(XJ), n, replace=False)] + (s - 1.0) * (CJ - G_ALL)
                Xm = np.vstack([H, J])
                y = np.array([0] * n + [1] * n)

                Z = PCA(n_components=min(N_PCA, 2 * n - 1, Xm.shape[1]),
                        random_state=seed).fit_transform(Xm)     # transductive: unsup only

                rec = {"separation_scale": s, "cells_per_source": n, "seed": seed,
                       "n_total": 2 * n}
                for m, (ari, acc, k) in unsupervised(Z, y, seed).items():
                    rec[f"ari_{m}"] = float(ari)
                    rec[f"acc_{m}"] = float(acc)
                    rec[f"k_{m}"] = int(k)
                rec.update({k: float(v)
                            for k, v in supervised_ceiling(Xm, y, seed, N_PCA).items()})
                rows.append(rec)
        print(f"  sep={s} done  t={time.time() - t0:.0f}s", flush=True)

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "gate2_supervised_upper_bound.csv", index=False)

    real = df[df.separation_scale == 1.0]
    res = {"n_runs_real": int(len(real)), "budgets": budgets, "n_seeds": len(SEEDS),
           "note": "unsupervised methods get transductive PCA (easier); the supervised probe "
                   "fits PCA inside the training fold only. This SHRINKS the gap and therefore "
                   "biases the comparison TOWARD the 'informational limit' conclusion, not "
                   "against it. The gap here is an underestimate; see "
                   "analysis/natural/gate2_drug_response.py for the matched-representation gap.",
           "real": {}}

    print(f"\n{'='*80}\nREAL DATA (separation scale = 1.0), median over {len(real)} runs")
    print("Accuracy is the common unit. Clusterers get best-permutation matching for free.")
    print(f"\n{'method':26s} {'median acc':>11s} {'median ARI':>11s} {'median k':>9s}")
    print("-" * 80)
    for m in UNSUP:
        a, ar = float(real[f"acc_{m}"].median()), float(real[f"ari_{m}"].median())
        kk = float(real[f"k_{m}"].median())
        res["real"][m] = {"acc_median": a, "ari_median": ar, "ari_max": float(real[f"ari_{m}"].max()),
                          "k_median": kk}
        print(f"  {m:24s} {a:>11.4f} {ar:>+11.4f} {kk:>9.1f}")
    print("-" * 80)
    for m in ["linear", "forest", "knn"]:
        a = float(real[f"probe_{m}_acc"].median())
        u = float(real[f"probe_{m}_auc"].median())
        res["real"][f"probe_{m}"] = {"acc_median": a, "auc_median": u}
        print(f"  {'SUPERVISED ' + m:24s} {a:>11.4f} {'':>11s}   (AUC {u:.4f})")
    pa, pu, pr = (float(real.probe_acc.median()), float(real.probe_auc.median()),
                  float(real.probe_ari.median()))
    res["real"]["supervised_ceiling"] = {"acc_median": pa, "auc_median": pu, "ari_median": pr,
                                         "acc_max": float(real.probe_acc.max())}
    print(f"  {'CEILING (best of 3)':24s} {pa:>11.4f} {pr:>+11.4f}   (AUC {pu:.4f})")

    best_acc = max(res["real"][m]["acc_median"] for m in UNSUP)
    best_ari = max(res["real"][m]["ari_median"] for m in UNSUP)
    res["real"]["best_unsupervised_acc_median"] = best_acc
    res["real"]["best_unsupervised_ari_median"] = best_ari
    res["real"]["chance_acc"] = 0.5

    # THE COMPARISON THAT DECIDES GATE 2 is ceiling-versus-best-unsupervised, NOT
    # ceiling-versus-chance. An AUC of 0.75 sounds high against chance, but if unsupervised
    # clustering already reaches the same accuracy then nothing is being missed by the
    # assignment step and the limit is informational. Conversely a large gap would mean the
    # information is present and only the unsupervised step fails, which is a different paper.
    gap = pa - best_acc
    res["gap_supervised_minus_best_unsupervised_acc"] = float(gap)
    res["verdict"] = (
        "INFORMATION LIMIT: unsupervised clustering already reaches the supervised ceiling "
        f"(gap {gap:+.3f} accuracy). The subpopulations overlap so heavily that even a "
        "label-supervised classifier cannot separate them; the partition is barely present, "
        "and the clustering step is extracting nearly all of what exists. Gate 2 stands, and "
        "it is a limit on the information, not on the algorithm."
        if gap < 0.05 else
        "ALGORITHMIC LIMIT: the supervised ceiling is well above every unsupervised method "
        f"(gap {gap:+.3f} accuracy). The information IS present and recoverable with labels; "
        "the unsupervised ASSIGNMENT step is the bottleneck. Gate 2 must be restated as a "
        "limit on unsupervised assignment, not on information content.")
    print(f"\n  chance accuracy              : 0.500")
    print(f"  best unsupervised accuracy   : {best_acc:.4f}  (ARI {best_ari:+.4f})")
    print(f"  supervised CEILING accuracy  : {pa:.4f}  (AUC {pu:.4f})")
    print(f"  gap (ceiling - unsupervised) : {gap:+.4f}   <-- this is the decisive quantity")
    print(f"\nVERDICT: {res['verdict']}")

    print(f"\n{'='*80}\nSEPARATION LADDER (median accuracy across budgets and seeds)")
    print(f"{chr(115)+chr(101)+chr(112):>5s} " + " ".join(f"{m:>10s}" for m in UNSUP) + f" {chr(99)+chr(101)+chr(105)+chr(108):>10s}")
    res["ladder"] = {}
    for s, g in df.groupby("separation_scale"):
        v = {m: float(g[f"acc_{m}"].median()) for m in UNSUP}
        v["probe_acc"] = float(g.probe_acc.median())
        v["probe_auc"] = float(g.probe_auc.median())
        res["ladder"][str(s)] = v
        print(f"{s:>5.1f} " + " ".join(f"{v[m]:>10.3f}" for m in UNSUP)
              + f" {v['probe_acc']:>10.3f}")

    json.dump(res, open(OUT / "gate2_supervised_upper_bound.json", "w"), indent=2)
    print(f"\nwrote {OUT/'gate2_supervised_upper_bound.csv'} and .json  ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
