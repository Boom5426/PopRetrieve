"""Distributional distances between two cell populations (eval + optional loss)."""
from __future__ import annotations

import torch


def _pdist2(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """Squared euclidean distances, [na, nb]."""
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
    large). Pass explicit `sigmas` to override."""
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
    coverage distance. A single temperature beta interpolates the two endpoints we
    report:

        beta -> 0    : arithmetic mean over subpops   (coverage_mean)
        beta -> +inf : maximum / worst subpop         (coverage_worst)

        D_beta = (1/beta) * ( logsumexp(beta * dists) - log K )

    The ranking SCORE is -D_beta (closer = higher). Degenerate limits (verified
    numerically in scripts/verify_degenerate_limits.py):
      * K == 1  -> D_beta == dists[0] for ANY beta  => coverage reduces EXACTLY to
        the global (single-population) distance. Coverage is a strict generalization.
      * beta->0 -> mean ; beta->inf -> max          => our coverage_mean / _worst are
        the two ends of one continuum, not separate heuristics.
    """
    dists = dists.reshape(-1)
    K = dists.shape[0]
    if K == 1:
        return dists[0]
    if beta <= 0:
        return dists.mean()
    s = dists.mean()
    c = dists - s
    # Small-beta cumulant (Taylor) expansion D_beta = mean + (beta/2)*var + O(beta^2)
    # avoids the catastrophic (logsumexp - logK)/beta cancellation as beta->0.
    if float(beta) * float(c.abs().max()) < 1e-3:
        return s + 0.5 * beta * (c * c).mean()
    logK = torch.log(torch.tensor(float(K), dtype=dists.dtype, device=dists.device))
    return s + (torch.logsumexp(beta * c, dim=0) - logK) / beta


def pcc_delta(pred_delta: torch.Tensor, true_delta: torch.Tensor) -> torch.Tensor:
    """Pearson correlation between predicted and true mean-expression deltas."""
    a = pred_delta - pred_delta.mean()
    b = true_delta - true_delta.mean()
    return (a * b).sum() / (a.norm() * b.norm()).clamp_min(1e-8)
