"""Soft subpopulation assignment head + coverage aggregator.

The head assigns each cell a soft membership over K latent subpopulations.  The
coverage aggregator collapses per-subpopulation distances into a single score
with a temperature ``beta`` that interpolates between the *mean* (beta -> 0, an
average-coverage objective) and the *max* (beta -> inf, a worst-subpopulation /
Hausdorff-like coverage objective).
"""
from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


class SubpopHead(nn.Module):
    def __init__(self, in_dim: int, K: int = 4):
        super().__init__()
        self.K = K
        self.assign = nn.Linear(in_dim, K)

    def forward(self, cell_emb: torch.Tensor) -> torch.Tensor:
        """[.,in_dim] -> soft assignment [.,K] (softmax over subpopulations)."""
        return F.softmax(self.assign(cell_emb), dim=-1)


def coverage_aggregate(dists: torch.Tensor, weights: torch.Tensor | None = None,
                       beta: float = 8.0) -> torch.Tensor:
    """dists [...,K] per-subpop distances (lower=better).  Returns an aggregated
    scalar-per-leading-dim.

    The aggregator is the (weighted) softmax-temperature log-sum-exp:

        agg = (1/beta) * logsumexp_k( beta * dists_k + log w_k )

    with the identity (REQUIRED, and the reason we use this form):

        * beta -> 0   =>  weighted MEAN of dists   (average coverage)
        * beta -> inf =>  MAX of dists             (worst-subpop coverage)

    Proof sketch:
        - beta -> inf: (1/beta) logsumexp(beta d) -> max_k d_k (standard smooth-max).
        - beta -> 0:   logsumexp(beta d_k + log w_k) = log( sum_k w_k e^{beta d_k} ).
          Expand e^{beta d_k} ~= 1 + beta d_k; with sum_k w_k = 1 this is
          log(1 + beta * sum_k w_k d_k) ~= beta * sum_k w_k d_k, so dividing by
          beta yields the weighted mean sum_k w_k d_k.

    ``weights`` (optional) [...,K] are normalized to sum to 1 over the last dim so
    the beta->0 limit is a proper weighted mean.  ``beta`` is clamped away from 0
    to keep the 1/beta finite; for tiny beta the value already equals the mean to
    first order.
    """
    beta = max(float(beta), 1e-6)
    if weights is None:
        log_w = torch.zeros_like(dists)
    else:
        w = weights / weights.sum(dim=-1, keepdim=True).clamp_min(1e-12)
        log_w = torch.log(w.clamp_min(1e-12))
    return torch.logsumexp(beta * dists + log_w, dim=-1) / beta
