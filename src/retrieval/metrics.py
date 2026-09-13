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

Two of the kernels come in a U-statistic and a V-statistic form (``energy_distance_u`` /
``energy_distance_v`` and ``mmd_rbf_u`` / ``mmd_rbf_v``). The V forms include self-pairs and are
biased upward by O(1/m); the U forms exclude self-pairs. Manuscript-facing scorers default to U.
The process-wide ``POPRETRIEVE_ESTIMATOR=v`` override is retained only as an explicitly labelled
legacy reproduction mode; new work should pass ``estimator='u'`` or use the default.

  score_mean_cosine        cosine of mean-delta signatures     (the "mean-out" incumbent)
  score_mean_l2            -||mean(P) - mean(Q)||
  score_energy             -energy_distance                    (K=1 distributional distance)
  score_mmd_rbf            -MMD^2 (median heuristic, forced)
  score_sliced_wasserstein -sliced-Wasserstein-1
  score_coverage           -aggregate_k base_metric over matched subpopulations
"""
from __future__ import annotations

import os
import sys
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


def energy_distance_v(X: torch.Tensor, Y: torch.Tensor) -> torch.Tensor:
    """V-statistic energy distance, 2 E|X-Y| - E|X-X'| - E|Y-Y'| with self-pairs INCLUDED.

    This is the scPerturbBench convention and the estimator behind every number this
    repository produced before 2026-09-02. It is retained unchanged so those numbers stay
    reproducible, and it is NOT the estimator to reach for in new work.

    The within-sample means run over all m^2 (respectively n^2) pairs, m of which are the zero
    self-distances, so each within term is deflated by a factor (m-1)/m and

        E_V = E_U + (1/m) E|X-X'| + (1/n) E|Y-Y'| + O(1/m^2),

    an upward bias of order 1/m. It cancels out of a ranking only when every candidate
    population has the same size. When they do not, the smaller candidates are pushed away from
    the query by an amount that has nothing to do with the biology, which is a ranking artefact
    rather than a rounding error: see docs/phase2/03_ORACLE_RETRIEVAL_RESULTS.md, where it
    consumes the whole of the measured population advantage. Use ``energy_distance_u`` unless
    you are reproducing an old number.
    """
    dxy = _pdist2(X, Y).mean()
    dxx = _pdist2(X, X).mean()
    dyy = _pdist2(Y, Y).mean()
    return 2 * dxy - dxx - dyy


def _offdiag_mean(D: torch.Tensor) -> torch.Tensor:
    """Mean of a square distance matrix over its off-diagonal entries only."""
    n = D.shape[0]
    if n < 2:
        return torch.zeros((), dtype=D.dtype, device=D.device)
    return (D.sum() - D.diagonal().sum()) / (n * (n - 1))


def energy_distance_u(X: torch.Tensor, Y: torch.Tensor) -> torch.Tensor:
    """U-statistic energy distance: self-pairs EXCLUDED from both within-sample terms.

        E_U = 2/(mn) sum_ij |x_i-y_j|
              - 1/(m(m-1)) sum_{i!=j} |x_i-x_j|
              - 1/(n(n-1)) sum_{i!=j} |y_i-y_j|

    Unbiased for the population energy distance at any m and n, so two candidate populations of
    different sizes are on the same scale and only their variances differ. This is the estimator
    to use whenever the populations being compared are not all the same size, which in this
    project is the common case rather than the exception.

    Degenerate inputs: with m < 2 or n < 2 the corresponding within term is undefined; it is
    taken as zero, which makes the value a cross-term-only quantity rather than an error. Callers
    that care should guard on the sample size themselves, as ``_base_dist`` does.
    """
    dxy = _pdist2(X, Y).mean()
    return 2 * dxy - _offdiag_mean(_pdist2(X, X)) - _offdiag_mean(_pdist2(Y, Y))


def _mmd_kernel(X: torch.Tensor, Y: torch.Tensor, sigmas, scales):
    """Return the multi-bandwidth RBF kernel closure shared by both MMD estimators.

    The bandwidth is the median heuristic taken on the POOLED sample, which is what makes the two
    estimators below differ only in which pairs they average over.
    """
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
    return k


def mmd_rbf_v(X: torch.Tensor, Y: torch.Tensor, sigmas=None,
              scales=(0.25, 1.0, 4.0)) -> torch.Tensor:
    """V-statistic multi-bandwidth RBF MMD^2, with self-pairs INCLUDED.

    This is the estimator behind every MMD number this repository produced before 2026-09-02 and
    it is kept unchanged for reproducibility. It is biased: k(x,x) = 1 for every RBF kernel, so
    the within terms carry m (respectively n) ones that do not belong to the population quantity,
    and

        MMD^2_V = MMD^2_U + (1 - E k(X,X'))/m + (1 - E k(Y,Y'))/n + O(1/m^2).

    The bias is positive and of order 1/m, the same shape as the energy distance's, so it has the
    same consequence for a ranking over candidate populations of unequal size. Use
    ``mmd_rbf_u`` in new work.

    By default the bandwidth is the median heuristic; fixed small sigmas underflow to zero in
    2000-dimensional gene space. Pass explicit ``sigmas`` to override.
    """
    k = _mmd_kernel(X, Y, sigmas, scales)
    return k(X, X).mean() + k(Y, Y).mean() - 2 * k(X, Y).mean()


def mmd_rbf_u(X: torch.Tensor, Y: torch.Tensor, sigmas=None,
              scales=(0.25, 1.0, 4.0)) -> torch.Tensor:
    """U-statistic multi-bandwidth RBF MMD^2, with self-pairs EXCLUDED.

        MMD^2_U = 1/(m(m-1)) sum_{i!=j} k(x_i,x_j)
                + 1/(n(n-1)) sum_{i!=j} k(y_i,y_j)
                - 2/(mn) sum_ij k(x_i,y_j)

    Unbiased at any m and n. Unlike the V-statistic it can be negative when the two samples come
    from the same distribution, which is correct rather than a defect: an unbiased estimator of a
    quantity that is zero must straddle zero.
    """
    k = _mmd_kernel(X, Y, sigmas, scales)
    return _offdiag_mean(k(X, X)) + _offdiag_mean(k(Y, Y)) - 2 * k(X, Y).mean()


# Unqualified low-level names are canonical U implementations. V is intentionally available only
# through the explicit *_v names or the explicit legacy estimator switch in the score wrappers.
energy_distance = energy_distance_u
mmd_rbf = mmd_rbf_u


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


# Which estimator the scorers use for the two U/V pairs.
#
# The manuscript pipeline is U by default. The environment override exists only for the
# explicitly labelled legacy estimator audit, which can re-run old V-statistic outputs without
# editing every historical call site.
_ESTIMATORS = ("u", "v")
_requested_estimator = os.environ.get("POPRETRIEVE_ESTIMATOR")
DEFAULT_ESTIMATOR = (_requested_estimator or "u").strip().lower()
if DEFAULT_ESTIMATOR not in _ESTIMATORS:
    raise ValueError(f"POPRETRIEVE_ESTIMATOR={DEFAULT_ESTIMATOR!r}; expected one of {_ESTIMATORS}")
if _requested_estimator is not None:
    print(f"[retrieval.metrics] POPRETRIEVE_ESTIMATOR={DEFAULT_ESTIMATOR!r} "
          f"(explicit legacy override; manuscript default is 'u')",
          file=sys.stderr, flush=True)


def _check_estimator(estimator: str) -> str:
    if estimator not in _ESTIMATORS:
        raise ValueError(f"unknown estimator {estimator!r}; expected one of {_ESTIMATORS}")
    return estimator


def _energy_dist(P, Q, max_cells: Optional[int] = 500, seed: int = 0,
                 min_cells: int = 2, estimator: str = DEFAULT_ESTIMATOR) -> float:
    """Positive energy distance with subsampling + a small-population guard."""
    _check_estimator(estimator)
    P = _subsample(P, max_cells, seed)
    Q = _subsample(Q, max_cells, seed + 1)
    if len(P) < min_cells or len(Q) < min_cells:
        return _PENALTY
    fn = energy_distance_u if estimator == "u" else energy_distance_v
    with torch.no_grad():
        return float(fn(_tensor(P), _tensor(Q)))


_BASE_METRICS = {"energy", "mmd", "sliced_w"}


def _base_dist(P, Q, base_metric: str, max_cells: Optional[int], seed: int,
               min_cells: int = 2, estimator: str = DEFAULT_ESTIMATOR) -> float:
    _check_estimator(estimator)
    P = _subsample(P, max_cells, seed)
    Q = _subsample(Q, max_cells, seed + 1)
    if len(P) < min_cells or len(Q) < min_cells:
        return _PENALTY
    with torch.no_grad():
        Pt, Qt = _tensor(P), _tensor(Q)
        if base_metric == "energy":
            return float((energy_distance_u if estimator == "u" else energy_distance_v)(Pt, Qt))
        if base_metric == "mmd":
            return float((mmd_rbf_u if estimator == "u" else mmd_rbf_v)(Pt, Qt))
        if base_metric == "sliced_w":
            # Sliced Wasserstein has no U/V pair: it is a quantile-matched estimator and does not
            # average over within-sample pairs at all, so ``estimator`` does not apply to it.
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


def score_mean_l2(P, Q, control_P: Optional[np.ndarray] = None,
                  control_Q: Optional[np.ndarray] = None, **_) -> float:
    """-Euclidean distance between mean-delta signatures.

    The magnitude-aware counterpart of ``score_mean_cosine``, and the control that separates two
    claims the project used to make as one. Cosine keeps only the DIRECTION of a mean response;
    this keeps direction and magnitude and nothing else. A population scorer that beats cosine has
    not yet shown that it used the population: it may only have used the magnitude, which is what
    Phase A measured (docs/phase2/03_ORACLE_RETRIEVAL_RESULTS.md: of a +0.0303 MRR gain over
    cosine, +0.0201 is recovered here).

    The control arguments mirror ``score_mean_cosine`` exactly, so the two scorers compare the
    same pair of vectors and differ only in how they compare them. Passing controls matters
    whenever the candidate and the query have DIFFERENT matched controls; where they share one, as
    in the controlled mixture task, the control cancels out of the difference and the arguments
    change nothing.
    """
    sig_P = _np(P).mean(0)
    sig_Q = _np(Q).mean(0)
    if control_P is not None:
        sig_P = sig_P - _np(control_P)
    if control_Q is not None:
        sig_Q = sig_Q - _np(control_Q)
    return -float(np.linalg.norm(sig_P - sig_Q))


def score_energy(P, Q, max_cells: int = 500, seed: int = 0,
                 estimator: str = DEFAULT_ESTIMATOR, **_) -> float:
    """-energy_distance (global K=1 distributional distance), U by default.

    ``estimator='v'`` is retained only for explicitly labelled legacy reproduction; ``u`` is the
    manuscript estimator and is appropriate when candidate populations differ in size.
    """
    return -_energy_dist(P, Q, max_cells=max_cells, seed=seed, estimator=estimator)


def score_mmd_rbf(P, Q, bandwidth: str = "median", max_cells: int = 500,
                  seed: int = 0, estimator: str = DEFAULT_ESTIMATOR, **_) -> float:
    """-MMD^2. ``bandwidth`` must be 'median' (median heuristic): fixed small bandwidths
    underflow to 0 in 2000-d gene space. See ``score_energy`` for ``estimator``."""
    if bandwidth != "median":
        raise ValueError("only bandwidth='median' is supported (see plan section 7.4)")
    return -_base_dist(P, Q, "mmd", max_cells=max_cells, seed=seed, estimator=estimator)


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
                   seed: int = 0, estimator: str = DEFAULT_ESTIMATOR, **_) -> float:
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
        dists.append(_base_dist(Pk, Qk, base_metric, max_cells=max_cells, seed=seed,
                                estimator=estimator))
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
