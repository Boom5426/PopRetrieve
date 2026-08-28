#!/usr/bin/env python
"""Experiment 15 — Resistance-precursor exploration (independent exploratory branch).

Hypothesis: perturbation-response *divergence* — the degree to which a perturbation
splits a population into distinct subpopulations rather than shifting it uniformly —
marks the emergence of resistance/persistence-associated minority states.

This is an EXPLORATORY side-branch (protocol §; does NOT gate the Nature Methods
main line). It uses only in-repo Frangieh melanoma Perturb-CITE-seq data.

Three parts:
  A  data-supported : for each KO, measure response divergence; identify divergent
                      minority states; test whether high-divergence minority states
                      are enriched for immune-evasion / antigen-presentation-loss /
                      quiescence marker programs relative to low-divergence states.
  B  honest-limit   : divergence -> post-treatment survival/expansion.  Frangieh has
                      NO drug timecourse / no post-treatment readout, so this is
                      reported as a limitation, not a result.
  C  method-contrast: does the PopRetrieve-top perturbation cover the resistance-associated
                      minority state that the mean-top perturbation collapses away?

Usage:
    QUICK=1 python src/experiments/exp15_resistance_precursor_exploration.py
    python src/experiments/exp15_resistance_precursor_exploration.py
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from retrieval.metrics import score_energy, score_mean_cosine
from utils.io import results_path, write_csv
from utils.logging import log, section

OUT = "exp15_resistance_precursor_exploration"

# Resistance-associated marker programs (melanoma immunotherapy).
# Only programs with adequate coverage in the Frangieh 2000-HVG panel are scored.
MARKER_SETS = {
    "IFN_response": ["STAT1", "IRF1", "GBP1", "GBP2", "ISG15", "B2M", "HLA-A", "HLA-B",
                     "HLA-C", "TAP1", "IDO1", "CXCL10", "CXCL11", "WARS", "PSMB9"],
    "antigen_presentation": ["B2M", "HLA-A", "HLA-B", "HLA-C", "HLA-E", "TAP1", "TAP2",
                             "TAPBP", "PSMB8", "PSMB9", "NLRC5", "CIITA"],
    "antigen_presentation_loss": ["B2M", "HLA-A", "HLA-B", "HLA-C", "TAP1", "PSMB8", "PSMB9"],
    "AXL_mesenchymal": ["AXL", "NGFR", "EGFR", "WNT5A", "JUN", "FOSL1", "SERPINE1",
                        "TGFBI", "INHBA"],
    "quiescence": ["CDKN1A", "CDKN1B", "CDKN2A", "MKI67", "TOP2A", "PCNA", "CCNB1"],
}
# Proliferation genes whose LOW expression marks quiescent/persister-like states
PROLIF_GENES = ["MKI67", "TOP2A", "PCNA", "CCNB1"]


def _score_program(X, gene_idx, ref_mu=None, ref_sd=None):
    """Mean z-scored marker-program expression per cell.

    Standardization uses a COMMON reference (ref_mu/ref_sd computed over the full
    query population) so that subgroup means are comparable — standardizing within
    each subgroup separately would force every subgroup mean to ~0.
    """
    if not gene_idx:
        return np.zeros(len(X))
    sub = X[:, gene_idx]
    if ref_mu is None:
        ref_mu = sub.mean(0)
    if ref_sd is None:
        ref_sd = sub.std(0) + 1e-8
    return ((sub - ref_mu) / ref_sd).mean(1)


def _response_divergence(treated_X, ctrl_mean, k=2, seed=0):
    """Divergence = between-subpopulation variance ratio of the treated response.

    High divergence = the KO splits cells into distinct response modes (not a uniform
    shift).  Returns (divergence, labels, minority_state_id, subpop_separation)."""
    from sklearn.cluster import KMeans
    delta = treated_X - ctrl_mean  # response relative to control
    if len(delta) < k + 1:
        return 0.0, np.zeros(len(delta), dtype=int), 0, 0.0
    km = KMeans(n_clusters=k, n_init=3, random_state=seed, max_iter=100).fit(delta)
    lab = km.labels_
    mu = delta.mean(0)
    sst = float(np.sum((delta - mu) ** 2))
    if sst < 1e-12:
        return 0.0, lab, 0, 0.0
    ssw = sum(float(np.sum((delta[lab == c] - delta[lab == c].mean(0)) ** 2))
              for c in np.unique(lab))
    divergence = (sst - ssw) / sst
    uniq, counts = np.unique(lab, return_counts=True)
    minority = int(uniq[np.argmin(counts)])
    # separation between subpop centroids (cosine distance)
    cents = np.array([delta[lab == c].mean(0) for c in uniq])
    if len(cents) >= 2:
        cn = cents / (np.linalg.norm(cents, axis=1, keepdims=True) + 1e-12)
        sep = float(1 - (cn[0] @ cn[1]))
    else:
        sep = 0.0
    return float(divergence), lab, minority, sep


# ── Part A: divergence -> marker-program enrichment ──────────────────────────

def run_part_A(ds, contexts, marker_idx, prolif_idx, min_cells=40, seed=0):
    """For each (context, KO): compute response divergence, split into subpops, and
    score marker programs in the divergent minority state vs the majority state."""
    rng = np.random.default_rng(seed)
    rows = []
    for ctx in contexts:
        ctrl_mean = ds.control_mean(ctx)
        kos = sorted(set(np.asarray(ds.pert)[(ds.context == ctx) & (~ds.is_control)].tolist()))
        for ko in kos:
            rows_idx = ds.treated_rows(ctx, ko)
            if len(rows_idx) < min_cells:
                continue
            if len(rows_idx) > 400:
                rows_idx = rng.choice(rows_idx, 400, replace=False)
            X = ds.X[rows_idx]
            div, lab, minority, sep = _response_divergence(X, ctrl_mean, seed=seed)
            majority = 1 - minority if set(np.unique(lab)) == {0, 1} else minority
            X_min = X[lab == minority]
            X_maj = X[lab == majority] if (lab == majority).any() else X[lab != minority]
            if len(X_min) < 5 or len(X_maj) < 5:
                continue
            row = {"context": ctx, "ko": ko, "n_cells": len(X),
                   "response_divergence": div, "subpop_separation": sep,
                   "minority_frac": float((lab == minority).mean()), "seed": seed}
            # Marker-program differential: minority - majority (standardized program score)
            # Reference statistics from the FULL query population (common baseline)
            for prog, gidx in marker_idx.items():
                if not gidx:
                    continue
                ref_mu = X[:, gidx].mean(0)
                ref_sd = X[:, gidx].std(0) + 1e-8
                s_min = _score_program(X_min, gidx, ref_mu, ref_sd).mean()
                s_maj = _score_program(X_maj, gidx, ref_mu, ref_sd).mean()
                row[f"prog_{prog}_minority_minus_majority"] = float(s_min - s_maj)
            # Proliferation (low = quiescent/persister-like)
            if prolif_idx:
                p_min = X_min[:, prolif_idx].mean()
                p_maj = X_maj[:, prolif_idx].mean()
                row["proliferation_minority_minus_majority"] = float(p_min - p_maj)
            rows.append(row)
    return pd.DataFrame(rows)


def _enrichment_summary(dfA):
    """Correlate response_divergence with each marker program's minority enrichment."""
    prog_cols = [c for c in dfA.columns if c.startswith("prog_")]
    rows = []
    for c in prog_cols:
        prog = c.replace("prog_", "").replace("_minority_minus_majority", "")
        # high-divergence vs low-divergence split at median
        med = dfA.response_divergence.median()
        hi = dfA[dfA.response_divergence >= med][c]
        lo = dfA[dfA.response_divergence < med][c]
        from scipy.stats import mannwhitneyu
        try:
            _, p = mannwhitneyu(hi.dropna(), lo.dropna(), alternative="two-sided")
        except Exception:
            p = float("nan")
        rows.append({
            "program": prog,
            "corr_divergence_enrichment": float(dfA.response_divergence.corr(dfA[c])),
            "mean_enrichment_high_div": float(hi.mean()),
            "mean_enrichment_low_div": float(lo.mean()),
            "high_minus_low": float(hi.mean() - lo.mean()),
            "mannwhitney_p": float(p),
        })
    return pd.DataFrame(rows).sort_values("high_minus_low", ascending=False)


