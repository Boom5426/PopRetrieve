"""The three degenerate-limit propositions as unit tests (exp06 / FINDINGS §10).

Proves the distribution-aware score is a strict generalization of mean-matching:
mean = zero-spread energy; global energy = coverage at K=1; one beta interpolates
mean <-> worst monotonically.
"""
import torch

from retrieval.metrics import energy_distance, coverage_aggregate

G = 200


def test_prop1_mean_is_zero_spread_limit():
    torch.manual_seed(0)
    P, T = torch.randn(120, G) + 0.7, torch.randn(90, G) - 0.4
    muP, muT = P.mean(0), T.mean(0)
    dmu = float((muP - muT).norm())
    # point masses at the means -> energy == 2||dmu|| (relative tol: float32 cdist
    # mm-mode leaves a tiny spurious self-distance residual at high dim)
    rel = 1e-3
    e_point = float(energy_distance(muP.expand(60, G).clone(), muT.expand(50, G).clone()))
    assert abs(e_point - 2 * dmu) < rel * 2 * dmu
    # shrinking within-population spread converges to the mean-only value
    curve = [float(energy_distance(muP + t * (P - muP), muT + t * (T - muT)))
             for t in (1.0, 0.1, 0.0)]
    assert abs(curve[-1] - 2 * dmu) < rel * 2 * dmu
    assert abs(curve[0] - 2 * dmu) > 1e-2       # full-population energy is lossy vs mean


def test_prop2_global_is_coverage_at_K1():
    torch.manual_seed(1)
    P, T = torch.randn(80, G), torch.randn(70, G) + 0.5
    g = energy_distance(P, T)
    for beta in (0.0, 0.1, 1.0, 10.0, 1e3):
        assert abs(float(coverage_aggregate(g.reshape(1), beta)) - float(g)) < 1e-6


def test_prop3_beta_interpolates_mean_to_worst():
    e = torch.tensor([0.20, 0.55, 1.30, 0.80])
    assert abs(float(coverage_aggregate(e, 1e-9)) - float(e.mean())) < 1e-4
    assert abs(float(coverage_aggregate(e, 1e9)) - float(e.max())) < 1e-4
    vals = [float(coverage_aggregate(e, b)) for b in (1e-9, 0.5, 1, 2, 5, 20, 1e9)]
    assert all(vals[i] <= vals[i + 1] + 1e-6 for i in range(len(vals) - 1))
