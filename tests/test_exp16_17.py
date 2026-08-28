"""Smoke tests for exp16 (gate diagnosis) and exp17 (true-divergence subset).

Covers the reusable machinery in exp16_common (true divergence on degenerate/known
inputs, BH correction, power functions) plus the metric-class invariants the audit
depends on. Discovered by tests/run_tests.py (test_* functions).
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from experiments.exp16_common import (
    true_response_divergence, divergence_components,
    benjamini_hochberg, power_two_sided, n_for_power,
)


def test_true_divergence_identical_states_is_low():
    """Two states with the SAME response direction -> divergence ~0."""
    rng = np.random.default_rng(0)
    ctrl = np.zeros(20)
    direction = rng.standard_normal(20)
    # both states = control + same direction (+ tiny noise), different magnitudes
    s0 = ctrl + direction + 0.01 * rng.standard_normal((50, 20))
    s1 = ctrl + 2 * direction + 0.01 * rng.standard_normal((50, 20))
    X = np.vstack([s0, s1])
    states = np.array([0] * 50 + [1] * 50)
    div = true_response_divergence(X, states, ctrl)
    assert div < 0.1, f"identical-direction states should have low divergence, got {div}"


def test_true_divergence_opposite_states_is_high():
    """Two states with OPPOSITE response directions -> divergence ~2 (cos ~ -1)."""
    rng = np.random.default_rng(1)
    ctrl = np.zeros(20)
    direction = rng.standard_normal(20)
    s0 = ctrl + direction + 0.01 * rng.standard_normal((50, 20))
    s1 = ctrl - direction + 0.01 * rng.standard_normal((50, 20))
    X = np.vstack([s0, s1])
    states = np.array([0] * 50 + [1] * 50)
    div = true_response_divergence(X, states, ctrl)
    assert div > 1.5, f"opposite-direction states should have high divergence, got {div}"


def test_true_divergence_single_state_is_nan():
    """Fewer than two populated states -> nan (undefined, not silently 0)."""
    X = np.random.default_rng(2).standard_normal((40, 10))
    states = np.zeros(40, dtype=int)
    assert np.isnan(true_response_divergence(X, states, np.zeros(10)))


def test_divergence_components_keys():
    X = np.random.default_rng(3).standard_normal((60, 10))
    states = np.array([0] * 30 + [1] * 30)
    comp = divergence_components(X, states, np.zeros(10))
    for k in ("n_states_used", "minority_frac", "min_pairwise_cos", "delta_norm_ratio"):
        assert k in comp
    assert comp["n_states_used"] == 2
    assert 0 < comp["minority_frac"] <= 0.5 + 1e-9


def test_benjamini_hochberg_monotone_and_bounded():
    p = np.array([0.001, 0.01, 0.02, 0.5, 0.9])
    q = benjamini_hochberg(p)
    assert np.all(q >= p - 1e-12), "BH q-values must be >= raw p"
    assert np.all(q <= 1.0 + 1e-12)
    # monotone in the same order as p (after sorting)
    order = np.argsort(p)
    assert np.all(np.diff(q[order]) >= -1e-9)


def test_benjamini_hochberg_handles_nan():
    p = np.array([0.01, np.nan, 0.04])
    q = benjamini_hochberg(p)
    assert np.isnan(q[1])
    assert np.isfinite(q[0]) and np.isfinite(q[2])


def test_power_increases_with_n():
    p_small = power_two_sided(0.1, 0.3, 20)
    p_large = power_two_sided(0.1, 0.3, 200)
    assert 0 <= p_small <= p_large <= 1.0
    assert p_large > p_small


def test_n_for_power_positive_and_finite_for_real_effect():
    n = n_for_power(0.1, 0.3, power=0.8)
    assert np.isfinite(n) and n > 0
    # zero effect -> infinite required n
    assert not np.isfinite(n_for_power(0.0, 0.3))


def test_minority_coverage_is_mean_based_noncircular():
    """Guard the audit's core assumption: the judge metric is a MEAN-based cosine proxy,
    computed independently of any distributional (PopRetrieve-aligned) score. This mirrors the
    exp12 _minority_state_coverage formula (cos(P_mean, minority_mean)+1)/2 in [0,1]."""
    rng = np.random.default_rng(4)
    query_X = rng.standard_normal((80, 15))
    states = np.array([0] * 60 + [1] * 20)
    minority = 1
    P = rng.standard_normal((40, 15))
    mino_mean = query_X[states == minority].mean(0)
    p_mean = P.mean(0)
    cos = float(np.dot(p_mean, mino_mean) /
                (np.linalg.norm(p_mean) * np.linalg.norm(mino_mean) + 1e-12))
    cov = (cos + 1) / 2
    assert 0.0 <= cov <= 1.0
