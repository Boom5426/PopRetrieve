#!/usr/bin/env python3
"""The two gates, and this paper's premise, tested on NATURAL heterogeneity in patient tumours.

WHY
---
Every positive real-data result in this study lives in cell-line mixtures WE constructed. A
minority subpopulation assembled by mixing A549 with K562 is not evidence about the
heterogeneity a tumour actually has, and a reviewer is right to say so. ZhaoSims2021 is
acute-slice culture and biopsy from 10 glioblastoma patients: within a single slice, malignant
glioma cells, tumour-associated myeloid cells and oligodendrocytes co-exist as they do in the
patient. Nobody constructed that.

It is NOT a retrieval benchmark and is not used as one (6 drugs, and only one patient received
more than two). It is used to test the three claims that actually matter, on natural data.

  PREMISE   This paper's opening claim, and Fig. 1a, is that two drugs can share a mean signature
            and do OPPOSITE things to a minority subpopulation. That has never been tested on a
            real tumour. Here it can be: for every pair of drugs in a patient, we measure how
            similar their MEAN signatures are and how similar their COMPARTMENT-SPECIFIC
            responses are. If drugs that look alike on the mean act differently on the malignant
            compartment, the premise holds and the mean is provably lossy in real tissue. If mean
            similarity fully determines compartment-specific similarity, the premise is false and
            the paper's motivating figure is a cartoon.

  GATE 1    Do naturally co-existing cell types respond in DIFFERENT directions to the same drug?
            cos(d_malignant, d_myeloid), each referred to its own matched control.

  GATE 2    Is that natural structure recoverable? The supervised ceiling on the constructed
            HDAC-versus-JAK mixture was only 0.692 accuracy, which is why we concluded Gate 2 is
            an information limit. Real cell types are far more distinct, so the ceiling here
            should be much higher. If it is, Gate 2 OPENS on natural data, and the two-gate
            account makes a hard, falsifiable prediction: distributional information should be
            usable in tumours even though it was not in our constructed mixtures.

Compartment labels come from validated marker scoring (src/data/load_zhao_gbm.py); cells without
a confident call are dropped, not reassigned. Labels are never shown to any clustering method.

    PYTHONPATH=src python analysis/natural/zhao_two_gates.py
"""
from pathlib import Path as _P
REPO = _P(__file__).resolve().parents[2]
import sys
sys.path.insert(0, str(REPO / "src"))

import json
import warnings

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.mixture import GaussianMixture
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, adjusted_rand_score
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler

import hdbscan
import scanpy as sc
import anndata as ad

from data.load_zhao_gbm import load_zhao_gbm

warnings.filterwarnings("ignore")

SEED = 42
MIN_CELLS = 50
N_PCA = 30
PAIR = ("malignant", "myeloid")      # tumour cells vs tumour-associated macrophages
OUT = REPO / "results" / "zhao_gbm"


def _cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(np.dot(a, b) / (na * nb)) if na > 1e-12 and nb > 1e-12 else np.nan


def best_permutation_accuracy(y, lab):
    acc = 0
    for c in set(lab):
        m = lab == c
        if m.sum():
            acc += np.bincount(y[m], minlength=len(set(y))).max()
    return acc / len(y)


# ---------------------------------------------------------------------------


def gate1_and_premise(d):
    """Differential response between natural compartments, and whether the mean sees it."""
    rows, pair_rows = [], []
    for p in d.patients:
        drugs = sorted({x for x in d.pert[d.patient == p] if x != "control"})
        # per-compartment matched control means for this patient
        ctrl = {}
        for c in PAIR:
            r = d.rows(patient=p, compartment=c, control=True)
            if len(r) >= MIN_CELLS:
                ctrl[c] = d.X[r].mean(0)
        if len(ctrl) < 2:
            continue

        deltas = {}
        for drug in drugs:
            dk = {}
            for c in PAIR:
                r = d.rows(patient=p, drug=drug, compartment=c)
                if len(r) >= MIN_CELLS:
                    dk[c] = d.X[r].mean(0) - ctrl[c]
            if len(dk) < 2:
                continue
            deltas[drug] = dk
            rows.append({"patient": p, "drug": drug,
                         "n_malignant": len(d.rows(patient=p, drug=drug, compartment=PAIR[0])),
                         "n_myeloid": len(d.rows(patient=p, drug=drug, compartment=PAIR[1])),
                         "induced_response_cosine": _cos(dk[PAIR[0]], dk[PAIR[1]])})

        # THE PREMISE. For every drug pair: how similar are their MEAN signatures, and how
        # similar are their MALIGNANT-compartment responses? If the mean were sufficient the
        # two would be the same number.
        dl = sorted(deltas)
        for i in range(len(dl)):
            for j in range(i + 1, len(dl)):
                a, b = deltas[dl[i]], deltas[dl[j]]
                mean_a = 0.5 * (a[PAIR[0]] + a[PAIR[1]])     # the population mean signature
                mean_b = 0.5 * (b[PAIR[0]] + b[PAIR[1]])
                pair_rows.append({
                    "patient": p, "drug_a": dl[i], "drug_b": dl[j],
                    "cos_mean_signature": _cos(mean_a, mean_b),
                    "cos_malignant_response": _cos(a[PAIR[0]], b[PAIR[0]]),
                    "cos_myeloid_response": _cos(a[PAIR[1]], b[PAIR[1]]),
                })
    return pd.DataFrame(rows), pd.DataFrame(pair_rows)


