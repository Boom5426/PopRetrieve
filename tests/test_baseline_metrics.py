"""Unit tests for the Phase-2 target-side + system metrics (target_metrics.py).

Degenerate-limit and monotonicity checks that pin the new metrics before they feed the
baseline-matrix. Runs under the offline runner (tests/run_tests.py) or pytest.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np

from retrieval.target_metrics import (
    network_proximity, stratify_by_divergence, target_hit_at_k, target_ndcg,
    target_precision_at_k, target_recall_at_k, divergence_bucket, Timer,
)


# --- target nDCG: bounds & ordering ---------------------------------------

def test_target_ndcg_perfect_is_one():
    rel = np.array([3.0, 2.0, 1.0, 0.0, 0.0])
    scores = rel.copy()                       # ranking == ideal
    assert abs(target_ndcg(scores, rel) - 1.0) < 1e-9


def test_target_ndcg_reversed_is_low():
    rel = np.array([3.0, 2.0, 1.0, 0.0, 0.0])
    scores = -rel                             # worst-possible order
    assert target_ndcg(scores, rel) < target_ndcg(rel, rel)


def test_target_ndcg_no_relevance_is_zero():
    rel = np.zeros(5)
    assert target_ndcg(np.arange(5.0), rel) == 0.0


def test_target_ndcg_between_zero_and_one():
    rng = np.random.default_rng(0)
    for _ in range(20):
        rel = rng.integers(0, 4, size=10).astype(float)
        scores = rng.normal(size=10)
        v = target_ndcg(scores, rel)
        assert -1e-9 <= v <= 1.0 + 1e-9


# --- target recall@K: monotone non-decreasing in K -------------------------

def test_target_recall_monotone_in_k():
    scores = np.array([5, 4, 3, 2, 1, 0], dtype=float)
    mask = np.array([0, 1, 0, 1, 0, 1], dtype=bool)   # 3 relevant
    recalls = [target_recall_at_k(scores, mask, k) for k in range(1, 7)]
    assert all(b >= a - 1e-12 for a, b in zip(recalls, recalls[1:]))
    assert abs(recalls[-1] - 1.0) < 1e-12             # all recovered at K=N


def test_target_recall_perfect_topk():
    scores = np.array([5, 4, 3, 2, 1], dtype=float)
    mask = np.array([1, 1, 0, 0, 0], dtype=bool)      # top-2 are the relevant ones
    assert abs(target_recall_at_k(scores, mask, 2) - 1.0) < 1e-12


def test_target_hit_and_precision():
    scores = np.array([5, 4, 3, 2, 1], dtype=float)
    mask = np.array([0, 0, 1, 0, 0], dtype=bool)
    assert target_hit_at_k(scores, mask, 1) == 0.0
    assert target_hit_at_k(scores, mask, 3) == 1.0
    assert abs(target_precision_at_k(scores, mask, 3) - (1.0 / 3)) < 1e-12


# --- network proximity: identity, symmetry-ish, disconnection --------------

def _line_graph_dist(n: int) -> np.ndarray:
    """Shortest-path distances on a path graph 0-1-2-...-(n-1)."""
    idx = np.arange(n)
    return np.abs(idx[:, None] - idx[None, :]).astype(float)


def test_proximity_zero_when_sets_share_node():
    D = _line_graph_dist(6)
    # query target 2 is also a drug target -> closest distance 0
    assert network_proximity(drug_targets=[2, 5], query_targets=[2], dist_matrix=D) == 0.0


def test_proximity_increases_with_separation():
    D = _line_graph_dist(10)
    near = network_proximity([3], [2], dist_matrix=D)     # distance 1
    far = network_proximity([9], [2], dist_matrix=D)      # distance 7
    assert near < far
    assert abs(near - 1.0) < 1e-12 and abs(far - 7.0) < 1e-12


def test_proximity_adjacency_matches_matrix():
    D = _line_graph_dist(6)
    adj = {i: {j for j in (i - 1, i + 1) if 0 <= j < 6} for i in range(6)}
    a = network_proximity([0], [4], dist_matrix=D)
    b = network_proximity([0], [4], adjacency=adj)
    assert abs(a - b) < 1e-12


def test_proximity_empty_set_is_nan():
    D = _line_graph_dist(4)
    assert np.isnan(network_proximity([], [1], dist_matrix=D))


# --- divergence bucketing & stratification --------------------------------

def test_divergence_bucket_edges():
    assert divergence_bucket(0.1) == "high(<0.3)"
    assert divergence_bucket(0.95) == "none(>0.9)"
    assert divergence_bucket(float("nan")) == "unknown"


def test_stratify_by_divergence_groups():
    recs = [
        {"divergence": 0.1, "hit": 1.0}, {"divergence": 0.2, "hit": 1.0},
        {"divergence": 0.95, "hit": 0.0}, {"divergence": 0.98, "hit": 0.0},
    ]
    out = stratify_by_divergence(recs, value_col="hit")
    hi = out[out.divergence_stratum == "high(<0.3)"]
    lo = out[out.divergence_stratum == "none(>0.9)"]
    assert abs(float(hi["hit_mean"].iloc[0]) - 1.0) < 1e-12 and int(hi["n"].iloc[0]) == 2
    assert abs(float(lo["hit_mean"].iloc[0]) - 0.0) < 1e-12 and int(lo["n"].iloc[0]) == 2


def test_timer_records_seconds():
    with Timer() as t:
        _ = sum(range(1000))
    assert "seconds" in t and t["seconds"] >= 0.0
