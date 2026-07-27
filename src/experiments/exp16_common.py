"""Shared machinery for exp16 (gate diagnosis) and exp17 (true-divergence subset).

The one quantity both experiments need that exp12 does NOT log is the *true
subpopulation response divergence* of each query — computed directly from the
rebuilt query population and the context control, WITHOUT passing through any
gate intermediate (structure_reliability / preference_conflict / the diagnostic
features). This decoupling is the whole point of the audit: we must be able to
compare the gate's labels against a divergence measure the gate never saw.

true_response_divergence(query_X, query_states, control_mean):
    For each query subpopulation state, form its RESPONSE DIRECTION delta
    (state mean - control mean). Divergence = 1 - mean pairwise cosine between
    state response deltas. High divergence <=> states respond in different
    directions <=> exactly the regime where distributional retrieval could help.

This is deliberately a *response* divergence (delta from control), not a raw
geometric spread of query_X, so it is comparable across contexts with different
baseline expression and is not identical to subpopulation_variance_ratio (which
is a raw within/between variance ratio of query_X, no control subtraction).
"""
from __future__ import annotations

import numpy as np

# ---------------------------------------------------------------------------
# The "not applicable" sentinel in exp12's per-query CSV
# ---------------------------------------------------------------------------
#
# exp12 encodes "this metric is undefined for this split type" as the literal value -1,
# not as NaN (exp12_partial_observed_retrieval.py, the leave_MoA_out and partial_library
# branches). Mechanism-of-action recovery is undefined for leave_MoA_out, because the whole
# MoA class is removed from the library, and for partial_library.
#
# If a sentinel is differenced like a real measurement, the paired gap becomes
# (-1) - (-1) = EXACTLY 0. On the shipped per_query_scores.csv that is 165 of 765 queries
# (21.6%): 120 leave_MoA_out + 45 partial_library. Those structural zeros were entering n,
# pinning median_gap at exactly 0.000 in every divergence stratum, shrinking sd_gap, and
# feeding the power calculation. The qualitative verdict on moa_ndcg (no EvalShift advantage)
# survives and in fact strengthens, but the published statistics did not.
#
# Mask them here, once, for every consumer.
SENTINEL = -1.0
SENTINEL_METRICS = ("moa_hit@1", "moa_hit@5", "moa_mrr", "moa_ndcg", "moa_rank",
                    "target_hit@5", "target_mrr")


def mask_undefined(df, metrics=None):
    """Turn exp12's -1 'not applicable' sentinel into NaN so it cannot enter a statistic.

    Only the metrics that actually use the sentinel are touched. Genuinely-defined metrics
    such as minority_state_coverage (a cosine, never negative here) are left alone.
    """
    out = df.copy()
    for c in (metrics if metrics is not None else SENTINEL_METRICS):
        if c in out.columns:
            out[c] = out[c].mask(out[c] <= SENTINEL + 1e-9)
    return out


def _unit(v: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    n = np.linalg.norm(v)
    return v / n if n > eps else v * 0.0


def true_response_divergence(query_X: np.ndarray, query_states: np.ndarray,
                             control_mean: np.ndarray, min_state_cells: int = 3) -> float:
    """1 - mean pairwise cosine of per-state response deltas. Range ~[0, 2].

    query_X       : (n_cells, n_genes) query population (treated cells)
    query_states  : (n_cells,) integer subpopulation labels
    control_mean  : (n_genes,) context control mean, to form response deltas
    Returns np.nan if fewer than two states have >= min_state_cells cells.
    """
    query_X = np.asarray(query_X, dtype=np.float64)
    control_mean = np.asarray(control_mean, dtype=np.float64).reshape(-1)
    states = [s for s in np.unique(query_states)
              if int(np.sum(query_states == s)) >= min_state_cells]
    if len(states) < 2:
        return float("nan")
    deltas = [_unit(query_X[query_states == s].mean(0) - control_mean) for s in states]
    cosims = []
    for i in range(len(deltas)):
        for j in range(i + 1, len(deltas)):
            cosims.append(float(np.dot(deltas[i], deltas[j])))
    if not cosims:
        return float("nan")
    return float(1.0 - np.mean(cosims))  # low cosine -> high divergence


def divergence_components(query_X, query_states, control_mean, min_state_cells: int = 3) -> dict:
    """Extra descriptors of the response divergence (for diagnostics / CSV columns)."""
    query_X = np.asarray(query_X, dtype=np.float64)
    control_mean = np.asarray(control_mean, dtype=np.float64).reshape(-1)
    uniq, counts = np.unique(query_states, return_counts=True)
    keep = [(s, c) for s, c in zip(uniq, counts) if c >= min_state_cells]
    out = {"n_states_used": len(keep),
           "minority_frac": float(counts.min() / counts.sum()) if len(counts) else float("nan")}
    if len(keep) < 2:
        out.update({"min_pairwise_cos": float("nan"), "delta_norm_ratio": float("nan")})
        return out
    states = [s for s, _ in keep]
    raw_deltas = [query_X[query_states == s].mean(0) - control_mean for s in states]
    deltas = [_unit(d) for d in raw_deltas]
    cosims = [float(np.dot(deltas[i], deltas[j]))
              for i in range(len(deltas)) for j in range(i + 1, len(deltas))]
    norms = [float(np.linalg.norm(d)) for d in raw_deltas]
    out["min_pairwise_cos"] = float(np.min(cosims))
    out["delta_norm_ratio"] = float(np.min(norms) / (np.max(norms) + 1e-12))
    return out


def benjamini_hochberg(pvals: np.ndarray, alpha: float = 0.05) -> np.ndarray:
    """Return BH-adjusted q-values for a 1D array of p-values (NaNs pass through)."""
    p = np.asarray(pvals, dtype=np.float64)
    finite = np.isfinite(p)
    q = np.full_like(p, np.nan)
    if finite.sum() == 0:
        return q
    idx = np.where(finite)[0]
    pf = p[idx]
    order = np.argsort(pf)
    n = len(pf)
    ranked = pf[order]
    adj = ranked * n / (np.arange(1, n + 1))
    adj = np.minimum.accumulate(adj[::-1])[::-1]  # enforce monotonicity
    adj = np.clip(adj, 0, 1)
    qf = np.empty(n)
    qf[order] = adj
    q[idx] = qf
    return q


def power_two_sided(effect, sd, n, alpha: float = 0.05) -> float:
    """Approx power of a one-sample (paired-difference) t-test via normal approx.

    effect : observed mean paired difference
    sd     : sd of the paired differences
    n      : sample size
    """
    from scipy.stats import norm
    if sd <= 0 or n < 2 or not np.isfinite(effect):
        return float("nan")
    se = sd / np.sqrt(n)
    z = abs(effect) / se
    zcrit = norm.ppf(1 - alpha / 2)
    return float(norm.cdf(z - zcrit) + norm.cdf(-z - zcrit))


def n_for_power(effect, sd, power: float = 0.8, alpha: float = 0.05) -> float:
    """Sample size to reach `power` for a paired-difference test (normal approx)."""
    from scipy.stats import norm
    if sd <= 0 or effect == 0 or not np.isfinite(effect):
        return float("inf")
    zpow = norm.ppf(power)
    zcrit = norm.ppf(1 - alpha / 2)
    return float(((zcrit + zpow) * sd / abs(effect)) ** 2)