# ── Part C: PopRetrieve-top vs mean-top minority rescue ─────────────────────────────

def run_part_C(ds, contexts, min_cells=40, seed=0, n_query=6):
    """Does the PopRetrieve-selected KO cover the divergent resistance minority state that the
    mean-selected KO collapses away?  Uses one held-out KO as the query, others as library."""
    rng = np.random.default_rng(seed)
    rows = []
    for ctx in contexts:
        ctrl_mean = ds.control_mean(ctx)
        kos = sorted(set(np.asarray(ds.pert)[(ds.context == ctx) & (~ds.is_control)].tolist()))
        # pick queries with highest divergence (most resistance-relevant)
        div_by_ko = {}
        for ko in kos:
            ridx = ds.treated_rows(ctx, ko)
            if len(ridx) < min_cells:
                continue
            if len(ridx) > 300:
                ridx = rng.choice(ridx, 300, replace=False)
            X = ds.X[ridx]
            div, lab, minority, sep = _response_divergence(X, ctrl_mean, seed=seed)
            div_by_ko[ko] = (div, ridx, lab, minority)
        top_kos = sorted(div_by_ko, key=lambda k: -div_by_ko[k][0])[:n_query]
        for ko in top_kos:
            div, ridx, lab, minority = div_by_ko[ko]
            qX = ds.X[ridx]
            mino_mean = qX[lab == minority].mean(0)
            lib = [k for k in kos if k != ko]
            cand = {}
            for k in lib:
                kr = ds.treated_rows(ctx, k)
                if len(kr) < 20:
                    continue
                if len(kr) > 150:
                    kr = rng.choice(kr, 150, replace=False)
                cand[k] = ds.X[kr]
            if len(cand) < 5:
                continue
            names = list(cand.keys())
            # mean-cosine top vs PopRetrieve-energy top
            mean_sc = np.array([score_mean_cosine(cand[n], qX, control_P=ctrl_mean,
                                                  control_Q=ctrl_mean) for n in names])
            energy_sc = np.array([score_energy(cand[n], qX, max_cells=min(150, len(cand[n]), len(qX)),
                                               seed=seed) for n in names])
            mean_top = names[int(np.argmax(mean_sc))]
            dart_top = names[int(np.argmax(energy_sc))]

            def _mino_cov(P):
                pm = P.mean(0)
                return float((np.dot(pm, mino_mean) /
                              (np.linalg.norm(pm) * np.linalg.norm(mino_mean) + 1e-12) + 1) / 2)

            rows.append({
                "context": ctx, "query_ko": ko, "response_divergence": div,
                "mean_top_ko": mean_top, "dart_top_ko": dart_top,
                "same_pick": mean_top == dart_top,
                "mean_top_minority_cov": _mino_cov(cand[mean_top]),
                "dart_top_minority_cov": _mino_cov(cand[dart_top]),
                "dart_minority_rescue": _mino_cov(cand[dart_top]) - _mino_cov(cand[mean_top]),
                "seed": seed,
            })
    return pd.DataFrame(rows)


