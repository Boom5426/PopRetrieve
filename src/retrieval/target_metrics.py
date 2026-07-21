"""Target-side + system metrics for the external-baselines comparison (Phase 2).

The package's ``evaluation.py`` already covers DRUG-side ranking (Hit@k / MRR / nDCG@10 /
median-rank) and the ranking-flip primitives (top-1 flip, top-k overlap, Kendall-tau,
delta-rank).  This module adds the pieces the baseline-matrix requires that were missing:

    target_ndcg          — nDCG of a ranked TARGET (gene) list against a graded relevance
                           vector (e.g. drug→target affinity weights).
    target_recall_at_k   — fraction of the relevant target set recovered in the top-K.
    target_hit_at_k      — 1 if any relevant target appears in the top-K.
    network_proximity    — Guney-style shortest-path proximity of a drug's target set to a
                           disease/query target set over a PPI graph (lower = closer). A
                           precomputed-column fallback (benchmark ``graph_proximity``) is
                           supported for when no graph is supplied.
    timed / Timer        — wall-clock runtime capture for the runtime column.
    stratify_by_divergence — bucket per-query records by response-divergence for the
                           divergence-stratified performance tables.

Everything is pure numpy/scipy so it runs without torch.
"""
from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Callable, Iterable, Optional, Sequence

import numpy as np


# ---------------------------------------------------------------------------
# Target-side ranking metrics
# ---------------------------------------------------------------------------


def _dcg(gains: np.ndarray) -> float:
    """Discounted cumulative gain of an already-ordered gain vector (1-indexed ranks)."""
    gains = np.asarray(gains, dtype=float)
    discounts = 1.0 / np.log2(np.arange(2, len(gains) + 2))
    return float(np.sum(gains * discounts))


def target_ndcg(ranked_scores: np.ndarray, relevance: np.ndarray,
                k: Optional[int] = None) -> float:
    """nDCG@k of a ranking induced by ``ranked_scores`` against graded ``relevance``.

    ``ranked_scores`` and ``relevance`` are parallel vectors over the SAME target vocab
    (higher score = predicted more relevant). ``relevance`` is the graded ground-truth gain
    (e.g. affinity weight; 0 = irrelevant). Returns 0 when there is no positive relevance.
    """
    scores = np.asarray(ranked_scores, dtype=float)
    rel = np.asarray(relevance, dtype=float)
    if scores.shape != rel.shape or rel.size == 0:
        raise ValueError("ranked_scores and relevance must be equal-length 1-D vectors")
    if not np.any(rel > 0):
        return 0.0
    n = len(scores) if k is None else min(k, len(scores))
    order = np.argsort(-scores, kind="stable")
    dcg = _dcg(rel[order][:n])
    ideal = _dcg(np.sort(rel)[::-1][:n])
    return float(dcg / ideal) if ideal > 0 else 0.0


def target_recall_at_k(ranked_scores: np.ndarray, relevant_mask: np.ndarray,
                       k: int) -> float:
    """Fraction of the relevant-target set that appears in the top-K of the ranking."""
    scores = np.asarray(ranked_scores, dtype=float)
    mask = np.asarray(relevant_mask, dtype=bool)
    n_rel = int(mask.sum())
    if n_rel == 0:
        return float("nan")
    topk = np.argsort(-scores, kind="stable")[:k]
    return float(mask[topk].sum() / n_rel)


def target_hit_at_k(ranked_scores: np.ndarray, relevant_mask: np.ndarray, k: int) -> float:
    """1.0 if any relevant target is in the top-K, else 0.0."""
    scores = np.asarray(ranked_scores, dtype=float)
    mask = np.asarray(relevant_mask, dtype=bool)
    if mask.sum() == 0:
        return float("nan")
    topk = np.argsort(-scores, kind="stable")[:k]
    return float(mask[topk].any())


def target_precision_at_k(ranked_scores: np.ndarray, relevant_mask: np.ndarray,
                          k: int) -> float:
    scores = np.asarray(ranked_scores, dtype=float)
    mask = np.asarray(relevant_mask, dtype=bool)
    topk = np.argsort(-scores, kind="stable")[:k]
    return float(mask[topk].sum() / k) if k else float("nan")


# ---------------------------------------------------------------------------
# Network proximity (PPI shortest-path; Guney et al. 2016 'closest' measure)
# ---------------------------------------------------------------------------


