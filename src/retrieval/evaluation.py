"""Retrieval evaluation + ranking-flip analysis.

Two layers:

1. Ported ranking metrics (from ``gidflow.metrics.ranking``): ``ranks_of_true`` and
   ``retrieval_metrics`` (Hit@k / MRR / nDCG@10 / median-rank) over a batch of
   queries ``scores`` of shape ``[Q, D]`` (higher score = better).

2. NEW ranking-flip primitives (plan §8-Exp7 / §14-Phase2) that operate on a
   SINGLE query's per-candidate score vectors from two rankers ``a`` and ``b``:
   top-1 flip (with decision direction), top-k overlap (Jaccard / fraction),
   Kendall-tau, Spearman-rho, and delta-rank of the ground-truth candidate. These
   turn "distance got bigger" into "the top-ranked drug actually changed".
"""
from __future__ import annotations

from typing import Optional, Sequence

import numpy as np
from scipy.stats import kendalltau, spearmanr

# ---------------------------------------------------------------------------
# Ported batch retrieval metrics
# ---------------------------------------------------------------------------


def ranks_of_true(scores: np.ndarray, true_pos: np.ndarray) -> np.ndarray:
    """1-indexed rank of the true candidate for each query (higher score = better)."""
    scores = np.asarray(scores, dtype=float)
    true_pos = np.asarray(true_pos)
    true_score = scores[np.arange(len(true_pos)), true_pos]        # [Q]
    strictly_greater = (scores > true_score[:, None]).sum(axis=1)  # [Q]
    return strictly_greater + 1


def retrieval_metrics(scores: np.ndarray, true_pos: np.ndarray,
                      ks: Sequence[int] = (1, 5, 10)) -> dict[str, float]:
    r = ranks_of_true(scores, true_pos).astype(float)
    D = np.asarray(scores).shape[1]
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
    return out


def hit_at_1(vals: np.ndarray, gt: int) -> float:
    """Convenience: Hit@1 of ground-truth index ``gt`` from a 1-D candidate score
    vector (mirrors the ``retrieval_metrics(vals[None], [gt])['hit@1']`` idiom)."""
    return float(retrieval_metrics(np.asarray(vals)[None], np.array([gt]))["hit@1"])


# ---------------------------------------------------------------------------
# Ranking-flip primitives (single query; a, b are 1-D score vectors over the SAME
# ordered candidate list)
# ---------------------------------------------------------------------------


def rank_of(scores: np.ndarray, index: int) -> int:
    """1-indexed rank of ``index`` in a single query's candidate scores."""
    scores = np.asarray(scores, dtype=float)
    return int((scores > scores[index]).sum() + 1)


def top1_index(scores: np.ndarray) -> int:
    return int(np.argmax(np.asarray(scores, dtype=float)))


def top1_flip(scores_a: np.ndarray, scores_b: np.ndarray) -> bool:
    """Does the #1 candidate change between ranker a and ranker b?"""
    return top1_index(scores_a) != top1_index(scores_b)


def topk_set(scores: np.ndarray, k: int) -> set[int]:
    order = np.argsort(-np.asarray(scores, dtype=float))
    return set(order[:k].tolist())


def topk_overlap(scores_a: np.ndarray, scores_b: np.ndarray, k: int,
                 metric: str = "jaccard") -> float:
    """Agreement of the two top-k candidate sets.

    metric='jaccard'   -> |A∩B| / |A∪B|
    metric='fraction'  -> |A∩B| / k        (fraction of a's top-k shared by b)
    """
    A, B = topk_set(scores_a, k), topk_set(scores_b, k)
    inter = len(A & B)
    if metric == "jaccard":
        union = len(A | B)
        return float(inter / union) if union else 1.0
    if metric == "fraction":
        return float(inter / k) if k else 1.0
    raise ValueError(f"unknown overlap metric {metric!r}")


def kendall_tau(scores_a: np.ndarray, scores_b: np.ndarray) -> float:
    tau = kendalltau(np.asarray(scores_a, dtype=float),
                     np.asarray(scores_b, dtype=float)).correlation
    return float(tau) if tau is not None and np.isfinite(tau) else float("nan")


def spearman_rho(scores_a: np.ndarray, scores_b: np.ndarray) -> float:
    rho = spearmanr(np.asarray(scores_a, dtype=float),
                    np.asarray(scores_b, dtype=float)).correlation
    return float(rho) if rho is not None and np.isfinite(rho) else float("nan")


def delta_rank(scores_a: np.ndarray, scores_b: np.ndarray, gt_index: int) -> int:
    """rank_of_true under ranker a  minus  rank under ranker b (a=incumbent, b=ours).
    Positive => ranker b ranks the ground truth HIGHER (better)."""
    return rank_of(scores_a, gt_index) - rank_of(scores_b, gt_index)


def decision_flip(scores_a: np.ndarray, scores_b: np.ndarray, names: Sequence[str],
                  gt_index: int) -> dict:
    """Characterize a single query's flip between incumbent ``a`` and ours ``b``.

    Returns the two top-1 candidate names, whether the ground truth is now #1 under
    b but was NOT under a (a 'real decision flip' toward the correct covers-both
    drug), and the delta-rank.
    """
    ia, ib = top1_index(scores_a), top1_index(scores_b)
    gt_name = names[gt_index]
    top_a, top_b = names[ia], names[ib]
    return {
        "top1_a": top_a,
        "top1_b": top_b,
        "flipped": ia != ib,
        "a_correct": ia == gt_index,
        "b_correct": ib == gt_index,
        # the money case: incumbent picked the wrong (majority-biased) drug, ours the GT
        "decision_flip_to_gt": (ib == gt_index) and (ia != gt_index),
        "delta_rank": delta_rank(scores_a, scores_b, gt_index),
        "gt": gt_name,
    }
