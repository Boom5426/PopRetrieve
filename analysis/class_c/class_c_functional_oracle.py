#!/usr/bin/env python3
"""Class C, semantically matched: does transcriptional similarity recover FUNCTIONAL similarity?

WHY THIS SCRIPT EXISTS
----------------------
The previous Class C analysis (class_c_magnitude_control_v2.py) graded a *similarity*
retriever against *absolute potency*. Those are different questions, and the mismatch is
ours, not the method's:

    retrieval asks   : which candidate's response distribution most resembles the query's?
    absolute potency : which candidate kills cells hardest?

A correctly working similarity retriever handed a weak query SHOULD return other weak
drugs. So "energy retrieval anti-correlates with potency" is close to definitional, and
"a query-independent magnitude scalar beats it" is near-tautological, because potency is
largely driven by response magnitude and the magnitude scalar sorts by magnitude. That
comparison cannot support a claim about therapeutic utility in either direction. It is
retained here only as a confounder audit.

The semantically matched external oracle for a retrieval task is DRUG-DRUG FUNCTIONAL
SIMILARITY: do the query drug and the candidate drug behave alike in an independent
functional assay? GDSC2 supplies exactly this. Each drug has a dose-response AUC profile
across ~969 cell lines. Two drugs with similar cross-cell-line sensitivity patterns are
functionally similar, regardless of how potent either is on average.

    oracle(q, c) = Spearman corr( AUC_profile(q), AUC_profile(c) ) across GDSC cell lines

This oracle is:
  * QUERY-DEPENDENT, so a query-independent scalar cannot game it. magnitude_only now serves
    as a falsifiable sanity check: it must land at ~0. If it does not, this script is wrong.
  * OUT-OF-CONTEXT. The three SciPlex3 lines (A549, K-562, MCF7) are EXCLUDED from the
    profile, so the oracle is never evaluated in the same biological context the
    transcriptional data came from.
  * MEAN-CENTERED per drug by construction (correlation), so a drug's overall potency LEVEL
    does not drive the similarity; only its SELECTIVITY PATTERN does. This is what makes the
    oracle independent of the magnitude channel that contaminated the potency version.

CONFOUNDER CONTROLS (a query-dependent oracle needs a query-dependent null)
  magnitude_only    rank by candidate response norm. QUERY-INDEPENDENT: identical ordering for
                    every query. Sanity check, must be ~0.
  magnitude_match   rank by -|mag(c) - mag(q)|. QUERY-DEPENDENT and performs no distributional
                    comparison. This is the null that a distributional score must beat.
  potency_match     rank by -|AUC(c) - AUC(q)| in the query's own line. Tests whether the
                    oracle is merely re-encoding potency level.

Cell-line main effects (some lines are broadly drug-sensitive) inflate every drug-drug
correlation. The profile is therefore double-centered: each cell line's mean AUC, taken
across ALL 286 GDSC2 drugs rather than only our 35, is subtracted before correlating. Both
the centered and uncentered oracles are reported; the centered one is primary.

    PYTHONPATH=src python analysis/class_c/class_c_functional_oracle.py
"""
from pathlib import Path as _P
REPO = _P(__file__).resolve().parents[2]
import sys
sys.path.insert(0, str(REPO / "src"))

import json
import numpy as np
import pandas as pd
from scipy import stats

from data.load_sciplex3 import load_sciplex3
from retrieval.metrics import score_energy, score_mean_cosine

SEED = 42
DOSE = 10000.0             # 10 uM, the dose every other retrieval experiment in the paper uses
GDSC_SOURCE = "GDSC2"      # GDSC1 and GDSC2 AUCs are not on a common scale
MIN_SHARED_LINES = 100     # a drug-drug correlation needs enough shared cell lines to mean anything
SCIPLEX_LINES = ["A549", "K562", "MCF7"]
GDSC_NAMES_OF_SCIPLEX_LINES = ["A549", "K-562", "MCF7"]   # GDSC spelling; held out of the profile

OUT = REPO / "results" / "upgrade"
# One canonical location, shared with analysis/class_c/match_drugs_v2.py, which reads it from
# RESULTS_AUDIT = results/upgrade. This used to point at results/_audit/, a directory that does
# not exist anywhere in the repository, so the two consumers of the same workbook disagreed and
# the one feeding main-text Fig. 4h/4i could never find it (audited 2026-07-27).
GDSC_XLSX = REPO / "results" / "upgrade" / "GDSC2_fitted_dose_response.xlsx"

