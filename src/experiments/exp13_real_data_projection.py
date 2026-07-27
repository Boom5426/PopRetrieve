#!/usr/bin/env python
"""Experiment 13 — Real-data projection onto the HIR-Bench regime plane.

Validates HIR-Bench against reality: project each real dataset / task onto the
HIR-Bench (structure_reliability, preference_conflict) plane, use the HIR-Bench
learned regime boundary to predict which method family should win, then compare
to the method family that actually wins on that real task.

Acceptance table (protocol §; the projection is "accepted" if these hold):
  CD34+ / low-conflict            -> HIR predicts mean_sufficient          (EvalShift no win)
  exp09 mean-only predictors      -> HIR predicts no_DART / mean_sufficient
  cross-line high-heterogeneity   -> HIR predicts DART_recommended
  Frangieh IFN heterogeneous      -> HIR predicts DART_recommended
  partial-observed high-conflict  -> HIR predicts DART_recommended

The HIR-Bench boundary (derived from results/exp11_hir_benchmark):
  - low/mid preference_conflict  -> mean and EvalShift tie (regret ~0)  -> mean_sufficient
  - high preference_conflict + reliable structure -> EvalShift lowers regret -> DART_recommended
  - predicted_mean information condition -> EvalShift advantage shrinks -> no_DART

Usage:
    QUICK=1 python src/experiments/exp13_real_data_projection.py
    python src/experiments/exp13_real_data_projection.py
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import pandas as pd

from retrieval.metrics import score_mean_cosine, score_energy
from utils.io import results_path, write_csv
from utils.logging import log, section

# Reuse exp12 diagnostics (single source of truth for the projection axes)
import exp12_partial_observed_retrieval as e12

OUT = "exp13_real_data_projection"
HIR = "results/exp11_hir_benchmark"

# ── HIR-Bench regime boundary (fit from the benchmark grid) ──────────────────

def fit_hir_boundary():
    """Derive the conflict threshold at which EvalShift starts beating mean (worst
    welfare, observed) from the HIR-Bench grid. Returns dict with thresholds.

    This fit needs BOTH HIR-Bench layers, and they must come from the SAME grid. They can
    legitimately come from different ones: the method-independent layer runs on the FULL
    13,440-instance grid in about an hour, while the method-performance layer scores 9
    retrieval methods per instance and does not finish on FULL at all (hence
    `exp11_hir_benchmark.py --skip-method-perf`). A mismatched pair shares no (grid_id, seed)
    at all, the merge empties, and the old code then died with `KeyError: 'mean'` several
    lines later. Check it here and say what is actually wrong.
    """
    mi = pd.read_csv(f"{HIR}/phase_grid_method_independent.csv")
    mp = pd.read_csv(f"{HIR}/phase_grid_method_performance.csv")
    key = ["grid_id", "seed"]
    m = mp.merge(mi[key + ["weighted_kendall_conflict"]], on=key, how="inner")
    if m.empty:
        raise RuntimeError(
            "HIR-Bench layers do not match: phase_grid_method_performance.csv "
            f"({mp.grid_id.nunique()} grid_ids) and phase_grid_method_independent.csv "
            f"({mi.grid_id.nunique()} grid_ids) share no (grid_id, seed), so they come from "
            "DIFFERENT grids. The boundary fit needs one coherent pair. See "
            "results/exp11_hir_benchmark/PROVENANCE.md, and re-run exp11 on a single grid "
            "WITHOUT --skip-method-perf to produce one.")
    # "DART_" is the FROZEN method-key prefix under which every published number was computed
    # and stored (see exp12.METHOD_FAMILY and results/exp11_hir_benchmark/*.csv). It is a data
    # identifier, not the project name, and must not be renamed with the project.
    m["family"] = m.method.map(lambda x: "DART" if x.startswith("DART") else "mean")
    obs = m[(m.information_condition == "observed") & (m.welfare_type == "worst")]

    # For each grid cell, min regret per family; distributional advantage = mean - distributional
    g = obs.groupby(key + ["family"]).decision_regret.min().reset_index()
    piv = g.pivot_table(index=key, columns="family", values="decision_regret").dropna()
    piv = piv.join(mi.set_index(key).weighted_kendall_conflict.groupby(level=[0, 1]).first())
    piv["dart_adv"] = piv["mean"] - piv["DART"]

    # The distributional family wins above a conflict threshold. Because HIR-Bench's weighted_kendall_conflict
    # and the real-data preference_conflict are DIFFERENT metrics on DIFFERENT scales, we
    # transfer the boundary as a PERCENTILE of the conflict distribution, not a raw value.
    piv = piv.sort_values("weighted_kendall_conflict").reset_index(drop=True)
    piv["dart_wins"] = (piv.dart_adv > 1e-4).astype(int)
    n = len(piv)
    conf_sorted = piv.weighted_kendall_conflict.values
    win_sorted = piv.dart_wins.values
    # Crossover = the top of the low-conflict band in which EvalShift essentially never wins.
    # Scan a sliding forward window; the crossover is the highest index i such that the
    # cells BELOW i have < 15% EvalShift wins (the "mean-sufficient" band). Percentile = i/n.
    crossover_idx = 0
    for i in range(1, n):
        if win_sorted[:i].mean() < 0.15:
            crossover_idx = i
        else:
            break
    crossover_pct = crossover_idx / n
    return {
        "conflict_crossover_percentile": float(crossover_pct),
        "conflict_threshold_synthetic": float(conf_sorted[min(crossover_idx, n - 1)]) if n else 0.5,
        "n_cells": int(n),
        "frac_cells_dart_wins": float(piv.dart_wins.mean()),
        "low_band_winrate": float(win_sorted[:max(1, crossover_idx)].mean()),
    }


def predict_regime(structure_reliability, preference_conflict, information_condition,
                   real_conflict_threshold, struct_threshold=0.4):
    """HIR-Bench prediction of the winning regime for a real task.

    real_conflict_threshold : the real-data preference_conflict value at the
    HIR-Bench crossover percentile (percentile transfer — see fit_hir_boundary +
    run()).  EvalShift is predicted only when conflict is in the upper part of the real
    distribution AND the query has reliable structure.
    """
    if information_condition in ("predicted_mean", "mean_only"):
        return "no_DART"  # information condition kills EvalShift advantage (exp09 thesis)
    if structure_reliability < struct_threshold:
        return "mean_sufficient"  # no reliable structure to exploit
    if preference_conflict >= real_conflict_threshold:
        return "DART_recommended"
    return "mean_sufficient"


# ── project a real task onto the HIR-Bench plane ─────────────────────────────

def _observed_best_family(cand_pops, query_X, query_states, ctrl, minority, seed=0):
    """Which method family (EvalShift vs mean) better covers the minority subpopulation.

    This is the biological target of the NM claim: does the selected drug reach the
    resistant/minority state that mean retrieval collapses away?  Coverage-of-minority
    is the outcome, NOT energy regret (which EvalShift optimizes and would make circular).
    """
    names = list(cand_pops.keys())
    fam_cov = {"DART": [], "mean": []}          # "DART_" is the frozen method-key prefix
    for method in e12.ALL_METHODS:
        sc = np.array([e12._score(method, cand_pops[n], query_X, query_states, ctrl=ctrl, seed=seed)
                       for n in names])
        top1 = names[int(np.argmax(sc))]
        cov = e12._minority_state_coverage(cand_pops[top1], query_X, query_states, minority)
        fam = "DART" if method.startswith("DART") else "mean"
        fam_cov[fam].append(cov)
    dart_cov = float(np.max(fam_cov["DART"]))
    mean_cov = float(np.max(fam_cov["mean"]))
    if dart_cov - mean_cov > 0.01:
        return "DART_recommended", dart_cov, mean_cov
    return "mean_sufficient", dart_cov, mean_cov


def _diagnose_task(dataset, task_id, information_condition, cand_pops, query_X,
                   query_states, ctrl, minority, seed=0):
    """Pass 1: compute a real task's HIR-Bench coordinates + observed outcome.
    Prediction is filled in pass 2 once the real-data conflict percentile is known."""
    names = list(cand_pops.keys())
    sc_mean = np.array([e12._score("mean_cosine", cand_pops[n], query_X, query_states,
                                   ctrl=ctrl, seed=seed) for n in names])
    sc_energy = np.array([e12._score("DART_energy", cand_pops[n], query_X, query_states,
                                     ctrl=ctrl, seed=seed) for n in names])

    svr = e12._subpop_variance_ratio(query_X, seed=seed)
    iso = e12._isotropy_index(query_X)
    div = e12._response_diversity(query_X)
    med = e12._mean_energy_disagreement(sc_mean, sc_energy)
    boot = e12._bootstrap_rank_stability(query_X, cand_pops, query_states, ctrl, seed=seed)
    pct = e12._preference_conflict_topk(cand_pops, query_X, query_states)
    srel = e12.structure_reliability(svr, iso, div, boot, energy_disagreement=med)
    observed, dart_cov, mean_cov = _observed_best_family(
        cand_pops, query_X, query_states, ctrl, minority, seed)

    return {
        "dataset": dataset, "task_id": task_id,
        "information_condition_mode": information_condition,
        "structure_reliability_score": srel, "preference_conflict": pct,
        "mean_vs_DART_disagreement": med,
        "subpop_variance_ratio": svr, "response_diversity": div,
        "bootstrap_rank_stability": boot,
        "observed_best_method": observed,
        "observed_dart_minority_cov": dart_cov, "observed_mean_minority_cov": mean_cov,
        "seed": seed,
    }


# ── real-dataset task builders ───────────────────────────────────────────────

def _sciplex_tasks(quick, seeds):
    """SciPlex3 within-line (leave-drug-out) and cross-line tasks."""
    from data.load_sciplex3 import load_sciplex3
    ds = load_sciplex3()
    drug2moa, drug2targets = e12._load_annotation()
    tasks = []
    contexts = ["A549"] if quick else ["A549", "K562", "MCF7"]
    n_drugs = 4 if quick else 10
    for ctx in contexts:
        all_drugs = sorted(set(np.asarray(ds.pert)[(ds.context == ctx) & (~ds.is_control)].tolist()))
        ctrl = ds.control_mean(ctx)
        for seed in seeds:
            rng = np.random.default_rng(seed)
            held = rng.choice(all_drugs, n_drugs, replace=False)
            for hd in held:
                rows = ds.treated_rows(ctx, hd)
                if len(rows) < 20:
                    continue
                if len(rows) > 200:
                    rows = rng.choice(rows, 200, replace=False)
                qX = ds.X[rows]
                qs, mino = e12._query_states(qX, k=2, seed=seed)
                lib = [d for d in all_drugs if d != hd]
                cand = e12._build_candidate_pops(ds, ctx, lib, max_cells=120, rng=rng)
                if len(cand) < 5:
                    continue
                tasks.append(("sciplex3_within_line", f"{ctx}:{hd}:s{seed}",
                              "observed", cand, qX, qs, ctrl, mino, seed))
    return tasks


def _crossline_tasks(quick, seeds):
    """Cross-line: query = drug response in line X, library = same drugs in line Y.
    Higher heterogeneity because the same drug's response differs across lines."""
    from data.load_sciplex3 import load_sciplex3
    ds = load_sciplex3()
    tasks = []
    pairs = [("K562", "A549")] if quick else [("K562", "A549"), ("A549", "MCF7"), ("K562", "MCF7")]
    n_drugs = 4 if quick else 10
    for qline, lline in pairs:
        q_drugs = sorted(set(np.asarray(ds.pert)[(ds.context == qline) & (~ds.is_control)].tolist()))
        l_drugs = sorted(set(np.asarray(ds.pert)[(ds.context == lline) & (~ds.is_control)].tolist()))
        common = sorted(set(q_drugs) & set(l_drugs))
        ctrl = ds.control_mean(lline)
        for seed in seeds:
            rng = np.random.default_rng(seed)
            held = rng.choice(common, n_drugs, replace=False)
            for hd in held:
                rows = ds.treated_rows(qline, hd)
                if len(rows) < 20:
                    continue
                if len(rows) > 200:
                    rows = rng.choice(rows, 200, replace=False)
                qX = ds.X[rows]
                qs, mino = e12._query_states(qX, k=2, seed=seed)
                lib = [d for d in common if d != hd]
                cand = e12._build_candidate_pops(ds, lline, lib, max_cells=120, rng=rng)
                if len(cand) < 5:
                    continue
                tasks.append(("sciplex3_cross_line", f"{qline}->{lline}:{hd}:s{seed}",
                              "observed", cand, qX, qs, ctrl, mino, seed))
    return tasks


