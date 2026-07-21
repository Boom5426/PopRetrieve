#!/usr/bin/env python3
"""Gate 2, measured on the SAME CONSTRUCT in constructed and natural data.

WHY THIS SCRIPT EXISTS: THE PREVIOUS COMPARISON WAS NOT A COMPARISON
--------------------------------------------------------------------
analysis/natural/zhao_two_gates.py::gate2_natural separates the MALIGNANT from the MYELOID
compartment using CONTROL cells (`control=True`). That is a CELL-TYPE identification task: a
glioma cell against a macrophage, two different lineages with thousands of differentially
expressed genes between them. It is trivially easy, and it reached a supervised ceiling of 0.964.

analysis/identifiability/gate2_supervised_upper_bound.py separates HDAC-TREATED from JAK-TREATED
K562 cells. That is a DRUG-RESPONSE identification task: one lineage, cells that differ only in
which drug they saw. It is hard, and it reached a ceiling of 0.692.

The paper then reported "0.964 in a real tumour against 0.692 in our constructed mixture, under an
identical protocol", and concluded that the information limit was a property of our benchmark
rather than of biology. THAT COMPARISON IS INVALID. The two numbers answer different questions.
Gate 2 is defined on the subpopulations a *retrieval score* must resolve inside a candidate
population, which is a drug-response partition, not a cell-type partition. Separating two lineages
says nothing about it.

This script measures Gate 2 on the drug-response partition in BOTH settings, so that the
constructed and the natural number finally mean the same thing:

    CONSTRUCTED : HDAC-treated vs JAK-treated K562 cells                (as before)
    NATURAL     : drug A-treated vs drug B-treated cells, WITHIN ONE
                  COMPARTMENT, WITHIN ONE PATIENT of ZhaoSims2021       (new; the matched test)

The natural arm is the K562 construct transplanted into tissue nobody assembled. If the ceiling
there is also low, then the information limit is real biology after all and the withdrawal in the
current draft was made on bad evidence. We do not know which way this goes.

A SECOND ERROR THIS SCRIPT FIXES: THE BIAS WAS STATED BACKWARDS
--------------------------------------------------------------
gate2_supervised_upper_bound.py asserts, in its code comment and in the paper's Methods, that
giving the clusterers the easier transductive PCA while making the supervised probe re-fit PCA
inside its training fold "biases the comparison AGAINST the conclusion we draw".

It does the opposite. The conclusion drawn is that the GAP (ceiling minus best unsupervised) is
SMALL, hence "the limit is informational, not algorithmic". Inflating the unsupervised arm and
deflating the supervised arm SHRINKS the gap. The design therefore FLATTERS that conclusion.

So the ceiling is computed here under BOTH representations:

    ceiling_infold       PCA re-fit inside each training fold. Honest, but deflated, and it is
                         not the representation the clusterers were given.
    ceiling_transductive PCA fit on the full mixture, i.e. THE SAME representation the clusterers
                         see. PCA is unsupervised, so it leaks no labels; this is the matched,
                         apples-to-apples comparison, and gap_matched is the gap to report.

    PYTHONPATH=src python analysis/natural/gate2_drug_response.py
"""
from pathlib import Path as _P
REPO = _P(__file__).resolve().parents[2]
import sys
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "analysis" / "identifiability"))

import itertools
import json
import time
import warnings

import numpy as np
import pandas as pd
import torch
from sklearn.decomposition import PCA

from gate2_supervised_upper_bound import (
    unsupervised, supervised_ceiling, best_permutation_accuracy, _classifiers, N_PCA, UNSUP,
)
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, roc_auc_score

from data.load_zhao_gbm import load_zhao_gbm

warnings.filterwarnings("ignore")

SEEDS = list(range(5))
MIN_CELLS = 50          # per drug, per compartment: below this a split is noise
N_CELLS = 150           # cells per source, capped by availability
N_CONSTRUCTED_PAIRS = 24  # single-drug K562 pairs kept, to match the natural arm's scale
DATA_PROC = REPO / "data" / "processed"
OUT = REPO / "results" / "zhao_gbm"