def network_proximity(drug_targets: Sequence[int], query_targets: Sequence[int],
                      dist_matrix: Optional[np.ndarray] = None,
                      adjacency: Optional[dict[int, set]] = None,
                      measure: str = "closest") -> float:
    """Guney-style network proximity d(T_drug, T_query) over a PPI graph (lower = closer).

    ``measure='closest'``: mean over query targets of the shortest-path distance to the
    nearest drug target (the standard proximity kernel).  ``measure='mean'``: mean over all
    (query,drug) target pairs.  Supply EITHER a precomputed ``dist_matrix`` [N×N of node
    shortest paths] OR an ``adjacency`` dict for on-the-fly BFS.  Returns NaN if either
    target set is empty; +inf contributions are ignored (disconnected).
    """
    S, T = list(drug_targets), list(query_targets)
    if not S or not T:
        return float("nan")
    if dist_matrix is not None:
        D = np.asarray(dist_matrix, dtype=float)
        sub = D[np.ix_(T, S)]                       # [|T|, |S|]
        if measure == "closest":
            per_t = np.nanmin(np.where(np.isfinite(sub), sub, np.nan), axis=1)
            per_t = per_t[np.isfinite(per_t)]
            return float(per_t.mean()) if per_t.size else float("inf")
        finite = sub[np.isfinite(sub)]
        return float(finite.mean()) if finite.size else float("inf")
    if adjacency is not None:
        def sp(src: int, targets: set) -> dict[int, int]:
            seen = {src: 0}; frontier = [src]
            remaining = set(targets)
            while frontier and remaining:
                nxt = []
                for u in frontier:
                    for v in adjacency.get(u, ()):  # neighbors
                        if v not in seen:
                            seen[v] = seen[u] + 1
                            nxt.append(v)
                    remaining.discard(u)
                frontier = nxt
            return seen
        if measure == "closest":
            vals = []
            for t in T:
                d = sp(t, set(S))
                reach = [d[s] for s in S if s in d]
                if reach:
                    vals.append(min(reach))
            return float(np.mean(vals)) if vals else float("inf")
        vals = []
        for t in T:
            d = sp(t, set(S))
            vals += [d[s] for s in S if s in d]
        return float(np.mean(vals)) if vals else float("inf")
    raise ValueError("network_proximity needs either dist_matrix or adjacency")


def proximity_from_column(values: Sequence[float], higher_is_closer: bool = True) -> np.ndarray:
    """Convenience: turn a benchmark 'graph_proximity' column into a distance-like array.

    The PDGrapher closed-loop benchmark stores ``graph_proximity`` as a similarity
    (higher = closer). Negate it (with ``higher_is_closer=True``) so downstream code that
    treats proximity as a distance (lower = closer) stays consistent.
    """
    v = np.asarray(values, dtype=float)
    return -v if higher_is_closer else v


# ---------------------------------------------------------------------------
# Runtime capture
# ---------------------------------------------------------------------------


@contextmanager
def Timer():
    """Context manager yielding a dict whose ``['seconds']`` is filled on exit."""
    rec: dict[str, float] = {}
    t0 = time.perf_counter()
    try:
        yield rec
    finally:
        rec["seconds"] = time.perf_counter() - t0


def timed(fn: Callable, *args, **kwargs) -> tuple:
    """Call ``fn`` and return (result, elapsed_seconds)."""
    t0 = time.perf_counter()
    out = fn(*args, **kwargs)
    return out, time.perf_counter() - t0


# ---------------------------------------------------------------------------
# Divergence stratification
# ---------------------------------------------------------------------------

# Standard response-cosine buckets: lower cosine => more divergent subpop responses.
DIVERGENCE_BINS = [-1.01, 0.3, 0.6, 0.9, 1.01]
DIVERGENCE_LABELS = ["high(<0.3)", "mid(0.3-0.6)", "low(0.6-0.9)", "none(>0.9)"]


def divergence_bucket(cosine_value: float,
                      bins: Sequence[float] = DIVERGENCE_BINS,
                      labels: Sequence[str] = DIVERGENCE_LABELS) -> str:
    """Map a subpop-response cosine to a divergence stratum label."""
    if cosine_value is None or not np.isfinite(cosine_value):
        return "unknown"
    idx = int(np.digitize([cosine_value], bins)[0]) - 1
    idx = max(0, min(idx, len(labels) - 1))
    return labels[idx]


def stratify_by_divergence(records, value_col: str, cos_col: str = "divergence",
                           group_cols: Optional[Sequence[str]] = None,
                           bins: Sequence[float] = DIVERGENCE_BINS,
                           labels: Sequence[str] = DIVERGENCE_LABELS):
    """Bucket a DataFrame of per-query records by response divergence and average.

    Returns a DataFrame with the divergence stratum, optional extra group columns, the
    mean of ``value_col`` and the count. Pure-pandas; imported lazily to keep this module
    torch/pandas-optional at import time.
    """
    import pandas as pd
    df = records.copy() if isinstance(records, pd.DataFrame) else pd.DataFrame(records)
    df["divergence_stratum"] = df[cos_col].apply(lambda v: divergence_bucket(v, bins, labels))
    keys = ["divergence_stratum"] + list(group_cols or [])
    out = (df.groupby(keys, sort=False)[value_col]
             .agg(["mean", "count"]).reset_index()
             .rename(columns={"mean": f"{value_col}_mean", "count": "n"}))
    return out