np.random.seed(SEED)


def dense(a):
    return a.toarray() if hasattr(a, "toarray") else np.asarray(a)


def build_functional_oracle(gdsc_drugs):
    """Drug x drug functional-similarity matrices from GDSC2 cross-cell-line AUC profiles.

    Returns (sim_centered, sim_raw, n_shared), each a DataFrame indexed by GDSC drug name.
    The SciPlex3 cell lines are excluded so the oracle is measured out of context.
    """
    if not GDSC_XLSX.exists():
        raise FileNotFoundError(
            f"{GDSC_XLSX} is missing, and this analysis cannot be re-run without it.\n"
            f"Download the GDSC2 fitted dose-response workbook from "
            f"https://www.cancerrxgene.org (bulk download; the file is named "
            f"GDSC2_fitted_dose_response_<RELEASE>.xlsx) and place it here.\n"
            f"The published numbers use GDSC2 release 8.5 "
            f"(GDSC2_fitted_dose_response_27Oct23.xlsx), verified: its AUCs match "
            f"results/upgrade/drug_match_table.csv 6/6 at 1e-5. Download that release and place "
            f"it here. If a different release is used, verify against drug_match_table.csv first "
            f"(DRUG_ID, cell line, AUC per matched compound); a mismatch means the Class-C "
            f"numbers must be recomputed and the change reported.")
    g = pd.read_excel(GDSC_XLSX)
    g = g[g.DATASET == GDSC_SOURCE]

    # hold out the three SciPlex3 contexts: the oracle must not be scored in the same
    # biological context the transcriptional query was measured in.
    n_before = g.CELL_LINE_NAME.nunique()
    g = g[~g.CELL_LINE_NAME.isin(GDSC_NAMES_OF_SCIPLEX_LINES)]
    print(f"GDSC2: {n_before} cell lines -> {g.CELL_LINE_NAME.nunique()} after holding out "
          f"{GDSC_NAMES_OF_SCIPLEX_LINES}")

    # drugs x cell lines AUC matrix over ALL GDSC2 drugs (needed for honest cell-line centering)
    full = g.pivot_table(index="DRUG_NAME", columns="CELL_LINE_NAME", values="AUC", aggfunc="mean")
    print(f"full AUC matrix: {full.shape[0]} drugs x {full.shape[1]} cell lines")

    # cell-line main effect estimated on ALL drugs, not just our 35
    line_mean = full.mean(axis=0)
    centered_full = full.sub(line_mean, axis=1)

    missing = [d for d in gdsc_drugs if d not in full.index]
    if missing:
        raise KeyError(f"matched GDSC drugs absent from the GDSC2 dose-response table: {missing}")
    raw = full.loc[gdsc_drugs]
    cen = centered_full.loc[gdsc_drugs]

    def pairwise(M):
        n = len(M)
        S = pd.DataFrame(np.full((n, n), np.nan), index=M.index, columns=M.index)
        N = pd.DataFrame(np.zeros((n, n), dtype=int), index=M.index, columns=M.index)
        V = M.values
        for i in range(n):
            for j in range(i + 1, n):
                ok = np.isfinite(V[i]) & np.isfinite(V[j])
                N.iloc[i, j] = N.iloc[j, i] = int(ok.sum())
                if ok.sum() >= MIN_SHARED_LINES:
                    r = stats.spearmanr(V[i][ok], V[j][ok])[0]
                    S.iloc[i, j] = S.iloc[j, i] = float(r)
        return S, N

    sim_cen, n_shared = pairwise(cen)
    sim_raw, _ = pairwise(raw)
    off = ~np.eye(len(sim_cen), dtype=bool)
    print(f"oracle: {np.isfinite(sim_cen.values[off]).sum() // 2} usable drug pairs "
          f"(>= {MIN_SHARED_LINES} shared lines); median shared lines "
          f"{int(np.median(n_shared.values[off]))}")
    print(f"centered oracle similarity: median {np.nanmedian(sim_cen.values[off]):+.3f}, "
          f"range [{np.nanmin(sim_cen.values[off]):+.3f}, {np.nanmax(sim_cen.values[off]):+.3f}]")
    return sim_cen, sim_raw, n_shared


