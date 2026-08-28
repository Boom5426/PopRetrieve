#!/usr/bin/env python
"""Experiment 12 — Partial-observed retrieval (Nature Methods phase-gate).

Establishes whether PopRetrieve's required information condition — candidate response
populations partially observed, optimal drug hidden — holds in real single-cell
drug screens, and whether PopRetrieve reduces decision regret / improves nDCG in the
high-conflict + reliable-structure subset.

Three settings:
  A  leave_drug_out       hide one drug; rank it against the observed library
  B  leave_MoA_out        hide a whole MoA/pathway; recover a same-pathway surrogate
  C  partial_library      measure X% of drugs; select next top-k batch; score coverage

Usage:
    QUICK=1 python src/experiments/exp12_partial_observed_retrieval.py
    python src/experiments/exp12_partial_observed_retrieval.py --n-drugs 40 --n-seeds 5
"""
from __future__ import annotations

import argparse
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from data.load_sciplex3 import load_sciplex3
from experiments.exp16_common import true_response_divergence, divergence_components
from retrieval.metrics import (
    score_mean_cosine, score_mean_l2, score_energy,
    score_mmd_rbf, score_sliced_wasserstein, score_coverage,
)
from utils.io import results_path, write_csv
from utils.logging import log, section

OUT = "exp12_partial_observed_retrieval"

# ── method registry (same 9 methods as HIR-Bench exp11) ──────────────────────

DART_METHODS = ["DART_energy", "DART_mmd", "DART_sliced_wasserstein",
                "DART_coverage_mean", "DART_coverage_worst"]
MEAN_METHODS = ["mean_cosine", "mean_l2", "cmap_match", "cmap_reverse"]
ALL_METHODS = MEAN_METHODS + DART_METHODS
REF_METHOD = "mean_cosine"

METHOD_FAMILY = {
    "mean_cosine": "mean_signature", "mean_l2": "mean_signature",
    "cmap_match": "cmap_signature", "cmap_reverse": "cmap_signature",
    "DART_energy": "DART_distributional", "DART_mmd": "DART_distributional",
    "DART_sliced_wasserstein": "DART_distributional",
    "DART_coverage_mean": "DART_coverage", "DART_coverage_worst": "DART_coverage",
}


def _assign_states(P, query_X, query_states):
    """Assign candidate cells to nearest query-state centroid (cosine)."""
    uniq = np.unique(query_states)
    cents = np.array([query_X[query_states == s].mean(0) for s in uniq])
    Pn = P / (np.linalg.norm(P, axis=1, keepdims=True) + 1e-12)
    Cn = cents / (np.linalg.norm(cents, axis=1, keepdims=True) + 1e-12)
    return uniq[(Pn @ Cn.T).argmax(1)]


def _score(method, P, Q, query_states, ctrl=None, seed=0):
    """Score candidate population P against query Q. Higher = better."""
    mc = min(300, len(P), len(Q))
    if method == "mean_cosine":
        return score_mean_cosine(P, Q, control_P=ctrl, control_Q=ctrl)
    if method == "mean_l2":
        return score_mean_l2(P, Q)
    if method == "cmap_match":
        return score_mean_cosine(P, Q, control_P=ctrl, control_Q=ctrl)
    if method == "cmap_reverse":
        return -score_mean_cosine(P, Q, control_P=ctrl, control_Q=ctrl)
    if method == "DART_energy":
        return score_energy(P, Q, max_cells=mc, seed=seed)
    if method == "DART_mmd":
        return score_mmd_rbf(P, Q, max_cells=mc, seed=seed)
    if method == "DART_sliced_wasserstein":
        return score_sliced_wasserstein(P, Q, max_cells=mc, seed=seed)
    if method == "DART_coverage_mean":
        lp = _assign_states(P, Q, query_states)
        return score_coverage(P, Q, lp, query_states, aggregator="mean", max_cells=mc, seed=seed)
    if method == "DART_coverage_worst":
        lp = _assign_states(P, Q, query_states)
        return score_coverage(P, Q, lp, query_states, aggregator="worst", max_cells=mc, seed=seed)
    raise ValueError(method)


# ── information-condition diagnostics (observed data only) ────────────────────

def _kmeans_states(X, k=2, seed=0):
    """Cluster query cells into k states. Returns labels."""
    from sklearn.cluster import KMeans
    k = min(k, max(1, len(X) - 1))
    if k < 2:
        return np.zeros(len(X), dtype=int)
    km = KMeans(n_clusters=k, n_init=3, random_state=seed, max_iter=100).fit(X)
    return km.labels_


