"""Unit tests for retrieval metrics + the NEW ranking-flip primitives (exp07)."""
import numpy as np

from retrieval.evaluation import (
    ranks_of_true, retrieval_metrics, hit_at_1, rank_of,
    top1_flip, topk_overlap, kendall_tau, spearman_rho, delta_rank, decision_flip,
)


def test_ranks_of_true():
    scores = np.array([[0.1, 0.9, 0.5]])
    assert ranks_of_true(scores, np.array([0]))[0] == 3   # true=idx0 is smallest
    assert ranks_of_true(scores, np.array([1]))[0] == 1   # true=idx1 is largest


def test_retrieval_metrics_and_hit_at_1():
    scores = np.array([[0.9, 0.1, 0.5, 0.2]])
    m = retrieval_metrics(scores, np.array([0]))
    assert m["hit@1"] == 1.0 and m["mrr"] == 1.0
    assert hit_at_1(np.array([0.9, 0.1, 0.5, 0.2]), 0) == 1.0
    assert hit_at_1(np.array([0.9, 0.1, 0.5, 0.2]), 1) == 0.0


def test_rank_of():
    assert rank_of(np.array([0.9, 0.1, 0.5]), 1) == 3
    assert rank_of(np.array([0.9, 0.1, 0.5]), 0) == 1


def test_top1_flip():
    a = np.array([0.9, 0.1, 0.5])
    b = np.array([0.1, 0.9, 0.5])
    assert top1_flip(a, b)
    assert not top1_flip(a, a)


def test_topk_overlap():
    a = np.array([3.0, 2, 1, 0])           # top-2 indices {0,1}
    assert topk_overlap(a, a, 2) == 1.0
    c = np.array([0.0, 1, 2, 3])           # top-2 indices {2,3}
    assert topk_overlap(a, c, 2, "jaccard") == 0.0
    assert topk_overlap(a, c, 2, "fraction") == 0.0


def test_kendall_and_spearman():
    a = np.array([1.0, 2, 3, 4])
    assert kendall_tau(a, a) > 0.99
    assert kendall_tau(a, a[::-1]) < -0.99
    assert spearman_rho(a, a) > 0.99


def test_delta_rank():
    a = np.array([0.9, 0.1, 0.5])          # gt idx1 -> rank 3
    b = np.array([0.1, 0.9, 0.5])          # gt idx1 -> rank 1
    assert delta_rank(a, b, 1) == 2        # ours ranks gt 2 positions higher


def test_decision_flip_to_gt():
    names = ["covers-both", "majority-only", "d1"]
    a = np.array([0.1, 0.9, 0.5])          # incumbent picks majority-only (wrong)
    b = np.array([0.9, 0.1, 0.5])          # ours picks covers-both (correct)
    d = decision_flip(a, b, names, 0)
    assert d["decision_flip_to_gt"]
    assert d["top1_a"] == "majority-only" and d["top1_b"] == "covers-both"
    assert not d["a_correct"] and d["b_correct"]
