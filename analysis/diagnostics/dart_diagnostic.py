"""
EvalShift diagnostic protocol: four probes for distributional retrieval methods.

Purpose
-------
Distinguish a REAL method null (the method genuinely has no oracle-independent
advantage) from an IMPLEMENTATION ARTIFACT (a null caused by an unfair comparison,
a broken metric, low statistical power, or a hidden confound).

Developed during the EvalShift audit (2026-07). Each probe returns a verdict dict.
These are dependency-light (numpy, scipy, scikit-learn) and operate on cell x gene
matrices already in memory.

The four probes
---------------
1. translation_invariance_probe
   Checks whether a distance is centering-invariant. Answers: "is comparing
   method A on raw cells vs method B on control-subtracted deltas an unfair
   comparison?" For translation-invariant distances (e.g. energy distance) the
   answer is no: E(P,Q) == E(P-c, Q-c). Falsifies the 'delta-vs-raw asymmetry'
   objection.

2. subsampling_power_probe
   Bootstraps a score under cell subsampling and reports the coefficient of
   variation (CV) at each n. Answers: "is the null caused by an estimator too
   noisy at the cell budget used?" A low CV at the operating n rules out
   power loss as the cause.

3. metric_blindspot_probe
   Compares a candidate scalar/mean-based metric against a cell-level reference
   metric. Answers: "does the reported metric actually measure what it claims,
   or is it structurally blind?" A near-zero dynamic range or negative rank
   correlation with the cell-level reference exposes a failed metric.

4. magnitude_confound_probe
   Tests whether a method's alignment with an external readout is explained by
   response magnitude alone. Answers: "is an apparent positive result just the
   near-tautology that larger perturbations track the readout?" If a
   query-independent magnitude scalar reproduces or beats the method's
   correlation, the positive is a confound, not distributional structure.

Usage
-----
    from dart_diagnostic import (
        translation_invariance_probe, subsampling_power_probe,
        metric_blindspot_probe, magnitude_confound_probe,
    )
    v1 = translation_invariance_probe(score_energy, pops)
    v2 = subsampling_power_probe(score_energy, P, Q, ns=[60,120,250,500])
    v3 = metric_blindspot_probe(mean_metric_fn, cell_metric_fn, cases)
    v4 = magnitude_confound_probe(method_scores, magnitudes, external_readout)
"""
from __future__ import annotations
import numpy as np
from scipy import stats


def translation_invariance_probe(score_fn, populations, n_pairs=10, seed=0):
    """Probe 1. Is score_fn translation-invariant (centering-independent)?

    score_fn(P, Q) -> float. populations: list of (n_cells, n_genes) arrays.
    Recomputes all pairwise scores after subtracting a common shift c from every
    cell of both populations, and correlates raw vs shifted score matrices.

    Verdict: is_translation_invariant True if Spearman rho of raw-vs-shifted
    pairwise scores is ~1.0 (>0.999). If True, a 'delta-vs-raw asymmetry'
    objection is falsified for this score.
    """
    rng = np.random.default_rng(seed)
    pops = populations[: min(len(populations), 8)]
    c = rng.normal(size=pops[0].shape[1]) * np.abs([p.mean() for p in pops]).mean()
    raw, shifted = [], []
    for i in range(len(pops)):
        for j in range(len(pops)):
            if i < j:
                raw.append(score_fn(pops[i], pops[j]))
                shifted.append(score_fn(pops[i] - c, pops[j] - c))
    raw, shifted = np.array(raw), np.array(shifted)
    rho, _ = stats.spearmanr(raw, shifted)
    max_abs_diff = float(np.max(np.abs(raw - shifted)))
    return {
        "probe": "translation_invariance",
        "spearman_raw_vs_shifted": float(rho),
        "max_abs_score_diff": max_abs_diff,
        "is_translation_invariant": bool(rho > 0.999 and max_abs_diff < 1e-3 * (np.abs(raw).mean() + 1e-9)),
        "interpretation": "If invariant, raw-vs-delta comparison is fair; delta-asymmetry objection falsified.",
    }