def main() -> None:
    match = pd.read_csv(OUT / "drug_match_table.csv")
    match = match[match.gdsc_source == GDSC_SOURCE].copy()
    match = match[match.sp_drug != "S-Ruxolitinib (INCB018424)"].copy()   # duplicate mapping
    sp2gdsc = dict(zip(match.sp_drug, match.gdsc_drug))
    gdsc_drugs = sorted(set(match.gdsc_drug))
    print(f"matched drugs: {len(sp2gdsc)} SciPlex3 names -> {len(gdsc_drugs)} GDSC2 drugs\n")

    sim_cen, sim_raw, n_shared = build_functional_oracle(gdsc_drugs)

    ds = load_sciplex3()
    obs = ds.obs
    if "dose_value" not in obs.columns:
        raise RuntimeError("no dose_value column: cannot restrict to 10 uM.")
    dose_v = obs["dose_value"].values

    rows = []
    for line in SCIPLEX_LINES:
        lm = match[match.cell_line == line]
        via = dict(zip(lm.sp_drug, lm.AUC))          # potency in the query's OWN line
        in_line = (obs["cell_line"] == line).values
        at_dose = in_line & (dose_v == DOSE)
        ctrl = dense(ds.X[in_line & obs["is_control"].values]).mean(0).astype(np.float64)

        cells, dmean, mag = {}, {}, {}
        for d in sorted(lm.sp_drug.unique()):
            m = at_dose & (obs["perturbation"] == d).values & (~obs["is_control"].values)
            if m.sum() >= 10:
                C = dense(ds.X[m]).astype(np.float64)
                cells[d] = C
                dmean[d] = C.mean(0) - ctrl
                mag[d] = float(np.linalg.norm(dmean[d]))
        valid = sorted(cells)
        if len(valid) < 8:
            print(f"  {line}: only {len(valid)} drugs at 10 uM, skipped")
            continue
        print(f"  {line}: {len(valid)} drugs at 10 uM")

        for q in valid:
            gq = sp2gdsc[q]
            # candidates must have a defined oracle value against this query
            cand = [c for c in valid if c != q and np.isfinite(sim_cen.loc[gq, sp2gdsc[c]])]
            if len(cand) < 8:
                continue
            qc = cells[q]

            e_sim, cos_ctrl, cos_raw, magonly, magmatch, potmatch = [], [], [], [], [], []
            orc_cen, orc_raw = [], []
            for c in cand:
                gc = sp2gdsc[c]
                # score_energy returns MINUS the distance: HIGHER = MORE SIMILAR.
                e_sim.append(score_energy(qc, cells[c], max_cells=500, seed=SEED))
                cos_ctrl.append(score_mean_cosine(cells[c], qc, control_P=ctrl, control_Q=ctrl))
                cos_raw.append(score_mean_cosine(cells[c], qc))
                magonly.append(mag[c])                              # query-independent
                magmatch.append(-abs(mag[c] - mag[q]))              # query-dependent null
                potmatch.append(-abs(via[c] - via[q]))              # is the oracle just potency?
                orc_cen.append(float(sim_cen.loc[gq, gc]))
                orc_raw.append(float(sim_raw.loc[gq, gc]))

            arrs = {k: np.asarray(v) for k, v in dict(
                energy=e_sim, mean_cosine_ctrl=cos_ctrl, mean_cosine_raw=cos_raw,
                magnitude_only=magonly, magnitude_match=magmatch, potency_match=potmatch).items()}
            orc_cen = np.asarray(orc_cen)
            orc_raw = np.asarray(orc_raw)

            # every scorer here is a SIMILARITY (higher = ranked first); the oracle is likewise
            # a similarity. Spearman between the two similarity vectors is the alignment.
            rec = {"cell_line": line, "query_drug": q, "gdsc_drug": gq, "n_cand": len(cand),
                   "query_magnitude": mag[q], "query_auc": via[q]}
            for k, v in arrs.items():
                rec[f"{k}_rho"] = float(stats.spearmanr(v, orc_cen)[0])
                rec[f"{k}_rho_uncentered"] = float(stats.spearmanr(v, orc_raw)[0])

            # partial: does energy still track the functional oracle once the query-dependent
            # magnitude-matching channel is removed? (rank-residualize both sides on magmatch)
            def resid(v):
                rv, rm = stats.rankdata(v), stats.rankdata(arrs["magnitude_match"])
                b = np.polyfit(rm, rv, 1)
                return rv - np.polyval(b, rm)
            rec["energy_rho_partial_magmatch"] = float(
                stats.spearmanr(resid(arrs["energy"]), resid(orc_cen))[0])
            rec["oracle_vs_potencymatch_rho"] = float(
                stats.spearmanr(arrs["potency_match"], orc_cen)[0])
            rows.append(rec)

    df = pd.DataFrame(rows)
    if df.empty:
        raise RuntimeError("no queries survived; refusing to write an empty result.")
    df.to_csv(OUT / "class_c_functional_oracle.csv", index=False)

    SCORERS = ["energy", "mean_cosine_ctrl", "mean_cosine_raw",
               "magnitude_match", "magnitude_only", "potency_match"]
    res = {"n_queries": int(len(df)), "dose_nM": DOSE, "gdsc_source": GDSC_SOURCE,
           "oracle": "Spearman corr of GDSC2 AUC profiles across cell lines, "
                     "SciPlex3 lines held out, cell-line-mean centered on all 286 drugs",
           "min_shared_lines": MIN_SHARED_LINES}

    print(f"\n{'='*72}\nSEMANTICALLY MATCHED ORACLE: drug-drug functional similarity")
    print(f"{'ranking':24s} {'median rho':>11s} {'mean rho':>10s} {'frac>0':>8s}")
    print("-" * 72)
    for k in SCORERS:
        c = f"{k}_rho"
        res[c] = {"median": float(df[c].median()), "mean": float(df[c].mean()),
                  "frac_positive": float((df[c] > 0).mean())}
        print(f"  {k:22s} {df[c].median():+11.4f} {df[c].mean():+10.4f} "
              f"{(df[c] > 0).mean():>8.2f}")

    print(f"\n  {'energy, partial on magnitude-match':22s} "
          f"{df.energy_rho_partial_magmatch.median():+11.4f} "
          f"{df.energy_rho_partial_magmatch.mean():+10.4f}")
    res["energy_rho_partial_magmatch"] = {
        "median": float(df.energy_rho_partial_magmatch.median()),
        "mean": float(df.energy_rho_partial_magmatch.mean())}
    res["oracle_vs_potencymatch_rho"] = {
        "median": float(df.oracle_vs_potencymatch_rho.median()),
        "note": "if this is large, the functional oracle is re-encoding potency level and is "
                "not an independent selectivity signal."}
    print(f"  oracle vs potency-matching (is the oracle just potency?): "
          f"median rho {df.oracle_vs_potencymatch_rho.median():+.3f}")

    print("\nSANITY CHECK. magnitude_only is query-independent: on a query-dependent oracle it "
          "must land at ~0.\n  observed median: "
          f"{df.magnitude_only_rho.median():+.4f}")

    print("\nPER CELL LINE (the honest unit: 3 lines, not 100+ pseudo-replicated queries)")
    res["per_line"] = {}
    for line, s in df.groupby("cell_line"):
        d = {k: float(s[f"{k}_rho"].median()) for k in SCORERS}
        d["n_queries"] = int(len(s))
        d["energy_partial"] = float(s.energy_rho_partial_magmatch.median())
        res["per_line"][line] = d
        print(f"  {line} (n={d['n_queries']:>3d}): energy {d['energy']:+.3f} | "
              f"mean(ctrl) {d['mean_cosine_ctrl']:+.3f} | magmatch {d['magnitude_match']:+.3f} "
              f"| magonly {d['magnitude_only']:+.3f} | energy|partial {d['energy_partial']:+.3f}")

    # Sign test on the honest unit is impossible with n=3 lines; report per-line direction and
    # a query-level Wilcoxon flagged as anticonservative, exactly as in the potency analysis.
    w = stats.wilcoxon(df.energy_rho, df.magnitude_match_rho)
    res["wilcoxon_energy_vs_magmatch"] = {
        "stat": float(w.statistic), "p": float(w.pvalue), "n": int(len(df)),
        "note": "queries within a cell line share a candidate pool, so this p-value is "
                "anticonservative. The honest unit is the 3 cell lines."}
    print(f"\nenergy > magnitude-match in {int((df.energy_rho > df.magnitude_match_rho).sum())}"
          f"/{len(df)} queries (Wilcoxon p={w.pvalue:.2e}, anticonservative; see note)")

    json.dump(res, open(OUT / "class_c_functional_oracle.json", "w"), indent=2)
    print(f"\nwrote {OUT/'class_c_functional_oracle.csv'} and .json")


if __name__ == "__main__":
    main()
