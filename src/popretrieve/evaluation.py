"""Stable public aliases for ranking and retrieval evaluation primitives."""

from retrieval.evaluation import (
    decision_flip,
    delta_rank,
    hit_at_1,
    kendall_tau,
    rank_of,
    ranks_of_true,
    retrieval_metrics,
    spearman_rho,
    top1_flip,
    top1_index,
    topk_overlap,
    topk_set,
)

__all__ = [
    "decision_flip",
    "delta_rank",
    "hit_at_1",
    "kendall_tau",
    "rank_of",
    "ranks_of_true",
    "retrieval_metrics",
    "spearman_rho",
    "top1_flip",
    "top1_index",
    "topk_overlap",
    "topk_set",
]