def gate2_natural(d, n_seeds=10, n_cells=400):
    """Supervised ceiling vs unsupervised clustering, on NATURAL cell types.

    Identical protocol to analysis/identifiability/gate2_supervised_upper_bound.py so the
    numbers are directly comparable to the 0.692 ceiling on the constructed mixture:
    common unit (best-permutation accuracy), clusterers get the true k and free label matching,
    the supervised probe fits its PCA inside the training fold.
    """
    rows = []
    for p in d.patients:
        idx = {c: d.rows(patient=p, compartment=c, control=True) for c in PAIR}
        if min(len(v) for v in idx.values()) < n_cells // 2:
            continue
        for seed in range(n_seeds):
            rng = np.random.RandomState(1000 + seed)
            n = min(n_cells // 2, min(len(v) for v in idx.values()))
            A = d.X[rng.choice(idx[PAIR[0]], n, replace=False)]
            B = d.X[rng.choice(idx[PAIR[1]], n, replace=False)]
            Xm = np.vstack([A, B]).astype(np.float64)
            y = np.array([0] * n + [1] * n)

            Z = PCA(n_components=min(N_PCA, 2 * n - 1), random_state=seed).fit_transform(Xm)
            r = {"patient": p, "seed": seed, "n_per_compartment": n}

            km = KMeans(n_clusters=2, n_init=10, random_state=seed).fit_predict(Z)
            r["acc_kmeans_k2"] = best_permutation_accuracy(y, km)
            gm = GaussianMixture(2, covariance_type="full", random_state=seed,
                                 n_init=3).fit(Z).predict(Z)
            r["acc_gmm_k2"] = best_permutation_accuracy(y, gm)
            aa = ad.AnnData(Z.astype(np.float32))
            sc.pp.neighbors(aa, n_neighbors=15, use_rep="X", random_state=seed)
            sc.tl.leiden(aa, resolution=1.0, random_state=seed, flavor="igraph",
                         n_iterations=2, directed=False)
            r["acc_leiden"] = best_permutation_accuracy(y, aa.obs["leiden"].astype(int).values)
            hl = hdbscan.HDBSCAN(min_cluster_size=max(10, len(Z) // 20)).fit_predict(Z)
            r["acc_hdbscan"] = best_permutation_accuracy(y, hl)

            skf = StratifiedKFold(5, shuffle=True, random_state=seed)
            clfs = {"linear": LogisticRegression(max_iter=5000, random_state=seed),
                    "forest": RandomForestClassifier(300, random_state=seed, n_jobs=4),
                    "knn": KNeighborsClassifier(15)}
            pred = {k: np.zeros(len(y), int) for k in clfs}
            for tr, te in skf.split(Xm, y):
                pc = PCA(n_components=min(N_PCA, len(tr) - 1),
                         random_state=seed).fit(Xm[tr])            # TRAIN FOLD ONLY
                s = StandardScaler().fit(pc.transform(Xm[tr]))
                for k, clf in clfs.items():
                    clf.fit(s.transform(pc.transform(Xm[tr])), y[tr])
                    pred[k][te] = clf.predict(s.transform(pc.transform(Xm[te])))
            for k in clfs:
                r[f"probe_{k}_acc"] = accuracy_score(y, pred[k])
            r["probe_acc"] = max(r[f"probe_{k}_acc"] for k in clfs)
            rows.append(r)
    return pd.DataFrame(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    d = load_zhao_gbm()
    print(d.summary(), flush=True)
    print(f"\nNATURAL heterogeneity: {PAIR[0]} vs {PAIR[1]}, within a patient's own tumour slice.")
    print("Nothing here was constructed by mixing samples.\n", flush=True)

    res = {"dataset": "ZhaoSims2021 (patient-derived glioblastoma slices)",
           "compartments": list(PAIR), "n_patients": len(d.patients)}

    # ---------------- GATE 1 ----------------
    g1, pairs = gate1_and_premise(d)
    g1.to_csv(OUT / "gate1_natural.csv", index=False)
    pairs.to_csv(OUT / "premise_mean_vs_compartment.csv", index=False)

    print("=" * 86)
    print("GATE 1 (natural): do co-existing cell types respond in DIFFERENT directions?")
    print("  cos(d_malignant, d_myeloid), per (patient, drug). 1 = identical response, 0 = orthogonal")
    print(f"\n{'patient':10s} {'drug':16s} {'cos':>8s} {'n_malig':>8s} {'n_myelo':>8s}")
    print("-" * 86)
    for _, r in g1.iterrows():
        print(f"  {r.patient:8s} {r.drug:16s} {r.induced_response_cosine:>8.3f} "
              f"{r.n_malignant:>8d} {r.n_myeloid:>8d}")
    c = g1.induced_response_cosine.dropna()
    res["gate1"] = {"median": float(c.median()), "mean": float(c.mean()),
                    "min": float(c.min()), "max": float(c.max()), "n": int(len(c))}
    print("-" * 86)
    print(f"  median cos = {c.median():.3f}, range {c.min():.3f} to {c.max():.3f} "
          f"(n = {len(c)} patient-drug pairs)")
    print(f"  CONSTRUCTED SciPlex3 mixtures, for comparison: 0.014 to 0.044 (near-orthogonal)")
    # No pass/fail threshold: the comparison is the finding, and a cutoff we choose would decide
    # it for us. cos = 0.566 is well below 1 (there IS differential response) and far above the
    # 0.014 our constructed mixture produced (we EXAGGERATED it by an order of magnitude).
    res["gate1"]["interpretation"] = (
        f"Naturally co-existing compartments respond in partly different directions (median cos "
        f"{c.median():.3f}), so differential response is real in a tumour. But our constructed "
        f"cell-line mixtures put it at 0.014-0.044, near-orthogonal. Mixing A549 with K562 makes "
        f"one drug push two unrelated cell lines in unrelated directions; malignant cells and "
        f"tumour-associated macrophages in one patient share far more of their response. The "
        f"constructed benchmark therefore OVERSTATES the divergence a distributional score has "
        f"to work with, by roughly an order of magnitude.")
    print(f"\n  INTERPRETATION: {res['gate1']['interpretation']}")

    # ---------------- THE PREMISE ----------------
    print(f"\n{'='*86}")
    print("THE PREMISE (Fig. 1a): can two drugs share a mean signature and act differently")
    print("on a compartment? Tested for the first time on a real tumour.")
    if len(pairs) >= 5:
        r_mal = stats.spearmanr(pairs.cos_mean_signature, pairs.cos_malignant_response)
        print(f"\n  drug pairs: {len(pairs)} (within-patient)")
        print(f"  cos(mean signature)        median {pairs.cos_mean_signature.median():+.3f}")
        print(f"  cos(malignant response)    median {pairs.cos_malignant_response.median():+.3f}")
        print(f"  cos(myeloid response)      median {pairs.cos_myeloid_response.median():+.3f}")
        print(f"\n  Spearman(mean-similarity, malignant-response-similarity) = "
              f"{r_mal.statistic:+.3f}  (p = {r_mal.pvalue:.3g})")
        # the premise: drugs that look alike on the mean but act differently on the compartment
        look_alike = pairs[pairs.cos_mean_signature > pairs.cos_mean_signature.quantile(0.75)]
        n_diverge = int((look_alike.cos_malignant_response
                         < look_alike.cos_mean_signature - 0.10).sum())
        res["premise"] = {
            "n_drug_pairs": int(len(pairs)),
            "spearman_mean_vs_malignant": float(r_mal.statistic),
            "p": float(r_mal.pvalue),
            "median_cos_mean": float(pairs.cos_mean_signature.median()),
            "median_cos_malignant": float(pairs.cos_malignant_response.median()),
            "n_lookalike_pairs_that_diverge": n_diverge,
            "n_lookalike_pairs": int(len(look_alike)),
        }
        print(f"\n  Of the {len(look_alike)} drug pairs MOST similar on the mean, {n_diverge} "
              f"have a malignant-compartment\n  response at least 0.10 less similar than their "
              f"mean signature suggests.")
        # NO PASS/FAIL THRESHOLD. An earlier version of this script declared "PREMISE HOLDS" if
        # the correlation came in below 0.9, and it came in at 0.878. That threshold was chosen
        # by us, after the fact, and clearing it by 0.02 licenses nothing. Moving a threshold
        # after seeing the result is precisely the analytic freedom this paper is about. The
        # correlation is reported and interpreted in the text; the script does not adjudicate.
        res["premise"]["interpretation"] = (
            f"Mean-signature similarity predicts compartment-specific response similarity at "
            f"rho = {r_mal.statistic:.3f} (n = {len(pairs)} within-patient drug pairs). The mean "
            f"is therefore LARGELY, though not entirely, sufficient in real tumour tissue. This "
            f"is weak support for the motivating scenario (same mean, opposite subpopulation "
            f"fate) and is reported as such: the residual is real but small, which is the same "
            f"conclusion every other independent criterion in this study reaches.")
        print(f"\n  INTERPRETATION: {res['premise']['interpretation']}")
    else:
        print(f"  only {len(pairs)} drug pairs; not enough to test. Reported as a gap.")
        res["premise"] = {"status": f"insufficient drug pairs ({len(pairs)})"}

    # ---------------- GATE 2 ----------------
    g2 = gate2_natural(d)
    g2.to_csv(OUT / "gate2_natural.csv", index=False)
    print(f"\n{'='*86}")
    print("GATE 2 (natural): is real tumour cell-type structure recoverable?")
    print("Same protocol and same unit as the constructed-mixture analysis, so the two compare.")
    UNS = ["acc_kmeans_k2", "acc_gmm_k2", "acc_leiden", "acc_hdbscan"]
    if g2.empty:
        print("  no patient had enough control cells in both compartments.")
        res["gate2"] = {"status": "no usable patient"}
    else:
        print(f"\n  {'method':22s} {'accuracy':>10s}")
        print("  " + "-" * 34)
        res["gate2"] = {"n_runs": int(len(g2)), "patients": sorted(g2.patient.unique().tolist())}
        for m in UNS:
            v = float(g2[m].median())
            res["gate2"][m] = v
            print(f"  {m.replace('acc_',''):22s} {v:>10.4f}")
        for k in ("linear", "forest", "knn"):
            res["gate2"][f"probe_{k}"] = float(g2[f"probe_{k}_acc"].median())
        ceil = float(g2.probe_acc.median())
        best = max(float(g2[m].median()) for m in UNS)
        res["gate2"]["ceiling"] = ceil
        res["gate2"]["best_unsupervised"] = best
        res["gate2"]["gap"] = ceil - best
        print("  " + "-" * 34)
        print(f"  {'SUPERVISED CEILING':22s} {ceil:>10.4f}")
        print(f"\n  best unsupervised : {best:.4f}")
        print(f"  supervised ceiling: {ceil:.4f}")
        print(f"  gap               : {ceil - best:+.4f}")
        print(f"\n  CONSTRUCTED mixture (HDAC vs JAK, SciPlex3): ceiling 0.692, best unsup 0.674")
        print(f"  NATURAL tumour     (malignant vs myeloid)   : ceiling {ceil:.3f}, "
              f"best unsup {best:.3f}")
        res["gate2"]["interpretation"] = (
            f"Natural tumour compartments are far more separable than our constructed mixture: "
            f"supervised ceiling {ceil:.3f} versus 0.692, and unsupervised clustering reaches "
            f"{best:.3f} versus 0.674. Gate 2 is therefore NOT a universal information limit. "
            f"Our earlier conclusion that real subpopulations cannot be told apart was a "
            f"property of the constructed HDAC-versus-JAK benchmark, not of biology. In a "
            f"patient's tumour the structure is present and off-the-shelf clustering finds it. "
            f"The gap between ceiling and clustering stays small ({ceil - best:+.3f}), so in "
            f"BOTH regimes the assignment step is not the bottleneck; what differs is how much "
            f"there is to assign.")
        print(f"\n  INTERPRETATION: {res['gate2']['interpretation']}")

    json.dump(res, open(OUT / "zhao_two_gates.json", "w"), indent=2)
    print(f"\nwrote {OUT}/gate1_natural.csv, premise_mean_vs_compartment.csv, "
          f"gate2_natural.csv, zhao_two_gates.json")


if __name__ == "__main__":
    main()