def _cd34_tasks(quick, seeds):
    """CD34+ hematopoietic: expected LOW conflict (more homogeneous)."""
    try:
        from data.load_cd34 import load_cd34
        ds = load_cd34()
    except Exception as e:
        log(f"  CD34 unavailable: {e}")
        return []
    tasks = []
    ctxs = ds.contexts[:1] if quick else ds.contexts
    for ctx in ctxs:
        all_drugs = sorted(set(np.asarray(ds.pert)[(ds.context == ctx) & (~ds.is_control)].tolist()))
        if len(all_drugs) < 3:
            continue
        ctrl = ds.control_mean(ctx)
        for seed in seeds:
            rng = np.random.default_rng(seed)
            held = rng.choice(all_drugs, min(4, len(all_drugs)), replace=False)
            for hd in held:
                rows = ds.treated_rows(ctx, hd)
                if len(rows) < 20:
                    continue
                if len(rows) > 200:
                    rows = rng.choice(rows, 200, replace=False)
                qX = ds.X[rows]
                qs, mino = e12._query_states(qX, k=2, seed=seed)
                lib = [d for d in all_drugs if d != hd]
                cand = e12._build_candidate_pops(ds, ctx, lib, max_cells=120, rng=rng)
                if len(cand) < 3:
                    continue
                tasks.append(("cd34", f"{ctx}:{hd}:s{seed}", "observed", cand, qX, qs, ctrl, mino, seed))
    return tasks


