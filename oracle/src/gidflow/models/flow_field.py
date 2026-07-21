"""Conditional velocity field in gene space for flow matching.

Predicts a velocity v(x, t | cond) that transports source cells to target cells.
The field is FiLM-conditioned on ``cond`` at every residual block, which lets the
conditioning modulate *per-gene* scale/shift rather than being averaged into a
single additive bias -- this guards against the mean-collapse failure mode where
the field degenerates into a population-level mean shift and ignores per-cell
structure.

Architecture:
    sinusoidal time embedding (time_dim)
    input projection of x [., G] -> [., hidden]
    n_blocks residual MLP blocks, each FiLM-modulated by MLP(cond) -> (scale, shift)
    final linear -> [., G]

The final layer is initialized near-zero so the initial field is ~0 (an
identity-preserving transport at t=0), which stabilizes early training.
"""
from __future__ import annotations

import math

import torch
import torch.nn as nn


def sinusoidal_time_embedding(t: torch.Tensor, dim: int) -> torch.Tensor:
    """t [M] in [0,1] -> [M, dim] sinusoidal embedding."""
    half = dim // 2
    freqs = torch.exp(
        -math.log(10000.0) * torch.arange(half, device=t.device, dtype=t.dtype) / max(half - 1, 1)
    )                                                     # [half]
    args = t[:, None] * freqs[None, :]                    # [M, half]
    emb = torch.cat([torch.sin(args), torch.cos(args)], dim=-1)  # [M, 2*half]
    if emb.shape[-1] < dim:                               # odd dim -> pad
        emb = torch.cat([emb, torch.zeros(emb.shape[0], dim - emb.shape[-1], device=t.device, dtype=t.dtype)], dim=-1)
    return emb


class _FiLMBlock(nn.Module):
    """Residual MLP block modulated by (scale, shift) derived from cond."""

    def __init__(self, hidden: int, cond_dim: int, dropout: float = 0.0):
        super().__init__()
        self.norm = nn.LayerNorm(hidden)
        self.fc1 = nn.Linear(hidden, hidden)
        self.fc2 = nn.Linear(hidden, hidden)
        self.act = nn.GELU()
        self.drop = nn.Dropout(dropout)
        self.film = nn.Linear(cond_dim, 2 * hidden)

    def forward(self, h: torch.Tensor, cond: torch.Tensor) -> torch.Tensor:
        scale, shift = self.film(cond).chunk(2, dim=-1)   # each [., hidden]
        y = self.norm(h)
        y = y * (1.0 + scale) + shift                     # FiLM
        y = self.fc2(self.drop(self.act(self.fc1(y))))
        return h + y


class FlowField(nn.Module):
    def __init__(self, n_genes: int, cond_dim: int, hidden: int = 512, n_blocks: int = 3,
                 time_dim: int = 64, dropout: float = 0.0):
        super().__init__()
        self.n_genes = n_genes
        self.time_dim = time_dim
        self.x_proj = nn.Linear(n_genes, hidden)
        self.t_proj = nn.Sequential(
            nn.Linear(time_dim, hidden), nn.GELU(), nn.Linear(hidden, hidden),
        )
        self.blocks = nn.ModuleList(
            [_FiLMBlock(hidden, cond_dim, dropout=dropout) for _ in range(n_blocks)]
        )
        self.out = nn.Linear(hidden, n_genes)
        self._init_weights()

    def _init_weights(self) -> None:
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)
                if m.bias is not None:
                    nn.init.zeros_(m.bias)
        # near-zero final layer => initial velocity ~ 0 (identity-preserving)
        nn.init.zeros_(self.out.weight)
        nn.init.zeros_(self.out.bias)

    def forward(self, x: torch.Tensor, t: torch.Tensor, cond: torch.Tensor) -> torch.Tensor:
        """x [M,G]; t [M] in [0,1]; cond [M,cond_dim] -> velocity [M,G]."""
        te = sinusoidal_time_embedding(t, self.time_dim).to(x.dtype)  # [M, time_dim]
        h = self.x_proj(x) + self.t_proj(te)                          # [M, hidden]
        for block in self.blocks:
            h = block(h, cond)
        return self.out(h)                                            # [M, G]
