"""Estimator audit: does the U or the V form of energy / MMD depend on sample size?

Phase-II found that the V-statistic energy distance erases the whole measured population
advantage once candidate populations differ in size (docs/phase2/03_ORACLE_RETRIEVAL_RESULTS.md).
These tests pin the reason down so the choice of estimator is a checked property rather than a
claim in a docstring. Four scenarios, all from the Phase-1 audit specification:

    null              P and Q from the same distribution, at several (m, n)
    mean shift        Q = P + delta, ranking stability
    variance shift    same mean, different covariance
    unequal sizes     m = 50 against n = 200, the case that actually occurs in the benchmark

Each test states the property it is protecting, so a failure says what broke rather than only
that a number moved.
"""
import numpy as np
import torch

from retrieval.metrics import (
    energy_distance, energy_distance_u, mmd_rbf, mmd_rbf_u, sliced_wasserstein,
)

G = 32
SIZES = (25, 50, 100, 200)


def _draw(n, g=G, seed=0, mu=0.0, sd=1.0):
    gen = torch.Generator().manual_seed(seed)
    return torch.randn(n, g, generator=gen) * sd + mu


# ---------------------------------------------------------------------------
# 1. Null: P and Q are the same distribution.
# ---------------------------------------------------------------------------

def test_null_u_is_centred_on_zero_and_v_is_not():
    """Under P = Q the population value is 0. The U form must straddle it; the V form must not.

    The V form's bias is E|X-X'|/m + E|Y-Y'|/n, which at these sizes is a large multiple of the
    Monte-Carlo scatter, so 'V is positive at every size' is a deterministic statement, not a
    lucky draw.
    """
    for n in SIZES:
        vals_u, vals_v = [], []
        for rep in range(12):
            P, Q = _draw(n, seed=100 * rep + n), _draw(n, seed=100 * rep + n + 7)
            vals_u.append(float(energy_distance_u(P, Q)))
            vals_v.append(float(energy_distance(P, Q)))
        mu_u, mu_v = float(np.mean(vals_u)), float(np.mean(vals_v))
        se_u = float(np.std(vals_u, ddof=1)) / np.sqrt(len(vals_u))
        assert abs(mu_u) < 4 * se_u, f"U not centred on zero at n={n}: {mu_u:.4g} +- {se_u:.4g}"
        assert mu_v > 0, f"V should be biased upward at n={n}, got {mu_v:.4g}"


def test_null_v_bias_shrinks_like_one_over_n():
    """The V form's null value must fall roughly as 1/n; the U form's must not trend at all."""
    means_v, means_u = [], []
    for n in SIZES:
        v = [float(energy_distance(_draw(n, seed=31 * r + n), _draw(n, seed=31 * r + n + 3)))
             for r in range(12)]
        u = [float(energy_distance_u(_draw(n, seed=31 * r + n), _draw(n, seed=31 * r + n + 3)))
             for r in range(12)]
        means_v.append(float(np.mean(v)))
        means_u.append(float(np.mean(u)))
    ratio = means_v[0] / means_v[-1]              # n = 25 against n = 200, a factor of 8 in n
    assert 4.0 < ratio < 16.0, f"V null does not scale like 1/n: ratio {ratio:.2f}"
    assert abs(means_u[0]) < 0.25 * means_v[0], "U null should be far below the V null"


def test_mmd_shows_the_same_pattern():
    """The MMD in this repository is the V form and carries the same 1/n bias."""
    for n in (25, 200):
        v = [float(mmd_rbf(_draw(n, seed=17 * r + n), _draw(n, seed=17 * r + n + 5)))
             for r in range(10)]
        u = [float(mmd_rbf_u(_draw(n, seed=17 * r + n), _draw(n, seed=17 * r + n + 5)))
             for r in range(10)]
        assert np.mean(v) > 0, f"V MMD should be biased upward at n={n}"
        assert abs(np.mean(u)) < 0.5 * np.mean(v), f"U MMD should be much closer to zero at n={n}"


# ---------------------------------------------------------------------------
# 2. Mean shift: both estimators must see it, and see it identically up to the bias.
# ---------------------------------------------------------------------------