def _frangieh_tasks(quick, seeds):
    """Frangieh Perturb-CITE-seq: IFNγ-driven heterogeneous KO responses."""
    try:
        from data.load_frangieh import load_frangieh
        ds = load_frangieh()
    except Exception as e:
        log(f"  Frangieh unavailable: {e}")
        return []
    tasks = []
    # Use immune-active heterogeneous contexts, not the Control baseline
    active = [c for c in ds.contexts if c != "Control"]
    ctxs = active[:1] if quick else active
    for ctx in ctxs:
        all_kos = sorted(set(np.asarray(ds.pert)[(ds.context == ctx) & (~ds.is_control)].tolist()))
        if len(all_kos) < 3:
            continue
        ctrl = ds.control_mean(ctx)
        for seed in seeds:
            rng = np.random.default_rng(seed)
            held = rng.choice(all_kos, min(4, len(all_kos)), replace=False)
            for hd in held:
                rows = ds.treated_rows(ctx, hd)
                if len(rows) < 20:
                    continue
                if len(rows) > 200:
                    rows = rng.choice(rows, 200, replace=False)
                qX = ds.X[rows]
                qs, mino = e12._query_states(qX, k=2, seed=seed)
                lib = [d for d in all_kos if d != hd]
                cand = e12._build_candidate_pops(ds, ctx, lib, max_cells=120, rng=rng)
                if len(cand) < 3:
                    continue
                tasks.append(("frangieh", f"{ctx}:{hd}:s{seed}", "observed", cand, qX, qs, ctrl, mino, seed))
    return tasks