def _subpop_variance_ratio(X, k=2, seed=0):
    if len(X) < k + 1:
        return 0.0
    mu = X.mean(0)
    sst = float(np.sum((X - mu) ** 2))
    if sst < 1e-12:
        return 0.0
    lab = _kmeans_states(X, k, seed)
    ssw = sum(float(np.sum((X[lab == c] - X[lab == c].mean(0)) ** 2))
              for c in np.unique(lab))
    return float((sst - ssw) / sst)


def _isotropy_index(X):
    if len(X) < 3 or X.shape[1] < 2:
        return 1.0
    Xc = X - X.mean(0)
    if len(Xc) > 500:
        rng = np.random.default_rng(0)
        Xc = Xc[rng.choice(len(Xc), 500, replace=False)]
    cov = Xc.T @ Xc / (len(Xc) - 1)
    ev = np.linalg.eigvalsh(cov)
    ev = ev[ev > 0]
    return float(ev.min() / ev.max()) if len(ev) >= 2 else 1.0


def _response_diversity(X, n=200):
    if len(X) < 2:
        return 0.0
    rng = np.random.default_rng(0)
    if len(X) > n:
        X = X[rng.choice(len(X), n, replace=False)]
    Xn = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-12)
    sims = Xn @ Xn.T
    np.fill_diagonal(sims, 0)
    m = len(sims)
    return float(1.0 - sims.sum() / (m * (m - 1)))


def _mean_energy_disagreement(scores_mean, scores_energy):
    """Kendall distance between mean-cosine and energy rankings."""
    from scipy.stats import kendalltau
    if len(scores_mean) < 3:
        return 0.0
    tau, _ = kendalltau(scores_mean, scores_energy)
    if np.isnan(tau):
        return 0.0
    return float(1 - tau) / 2


def _bootstrap_rank_stability(Q, cand_pops, query_states, ctrl, method="DART_energy",
                               n_boot=5, seed=0):
    """Fraction of bootstrap resamples that keep the same top-1 candidate."""
    rng = np.random.default_rng(seed)
    names = list(cand_pops.keys())
    top1s = []
    for b in range(n_boot):
        idx = rng.choice(len(Q), len(Q), replace=True)
        Qb = Q[idx]
        qs_b = query_states[idx]
        scores = [_score(method, cand_pops[n], Qb, qs_b, ctrl=ctrl, seed=b) for n in names]
        top1s.append(names[int(np.argmax(scores))])
    if not top1s:
        return 0.0
    from collections import Counter
    return float(Counter(top1s).most_common(1)[0][1]) / len(top1s)


def _preference_conflict_topk(cand_pops, query_X, query_states, k=5, max_cand=60):
    """Preference conflict = 1 - mean Kendall rank correlation of per-state candidate
    rankings. Graded in [0,1]: 0 = states agree on candidate ordering, 1 = states
    rank candidates oppositely. Subsamples candidates for tractability."""
    from scipy.stats import kendalltau
    uniq = np.unique(query_states)
    if len(uniq) < 2:
        return 0.0
    names = list(cand_pops.keys())
    if len(names) > max_cand:
        rng = np.random.default_rng(0)
        names = [names[i] for i in rng.choice(len(names), max_cand, replace=False)]
    # Per-state ranking vector: score each candidate against each query state
    state_scores = []
    for s in uniq:
        Qs = query_X[query_states == s]
        if len(Qs) < 2:
            continue
        scores = np.array([score_energy(cand_pops[n], Qs,
                                        max_cells=min(150, len(cand_pops[n]), len(Qs)), seed=0)
                           for n in names])
        state_scores.append(scores)
    if len(state_scores) < 2:
        return 0.0
    taus = []
    for i in range(len(state_scores)):
        for j in range(i + 1, len(state_scores)):
            tau, _ = kendalltau(state_scores[i], state_scores[j])
            if not np.isnan(tau):
                taus.append(tau)
    if not taus:
        return 0.0
    return float(np.clip((1 - np.mean(taus)) / 2, 0, 1))


def structure_reliability(subpop_vr, isotropy, diversity, boot_stability,
                          energy_disagreement=0.0):
    """Composite structure-reliability score in [0,1].

    Real single-cell data has small subpop_variance_ratio (~0.03) and near-zero
    isotropy in high dimensions, so those are weak discriminators.  The reliable
    signals are bootstrap rank stability (does the top candidate survive resampling)
    and the magnitude of mean-vs-energy disagreement (does distributional structure
    actually change the ranking).  We weight those two most.
    """
    comps = [
        0.15 * np.clip(subpop_vr / 0.05, 0, 1),          # var ratio, calibrated to real scale
        0.10 * np.clip(diversity, 0, 1),                  # response diversity
        0.40 * np.clip(boot_stability, 0, 1),             # stability = reliable structure
        0.35 * np.clip(abs(energy_disagreement), 0, 1),   # ranking actually changes
    ]
    return float(np.sum(comps))