def ceiling_transductive(Z, y, seed):
    """The ceiling under THE SAME representation the clusterers were given.

    PCA is already fit on the full mixture (transductive) by the caller. PCA sees no labels, so
    this leaks no label information; it simply puts the probe and the clusterers on equal footing.
    Only the classifier is cross-validated.
    """
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
    names = list(_classifiers(0))
    pred = {m: np.zeros(len(y), dtype=int) for m in names}
    prob = {m: np.zeros(len(y), dtype=float) for m in names}
    for tr, te in skf.split(Z, y):
        s = StandardScaler().fit(Z[tr])
        Ztr, Zte = s.transform(Z[tr]), s.transform(Z[te])
        for m, clf in _classifiers(seed).items():
            clf.fit(Ztr, y[tr])
            pred[m][te] = clf.predict(Zte)
            prob[m][te] = clf.predict_proba(Zte)[:, 1]
    acc = {m: accuracy_score(y, pred[m]) for m in names}
    auc = {m: roc_auc_score(y, prob[m]) for m in names}
    # Return every method, not only the winner. The GAP is a difference of two MAXIMA (best of 3
    # classifiers minus best of 4 clusterers), and a maximum over methods is upward-biased: the
    # winner's curse inflates the ceiling and the best-unsupervised term alike, and the two biases
    # do not cancel. Storing every method lets the uncertainty analysis report fixed-method gaps
    # that involve no selection at all.
    return max(acc.values()), max(auc.values()), acc


def score_split(Xa, Xb, seed):
    """One binary identifiability problem, scored in the paper's common unit."""
    n = min(len(Xa), len(Xb), N_CELLS)
    rng = np.random.RandomState(1000 + seed)
    A = Xa[rng.choice(len(Xa), n, replace=False)]
    B = Xb[rng.choice(len(Xb), n, replace=False)]
    Xm = np.vstack([A, B]).astype(np.float64)
    y = np.array([0] * n + [1] * n)

    k = min(N_PCA, 2 * n - 1, Xm.shape[1])
    Z = PCA(n_components=k, random_state=seed).fit_transform(Xm)   # transductive, as clusterers get

    rec = {"seed": seed, "n_per_source": n}
    for m, (ari, acc, kk) in unsupervised(Z, y, seed).items():
        rec[f"acc_{m}"] = float(acc)
    rec["best_unsup"] = max(rec[f"acc_{m}"] for m in UNSUP)

    sup = supervised_ceiling(Xm, y, seed, N_PCA)                   # in-fold PCA (deflated)
    rec["ceiling_infold"] = float(sup["probe_acc"])
    rec["ceiling_infold_auc"] = float(sup["probe_auc"])

    ct, cta, per_method = ceiling_transductive(Z, y, seed)         # matched representation
    rec["ceiling_matched"] = float(ct)
    rec["ceiling_matched_auc"] = float(cta)
    for m, v in per_method.items():                                 # no max taken: every probe
        rec[f"sup_{m}"] = float(v)

    rec["gap_infold"] = rec["ceiling_infold"] - rec["best_unsup"]
    rec["gap_matched"] = rec["ceiling_matched"] - rec["best_unsup"]
    return rec


