"""DrugEncoder: Morgan ECFP4 fingerprint [B, 2048] -> drug_emb [B, H]."""
from __future__ import annotations

import torch
import torch.nn as nn


class DrugEncoder(nn.Module):
    def __init__(self, fp_dim: int = 2048, hidden: int = 512, out_dim: int = 256,
                 dropout: float = 0.1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(fp_dim, hidden), nn.LayerNorm(hidden), nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(hidden, out_dim), nn.LayerNorm(out_dim), nn.GELU(),
        )
        self.out_dim = out_dim

    def forward(self, fp: torch.Tensor) -> torch.Tensor:
        return self.net(fp)