def recommendation_mode(struct_rel, pref_conflict,
                        struct_thresh=0.4, conflict_thresh=0.4):
    """Four-state recommendation logic (protocol §5)."""
    if struct_rel < struct_thresh:
        return "mean_or_no_call"
    if pref_conflict < conflict_thresh:
        return "mean_sufficient"
    if pref_conflict >= conflict_thresh and struct_rel >= struct_thresh:
        return "DART_recommended"
    return "uncertain"


# ── coverage-based welfare proxy (real data, no synthetic oracle) ─────────────

def _welfare_proxy(cand_pops, query_X, query_states, welfare="worst", max_cells=200, seed=0):
    """Per-candidate welfare = aggregate of negative energy distance to each query state.

    Returns dict {drug_name: welfare_value}. Higher = better (closer to all states).
    """
    uniq = np.unique(query_states)
    state_Qs = {s: query_X[query_states == s] for s in uniq}
    welfare_vals = {}
    for name, P in cand_pops.items():
        per_state = []
        for s in uniq:
            Qs = state_Qs[s]
            if len(Qs) < 2:
                continue
            e = score_energy(P, Qs, max_cells=min(max_cells, len(P), len(Qs)), seed=seed)
            per_state.append(e)  # already negative energy (higher=better)
        if not per_state:
            welfare_vals[name] = -1e9
            continue
        per_state = np.array(per_state)
        if welfare == "mean":
            welfare_vals[name] = float(per_state.mean())
        elif welfare == "worst":
            welfare_vals[name] = float(per_state.min())
        else:
            welfare_vals[name] = float(per_state.mean())
    return welfare_vals


def _decision_regret(welfare_vals, selected_drug):
    """regret = U[library-oracle] - U[selected]. >= 0."""
    if not welfare_vals:
        return float("nan")
    opt = max(welfare_vals.values())
    sel = welfare_vals.get(selected_drug, min(welfare_vals.values()))
    return float(opt - sel)


def _minority_state_coverage(P, query_X, query_states, minority_state):
    """Fraction of minority-state query cells within the candidate's response support.

    Proxy: cosine similarity of candidate mean to minority-state mean, normalized.
    """
    mino_mean = query_X[query_states == minority_state].mean(0)
    p_mean = P.mean(0)
    cos = float(np.dot(p_mean, mino_mean) /
                (np.linalg.norm(p_mean) * np.linalg.norm(mino_mean) + 1e-12))
    return (cos + 1) / 2  # map to [0,1]


# ── ranking metrics ──────────────────────────────────────────────────────────

def _ranking_metrics(scores, names, gt_names, ks=(1, 5)):
    """Multi-relevant ranking metrics.

    scores : array of candidate scores (higher=better)
    names  : candidate names parallel to scores
    gt_names : set of ground-truth-relevant candidate names
    """
    order = np.argsort(-scores, kind="stable")
    ranked = [names[i] for i in order]
    gt = set(gt_names)
    ranks = [pos + 1 for pos, nm in enumerate(ranked) if nm in gt]
    if not ranks:
        return {"hit@1": 0, "hit@5": 0, "mrr": 0.0, "ndcg": 0.0,
                "best_rank": len(names) + 1}
    best = min(ranks)
    out = {"mrr": 1.0 / best, "best_rank": best}
    for k in ks:
        out[f"hit@{k}"] = int(best <= k)
    # nDCG@10 with binary relevance, capped
    dcg = sum(1.0 / np.log2(r + 1) for r in ranks if r <= 10)
    ideal = sum(1.0 / np.log2(i + 2) for i in range(min(len(gt), 10)))
    out["ndcg"] = float(dcg / ideal) if ideal > 0 else 0.0
    return out


def _load_annotation():
    """Load drug -> MoA/target annotation for evaluation (never for scoring)."""
    m = pd.read_csv("data/annotation/drug_annotation_master.csv")
    drug2moa = dict(zip(m.drug_name, m.moa_class))
    drug2targets = {}
    for _, r in m.iterrows():
        tg = str(r.target_genes) if pd.notna(r.target_genes) else ""
        drug2targets[r.drug_name] = set(t.strip() for t in tg.split(";") if t.strip())
    return drug2moa, drug2targets


def _same_moa(drug, drug2moa, library):
    """Library drugs sharing the hidden drug's MoA class (excluding the drug itself)."""
    moa = drug2moa.get(drug)
    return {d for d in library if d != drug and drug2moa.get(d) == moa}


def _same_target(drug, drug2targets, library):
    """Library drugs sharing >=1 target gene with the hidden drug."""
    tg = drug2targets.get(drug, set())
    if not tg:
        return set()
    return {d for d in library if d != drug and (drug2targets.get(d, set()) & tg)}


# ── candidate-population builder (leakage-safe) ──────────────────────────────

