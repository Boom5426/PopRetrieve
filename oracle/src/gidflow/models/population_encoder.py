"""Set encoder that maps a cell population [B, N, G] -> a vector z [B, H].

Uses masked four-way pooling (mean / max / std / attention) over cells, which is
permutation-invariant and robust to variable population sizes.
"""
from __future__ import annotations

import torch
import torch.nn as nn


def _masked_mean(x: torch.Tensor, m: torch.Tensor) -> torch.Tensor:
    # x [B,N,D], m [B,N,1]
    s = (x * m).sum(1)
    n = m.sum(1).clamp_min(1.0)
    return s / n


def _masked_max(x: torch.Tensor, m: torch.Tensor) -> torch.Tensor:
    neg = torch.finfo(x.dtype).min
    xm = x.masked_fill(m == 0, neg)
    out = xm.max(1).values
    # guard populations that were entirely masked
    out = out.masked_fill(m.sum(1) == 0, 0.0)
    return out


def _masked_std(x: torch.Tensor, m: torch.Tensor, mean: torch.Tensor) -> torch.Tensor:
    var = _masked_mean((x - mean.unsqueeze(1)) ** 2, m)
    return torch.sqrt(var.clamp_min(1e-8))


class PopulationEncoder(nn.Module):
    def __init__(self, n_genes: int, hidden: int = 512, out_dim: int = 256,
                 depth: int = 2, dropout: float = 0.1):
        super().__init__()
        layers: list[nn.Module] = []
        d = n_genes
        for _ in range(depth):
            layers += [nn.Linear(d, hidden), nn.LayerNorm(hidden), nn.GELU(),
                       nn.Dropout(dropout)]
            d = hidden
        self.cell_mlp = nn.Sequential(*layers)
        self.attn = nn.Linear(hidden, 1)          # attention-pool scores
        self.proj = nn.Sequential(
            nn.Linear(4 * hidden, out_dim), nn.LayerNorm(out_dim), nn.GELU(),
            nn.Linear(out_dim, out_dim),
        )
        self.out_dim = out_dim

    def encode_cells(self, cells: torch.Tensor, mask: torch.Tensor | None = None) -> torch.Tensor:
        """[B,N,G] -> per-cell latent [B,N,hidden] (the pre-pooling cell_mlp output)."""
        return self.cell_mlp(cells)

    def forward(self, cells: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        # cells [B,N,G], mask [B,N] bool
        h = self.cell_mlp(cells)                  # [B,N,H]
        m = mask.unsqueeze(-1).float()            # [B,N,1]
        mean = _masked_mean(h, m)
        mx = _masked_max(h, m)
        std = _masked_std(h, m, mean)
        # attention pooling. Fill with the *scores* dtype's min (under bf16
        # autocast the Linear output is bf16 while h stays fp32, so using
        # h.dtype's min would overflow bf16).
        raw = self.attn(h)                        # [B,N,1]
        scores = raw.masked_fill(m == 0, torch.finfo(raw.dtype).min)
        w = torch.softmax(scores, dim=1)
        att = (w * h).sum(1)                      # [B,H]
        pooled = torch.cat([mean, mx, std, att], dim=-1)  # [B,4H]
        return self.proj(pooled)                  # [B,out_dim]