def _predicted_mean_tasks(quick, seeds):
    """exp09-style: candidate library replaced by mean-only predicted responses.
    Each candidate becomes its per-drug mean broadcast to a cloud -> no subpop
    structure. HIR should predict no_DART."""
    from data.load_sciplex3 import load_sciplex3
    ds = load_sciplex3()
    tasks = []
    ctx = "A549"
    all_drugs = sorted(set(np.asarray(ds.pert)[(ds.context == ctx) & (~ds.is_control)].tolist()))
    ctrl = ds.control_mean(ctx)
    n_drugs = 3 if quick else 8
    for seed in seeds:
        rng = np.random.default_rng(seed)
        held = rng.choice(all_drugs, n_drugs, replace=False)
        for hd in held:
            rows = ds.treated_rows(ctx, hd)
            if len(rows) < 20:
                continue
            if len(rows) > 200:
                rows = rng.choice(rows, 200, replace=False)
            qX = ds.X[rows]
            qs, mino = e12._query_states(qX, k=2, seed=seed)
            lib = [d for d in all_drugs if d != hd]
            # mean-only predicted candidates: each drug -> its mean, tiled with tiny noise
            cand = {}
            for d in lib:
                dr = ds.treated_rows(ctx, d)
                if len(dr) < 10:
                    continue
                mu = ds.X[dr].mean(0)
                cloud = np.tile(mu, (60, 1)) + rng.normal(0, 1e-3, (60, len(mu)))
                cand[d] = cloud
            if len(cand) < 5:
                continue
            tasks.append(("sciplex3_predicted_mean", f"{ctx}:{hd}:s{seed}",
                          "predicted_mean", cand, qX, qs, ctrl, mino, seed))
    return tasks


