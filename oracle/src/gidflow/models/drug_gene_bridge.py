"""DrugGeneBridge: bridges drug chemistry -> protein target space + match space.

drug_emb --cross-attention over learnable protein embeddings-->
    target_logits [P]   (BCE supervised against DrugCentral protein targets)
    drug context        (attention-weighted protein embeddings)
-> drug_proj_head -> drug_proj [128]
-> (+ dose conditioning) -> drug_proj_cond [128] (L2-normalized, matches gap_emb)
"""
from __future__ import annotations

import math

import torch
import torch.nn as nn
import torch.nn.functional as F


class DrugGeneBridge(nn.Module):
    def __init__(self, drug_dim: int = 256, n_proteins: int = 1742, attn_dim: int = 256,
                 emb_dim: int = 128, dropout: float = 0.1):
        super().__init__()
        self.n_proteins = n_proteins
        self.protein_emb = nn.Parameter(torch.randn(n_proteins, attn_dim) * 0.02)
        self.q_proj = nn.Linear(drug_dim, attn_dim)
        self.v_proj = nn.Linear(attn_dim, attn_dim)
        self.scale = 1.0 / math.sqrt(attn_dim)
        self.drug_proj_head = nn.Sequential(
            nn.Linear(drug_dim + attn_dim, emb_dim), nn.LayerNorm(emb_dim), nn.GELU(),
            nn.Dropout(dropout),
            nn.Linear(emb_dim, emb_dim),
        )
        self.dose_mlp = nn.Sequential(
            nn.Linear(1, 64), nn.GELU(), nn.Linear(64, emb_dim),
        )
        self.emb_dim = emb_dim

    def encode(self, drug_emb: torch.Tensor) -> dict[str, torch.Tensor]:
        # attention logits of drug over each protein == target logits
        q = self.q_proj(drug_emb)                              # [B, A]
        logits = (q @ self.protein_emb.t()) * self.scale       # [B, P]  target_logits
        w = torch.softmax(logits, dim=-1)                      # [B, P]
        v = self.v_proj(self.protein_emb)                      # [P, A]
        context = w @ v                                        # [B, A]
        drug_proj = self.drug_proj_head(torch.cat([drug_emb, context], dim=-1))  # [B,128] pre-norm
        return {"target_logits": logits, "drug_proj": drug_proj}

    def condition(self, drug_proj: torch.Tensor, log_dose: torch.Tensor) -> torch.Tensor:
        """Add dose conditioning and L2-normalize -> drug_proj_cond [., 128]."""
        d = self.dose_mlp(log_dose.unsqueeze(-1))              # [., 128]
        return F.normalize(drug_proj + d, dim=-1)

    def forward(self, drug_emb: torch.Tensor, log_dose: torch.Tensor) -> dict[str, torch.Tensor]:
        out = self.encode(drug_emb)
        out["drug_proj_cond"] = self.condition(out["drug_proj"], log_dose)
        return out
