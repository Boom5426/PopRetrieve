"""Retrieval metrics: Hit@k, MRR, nDCG@10, median/mean rank, MOA-AUC + bootstrap CI."""
from __future__ import annotations

from typing import Optional

import numpy as np


def ranks_of_true(scores: np.ndarray, true_pos: np.ndarray) -> np.ndarray:
    """1-indexed rank of the true candidate for each query (higher score = better)."""
    true_score = scores[np.arange(len(true_pos)), true_pos]                  # [Q]
    strictly_greater = (scores > true_score[:, None]).sum(axis=1)           # [Q]
    return strictly_greater + 1


def moa_auc(scores: np.ndarray, moa_same: np.ndarray, true_pos: np.ndarray) -> np.ndarray:
    """Per-query AUC of ranking same-MOA candidates above others (excludes the
    true drug itself).  Returns per-query AUC (nan where undefined)."""
    Q, D = scores.shape
    out = np.full(Q, np.nan)
    for q in range(Q):
        pos = moa_same[q].astype(bool).copy()
        pos[true_pos[q]] = False                       # exclude the true drug
        neg = ~pos
        neg[true_pos[q]] = False
        npos, nneg = pos.sum(), neg.sum()
        if npos == 0 or nneg == 0:
            continue
        order = np.argsort(scores[q])                  # ascending
        rank = np.empty(D); rank[order] = np.arange(1, D + 1)
        auc = (rank[pos].sum() - npos * (npos + 1) / 2) / (npos * nneg)
        out[q] = auc
    return out


def retrieval_metrics(scores: np.ndarray, true_pos: np.ndarray,
                      moa_same: Optional[np.ndarray] = None,
                      ks=(1, 5, 10)) -> dict[str, float]:
    r = ranks_of_true(scores, true_pos).astype(float)
    D = scores.shape[1]
    out: dict[str, float] = {}
    for k in ks:
        out[f"hit@{k}"] = float(np.mean(r <= k))
    out["mrr"] = float(np.mean(1.0 / r))
    ndcg = np.where(r <= 10, 1.0 / np.log2(r + 1), 0.0)
    out["ndcg@10"] = float(np.mean(ndcg))
    out["median_rank"] = float(np.median(r))
    out["mean_rank"] = float(np.mean(r))
    out["median_rank_frac"] = float(np.median(r) / D)
    out["n_queries"] = int(len(r))
    if moa_same is not None:
        a = moa_auc(scores, moa_same, true_pos)
        out["moa_auc"] = float(np.nanmean(a)) if np.isfinite(a).any() else float("nan")
    return out


def bootstrap_ci(scores: np.ndarray, true_pos: np.ndarray, metric: str = "hit@10",
                 moa_same: Optional[np.ndarray] = None, n_boot: int = 1000,
                 seed: int = 0) -> tuple[float, float, float]:
    """Return (point, lo95, hi95) for a metric via query resampling."""
    rng = np.random.default_rng(seed)
    Q = len(true_pos)
    point = retrieval_metrics(scores, true_pos, moa_same)[metric]
    vals = []
    for _ in range(n_boot):
        idx = rng.integers(0, Q, Q)
        ms = moa_same[idx] if moa_same is not None else None
        vals.append(retrieval_metrics(scores[idx], true_pos[idx], ms)[metric])
    lo, hi = np.percentile(vals, [2.5, 97.5])
    return float(point), float(lo), float(hi)