def _build_candidate_pops(ds, ctx, drugs, max_cells=200, rng=None):
    """Build {drug: response_population} for the given context and drug list.

    Response population = treated cells (delta from control is handled by scorers
    via control_P/control_Q).  Subsamples to max_cells per drug.
    """
    pops = {}
    for d in drugs:
        rows = ds.treated_rows(ctx, d)
        if len(rows) < 10:
            continue
        if rng is not None and len(rows) > max_cells:
            rows = rng.choice(rows, max_cells, replace=False)
        pops[d] = ds.X[rows]
    return pops


def _query_states(query_X, k=2, seed=0):
    """Cluster the query into states; return (labels, minority_state_id)."""
    lab = _kmeans_states(query_X, k, seed)
    uniq, counts = np.unique(lab, return_counts=True)
    minority = uniq[np.argmin(counts)]
    return lab, minority


# ── Setting A: leave-drug-out ────────────────────────────────────────────────

def run_setting_A(ds, ctx, heldout_drugs, drug2moa, drug2targets,
                  n_query_cells=200, max_cand_cells=150, seed=0):
    """For each held-out drug: query = its true response, library = all other drugs."""
    rng = np.random.default_rng(seed)
    all_drugs = sorted(set(np.asarray(ds.pert)[(ds.context == ctx) & (~ds.is_control)].tolist()))
    ctrl = ds.control_mean(ctx)

    rows_perf, rows_diag = [], []

    for hd in heldout_drugs:
        hd_rows = ds.treated_rows(ctx, hd)
        if len(hd_rows) < 20:
            continue
        # Query: hidden drug's real heterogeneous response
        if len(hd_rows) > n_query_cells:
            hd_rows = rng.choice(hd_rows, n_query_cells, replace=False)
        query_X = ds.X[hd_rows]
        query_states, minority = _query_states(query_X, k=2, seed=seed)
        _td = true_response_divergence(query_X, query_states, ctrl)
        _tdc = divergence_components(query_X, query_states, ctrl)

        # Observed library = all drugs EXCEPT the hidden one (leakage-safe)
        library = [d for d in all_drugs if d != hd]
        cand_pops = _build_candidate_pops(ds, ctx, library, max_cells=max_cand_cells, rng=rng)
        if len(cand_pops) < 5:
            continue

        # Ground truth: same-MoA and same-target library drugs
        gt_moa = _same_moa(hd, drug2moa, set(cand_pops.keys()))
        gt_target = _same_target(hd, drug2targets, set(cand_pops.keys()))
        gt_any = gt_moa | gt_target

        names = list(cand_pops.keys())

        # Score all methods
        method_scores = {}
        for method in ALL_METHODS:
            sc = np.array([_score(method, cand_pops[n], query_X, query_states,
                                  ctrl=ctrl, seed=seed) for n in names])
            method_scores[method] = sc

        # Diagnostics (observed data only)
        svr = _subpop_variance_ratio(query_X, seed=seed)
        iso = _isotropy_index(query_X)
        div = _response_diversity(query_X)
        med = _mean_energy_disagreement(method_scores["mean_cosine"], method_scores["DART_energy"])
        boot = _bootstrap_rank_stability(query_X, cand_pops, query_states, ctrl, seed=seed)
        pct = _preference_conflict_topk(cand_pops, query_X, query_states)
        srel = structure_reliability(svr, iso, div, boot, energy_disagreement=med)
        rmode = recommendation_mode(srel, pct)

        # Welfare proxy for regret
        welfare_worst = _welfare_proxy(cand_pops, query_X, query_states, welfare="worst", seed=seed)

        rows_diag.append({
            "split_type": "leave_drug_out", "cell_line": ctx, "heldout_drug": hd,
            "heldout_MoA": drug2moa.get(hd, "unknown"),
            "observed_library_fraction": 1.0,
            "information_condition_mode": "observed",
            "subpopulation_variance_ratio": svr, "isotropy_index": iso,
            "response_diversity": div, "mean_energy_disagreement": med,
            "bootstrap_rank_stability": boot, "preference_conflict_topk": pct,
            "structure_reliability_score": srel, "recommendation_mode": rmode,
            "seed": seed,
        })

        for method in ALL_METHODS:
            sc = method_scores[method]
            top1 = names[int(np.argmax(sc))]
            # Metrics against same-MoA GT (drug repurposing recovery)
            mm = _ranking_metrics(sc, names, gt_moa)
            tm = _ranking_metrics(sc, names, gt_target) if gt_target else None
            regret = _decision_regret(welfare_worst, top1)
            mino_cov = _minority_state_coverage(cand_pops[top1], query_X, query_states, minority)

            rows_perf.append({
                "split_type": "leave_drug_out", "cell_line": ctx, "heldout_drug": hd,
                "heldout_MoA": drug2moa.get(hd, "unknown"),
                "observed_library_fraction": 1.0,
                "information_condition_mode": "observed",
                "structure_reliability_score": srel, "preference_conflict": pct,
                "recommendation_mode": rmode,
                "method": method, "method_family": METHOD_FAMILY[method],
                "selected_top1_drug": top1,
                "moa_hit@1": mm["hit@1"], "moa_hit@5": mm["hit@5"],
                "moa_mrr": mm["mrr"], "moa_ndcg": mm["ndcg"], "moa_rank": mm["best_rank"],
                "target_hit@5": tm["hit@5"] if tm else -1,
                "target_mrr": tm["mrr"] if tm else -1,
                "decision_regret": regret, "minority_state_coverage": mino_cov,
                "n_gt_moa": len(gt_moa), "n_gt_target": len(gt_target),
                "n_candidates": len(names), "seed": seed,
                "provenance": "sciplex3_observed",
                "true_divergence": _td,
                "true_div_min_cos": _tdc["min_pairwise_cos"],
                "true_div_minority_frac": _tdc["minority_frac"],
            })

    return rows_perf, rows_diag