def constructed_arm():
    """K562 drug-response splits, in TWO granularities.

    constructed_class : HDAC-class cells vs JAK-class cells, pooling every drug in each class.
                        This is what the paper reported (ceiling 0.692).
    constructed_drug  : ONE HDAC drug vs ONE JAK drug.

    The distinction is a confound and it runs in the paper's favour, so it must be closed. The
    natural arm compares a single drug against a single drug; the class-pooled arm carries the
    extra within-class variance of several distinct compounds, which makes its partition harder
    for reasons that have nothing to do with the mixture being constructed. Only
    constructed_drug is a like-for-like comparator for the natural arm.
    """
    d = torch.load(DATA_PROC / "sciplex3_all.pt", weights_only=False)
    X = d["X"]
    X = X.numpy() if hasattr(X, "numpy") else np.asarray(X)
    obs = d["obs"].reset_index(drop=True)
    base = ((obs["cell_line"] == "K562") & (obs["dose_value"] == 10000.0)
            & (~obs["is_control"].astype(bool)))
    tgt = obs["target"].astype(str).str.upper()
    hm = (base & tgt.str.contains("HDAC")).values
    jm = (base & tgt.str.contains("JAK")).values
    XH = X[np.where(hm)[0]].astype(np.float64)
    XJ = X[np.where(jm)[0]].astype(np.float64)
    print(f"CONSTRUCTED  HDAC {len(XH)} cells vs JAK {len(XJ)} cells", flush=True)

    rows = []
    for seed in SEEDS:
        r = score_split(XH, XJ, seed)
        r.update({"arm": "constructed_class", "unit": "K562 HDAC-class vs JAK-class (pooled)",
                  "patient": "-", "compartment": "K562", "drug_a": "HDAC-class",
                  "drug_b": "JAK-class"})
        rows.append(r)

    # like-for-like: one drug against one drug, exactly as the natural arm does
    prod = obs["product_name"] if "product_name" in obs else obs["perturbation"]
    hdrugs = [(dr, np.where(hm & (prod == dr).values)[0]) for dr in sorted(set(prod[hm]))]
    jdrugs = [(dr, np.where(jm & (prod == dr).values)[0]) for dr in sorted(set(prod[jm]))]
    hdrugs = [(a, b) for a, b in hdrugs if len(b) >= MIN_CELLS]
    jdrugs = [(a, b) for a, b in jdrugs if len(b) >= MIN_CELLS]
    all_pairs = list(itertools.product(hdrugs, jdrugs))
    # The full cross product is 27 x 19 = 513 pairs, which is 25x the natural arm's pair count and
    # would take hours for no extra information. Subsample to a comparable number, with a fixed
    # seed. THE CAP IS REPORTED, not silent: a truncation that goes unmentioned reads as full
    # coverage, which is the reporting failure this paper is about.
    rng = np.random.RandomState(0)
    if len(all_pairs) > N_CONSTRUCTED_PAIRS:
        keep = rng.choice(len(all_pairs), N_CONSTRUCTED_PAIRS, replace=False)
        pairs = [all_pairs[i] for i in sorted(keep)]
    else:
        pairs = all_pairs
    print(f"CONSTRUCTED  single-drug arm: {len(hdrugs)} HDAC x {len(jdrugs)} JAK drugs "
          f"(>= {MIN_CELLS} cells) = {len(all_pairs)} pairs; "
          f"SUBSAMPLED to {len(pairs)} (seed 0) to match the natural arm's scale", flush=True)
    for (da, ia), (db, ib) in pairs:
        for seed in SEEDS:
            r = score_split(X[ia].astype(np.float64), X[ib].astype(np.float64), seed)
            r.update({"arm": "constructed_drug", "unit": f"K562 {da} vs {db}",
                      "patient": "-", "compartment": "K562", "drug_a": da, "drug_b": db})
            rows.append(r)
    return rows


def natural_arm():
    """Drug A vs drug B cells, WITHIN one compartment, WITHIN one patient. The matched test."""
    z = load_zhao_gbm()
    print(z.summary(), flush=True)
    rows = []
    for p in z.patients:
        for comp in ["malignant", "myeloid"]:
            drugs = []
            for dr in sorted(set(z.pert[z.rows(patient=p, compartment=comp, control=False)])):
                idx = z.rows(patient=p, drug=dr, compartment=comp, control=False)
                if len(idx) >= MIN_CELLS:
                    drugs.append((dr, idx))
            for (da, ia), (db, ib) in itertools.combinations(drugs, 2):
                for seed in SEEDS:
                    r = score_split(z.X[ia].astype(np.float64), z.X[ib].astype(np.float64), seed)
                    r.update({"arm": "natural", "unit": f"{comp} cells, {da} vs {db}",
                              "patient": p, "compartment": comp, "drug_a": da, "drug_b": db})
                    rows.append(r)
                print(f"  {p} {comp:10s} {da[:14]:14s} vs {db[:14]:14s} "
                      f"n={min(len(ia), len(ib), N_CELLS):3d}  "
                      f"ceiling(matched) {np.mean([x['ceiling_matched'] for x in rows[-len(SEEDS):]]):.3f}",
                      flush=True)
    return rows