def run(quick=False):
    section(f"EXP15 RESISTANCE-PRECURSOR EXPLORATION ({'QUICK' if quick else 'FULL'})")
    from data.load_frangieh import load_frangieh
    ds = load_frangieh()
    genes = list(ds.gene_names)
    gidx = {g: i for i, g in enumerate(genes)}
    marker_idx = {prog: [gidx[g] for g in gl if g in gidx] for prog, gl in MARKER_SETS.items()}
    prolif_idx = [gidx[g] for g in PROLIF_GENES if g in gidx]
    log("  marker coverage: " + ", ".join(f"{p}={len(ix)}" for p, ix in marker_idx.items()))

    # Immune-active contexts (resistance-relevant); Control is baseline
    active = [c for c in ds.contexts if c != "Control"]
    contexts = active[:1] if quick else active
    seed = 0

    # Part A: divergence -> marker enrichment
    dfA = run_part_A(ds, contexts, marker_idx, prolif_idx, seed=seed)
    write_csv(dfA, results_path(OUT, "divergence_marker_enrichment.csv"))
    log(f"  Part A: {len(dfA)} KO x context rows")

    dfE = _enrichment_summary(dfA)
    write_csv(dfE, results_path(OUT, "enrichment_summary.csv"))
    section("PART A — divergence -> program enrichment (high vs low divergence)")
    for _, r in dfE.iterrows():
        sig = "*" if r.mannwhitney_p < 0.05 else " "
        log(f"  {sig} {r.program:26s} high-low={r.high_minus_low:+.3f} "
            f"corr={r.corr_divergence_enrichment:+.3f} p={r.mannwhitney_p:.3g}")

    # Part C: PopRetrieve vs mean minority rescue
    dfC = run_part_C(ds, contexts, seed=seed, n_query=4 if quick else 8)
    write_csv(dfC, results_path(OUT, "dart_vs_mean_minority_rescue.csv"))
    section("PART C — PopRetrieve-top vs mean-top minority rescue")
    if len(dfC) > 0:
        log(f"  queries: {len(dfC)}, different pick: {int((~dfC.same_pick).sum())}/{len(dfC)}")
        log(f"  mean PopRetrieve minority rescue: {dfC.dart_minority_rescue.mean():+.4f} "
            f"(>0 => PopRetrieve covers resistance minority better)")
        log(f"  frac queries PopRetrieve rescues: {(dfC.dart_minority_rescue > 0).mean():.2f}")

    return dfA, dfE, dfC


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    quick = args.quick or os.environ.get("QUICK") == "1"
    run(quick=quick)


if __name__ == "__main__":
    main()