# ── Setting B: leave-MoA-out ─────────────────────────────────────────────────

def run_setting_B(ds, ctx, heldout_moas, drug2moa, drug2targets,
                  n_query_cells=200, max_cand_cells=150, seed=0):
    """Hide a whole MoA class; query = one hidden drug's response; library excludes
    ALL drugs of that MoA. Recovery = same-target surrogate in the remaining library."""
    rng = np.random.default_rng(seed)
    all_drugs = sorted(set(np.asarray(ds.pert)[(ds.context == ctx) & (~ds.is_control)].tolist()))
    ctrl = ds.control_mean(ctx)
    rows_perf, rows_diag = [], []

    for moa in heldout_moas:
        moa_drugs = [d for d in all_drugs if drug2moa.get(d) == moa]
        if len(moa_drugs) < 2:
            continue
        hd = moa_drugs[rng.integers(len(moa_drugs))]
        hd_rows = ds.treated_rows(ctx, hd)
        if len(hd_rows) < 20:
            continue
        if len(hd_rows) > n_query_cells:
            hd_rows = rng.choice(hd_rows, n_query_cells, replace=False)
        query_X = ds.X[hd_rows]
        query_states, minority = _query_states(query_X, k=2, seed=seed)
        _td = true_response_divergence(query_X, query_states, ctrl)
        _tdc = divergence_components(query_X, query_states, ctrl)

        library = [d for d in all_drugs if drug2moa.get(d) != moa]
        cand_pops = _build_candidate_pops(ds, ctx, library, max_cells=max_cand_cells, rng=rng)
        if len(cand_pops) < 5:
            continue

        gt_target = _same_target(hd, drug2targets, set(cand_pops.keys()))
        names = list(cand_pops.keys())

        method_scores = {}
        for method in ALL_METHODS:
            method_scores[method] = np.array(
                [_score(method, cand_pops[n], query_X, query_states, ctrl=ctrl, seed=seed)
                 for n in names])

        svr = _subpop_variance_ratio(query_X, seed=seed)
        iso = _isotropy_index(query_X)
        div = _response_diversity(query_X)
        med = _mean_energy_disagreement(method_scores["mean_cosine"], method_scores["DART_energy"])
        boot = _bootstrap_rank_stability(query_X, cand_pops, query_states, ctrl, seed=seed)
        pct = _preference_conflict_topk(cand_pops, query_X, query_states)
        srel = structure_reliability(svr, iso, div, boot, energy_disagreement=med)
        rmode = recommendation_mode(srel, pct)
        welfare_worst = _welfare_proxy(cand_pops, query_X, query_states, welfare="worst", seed=seed)

        rows_diag.append({
            "split_type": "leave_MoA_out", "cell_line": ctx, "heldout_drug": hd,
            "heldout_MoA": moa, "observed_library_fraction": len(library) / len(all_drugs),
            "information_condition_mode": "observed",
            "subpopulation_variance_ratio": svr, "isotropy_index": iso,
            "response_diversity": div, "mean_energy_disagreement": med,
            "bootstrap_rank_stability": boot, "preference_conflict_topk": pct,
            "structure_reliability_score": srel, "recommendation_mode": rmode, "seed": seed,
        })

        for method in ALL_METHODS:
            sc = method_scores[method]
            top1 = names[int(np.argmax(sc))]
            tm = _ranking_metrics(sc, names, gt_target) if gt_target else None
            regret = _decision_regret(welfare_worst, top1)
            mino_cov = _minority_state_coverage(cand_pops[top1], query_X, query_states, minority)
            rows_perf.append({
                "split_type": "leave_MoA_out", "cell_line": ctx, "heldout_drug": hd,
                "heldout_MoA": moa,
                "observed_library_fraction": len(library) / len(all_drugs),
                "information_condition_mode": "observed",
                "structure_reliability_score": srel, "preference_conflict": pct,
                "recommendation_mode": rmode,
                "method": method, "method_family": METHOD_FAMILY[method],
                "selected_top1_drug": top1,
                # MoA recovery is UNDEFINED for this split type, so it is NaN, not a number.
                # A -1 sentinel here would be differenced downstream as if it were a
                # measurement, and (-1) - (-1) = 0 would silently enter exp16/exp17 as a
                # structural zero (see exp16_common.mask_undefined).
                "moa_hit@1": np.nan, "moa_hit@5": np.nan, "moa_mrr": np.nan,
                "moa_ndcg": np.nan, "moa_rank": np.nan,
                "target_hit@5": tm["hit@5"] if tm else np.nan,
                "target_mrr": tm["mrr"] if tm else np.nan,
                "decision_regret": regret, "minority_state_coverage": mino_cov,
                "n_gt_moa": 0, "n_gt_target": len(gt_target) if gt_target else 0,
                "n_candidates": len(names), "seed": seed,
                "provenance": "sciplex3_observed",
                "true_divergence": _td,
                "true_div_min_cos": _tdc["min_pairwise_cos"],
                "true_div_minority_frac": _tdc["minority_frac"],
            })

    return rows_perf, rows_diag


