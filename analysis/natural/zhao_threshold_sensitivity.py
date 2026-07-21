#!/usr/bin/env python3
"""Do the natural-tissue headline numbers survive the compartment-assignment thresholds?

WHY (audit finding M21)
-----------------------
Three numbers carry the natural-heterogeneity result and every one depends on how cells are
assigned to compartments: the Gate-2 supervised ceiling (0.923) and best unsupervised (0.777), the
Gate-1 induced cosine (0.566), and the premise correlation (rho 0.878). The assignment uses two
hand-picked constants, an expression floor of 0.25 and a z-margin of 0.25, and drops 39.9% of cells
as unassignable. The discarded cells are BY CONSTRUCTION the hardest to classify, so a strict
threshold could flatter every number and a loose one could pull in ambiguous cells that wreck it.
This script re-derives all four numbers across a grid of (floor, margin) and reports how they move.

It reimplements the assignment inline rather than importing the production loader, so nothing here
can alter data/processed/zhao_gbm.npz or the numbers the paper reports. It reuses the exact scoring
rule and the exact Gate-2 scorer (score_split) so the per-threshold numbers are comparable to the
headline ones.

    PYTHONPATH=src python analysis/natural/zhao_threshold_sensitivity.py
"""
from pathlib import Path as _P
REPO = _P(__file__).resolve().parents[2]
import sys
sys.path.insert(0, str(REPO / "src"))
sys.path.insert(0, str(REPO / "analysis" / "natural"))
sys.path.insert(0, str(REPO / "analysis" / "identifiability"))

import itertools
import json
import warnings

import numpy as np
import pandas as pd
from scipy import stats

from data.load_zhao_gbm import MARKERS, KEY_MARKERS, _score, _raw_mean, RAW, N_HVG
from gate2_drug_response import score_split, N_CELLS

warnings.filterwarnings("ignore")

MIN_CELLS = 50
PAIR = ["malignant", "myeloid"]
GRID = [(0.10, 0.10), (0.25, 0.25), (0.40, 0.40), (0.50, 0.50)]  # (0.25, 0.25) is the paper's
OUT = REPO / "results" / "zhao_gbm"


def load_once():
    """Normalize/log1p once, compute marker scores and the HVG matrix; all threshold-independent."""
    import anndata as ad
    import scanpy as sc
    a = ad.read_h5ad(RAW)
    a.var_names = [str(v).upper() for v in a.var_names]
    a.var_names_make_unique()
    sc.pp.filter_cells(a, min_genes=200)
    sc.pp.normalize_total(a, target_sum=1e4)
    sc.pp.log1p(a)
    gene_idx = {g: i for i, g in enumerate(a.var_names)}
    Xl = a.X.toarray() if hasattr(a.X, "toarray") else np.asarray(a.X)
    names = list(MARKERS)
    scores = np.vstack([_score(Xl, gene_idx, m) for m in MARKERS.values()]).T
    keyexp = np.vstack([_raw_mean(Xl, gene_idx, KEY_MARKERS[n]) for n in names]).T
    sc.pp.highly_variable_genes(a, n_top_genes=N_HVG, flavor="seurat")
    ah = a[:, a.var.highly_variable].copy()
    X = (ah.X.toarray() if hasattr(ah.X, "toarray") else np.asarray(ah.X)).astype(np.float32)
    pert = a.obs["perturbation"].astype(str).values
    patient = a.obs["sample"].astype(str).values
    return X, scores, keyexp, names, pert, patient


def assign(scores, keyexp, names, floor, margin):
    top = scores.argmax(1)
    marg = scores.max(1) - np.sort(scores, axis=1)[:, -2]
    own = keyexp[np.arange(len(top)), top]
    called = (own >= floor) & (marg >= margin)
    labels = np.where(called, np.array(names)[top], "unassigned")
    # validation: each called compartment must express its own key markers most strongly
    ok = True
    for i, n in enumerate(names):
        m = labels == n
        if m.sum() == 0:
            continue
        means = [keyexp[m, j].mean() for j in range(len(names))]
        ok = ok and (int(np.argmax(means)) == i)
    return labels, float((labels == "unassigned").mean()), ok


