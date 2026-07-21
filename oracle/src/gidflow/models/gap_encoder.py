"""GapEncoder: (z_source, z_target) -> transition embedding gap_emb [128].

Also carries cell-line conditioning and a Phase-1 auxiliary reconstruction head
that decodes the mean expression delta (target_mean - source_mean) from the
(pre-normalization) transition vector.
"""
from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


class GapEncoder(nn.Module):
    def __init__(self, pop_dim: int = 256, z_gap_dim: int = 256, emb_dim: int = 128,
                 n_cell_lines: int = 3, n_genes: int = 2000, dropout: float = 0.1):
        super().__init__()
        self.cell_line_emb = nn.Embedding(n_cell_lines, 32)
        in_dim = 3 * pop_dim + 32
        self.gap_mlp = nn.Sequential(
            nn.Linear(in_dim, z_gap_dim), nn.LayerNorm(z_gap_dim), nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(z_gap_dim, z_gap_dim), nn.LayerNorm(z_gap_dim), nn.GELU(),
        )
        self.gap_proj = nn.Sequential(
            nn.Linear(z_gap_dim, emb_dim), nn.LayerNorm(emb_dim),
        )
        # auxiliary reconstruction of mean expression delta (Phase 1)
        self.recon_mlp = nn.Sequential(
            nn.Linear(emb_dim, 512), nn.GELU(), nn.Linear(512, n_genes),
        )
        self.emb_dim = emb_dim

    def forward(self, z_source: torch.Tensor, z_target: torch.Tensor,
                cell_line_idx: torch.Tensor) -> dict[str, torch.Tensor]:
        cl = self.cell_line_emb(cell_line_idx)                 # [B,32]
        feat = torch.cat([z_source, z_target, z_target - z_source, cl], dim=-1)
        z_gap = self.gap_mlp(feat)                             # [B, z_gap_dim]
        gap_pre = self.gap_proj(z_gap)                         # [B, emb_dim] (pre-norm)
        gap_emb = F.normalize(gap_pre, dim=-1)                 # unit sphere
        return {"z_gap": z_gap, "gap_pre": gap_pre, "gap_emb": gap_emb}

    def reconstruct_delta(self, gap_pre: torch.Tensor) -> torch.Tensor:
        return self.recon_mlp(gap_pre)                         # [B, n_genes]