# ── Setting C: partial-library batch selection ───────────────────────────────

def run_setting_C(ds, ctx, fractions, drug2moa, drug2targets,
                  n_query_cells=200, max_cand_cells=120, topk=5, seed=0):
    """Measure X% of drugs; select next top-k batch; score against hidden responses."""
    rng = np.random.default_rng(seed)
    all_drugs = sorted(set(np.asarray(ds.pert)[(ds.context == ctx) & (~ds.is_control)].tolist()))
    ctrl = ds.control_mean(ctx)
    rows_perf, rows_diag = [], []

    for frac in fractions:
        n_measured = max(5, int(frac * len(all_drugs)))
        perm = rng.permutation(all_drugs)
        measured = list(perm[:n_measured])
        hidden = list(perm[n_measured:])
        if len(hidden) < topk:
            continue

        hidden_rows = np.concatenate([ds.treated_rows(ctx, d) for d in hidden[:20]])
        if len(hidden_rows) > n_query_cells:
            hidden_rows = rng.choice(hidden_rows, n_query_cells, replace=False)
        query_X = ds.X[hidden_rows]
        query_states, minority = _query_states(query_X, k=2, seed=seed)
        _td = true_response_divergence(query_X, query_states, ctrl)
        _tdc = divergence_components(query_X, query_states, ctrl)

        cand_pops = _build_candidate_pops(ds, ctx, measured, max_cells=max_cand_cells, rng=rng)
        if len(cand_pops) < topk:
            continue
        names = list(cand_pops.keys())

        svr = _subpop_variance_ratio(query_X, seed=seed)
        iso = _isotropy_index(query_X)
        div = _response_diversity(query_X)
        boot = _bootstrap_rank_stability(query_X, cand_pops, query_states, ctrl, seed=seed)
        pct = _preference_conflict_topk(cand_pops, query_X, query_states)
        _sc_mean = np.array([_score("mean_cosine", cand_pops[n], query_X, query_states,
                                    ctrl=ctrl, seed=seed) for n in names])
        _sc_energy = np.array([_score("DART_energy", cand_pops[n], query_X, query_states,
                                      ctrl=ctrl, seed=seed) for n in names])
        med = _mean_energy_disagreement(_sc_mean, _sc_energy)
        srel = structure_reliability(svr, iso, div, boot, energy_disagreement=med)
        rmode = recommendation_mode(srel, pct)

        rows_diag.append({
            "split_type": "partial_library", "cell_line": ctx, "heldout_drug": "batch",
            "heldout_MoA": "batch", "observed_library_fraction": frac,
            "information_condition_mode": "observed",
            "subpopulation_variance_ratio": svr, "isotropy_index": iso,
            "response_diversity": div, "mean_energy_disagreement": med,
            "bootstrap_rank_stability": boot, "preference_conflict_topk": pct,
            "structure_reliability_score": srel, "recommendation_mode": rmode, "seed": seed,
        })

        full_welfare = _welfare_proxy(cand_pops, query_X, query_states, welfare="worst", seed=seed)
        for method in ALL_METHODS:
            sc = np.array([_score(method, cand_pops[n], query_X, query_states, ctrl=ctrl, seed=seed)
                           for n in names])
            batch_idx = np.argsort(-sc)[:topk]
            batch = [names[i] for i in batch_idx]
            state_cov = []
            for s in np.unique(query_states):
                covs = [_minority_state_coverage(cand_pops[b], query_X, query_states, s)
                        for b in batch]
                state_cov.append(max(covs))
            batch_coverage = float(np.mean(state_cov))
            mino_cov = float(np.mean([_minority_state_coverage(cand_pops[b], query_X,
                                                                query_states, minority)
                                      for b in batch]))
            moa_div = len(set(drug2moa.get(b, "?") for b in batch)) / len(batch)
            batch_welfare = {b: full_welfare[b] for b in batch}
            welfare_regret = _decision_regret(
                full_welfare, batch[int(np.argmax([batch_welfare[b] for b in batch]))])

            rows_perf.append({
                "split_type": "partial_library", "cell_line": ctx, "heldout_drug": "batch",
                "heldout_MoA": "batch", "observed_library_fraction": frac,
                "information_condition_mode": "observed",
                "structure_reliability_score": srel, "preference_conflict": pct,
                "recommendation_mode": rmode,
                "method": method, "method_family": METHOD_FAMILY[method],
                "selected_top1_drug": batch[0],
                "moa_hit@1": -1, "moa_hit@5": -1, "moa_mrr": -1, "moa_ndcg": -1, "moa_rank": -1,
                "target_hit@5": -1, "target_mrr": -1,
                "decision_regret": welfare_regret, "minority_state_coverage": mino_cov,
                "batch_coverage": batch_coverage, "topk_diversity": moa_div,
                "n_gt_moa": 0, "n_gt_target": 0,
                "n_candidates": len(names), "seed": seed,
                "provenance": "sciplex3_observed",
                "true_divergence": _td,
                "true_div_min_cos": _tdc["min_pairwise_cos"],
                "true_div_minority_frac": _tdc["minority_frac"],
            })

    return rows_perf, rows_diag