def main():
    X, scores, keyexp, names, pert, patient = load_once()
    print(f"loaded {X.shape[0]} cells x {X.shape[1]} HVG\n", flush=True)
    is_ctrl = pert == "control"

    rows = []
    for floor, margin in GRID:
        labels, frac_un, valid = assign(scores, keyexp, names, floor, margin)
        tag = f"floor={floor:.2f} margin={margin:.2f}"
        paper = (abs(floor - 0.25) < 1e-9 and abs(margin - 0.25) < 1e-9)
        comp = {c: labels == c for c in PAIR}
        n_mal, n_mye = int(comp["malignant"].sum()), int(comp["myeloid"].sum())

        # ---- Gate 2: drug-response subpop, within compartment, within patient ----
        g2 = []
        for p in sorted(set(patient)):
            for c in PAIR:
                sel = comp[c] & (patient == p) & ~is_ctrl
                drugs = [(d, np.where(sel & (pert == d))[0])
                         for d in sorted(set(pert[sel].tolist()))]
                drugs = [(d, idx) for d, idx in drugs if len(idx) >= MIN_CELLS]
                for (da, ia), (db, ib) in itertools.combinations(drugs, 2):
                    for seed in range(3):
                        r = score_split(X[ia].astype(np.float64), X[ib].astype(np.float64), seed)
                        g2.append((r["ceiling_matched"], r["best_unsup"], r["gap_matched"]))
        # ---- Gate 1: induced cosine malignant vs myeloid ----
        g1 = []
        for p in sorted(set(patient)):
            for d in sorted(set(pert[(patient == p) & ~is_ctrl].tolist())):
                dk = {}
                okc = True
                for c in PAIR:
                    tsel = comp[c] & (patient == p) & (pert == d)
                    csel = comp[c] & (patient == p) & is_ctrl
                    if tsel.sum() < MIN_CELLS or csel.sum() < MIN_CELLS:
                        okc = False; break
                    dk[c] = X[tsel].astype(np.float64).mean(0) - X[csel].astype(np.float64).mean(0)
                if okc:
                    a, b = dk["malignant"], dk["myeloid"]
                    g1.append(float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12)))
        # ---- premise: mean-signature similarity vs malignant-compartment similarity ----
        prem = premise(X, comp, patient, pert, is_ctrl)

        row = {"floor": floor, "margin": margin, "is_paper_setting": paper,
               "valid": valid, "frac_unassigned": round(frac_un, 3),
               "n_malignant": n_mal, "n_myeloid": n_mye,
               "gate2_ceiling": _med(g2, 0), "gate2_unsup": _med(g2, 1),
               "gate2_gap": _med(g2, 2), "n_gate2_splits": len(g2),
               "gate1_cos": float(np.median(g1)) if g1 else np.nan, "n_gate1": len(g1),
               "premise_rho": prem[0], "n_premise": prem[1]}
        rows.append(row)
        star = "  <-- PAPER" if paper else ""
        print(f"{tag}{star}", flush=True)
        print(f"   valid={valid}  dropped={frac_un:.1%}  malignant={n_mal} myeloid={n_mye}")
        print(f"   Gate2 ceiling={row['gate2_ceiling']:.3f} unsup={row['gate2_unsup']:.3f} "
              f"gap={row['gate2_gap']:+.3f} (n={len(g2)}) | Gate1 cos={row['gate1_cos']:.3f} "
              f"(n={len(g1)}) | premise rho={prem[0]:.3f} (n={prem[1]})\n", flush=True)

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "zhao_threshold_sensitivity.csv", index=False)
    json.dump(rows, open(OUT / "zhao_threshold_sensitivity.json", "w"), indent=2)

    print("=" * 92)
    print("SENSITIVITY SUMMARY (paper setting is floor=margin=0.25)")
    print(df[["floor", "margin", "valid", "frac_unassigned", "gate2_ceiling", "gate2_unsup",
              "gate2_gap", "gate1_cos", "premise_rho"]].to_string(index=False))
    print("\nIf the headline numbers (ceiling ~0.923, unsup ~0.777, gap ~0.117, Gate1 ~0.566,")
    print("premise ~0.878) are stable across rows that pass validation, the threshold choice does")
    print("not drive the result. No verdict is hard-coded.")
    print(f"\nwrote {OUT/'zhao_threshold_sensitivity.csv'} and .json")


def _med(triples, i):
    v = [t[i] for t in triples]
    return float(np.median(v)) if v else float("nan")


def premise(X, comp, patient, pert, is_ctrl):
    def _cos(a, b):
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))
    xs, ys = [], []
    for p in sorted(set(patient)):
        drugs = sorted(set(pert[(patient == p) & ~is_ctrl].tolist()))
        sig, malr = {}, {}
        cmean = X[(patient == p) & is_ctrl].astype(np.float64).mean(0) \
            if ((patient == p) & is_ctrl).sum() else None
        mal_c = comp["malignant"] & (patient == p) & is_ctrl
        for d in drugs:
            allsel = (patient == p) & (pert == d)
            msel = comp["malignant"] & (patient == p) & (pert == d)
            if allsel.sum() < MIN_CELLS or msel.sum() < MIN_CELLS or cmean is None \
                    or mal_c.sum() < MIN_CELLS:
                continue
            sig[d] = X[allsel].astype(np.float64).mean(0) - cmean
            malr[d] = X[msel].astype(np.float64).mean(0) - X[mal_c].astype(np.float64).mean(0)
        for da, db in itertools.combinations(sorted(sig), 2):
            xs.append(_cos(sig[da], sig[db]))
            ys.append(_cos(malr[da], malr[db]))
    if len(xs) < 3:
        return (float("nan"), len(xs))
    return (float(stats.spearmanr(xs, ys)[0]), len(xs))


if __name__ == "__main__":
    main()