def test_mean_shift_is_ranked_identically_at_equal_sizes():
    """At equal sample sizes the V bias is a constant offset, so both forms give the same order."""
    Q = _draw(100, seed=1)
    deltas = [0.0, 0.25, 0.5, 1.0, 2.0]
    du, dv = [], []
    for i, d in enumerate(deltas):
        P = _draw(100, seed=200 + i) + d
        du.append(float(energy_distance_u(P, Q)))
        dv.append(float(energy_distance(P, Q)))
    assert du == sorted(du), f"U not monotone in the mean shift: {du}"
    assert dv == sorted(dv), f"V not monotone in the mean shift: {dv}"
    offs = np.array(dv) - np.array(du)
    assert offs.std() < 0.05 * offs.mean(), "the V-U gap should be near-constant at equal sizes"


# ---------------------------------------------------------------------------
# 3. Variance shift: same mean, different covariance.
# ---------------------------------------------------------------------------

def test_variance_shift_is_detected_by_both():
    """A pure covariance difference must register: it is the part a mean scorer cannot see."""
    Q = _draw(150, seed=11)
    same = _draw(150, seed=12)
    wider = _draw(150, seed=13, sd=1.6)
    assert float(energy_distance_u(wider, Q)) > float(energy_distance_u(same, Q))
    assert float(mmd_rbf_u(wider, Q)) > float(mmd_rbf_u(same, Q))


# ---------------------------------------------------------------------------
# 4. Unequal sample sizes: the case the benchmark actually contains.
# ---------------------------------------------------------------------------

def test_unequal_sizes_do_not_bias_the_u_form():
    """A 50-cell candidate and a 200-cell candidate drawn from the SAME distribution as the query
    must be scored equally in expectation. Under V the smaller one is pushed away, which is the
    ranking artefact this whole audit exists to remove."""
    Q = _draw(200, seed=21)
    small_u, big_u, small_v, big_v = [], [], [], []
    for rep in range(16):
        small_u.append(float(energy_distance_u(_draw(50, seed=300 + rep), Q)))
        big_u.append(float(energy_distance_u(_draw(200, seed=400 + rep), Q)))
        small_v.append(float(energy_distance(_draw(50, seed=300 + rep), Q)))
        big_v.append(float(energy_distance(_draw(200, seed=400 + rep), Q)))
    gap_u = float(np.mean(small_u) - np.mean(big_u))
    gap_v = float(np.mean(small_v) - np.mean(big_v))
    se = float(np.sqrt(np.var(small_u, ddof=1) / 16 + np.var(big_u, ddof=1) / 16))
    assert abs(gap_u) < 4 * se, f"U penalises the smaller sample: gap {gap_u:.4g} +- {se:.4g}"
    assert gap_v > 6 * se, f"V should penalise the smaller sample, got {gap_v:.4g}"


def test_unequal_sizes_can_reorder_two_candidates_under_v():
    """The bias is large enough to change a decision, not only a value.

    A 50-cell candidate drawn from the query's own distribution is compared against a 200-cell
    candidate drawn from a slightly shifted one. The shift is chosen so the U form prefers the
    correct (unshifted) candidate; the V form must be shown to flip that preference at least
    sometimes, which is what makes the estimator a ranking issue.
    """
    Q = _draw(200, seed=31)
    flips_v = flips_u = 0
    for rep in range(20):
        right = _draw(50, seed=500 + rep)                 # same distribution, few cells
        wrong = _draw(200, seed=600 + rep) + 0.06         # shifted, many cells
        if float(energy_distance_u(right, Q)) > float(energy_distance_u(wrong, Q)):
            flips_u += 1
        if float(energy_distance(right, Q)) > float(energy_distance(wrong, Q)):
            flips_v += 1
    assert flips_v > flips_u, (f"V should misrank the small correct candidate more often than U: "
                               f"V {flips_v}/20 vs U {flips_u}/20")


def test_sliced_wasserstein_has_no_u_v_pair_but_is_size_sensitive():
    """Recorded rather than fixed: sliced Wasserstein compares quantile functions and averages no
    within-sample pairs, so no U/V distinction applies to it. Its null value still falls with
    sample size, which is why it is reported as a secondary scorer and never as the primary one."""
    small = [float(sliced_wasserstein(_draw(25, seed=700 + r), _draw(25, seed=800 + r)))
             for r in range(10)]
    big = [float(sliced_wasserstein(_draw(200, seed=700 + r), _draw(200, seed=800 + r)))
           for r in range(10)]
    assert np.mean(small) > np.mean(big) > 0