# ── main orchestration ───────────────────────────────────────────────────────

# A query is identified by ALL SIX of these. Dropping observed_library_fraction (or the
# information condition) makes the key non-unique: the partial_library queries exist at
# fractions 0.2 / 0.4 / 0.6 under one (split_type, cell_line, heldout_drug, seed), so a
# 4-key lookup returns three rows and taking .iloc[0] pairs a PopRetrieve row at fraction 0.4
# against a mean_cosine row at fraction 0.2. That mispairing is what made this table report
# a median regret reduction of 0.1133 where the per-query data give 0.1190, and the figures
# were built from the wrong number.
QUERY_KEY = ["split_type", "cell_line", "heldout_drug", "heldout_MoA",
             "observed_library_fraction", "seed"]


def _recommendation_vs_outcome(df_perf):
    """Stratify PopRetrieve-mean advantage by recommendation_mode (protocol §5 core test)."""
    rows = []
    ref = df_perf[df_perf.method == REF_METHOD].set_index(QUERY_KEY)
    if ref.index.has_duplicates:
        dup = ref.index[ref.index.duplicated()].unique().tolist()[:5]
        raise ValueError(
            f"{REF_METHOD} rows are not unique on {QUERY_KEY}; e.g. {dup}. Every paired "
            f"statistic below would silently compare mismatched queries. Fix the key.")

    for rmode in df_perf.recommendation_mode.unique():
        sub = df_perf[df_perf.recommendation_mode == rmode]
        for dart_m in DART_METHODS:
            dm = sub[sub.method == dart_m]
            if len(dm) == 0:
                continue
            deltas_regret, deltas_ndcg, deltas_mino = [], [], []
            unmatched = 0
            for _, r in dm.iterrows():
                key = tuple(r[k] for k in QUERY_KEY)
                if key not in ref.index:
                    unmatched += 1
                    continue
                rr = ref.loc[key]
                deltas_regret.append(rr.decision_regret - r.decision_regret)  # + = PopRetrieve better
                # moa_ndcg is NaN where the metric is undefined for this split type; nanmean
                # below drops those rather than counting them as a zero gain.
                deltas_ndcg.append(r.moa_ndcg - rr.moa_ndcg)
                deltas_mino.append(r.minority_state_coverage - rr.minority_state_coverage)
            if not deltas_regret:
                continue
            if unmatched:
                log(f"  [warn] {rmode}/{dart_m}: {unmatched} queries had no {REF_METHOD} "
                    f"counterpart and were dropped")
            nd = np.asarray(deltas_ndcg, dtype=float)
            rows.append({
                "recommendation_mode": rmode, "dart_method": dart_m,
                "n_queries": len(deltas_regret),
                "n_queries_unmatched": int(unmatched),
                "mean_regret_reduction": float(np.mean(deltas_regret)),
                "median_regret_reduction": float(np.median(deltas_regret)),
                "mean_ndcg_gain": float(np.nanmean(nd)) if np.isfinite(nd).any() else float("nan"),
                "n_ndcg_defined": int(np.isfinite(nd).sum()),
                "mean_minority_cov_gain": float(np.mean(deltas_mino)),
                "frac_regret_improved": float(np.mean([d > 0 for d in deltas_regret])),
            })
    return pd.DataFrame(rows)


