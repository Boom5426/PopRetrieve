"""Distribution-to-distribution retrieval metrics (self-contained).

This module is the numerical heart of the package. The four population-level
distance kernels — ``energy_distance``, ``mmd_rbf`` (median-heuristic bandwidth),
``sliced_wasserstein``, ``coverage_aggregate`` — are vendored verbatim from the
validated implementation in ``src/gidflow/losses/distribution.py`` so the package
carries no dependency on ``gidflow`` yet reproduces its numbers exactly.

On top of the kernels we expose the unified ranking interface required by the
project plan §7::

    score(P, Q, **kwargs) -> float          # higher = better match

Convention: a *similarity* is returned as-is; a *distance* is returned negated,
so every scorer ranks candidates in descending ``score``.

  score_mean_cosine        cosine of mean-delta signatures     (the "mean-out" incumbent)
  score_mean_l2            -||mean(P) - mean(Q)||
  score_energy             -energy_distance                    (K=1 distributional distance)
  score_mmd_rbf            -MMD^2 (median heuristic, forced)
  score_sliced_wasserstein -sliced-Wasserstein-1
  score_coverage           -aggregate_k base_metric over matched subpopulations
"""
from __future__ import annotations

from typing import Optional, Sequence

import numpy as np
import torch

_PENALTY = 1e6  # distance assigned when a (sub)population is too small to score

# ---------------------------------------------------------------------------
# Vendored distance kernels (verbatim from gidflow.losses.distribution)
# ---------------------------------------------------------------------------


