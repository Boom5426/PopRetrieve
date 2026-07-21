"""Unit tests for the vendored distance kernels + unified score interface."""
import numpy as np
import torch

from retrieval.metrics import (
    energy_distance, coverage_aggregate, mmd_rbf,
    score_energy, score_mean_cosine, score_mean_l2, score_coverage,
)


def test_energy_zero_spread_limit():
    torch.manual_seed(0)
    G = 50
    muP, muT = torch.randn(G), torch.randn(G)
    Pm, Tm = muP.expand(30, G).clone(), muT.expand(20, G).clone()
    e = float(energy_distance(Pm, Tm))
    dmu = float((muP - muT).norm())
    assert abs(e - 2 * dmu) < 1e-3 * 2 * dmu     # relative tol (float32 cdist mm-mode)


def test_energy_of_identical_is_zero():
    torch.manual_seed(0)
    P = torch.randn(40, 20)
    assert abs(float(energy_distance(P, P))) < 1e-5


def test_coverage_K1_equals_global():
    torch.manual_seed(1)
    P, T = torch.randn(40, 20), torch.randn(35, 20) + 0.3
    g = energy_distance(P, T)
    for beta in (0.0, 0.5, 1.0, 10.0, 1e3):
        assert abs(float(coverage_aggregate(g.reshape(1), beta)) - float(g)) < 1e-6


def test_coverage_endpoints_mean_and_worst():
    e = torch.tensor([0.2, 0.5, 1.3, 0.8])
    assert abs(float(coverage_aggregate(e, 1e-9)) - float(e.mean())) < 1e-4
    assert abs(float(coverage_aggregate(e, 1e9)) - float(e.max())) < 1e-4


def test_coverage_monotone_in_beta():
    e = torch.tensor([0.2, 0.5, 1.3, 0.8])
    vals = [float(coverage_aggregate(e, b)) for b in (1e-9, 0.5, 1, 2, 5, 20, 1e9)]
    assert all(vals[i] <= vals[i + 1] + 1e-6 for i in range(len(vals) - 1))


def test_mmd_median_heuristic_nonzero_in_highdim():
    # fixed small bandwidths underflow to 0 in 2000-d; median heuristic must not
    torch.manual_seed(2)
    P, T = torch.randn(60, 2000), torch.randn(60, 2000) + 0.5
    assert float(mmd_rbf(P, T)) > 1e-6


def test_score_conventions_identical_populations():
    rng = np.random.default_rng(0)
    P = rng.normal(size=(50, 20)).astype("float32")
    Q = P.copy()
    assert score_mean_cosine(P, Q) > 0.999          # identical means -> cosine 1
    assert score_mean_l2(P, Q) > -1e-4              # zero distance -> ~0
    assert score_energy(P, Q) > -1e-4               # zero energy -> score ~0


def test_score_coverage_penalizes_missing_subpop():
    rng = np.random.default_rng(0)
    Q = rng.normal(size=(40, 10)).astype("float32")
    labQ = np.array([0] * 20 + [1] * 20)
    P = rng.normal(size=(40, 10)).astype("float32")
    labP = np.zeros(40, int)                          # candidate has NO subpop-1 cells
    s_full = score_coverage(Q, Q, labQ, labQ, aggregator="mean")
    s_missing = score_coverage(P, Q, labP, labQ, aggregator="mean")
    assert s_missing < s_full                         # missing subpop -> heavy penalty