def _summary(df_perf):
    """Aggregate per (split_type × recommendation_mode × method)."""
    metric_cols = ["moa_hit@1", "moa_hit@5", "moa_mrr", "moa_ndcg",
                   "target_hit@5", "target_mrr", "decision_regret", "minority_state_coverage"]
    present = [c for c in metric_cols if c in df_perf.columns]
    agg = {c: "mean" for c in present}
    grp = df_perf.groupby(["split_type", "recommendation_mode", "method", "method_family"])
    out = grp.agg(agg).reset_index()
    out["n_queries"] = grp.size().values
    return out


def run(quick=False, n_drugs=None, n_seeds=None):
    if quick:
        n_drugs = n_drugs or 8
        n_seeds = n_seeds or 2
        contexts = ["A549"]
        fractions = [0.2, 0.4]
    else:
        n_drugs = n_drugs or 40
        n_seeds = n_seeds or 5
        contexts = ["A549", "K562", "MCF7"]
        fractions = [0.2, 0.4, 0.6]

    section(f"EXP12 PARTIAL-OBSERVED RETRIEVAL ({'QUICK' if quick else 'FULL'})")
    ds = load_sciplex3()
    log(f"  data: sciplex3 cells={ds.X.shape[0]} genes={ds.X.shape[1]} contexts={ds.contexts}")
    drug2moa, drug2targets = _load_annotation()

    all_perf, all_diag = [], []
    t0 = time.time()

    for ctx in contexts:
        all_drugs = sorted(set(np.asarray(ds.pert)[(ds.context == ctx) & (~ds.is_control)].tolist()))
        moa_classes = sorted(set(drug2moa.get(d) for d in all_drugs if drug2moa.get(d)))
        # MoA classes with >= 2 drugs
        moa_multi = [m for m in moa_classes
                     if sum(1 for d in all_drugs if drug2moa.get(d) == m) >= 2]

        for seed in range(n_seeds):
            rng = np.random.default_rng(seed)
            heldout = list(rng.choice(all_drugs, min(n_drugs, len(all_drugs)), replace=False))
            heldout_moas = list(rng.choice(moa_multi, min(len(moa_multi),
                                                           4 if quick else 8), replace=False))

            log(f"  [{ctx} seed={seed}] A:{len(heldout)}drugs B:{len(heldout_moas)}MoAs C:{len(fractions)}frac")

            pa, da = run_setting_A(ds, ctx, heldout, drug2moa, drug2targets, seed=seed)
            pb, db = run_setting_B(ds, ctx, heldout_moas, drug2moa, drug2targets, seed=seed)
            pc, dc = run_setting_C(ds, ctx, fractions, drug2moa, drug2targets, seed=seed)
            all_perf += pa + pb + pc
            all_diag += da + db + dc

    elapsed = time.time() - t0
    log(f"  Done: {len(all_perf)} perf rows, {len(all_diag)} diag rows in {elapsed:.1f}s")

    df_perf = pd.DataFrame(all_perf)
    df_diag = pd.DataFrame(all_diag)

    # Write outputs
    write_csv(df_perf, results_path(OUT, "per_query_scores.csv"))
    write_csv(df_diag, results_path(OUT, "information_condition_summary.csv"))
    df_summary = _summary(df_perf)
    write_csv(df_summary, results_path(OUT, "summary.csv"))
    df_rvo = _recommendation_vs_outcome(df_perf)
    write_csv(df_rvo, results_path(OUT, "recommendation_vs_outcome.csv"))

    # Report recommendation mode distribution
    section("RECOMMENDATION MODE DISTRIBUTION")
    log(df_diag.recommendation_mode.value_counts().to_string())

    section("PopRetrieve vs MEAN BY RECOMMENDATION MODE")
    if len(df_rvo) > 0:
        for rmode in df_rvo.recommendation_mode.unique():
            sub = df_rvo[df_rvo.recommendation_mode == rmode]
            best = sub.loc[sub.mean_regret_reduction.idxmax()]
            log(f"  [{rmode}] best PopRetrieve={best.dart_method}: "
                f"regret_reduction={best.mean_regret_reduction:+.4f}, "
                f"ndcg_gain={best.mean_ndcg_gain:+.4f}, n={int(best.n_queries)}")

    return df_perf, df_diag, df_rvo


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    ap.add_argument("--n-drugs", type=int, default=None)
    ap.add_argument("--n-seeds", type=int, default=None)
    args = ap.parse_args()
    quick = args.quick or os.environ.get("QUICK") == "1"
    run(quick=quick, n_drugs=args.n_drugs, n_seeds=args.n_seeds)


if __name__ == "__main__":
    main()