def subsampling_power_probe(score_fn, P, Q, ns=(60, 120, 250, 500), n_boot=30, seed=0):
    """Probe 2. Estimator stability vs cell budget.

    Bootstraps score_fn(P_sub, Q_sub) at each subsample size n and reports the
    coefficient of variation (CV). Low CV at the operating n rules out power
    loss as the cause of a null.

    Verdict: power_loss_likely True if CV at the smallest n exceeds 0.25.
    """
    rng = np.random.default_rng(seed)
    out = {}
    for n in ns:
        vals = []
        for _ in range(n_boot):
            pi = rng.choice(len(P), min(n, len(P)), replace=len(P) < n)
            qi = rng.choice(len(Q), min(n, len(Q)), replace=len(Q) < n)
            vals.append(score_fn(P[pi], Q[qi]))
        vals = np.array(vals, float)
        out[int(n)] = {"mean": float(vals.mean()), "std": float(vals.std()),
                       "cv": float(vals.std() / (abs(vals.mean()) + 1e-12))}
    cv_small = out[int(min(ns))]["cv"]
    return {
        "probe": "subsampling_power",
        "by_n": out,
        "cv_at_smallest_n": cv_small,
        "power_loss_likely": bool(cv_small > 0.25),
        "interpretation": "Low CV at operating n means the estimator is stable; power loss does not explain the null.",
    }


def metric_blindspot_probe(mean_metric_fn, cell_metric_fn, cases):
    """Probe 3. Does a mean/scalar metric actually measure the property?

    mean_metric_fn(case) and cell_metric_fn(case) each return a float for the
    same case (case is any object both accept). Compares their rank correlation
    and the mean-metric dynamic range across cases.

    Verdict: metric_is_blind True if the two disagree (rho <= 0) OR the
    mean-metric has near-zero dynamic range (CV < 0.05).
    """
    mvals = np.array([mean_metric_fn(c) for c in cases], float)
    cvals = np.array([cell_metric_fn(c) for c in cases], float)
    rho, p = stats.spearmanr(mvals, cvals)
    cv = float(mvals.std() / (abs(mvals.mean()) + 1e-12))
    return {
        "probe": "metric_blindspot",
        "spearman_mean_vs_cell": float(rho),
        "mean_metric_cv": cv,
        "n_cases": len(cases),
        "metric_is_blind": bool((rho <= 0) or (cv < 0.05)),
        "interpretation": "Negative/zero correlation with the cell-level reference, or near-zero dynamic range, means the scalar metric is structurally blind.",
    }


def magnitude_confound_probe(method_scores, magnitudes, external_readout, higher_is_better_method=False):
    """Probe 4. Is a method's readout-alignment a response-magnitude artifact?

    method_scores: per-candidate method score (array).
    magnitudes: per-candidate response magnitude ||mean_treated - mean_control|| (array).
    external_readout: per-candidate external functional readout (array, e.g. GDSC AUC).
    higher_is_better_method: whether a higher method score means 'more similar/better'.

    Compares the method's rank correlation with the readout against a
    query-independent magnitude-only ranking, and reports how much of the method
    score is explained by magnitude.

    Verdict: is_magnitude_confound True if magnitude-only correlation with the
    readout is >= the method's (magnitude alone does as well or better) AND the
    method score is strongly explained by magnitude (|rho| > 0.5).
    """
    ms = np.asarray(method_scores, float)
    mag = np.asarray(magnitudes, float)
    ext = np.asarray(external_readout, float)
    method_rank = stats.rankdata(-ms if higher_is_better_method else ms)
    ext_rank = stats.rankdata(ext)
    rho_method, _ = stats.spearmanr(method_rank, ext_rank)
    rho_mag, _ = stats.spearmanr(stats.rankdata(-mag), ext_rank)     # larger magnitude first
    rho_method_mag, _ = stats.spearmanr(ms, mag)
    return {
        "probe": "magnitude_confound",
        "method_vs_readout_rho": float(rho_method),
        "magnitude_only_vs_readout_rho": float(rho_mag),
        "method_explained_by_magnitude_rho": float(rho_method_mag),
        "is_magnitude_confound": bool(abs(rho_mag) >= abs(rho_method) and abs(rho_method_mag) > 0.5),
        "interpretation": "If a query-independent magnitude scalar matches/beats the method and explains its score, the positive is a magnitude confound, not distributional structure.",
    }


ALL_PROBES = [
    translation_invariance_probe,
    subsampling_power_probe,
    metric_blindspot_probe,
    magnitude_confound_probe,
]