def main():
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    rows = constructed_arm() + natural_arm()
    df = pd.DataFrame(rows)
    df.to_csv(OUT / "gate2_drug_response.csv", index=False)

    print(f"\n{'=' * 96}")
    print("GATE 2 ON THE SAME CONSTRUCT: drug-response subpopulations, constructed vs natural.")
    print("The previous natural number (0.964) separated CELL TYPES and is not comparable.\n")
    print(f"{'arm':12s} {'n splits':>8s} {'best unsup':>11s} {'ceiling':>9s} {'ceiling':>9s} "
          f"{'gap':>8s} {'gap':>8s}")
    print(f"{'':12s} {'':>8s} {'(transd.)':>11s} {'(in-fold)':>9s} {'(matched)':>9s} "
          f"{'(in-fold)':>8s} {'(matched)':>8s}")
    print("-" * 96)
    res = {}
    for arm, s in df.groupby("arm"):
        # median over splits; the honest unit for the natural arm is the (patient, drug-pair) split
        g = s.groupby(["patient", "compartment", "drug_a", "drug_b"]).median(numeric_only=True)
        r = {k: float(g[k].median()) for k in
             ["best_unsup", "ceiling_infold", "ceiling_matched", "gap_infold", "gap_matched"]}
        r["n_splits"] = int(len(g))
        res[arm] = r
        print(f"{arm:12s} {r['n_splits']:>8d} {r['best_unsup']:>11.3f} {r['ceiling_infold']:>9.3f} "
              f"{r['ceiling_matched']:>9.3f} {r['gap_infold']:>+8.3f} {r['gap_matched']:>+8.3f}")
    print("-" * 96)

    print("\nPER (patient, compartment, drug pair) IN THE NATURAL ARM  [the honest unit]")
    nat = df[df.arm == "natural"]
    if len(nat):
        g = nat.groupby(["patient", "compartment", "drug_a", "drug_b"]).median(numeric_only=True)
        for k, v in g.iterrows():
            print(f"  {k[0]:7s} {k[1]:10s} {k[2][:16]:16s} vs {k[3][:16]:16s} "
                  f"unsup {v.best_unsup:.3f}  ceiling {v.ceiling_matched:.3f}  "
                  f"gap {v.gap_matched:+.3f}")
        res["n_patients"] = int(nat.patient.nunique())
        res["n_drug_pairs"] = int(g.shape[0])
        print(f"\n  {res['n_drug_pairs']} drug-pair splits across {res['n_patients']} patients")

    # The comparison the paper actually needs, stated without a verdict.
    # constructed_drug, not constructed_class, is the like-for-like comparator: the natural arm
    # is one drug against one drug, and pooling several drugs per class adds within-class
    # variance that makes the constructed task harder for reasons unrelated to its being
    # constructed. Quoting constructed_class against natural would inflate the contrast.
    if "constructed_drug" in res and "natural" in res:
        res["headline"] = {
            "comparator": "constructed_drug (one drug vs one drug), NOT constructed_class",
            "constructed_drug_ceiling_matched": res["constructed_drug"]["ceiling_matched"],
            "natural_ceiling_matched": res["natural"]["ceiling_matched"],
            "constructed_drug_gap_matched": res["constructed_drug"]["gap_matched"],
            "natural_gap_matched": res["natural"]["gap_matched"],
        }
        if "constructed_class" in res:
            res["headline"]["constructed_class_ceiling_matched"] = \
                res["constructed_class"]["ceiling_matched"]
        print(f"\nLIKE FOR LIKE (one drug vs one drug, matched representation): the supervised "
              f"ceiling is {res['constructed_drug']['ceiling_matched']:.3f} in the K562 mixture "
              f"we built and {res['natural']['ceiling_matched']:.3f} in a real tumour.")
        print("No pass/fail threshold is applied. The numbers are reported and interpreted in "
              "the text.")

    json.dump(res, open(OUT / "gate2_drug_response.json", "w"), indent=2)
    print(f"\nwrote {OUT/'gate2_drug_response.csv'} and .json   [{time.time()-t0:.0f}s]")


if __name__ == "__main__":
    main()