def _acceptance_report(df, boundary):
    """Check the projection against the acceptance table."""
    lines = ["# exp13 Real-Data Projection — Acceptance Report\n"]
    lines.append(f"HIR-Bench boundary transferred by percentile: crossover_percentile = "
                 f"{boundary['conflict_crossover_percentile']:.3f} "
                 f"(fit on {boundary['n_cells']} grid cells; EvalShift wins in "
                 f"{boundary['frac_cells_dart_wins']:.1%}). Real-data conflict threshold at that "
                 f"percentile = {boundary.get('real_conflict_threshold', float('nan')):.4f}.\n")
    lines.append(f"Overall projection accuracy: **{df.prediction_correct.mean():.1%}** "
                 f"({int(df.prediction_correct.sum())}/{len(df)} tasks)\n")

    lines.append("## Primary acceptance test — projection vs. observed agreement\n")
    lines.append("The projection would be *accepted* if the HIR-Bench regime prediction agreed "
                 "with the method family that actually gives higher minority-state coverage on the "
                 "real task, better than a trivial predictor does.\n")

    # An accuracy is only interpretable against the majority-class baseline: the accuracy a
    # CONSTANT predictor, one that always names the most common observed label, would score.
    # Here the observed label has NO variance at all (every task is 'mean_sufficient', because
    # no task clears the dart_cov - mean_cov > 0.01 margin), so the baseline is 100% and any
    # accuracy below that is WORSE than saying nothing. Reporting PASS off a >=0.6 threshold
    # against a constant ground truth is not a test, so it is not reported as one.
    labels = df.observed_best_method
    majority_acc = float(labels.value_counts(normalize=True).max())
    degenerate = labels.nunique() <= 1
    overall = float(df.prediction_correct.mean())

    lines.append(f"- observed-label distribution: "
                 f"{dict(labels.value_counts())} (n={len(df)})")
    lines.append(f"- majority-class baseline (a constant predictor): **{majority_acc:.1%}**")
    lines.append(f"- projection accuracy: **{overall:.1%}**")
    if degenerate:
        lines.append(
            f"\n> **VACUOUS — no verdict.** The observed label is CONSTANT "
            f"('{labels.iloc[0]}') across all {len(df)} tasks, so it carries zero information "
            f"and no predictor can be discriminated on it. A constant predictor scores "
            f"{majority_acc:.0%}; the projection scores {overall:.1%}, i.e. "
            f"{majority_acc - overall:.1%} WORSE than saying nothing. This acceptance test "
            f"cannot pass or fail and is reported as vacuous.\n")
        lines.append(
            "> The informative reading of the same data is the paper's own negative claim: "
            f"**0 of {len(df)} real-data tasks are distributionally dominant**. The largest "
            "observed EvalShift-minus-mean coverage margin across all tasks is below the 0.01 "
            "decision threshold, which is the finding, not a failure of the projection.\n")
    else:
        lines.append("| dataset | agreement | n | beats majority baseline |")
        lines.append("|---|---|---|---|")
        for dsname in df.dataset.unique():
            sub = df[df.dataset == dsname]
            agr = float(sub.prediction_correct.mean())
            base = float(sub.observed_best_method.value_counts(normalize=True).max())
            lines.append(f"| {dsname} | {agr:.2f} | {len(sub)} | "
                         f"{'YES' if agr > base else 'NO'} (baseline {base:.2f}) |")
        lines.append(f"| **overall** | **{overall:.2f}** | {len(df)} | "
                     f"**{'YES' if overall > majority_acc else 'NO'}** "
                     f"(baseline {majority_acc:.2f}) |")

    lines.append("\n## Information-condition check (and what it does NOT show)\n")
    pm = df[df.dataset == "sciplex3_predicted_mean"]
    pm_ok = pm.HIR_predicted_regime.isin(["no_DART", "mean_sufficient"]).mean() if len(pm) else float("nan")
    lines.append(f"- predicted_mean → no_DART: {pm_ok:.0%}.")
    lines.append("- **This is a tautology, not evidence.** `predict_regime` returns 'no_DART' "
                 "unconditionally whenever `information_condition` is 'predicted_mean' or "
                 "'mean_only' (see predict_regime), so this rate is 100% by construction and can "
                 "never be anything else. It restates the rule; it does not test it. The claim "
                 "that mean-only predicted libraries offer no EvalShift advantage rests on exp09, not "
                 "on this line.")
    # Observed regime distribution per dataset (what the DATA says, independent of prediction)
    datasets = list(df.dataset.unique())
    lines.append("\n## Observed regime by dataset (data ground truth)\n")
    lines.append("| dataset | observed EvalShift-favoured | observed mean-sufficient | conflict (mean) | structure (mean) |")
    lines.append("|---|---|---|---|---|")
    for dsname in datasets:
        sub = df[df.dataset == dsname]
        nd = int((sub.observed_best_method == "DART_recommended").sum())
        nm = int((sub.observed_best_method == "mean_sufficient").sum())
        lines.append(f"| {dsname} | {nd} | {nm} | {sub.preference_conflict.mean():.3f} | "
                     f"{sub.structure_reliability_score.mean():.3f} |")
    lines.append("\n*Note:* the observed regime is defined by minority-state coverage (not energy "
                 "regret), so it does not mechanically favour EvalShift. Where the real data places a "
                 "dataset in the low-conflict band (e.g. cross-line, CD34+), mean retrieval is "
                 "genuinely sufficient — the projection reflects the data, not a prior expectation.\n")
    return "\n".join(lines)


