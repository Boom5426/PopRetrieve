#!/usr/bin/env python3
"""Class C, second oracle: does RNA-based retrieval recover the PROTEIN-level response?

WHY A SECOND ORACLE
-------------------
The GDSC functional oracle (class_c_functional_oracle.py) found something specific: energy
retrieval beats the correctly specified mean incumbent on an independent readout (+0.276 vs
+0.083), but a query-dependent scalar that merely matches response MAGNITUDE, comparing no
distributions at all, reaches +0.232, and partialling that channel out leaves energy with +0.097.
The gain is real; almost none of it is distributional.

That is a strong claim to rest on one oracle, and the GDSC one has real weaknesses: it is a
separate bulk assay, joined by compound identity, under a different dose regime. This script tests
the same claim against an oracle with the opposite weaknesses and the opposite strengths.

Frangieh et al. Perturb-CITE-seq measures RNA and 24 surface PROTEINS in the SAME 218,331 cells,
barcode-for-barcode. The proteins are the phenotype the assay was built to read: HLA-A, HLA-E,
CD274 (PD-L1), CD58, CD47, the immune-evasion axis of melanoma. A retrieval score computed on RNA
never sees them.

    oracle(q, c) = cos( protein_delta(q), protein_delta(c) )

This is semantically matched to retrieval (do these two perturbations DO the same thing?), it is
measured on the same cells (no cross-assay compound matching, no dose mismatch), and it lives in a
different molecular layer from the one the scorer reads. Its weakness is the mirror image of
GDSC's: it is still a molecular readout, not viability or survival. Two oracles with disjoint
failure modes agreeing is worth more than either alone.

THE CONTROLS ARE THE SAME ONES, AND FOR THE SAME REASON
  magnitude_match   rank by -|  ||d_c|| - ||d_q||  |. Query-dependent, compares NO distributions.
                    This is the null a distributional score has to beat, and on GDSC it very nearly
                    was not beaten.
  magnitude_only    rank by ||d_c||. Query-INDEPENDENT: one ordering for every query. A sanity
                    check, not a competitor.

ADT PREPROCESSING. Counts are CLR-normalized within each cell, which is the standard for CITE-seq
and is what makes protein deltas comparable across cells. The four isotype controls (Rat_IgG2a,
Mouse_IgG1/IgG2a/IgG2b) are BACKGROUND, not phenotype, and are dropped; leaving them in would let
a scorer be rewarded for tracking nonspecific antibody binding.

    PYTHONPATH=src python analysis/class_c/class_c_protein_oracle.py
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

from retrieval.metrics import score_energy, score_mean_cosine

warnings.filterwarnings("ignore")

SEED = 42
MIN_CELLS = 60            # per perturbation, in the shared control condition
MAX_CELLS = 250           # energy distance is O(n*m); 250 keeps 3 conditions x ~200 KOs tractable
ISOTYPES = ["Rat_IgG2a", "Mouse_IgG1", "Mouse_IgG2a", "Mouse_IgG2b"]

RAW = REPO / "data" / "raw" / "frangieh2021"
PROC = REPO / "data" / "processed"
OUT = REPO / "results" / "upgrade"


def _cos(a, b):
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return float(np.dot(a, b) / (na * nb)) if na > 1e-12 and nb > 1e-12 else np.nan


def clr(X):
    """Centered log-ratio within each cell: the standard CITE-seq ADT normalization."""
    L = np.log1p(X)
    return (L - L.mean(1, keepdims=True)).astype(np.float32)


def main():
    import anndata as ad
    import scanpy as sc

    # THE JOIN IS THE PART THAT CAN SILENTLY DESTROY THIS ANALYSIS.
    # The cached RNA tensor has 218,023 cells and the protein file has 218,331: the row orders do
    # NOT correspond. Concatenating them by position would pair each cell's protein response with
    # some other cell's RNA, producing a result that looks entirely normal and is pure noise. RNA
    # is therefore rebuilt here from the source h5ad and aligned to the protein file BY BARCODE.
    p = ad.read_h5ad(RAW / "FrangiehIzar2021_protein.h5ad")
    r = ad.read_h5ad(RAW / "FrangiehIzar2021_RNA.h5ad")

    shared = [b for b in p.obs_names if b in set(r.obs_names)]
    if len(shared) < 0.9 * min(len(p), len(r)):
        raise RuntimeError(f"only {len(shared)} shared barcodes between RNA ({len(r)}) and "
                           f"protein ({len(p)}); refusing to proceed on a partial join.")
    p = p[shared].copy()
    r = r[shared].copy()
    print(f"joined by barcode: {len(shared)} cells present in BOTH the RNA and protein assays")
    assert list(p.obs_names) == list(r.obs_names), "barcode alignment failed after subsetting"

    # ---- protein (the oracle) ----
    keep_prot = [i for i, v in enumerate(p.var_names) if str(v) not in ISOTYPES]
    prot_names = [str(p.var_names[i]) for i in keep_prot]
    P = p.X.toarray() if hasattr(p.X, "toarray") else np.asarray(p.X)
    P = clr(P)[:, keep_prot]
    print(f"protein: {P.shape[0]} cells x {P.shape[1]} markers "
          f"({len(ISOTYPES)} isotype controls dropped)")
    print(f"  {', '.join(prot_names)}")

    # ---- RNA (what the retrieval score sees), same preprocessing as everywhere else ----
    sc.pp.normalize_total(r, target_sum=1e4)
    sc.pp.log1p(r)
    sc.pp.highly_variable_genes(r, n_top_genes=2000, flavor="seurat")
    r = r[:, r.var.highly_variable].copy()
    R = (r.X.toarray() if hasattr(r.X, "toarray") else np.asarray(r.X)).astype(np.float32)
    pert = r.obs["perturbation"].astype(str).values
    is_ctrl = pert == "control"

    # THE IMMUNE CONDITION IS NOT OPTIONAL. Frangieh's three conditions (Control, IFN-gamma,
    # Co-culture) live in `perturbation_2`, not in a column called `condition`. A first version of
    # this script silently fell back to a single pooled condition, which defines every knockout's
    # effect against a control mixed across all three. Condition and perturbation effects then
    # confound: a KO measured mostly under IFN-gamma gets credited with the IFN-gamma response.
    # Each condition is analysed separately, with its own controls.
    if "perturbation_2" not in r.obs.columns:
        raise RuntimeError("no 'perturbation_2' column: cannot separate the immune conditions, "
                           "and pooling them would confound condition with perturbation.")
    cond = r.obs["perturbation_2"].astype(str).values
    print(f"RNA:     {R.shape[0]} cells x {R.shape[1]} HVG | "
          f"{len(set(pert)) - 1} knockouts | conditions {sorted(set(cond.tolist()))}")

    # one condition at a time: a KO's effect is defined against controls in the SAME condition
    res = {"oracle": "cos of CLR-normalized surface-protein response, same cells",
           "proteins": prot_names, "min_cells": MIN_CELLS, "per_condition": {}}
    rows = []

    for cnd in sorted(set(cond.tolist())):
        m_cnd = cond == cnd
        ctrl_idx = np.where(m_cnd & is_ctrl)[0]
        if len(ctrl_idx) < MIN_CELLS:
            continue
        rna_ctrl = R[ctrl_idx].mean(0)
        prot_ctrl = P[ctrl_idx].mean(0)

        kos, cells, rna_d, prot_d, mag = [], {}, {}, {}, {}
        for k in sorted(set(pert[m_cnd & ~is_ctrl].tolist())):
            idx = np.where(m_cnd & (pert == k) & ~is_ctrl)[0]
            if len(idx) < MIN_CELLS:
                continue
            kos.append(k)
            cells[k] = R[idx].astype(np.float64)
            rna_d[k] = R[idx].mean(0) - rna_ctrl
            prot_d[k] = P[idx].mean(0) - prot_ctrl
            mag[k] = float(np.linalg.norm(rna_d[k]))
        if len(kos) < 10:
            print(f"  {cnd}: only {len(kos)} KOs with >= {MIN_CELLS} cells, skipped")
            continue
        print(f"\n{cnd}: {len(kos)} knockouts, {len(ctrl_idx)} control cells", flush=True)

        rng = np.random.default_rng(SEED)
        for qi, q in enumerate(kos):
            if qi % 25 == 0:
                print(f"    {cnd}: query {qi}/{len(kos)}", flush=True)
            cand = [c for c in kos if c != q]
            qc = cells[q][rng.choice(len(cells[q]), min(len(cells[q]), MAX_CELLS),
                                     replace=False)]
            e, mc, mm, mo, orc = [], [], [], [], []
            for c in cand:
                cc = cells[c][rng.choice(len(cells[c]), min(len(cells[c]), MAX_CELLS),
                                         replace=False)]
                e.append(score_energy(qc, cc, max_cells=MAX_CELLS, seed=SEED))
                mc.append(score_mean_cosine(cc, qc, control_P=rna_ctrl, control_Q=rna_ctrl))
                mm.append(-abs(mag[c] - mag[q]))          # query-dependent scalar null
                mo.append(mag[c])                          # query-INDEPENDENT sanity check
                orc.append(_cos(prot_d[q], prot_d[c]))     # THE ORACLE (protein layer)
            orc = np.asarray(orc)
            arrs = {"energy": np.asarray(e), "mean_cosine_ctrl": np.asarray(mc),
                    "magnitude_match": np.asarray(mm), "magnitude_only": np.asarray(mo)}
            rec = {"condition": cnd, "query": q, "n_cand": len(cand), "query_magnitude": mag[q]}
            for k, v in arrs.items():
                rec[f"{k}_rho"] = float(stats.spearmanr(v, orc)[0])

            def resid(v):
                rv, rm = stats.rankdata(v), stats.rankdata(arrs["magnitude_match"])
                return rv - np.polyval(np.polyfit(rm, rv, 1), rm)
            rec["energy_rho_partial_magmatch"] = float(
                stats.spearmanr(resid(arrs["energy"]), resid(orc))[0])
            rows.append(rec)

    df = pd.DataFrame(rows)
    if df.empty:
        raise RuntimeError("no queries survived; refusing to write an empty result.")
    df.to_csv(OUT / "class_c_protein_oracle.csv", index=False)

    SCORERS = ["energy", "mean_cosine_ctrl", "magnitude_match", "magnitude_only"]
    print(f"\n{'='*78}")
    print("PROTEIN ORACLE: does RNA retrieval recover the surface-protein response?")
    print(f"{'ranking':24s} {'median rho':>11s} {'mean rho':>10s} {'frac>0':>8s}")
    print("-" * 78)
    for k in SCORERS:
        c = f"{k}_rho"
        res[c] = {"median": float(df[c].median()), "mean": float(df[c].mean()),
                  "frac_positive": float((df[c] > 0).mean())}
        print(f"  {k:22s} {df[c].median():+11.4f} {df[c].mean():+10.4f} "
              f"{(df[c] > 0).mean():>8.2f}")
    pm = df.energy_rho_partial_magmatch
    res["energy_rho_partial_magmatch"] = {"median": float(pm.median()), "mean": float(pm.mean())}
    print(f"\n  {'energy | magnitude-match':22s} {pm.median():+11.4f} {pm.mean():+10.4f}")

    print("\nPER CONDITION (the honest unit: conditions, not pseudo-replicated queries)")
    res["per_condition"] = {}
    for cnd, s in df.groupby("condition"):
        v = {k: float(s[f"{k}_rho"].median()) for k in SCORERS}
        v["n_queries"] = int(len(s))
        v["energy_partial"] = float(s.energy_rho_partial_magmatch.median())
        v["energy_beats_magmatch"] = int((s.energy_rho > s.magnitude_match_rho).sum())
        res["per_condition"][cnd] = v
        print(f"  {cnd:14s} (n={v['n_queries']:>3d}): energy {v['energy']:+.3f} | "
              f"mean {v['mean_cosine_ctrl']:+.3f} | magmatch {v['magnitude_match']:+.3f} | "
              f"energy|partial {v['energy_partial']:+.3f} | "
              f"energy>magmatch {v['energy_beats_magmatch']}/{v['n_queries']}")

    w = stats.wilcoxon(df.energy_rho, df.magnitude_match_rho)
    res["wilcoxon_energy_vs_magmatch"] = {
        "p": float(w.pvalue), "n": int(len(df)),
        "note": "queries within a condition share a candidate pool, so this is anticonservative."}
    print(f"\nenergy > magnitude-match in "
          f"{int((df.energy_rho > df.magnitude_match_rho).sum())}/{len(df)} queries "
          f"(Wilcoxon p={w.pvalue:.2e}, anticonservative)")

    json.dump(res, open(OUT / "class_c_protein_oracle.json", "w"), indent=2)
    print(f"\nwrote {OUT/'class_c_protein_oracle.csv'} and .json")


if __name__ == "__main__":
    main()
