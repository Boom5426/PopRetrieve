"""OT conditional flow-matching primitives (no POT; exact assignment via scipy).

We use *minibatch optimal transport* conditional flow matching (OT-CFM): given a
source population ``x0`` and a target population ``x1`` of the same size, we solve
the exact assignment problem on the squared-euclidean cost with the Hungarian
algorithm (``scipy.optimize.linear_sum_assignment``), then regress the field onto
the straight-line displacement between paired points.

The assignment runs on CPU numpy (scipy requirement); everything else stays on
the tensors' device.
"""
from __future__ import annotations

import numpy as np
import torch
import torch.nn.functional as F
from scipy.optimize import linear_sum_assignment


def minibatch_ot_pairing(x0: torch.Tensor, x1: torch.Tensor) -> torch.Tensor:
    """x0,x1 [N,G] tensors -> permutation index perm [N] (long) so x0[i] pairs
    x1[perm[i]], via exact assignment on the [N,N] squared-euclidean cost
    (linear_sum_assignment on CPU numpy)."""
    # squared-euclidean cost [N,N]; compute on-device then move only the cost to cpu
    cost = torch.cdist(x0, x1, p=2) ** 2                       # [N, N]
    cost_np = cost.detach().to("cpu", dtype=torch.float64).numpy()
    row_ind, col_ind = linear_sum_assignment(cost_np)          # row_ind == arange(N)
    perm = np.empty(x0.shape[0], dtype=np.int64)
    perm[row_ind] = col_ind
    return torch.as_tensor(perm, dtype=torch.long, device=x0.device)


def flow_matching_loss(field, x0: torch.Tensor, x1: torch.Tensor, cond: torch.Tensor,
                       n_time_samples: int = 1, generator: torch.Generator | None = None) -> torch.Tensor:
    """One population pair.

    x0,x1 [N,G]; cond [N,cond_dim] (per-cell, drug cond broadcast).
    Pair via minibatch_ot_pairing, sample t~U(0,1) [N], x_t=(1-t)x0+t*x1[perm],
    target u=x1[perm]-x0, return MSE(field(x_t,t,cond), u).

    ``n_time_samples`` resamples t (and re-evaluates the field) that many times and
    averages the MSE, giving a lower-variance estimate of the time-marginal loss.
    """
    perm = minibatch_ot_pairing(x0, x1)                        # [N]
    x1p = x1[perm]                                             # [N, G]
    u = x1p - x0                                               # target velocity [N, G]
    N = x0.shape[0]
    total = x0.new_zeros(())
    for _ in range(max(1, n_time_samples)):
        t = torch.rand(N, device=x0.device, dtype=x0.dtype, generator=generator)  # [N]
        x_t = (1.0 - t)[:, None] * x0 + t[:, None] * x1p       # [N, G]
        v = field(x_t, t, cond)                                # [N, G]
        total = total + F.mse_loss(v, u)
    return total / max(1, n_time_samples)


@torch.no_grad()
def euler_integrate(field, x0: torch.Tensor, cond: torch.Tensor, n_steps: int = 8) -> torch.Tensor:
    """x0 [M,G], cond [M,cond_dim] -> x1_hat [M,G] by forward Euler of
    dx/dt = field(x, t, cond) over t in [0,1]."""
    x = x0
    dt = 1.0 / max(1, n_steps)
    M = x0.shape[0]
    for i in range(n_steps):
        t = torch.full((M,), i * dt, device=x0.device, dtype=x0.dtype)
        x = x + dt * field(x, t, cond)
    return x