def run(quick=False):
    section(f"EXP13 REAL-DATA PROJECTION ({'QUICK' if quick else 'FULL'})")
    boundary = fit_hir_boundary()
    log(f"  HIR boundary: crossover_percentile={boundary['conflict_crossover_percentile']:.3f}, "
        f"EvalShift wins {boundary['frac_cells_dart_wins']:.1%} of {boundary['n_cells']} cells")

    seeds = [0, 1] if quick else [0, 1, 2]
    all_tasks = []
    all_tasks += _sciplex_tasks(quick, seeds)
    all_tasks += _crossline_tasks(quick, seeds)
    all_tasks += _cd34_tasks(quick, seeds)
    all_tasks += _frangieh_tasks(quick, seeds)
    all_tasks += _predicted_mean_tasks(quick, seeds)
    log(f"  built {len(all_tasks)} real tasks")

    # ── Pass 1: diagnose every task (coordinates + observed outcome) ─────────
    # A task that fails must not vanish: the headline is "0 of N tasks distributionally
    # dominant", so a silently dropped task shrinks N and quietly strengthens the claim.
    # Failures are recorded and reported, and the denominator stays auditable.
    rows, failures = [], []
    for i, (dataset, tid, info, cand, qX, qs, ctrl, mino, seed) in enumerate(all_tasks):
        try:
            rows.append(_diagnose_task(dataset, tid, info, cand, qX, qs, ctrl, mino, seed))
        except Exception as e:
            failures.append({"dataset": dataset, "task_id": tid, "seed": seed,
                             "error": f"{type(e).__name__}: {e}"})
            log(f"  [FAILED] task {tid}: {type(e).__name__}: {e}")
        if (i + 1) % 20 == 0:
            log(f"    [{i+1}/{len(all_tasks)}]")
    df = pd.DataFrame(rows)
    log(f"  diagnosed {len(df)}/{len(all_tasks)} tasks ({len(failures)} failed)")

    # Stamp which CONFIGURATION produced these artifacts. This is not bookkeeping: the QUICK
    # configuration builds exactly 37 tasks, and a QUICK run had been quoted in the manuscript
    # as the real-data result ("0 of 37 real-data tasks are distributionally dominant"). The
    # FULL configuration builds 239 and the answer is not zero. Nothing on disk said which had
    # been run. Now something does. See CORRECTIONS.md R13.
    prov = pd.DataFrame([{
        "configuration": "QUICK" if quick else "FULL",
        "n_tasks": len(df),
        "n_tasks_built": len(all_tasks),
        "n_failed": len(failures),
        "seeds": ",".join(str(s) for s in seeds),
        "note": ("QUICK is a SANITY configuration (1 cell line, 4 drugs, 1 cross-line pair, "
                 "2 seeds) and builds 37 tasks. Do NOT quote a QUICK run as a real-data "
                 "result. FULL builds 239."),
    }])
    write_csv(prov, results_path(OUT, "PROVENANCE.csv"))
    Path(results_path(OUT, "PROVENANCE.md")).write_text(
        f"# exp13 provenance\n\n"
        f"These artifacts come from the **{'QUICK' if quick else 'FULL'}** configuration: "
        f"**{len(df)} tasks** (of {len(all_tasks)} built, {len(failures)} failed), "
        f"seeds {seeds}.\n\n"
        f"| configuration | tasks | what it is |\n|---|---:|---|\n"
        f"| QUICK | 37 | 1 cell line, 4 drugs, 1 cross-line pair, 2 seeds. A **sanity run**. |\n"
        f"| FULL | 239 | 3 cell lines, 10 drugs, 3 cross-line pairs, 3 seeds. |\n\n"
        f"The manuscript once reported \"0 of 37 real-data tasks are distributionally "
        f"dominant\". 37 is the QUICK task count: a sanity run had been quoted as the "
        f"real-data result, and nothing on disk recorded that. On the FULL run 11 of the 215 "
        f"observed-condition tasks are dominant. See CORRECTIONS.md R13.\n")
    log(f"  stamped PROVENANCE ({'QUICK' if quick else 'FULL'}, {len(df)} tasks)")
    if failures:
        write_csv(pd.DataFrame(failures), results_path(OUT, "failed_tasks.csv"))
        log(f"  WARNING: {len(failures)} task(s) dropped; see failed_tasks.csv. "
            f"Every count reported below is out of {len(df)}, not {len(all_tasks)}.")

    # ── Percentile transfer: real conflict threshold at HIR crossover percentile ──
    # Only the OBSERVED-condition tasks define the real conflict distribution.
    obs_conf = df[df.information_condition_mode == "observed"].preference_conflict
    real_conflict_threshold = float(np.quantile(obs_conf, boundary["conflict_crossover_percentile"]))
    boundary["real_conflict_threshold"] = real_conflict_threshold
    log(f"  real_conflict_threshold (percentile-transferred) = {real_conflict_threshold:.4f}")

    # ── Pass 2: predict regime using the transferred threshold ──────────────
    preds, correct = [], []
    for _, r in df.iterrows():
        p = predict_regime(r.structure_reliability_score, r.preference_conflict,
                           r.information_condition_mode, real_conflict_threshold)
        preds.append(p)
        if p == "no_DART":
            correct.append(r.observed_best_method == "mean_sufficient")
        else:
            correct.append(p == r.observed_best_method)
    df["HIR_predicted_regime"] = preds
    df["prediction_correct"] = correct

    write_csv(df, results_path(OUT, "projection.csv"))
    report = _acceptance_report(df, boundary)
    Path(results_path(OUT, "acceptance_report.md")).write_text(report)

    section("PROJECTION SUMMARY")
    log(f"  overall accuracy: {df.prediction_correct.mean():.1%} ({int(df.prediction_correct.sum())}/{len(df)})")
    log("\n  by dataset:")
    for dsname in df.dataset.unique():
        sub = df[df.dataset == dsname]
        pred_dist = sub.HIR_predicted_regime.value_counts().to_dict()
        log(f"    {dsname:28s} acc={sub.prediction_correct.mean():.2f} n={len(sub)} pred={pred_dist}")
    return df, boundary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()
    quick = args.quick or os.environ.get("QUICK") == "1"
    run(quick=quick)


if __name__ == "__main__":
    main()