def _pdist2(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """Euclidean distances, [na, nb]."""
    return torch.cdist(a, b, p=2)


def energy_distance(X: torch.Tensor, Y: torch.Tensor) -> torch.Tensor:
    """E-distance = 2 E|X-Y| - E|X-X'| - E|Y-Y'|  (scPerturbBench metric, lower=closer)."""
    dxy = _pdist2(X, Y).mean()
    dxx = _pdist2(X, X).mean()
    dyy = _pdist2(Y, Y).mean()
    return 2 * dxy - dxx - dyy


def mmd_rbf(X: torch.Tensor, Y: torch.Tensor, sigmas=None,
            scales=(0.25, 1.0, 4.0)) -> torch.Tensor:
    """Multi-bandwidth RBF MMD^2. By default uses the MEDIAN-HEURISTIC bandwidth
    (fixed small sigmas vanish in high-dim gene space, where pairwise distances are
    large). Pass explicit ``sigmas`` to override."""
    if sigmas is None:
        with torch.no_grad():
            Z = torch.cat([X, Y], 0)
            d2 = _pdist2(Z, Z) ** 2
            med = d2[d2 > 0].median().clamp_min(1e-12)      # ~ 2*sigma^2 scale
        denoms = [med * s for s in scales]
    else:
        denoms = [2 * s * s for s in sigmas]

    def k(a, b):
        d2 = _pdist2(a, b) ** 2
        out = 0.0
        for dn in denoms:
            out = out + torch.exp(-d2 / dn)
        return out / len(denoms)
    return k(X, X).mean() + k(Y, Y).mean() - 2 * k(X, Y).mean()


def sliced_wasserstein(X: torch.Tensor, Y: torch.Tensor, n_proj: int = 64,
                       n_q: int = 100, seed: int = 0) -> torch.Tensor:
    """Sliced-Wasserstein-1 distance: mean over random 1D projections of the
    quantile-matched W1 (handles unequal sample sizes via quantiles). lower=closer."""
    d = X.shape[1]
    g = torch.Generator(device=X.device).manual_seed(seed)
    theta = torch.randn(d, n_proj, generator=g, device=X.device, dtype=X.dtype)
    theta = theta / theta.norm(dim=0, keepdim=True).clamp_min(1e-12)
    qs = torch.linspace(0, 1, n_q, device=X.device, dtype=X.dtype)
    xq = torch.quantile((X @ theta), qs, dim=0)       # [n_q, n_proj]
    yq = torch.quantile((Y @ theta), qs, dim=0)
    return (xq - yq).abs().mean()


def coverage_aggregate(dists: torch.Tensor, beta: float) -> torch.Tensor:
    """Soft-max (log-sum-exp) aggregation of K per-subpopulation distances into one
    coverage distance. A single temperature ``beta`` interpolates the two endpoints:

        beta -> 0    : arithmetic mean over subpops   (coverage_mean)
        beta -> +inf : maximum / worst subpop         (coverage_worst)

        D_beta = (1/beta) * ( logsumexp(beta * dists) - log K )

    Degenerate limits (proven in exp06): K == 1 -> D_beta == dists[0] for ANY beta
    (coverage strictly generalizes the global distance); beta->0 -> mean; beta->inf
    -> max. The ranking SCORE is ``-D_beta`` (closer = higher)."""
    dists = dists.reshape(-1)
    K = dists.shape[0]
    if K == 1:
        return dists[0]
    if beta <= 0:
        return dists.mean()
    s = dists.mean()
    c = dists - s
    # Small-beta cumulant (Taylor) expansion avoids the (logsumexp-logK)/beta
    # cancellation as beta->0: D_beta = mean + (beta/2)*var + O(beta^2).
    if float(beta) * float(c.abs().max()) < 1e-3:
        return s + 0.5 * beta * (c * c).mean()
    logK = torch.log(torch.tensor(float(K), dtype=dists.dtype, device=dists.device))
    return s + (torch.logsumexp(beta * c, dim=0) - logK) / beta


def pcc_delta(pred_delta: torch.Tensor, true_delta: torch.Tensor) -> torch.Tensor:
    """Pearson correlation between predicted and true mean-expression deltas."""
    a = pred_delta - pred_delta.mean()
    b = true_delta - true_delta.mean()
    return (a * b).sum() / (a.norm() * b.norm()).clamp_min(1e-8)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

_DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def _np(x) -> np.ndarray:
    if isinstance(x, torch.Tensor):
        return x.detach().cpu().numpy()
    return np.asarray(x)


def _tensor(x, device=None) -> torch.Tensor:
    device = device or _DEVICE
    if isinstance(x, torch.Tensor):
        return x.to(device=device, dtype=torch.float32)
    return torch.as_tensor(np.asarray(x, dtype=np.float32), device=device)


def _subsample(X: np.ndarray, max_cells: Optional[int], seed: int) -> np.ndarray:
    X = _np(X)
    if max_cells is None or len(X) <= max_cells:
        return X
    idx = np.random.default_rng(seed).choice(len(X), max_cells, replace=False)
    return X[idx]


def _cos(a: np.ndarray, b: np.ndarray) -> float:
    na, nb = np.linalg.norm(a), np.linalg.norm(b)
    return 0.0 if na < 1e-12 or nb < 1e-12 else float(a @ b / (na * nb))


def _energy_dist(P, Q, max_cells: Optional[int] = 500, seed: int = 0,
                 min_cells: int = 2) -> float:
    """Positive energy distance with subsampling + a small-population guard."""
    P = _subsample(P, max_cells, seed)
    Q = _subsample(Q, max_cells, seed + 1)
    if len(P) < min_cells or len(Q) < min_cells:
        return _PENALTY
    with torch.no_grad():
        return float(energy_distance(_tensor(P), _tensor(Q)))


_BASE_METRICS = {"energy", "mmd", "sliced_w"}


def _base_dist(P, Q, base_metric: str, max_cells: Optional[int], seed: int,
               min_cells: int = 2) -> float:
    P = _subsample(P, max_cells, seed)
    Q = _subsample(Q, max_cells, seed + 1)
    if len(P) < min_cells or len(Q) < min_cells:
        return _PENALTY
    with torch.no_grad():
        Pt, Qt = _tensor(P), _tensor(Q)
        if base_metric == "energy":
            return float(energy_distance(Pt, Qt))
        if base_metric == "mmd":
            return float(mmd_rbf(Pt, Qt))
        if base_metric == "sliced_w":
            return float(sliced_wasserstein(Pt, Qt))
    raise ValueError(f"unknown base_metric {base_metric!r}; expected one of {_BASE_METRICS}")


def _beta_for(aggregator: str, beta: Optional[float]) -> float:
    if aggregator == "mean":
        return 0.0
    if aggregator == "worst":
        return 1e9
    if aggregator == "softmax_beta":
        if beta is None:
            raise ValueError("aggregator='softmax_beta' requires beta=<float>")
        return float(beta)
    raise ValueError(f"unknown aggregator {aggregator!r}")


# ---------------------------------------------------------------------------
# Unified score interface (plan §7): score(P, Q, **kwargs) -> float
# P = candidate population, Q = query/target population.
# ---------------------------------------------------------------------------


def score_mean_cosine(P, Q, control_P: Optional[np.ndarray] = None,
                      control_Q: Optional[np.ndarray] = None, **_) -> float:
    """Cosine of mean-delta signatures. With matched controls this measures drug
    RESPONSE direction (baseline identity removed); the incumbent 'mean-out' scorer."""
    sig_P = _np(P).mean(0)
    sig_Q = _np(Q).mean(0)
    if control_P is not None:
        sig_P = sig_P - _np(control_P)
    if control_Q is not None:
        sig_Q = sig_Q - _np(control_Q)
    return _cos(sig_Q, sig_P)


def score_mean_l2(P, Q, **_) -> float:
    """-Euclidean distance between population means."""
    return -float(np.linalg.norm(_np(P).mean(0) - _np(Q).mean(0)))


def score_energy(P, Q, max_cells: int = 500, seed: int = 0, **_) -> float:
    """-energy_distance (global K=1 distributional distance)."""
    return -_energy_dist(P, Q, max_cells=max_cells, seed=seed)


def score_mmd_rbf(P, Q, bandwidth: str = "median", max_cells: int = 500,
                  seed: int = 0, **_) -> float:
    """-MMD^2. ``bandwidth`` must be 'median' (median heuristic) — fixed small
    bandwidths underflow to 0 in 2000-d gene space."""
    if bandwidth != "median":
        raise ValueError("only bandwidth='median' is supported (see plan §7.4)")
    return -_base_dist(P, Q, "mmd", max_cells=max_cells, seed=seed)


def score_sliced_wasserstein(P, Q, n_projections: int = 128, max_cells: int = 500,
                             seed: int = 0, **_) -> float:
    """-sliced-Wasserstein-1 distance over ``n_projections`` random directions."""
    Ps = _subsample(P, max_cells, seed)
    Qs = _subsample(Q, max_cells, seed + 1)
    if len(Ps) < 2 or len(Qs) < 2:
        return -_PENALTY
    with torch.no_grad():
        return -float(sliced_wasserstein(_tensor(Ps), _tensor(Qs), n_proj=n_projections))


def score_coverage(P, Q, labels_P: np.ndarray, labels_Q: np.ndarray,
                   base_metric: str = "energy", aggregator: str = "mean",
                   beta: Optional[float] = None, max_cells: int = 500,
                   seed: int = 0, **_) -> float:
    """-aggregate_k base_metric(P_k, Q_k) over subpopulations shared by P and Q.

    Subpopulations are defined by the target labels ``labels_Q``; a candidate that
    lacks a subpopulation is penalized (that subpop's distance = _PENALTY). The
    aggregator is routed through ``coverage_aggregate`` so 'mean'/'worst' are the
    two endpoints of one temperature continuum and K=1 reduces to the global score.
    """
    labels_P = _np(labels_P).astype(int)
    labels_Q = _np(labels_Q).astype(int)
    P, Q = _np(P), _np(Q)
    dists = []
    for k in sorted(np.unique(labels_Q).tolist()):
        Qk = Q[labels_Q == k]
        Pk = P[labels_P == k]
        dists.append(_base_dist(Pk, Qk, base_metric, max_cells=max_cells, seed=seed))
    agg = coverage_aggregate(torch.tensor(dists, dtype=torch.float32),
                             _beta_for(aggregator, beta))
    return -float(agg)


# Registry for config-driven dispatch.
SCORERS = {
    "mean_cosine": score_mean_cosine,
    "mean_l2": score_mean_l2,
    "energy": score_energy,
    "mmd_rbf": score_mmd_rbf,
    "sliced_wasserstein": score_sliced_wasserstein,
    "coverage": score_coverage,
}


def available_scorers() -> Sequence[str]:
    return tuple(SCORERS)
