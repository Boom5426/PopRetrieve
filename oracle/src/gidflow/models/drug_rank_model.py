"""Top-level DrugRank-Flow model tying the three spaces together.

  transition side:  source/target populations -> PopulationEncoder -> GapEncoder -> gap_emb [128]
  drug side:        drug_idx -> Morgan fp -> DrugEncoder -> DrugGeneBridge -> drug_proj_cond [128]
  match:            score = cosine(gap_emb, drug_proj_cond)
"""
from __future__ import annotations

from typing import Optional

import torch
import torch.nn as nn

from ..data.batch import DrugRankBatch
from .drug_encoder import DrugEncoder
from .drug_gene_bridge import DrugGeneBridge
from .gap_encoder import GapEncoder
from .population_encoder import PopulationEncoder


class DrugRankModel(nn.Module):
    def __init__(
        self,
        n_genes: int,
        n_drugs: int,
        n_proteins: int,
        drug_features: torch.Tensor,     # [n_drugs, fp_dim]
        n_cell_lines: int = 3,
        pop_hidden: int = 512,
        pop_dim: int = 256,
        drug_hidden: int = 512,
        drug_dim: int = 256,
        emb_dim: int = 128,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.pop_encoder = PopulationEncoder(n_genes, pop_hidden, pop_dim, dropout=dropout)
        self.gap_encoder = GapEncoder(pop_dim, pop_dim, emb_dim, n_cell_lines, n_genes, dropout)
        self.drug_encoder = DrugEncoder(drug_features.shape[1], drug_hidden, drug_dim, dropout)
        self.bridge = DrugGeneBridge(drug_dim, n_proteins, drug_dim, emb_dim, dropout)
        self.register_buffer("drug_features", drug_features.float())  # [n_drugs, fp_dim]
        self.n_drugs = n_drugs
        self.emb_dim = emb_dim

    # ---- transition side ----
    def encode_transition(self, batch: DrugRankBatch) -> dict[str, torch.Tensor]:
        z_src = self.pop_encoder(batch.source_cells, batch.source_mask)
        z_tgt = self.pop_encoder(batch.target_cells, batch.target_mask)
        return self.gap_encoder(z_src, z_tgt, batch.cell_line_idx)

    # ---- drug side ----
    def encode_drug_idx(self, drug_idx: torch.Tensor, log_dose: torch.Tensor) -> dict[str, torch.Tensor]:
        fp = self.drug_features[drug_idx]
        drug_emb = self.drug_encoder(fp)
        return self.bridge(drug_emb, log_dose)

    def encode_all_drugs(self) -> dict[str, torch.Tensor]:
        """Base (dose-free) projections + target logits for the full library."""
        drug_emb = self.drug_encoder(self.drug_features)
        return self.bridge.encode(drug_emb)   # {'target_logits':[D,P], 'drug_proj':[D,128]}

    def gallery_cond(self, drug_proj: torch.Tensor, log_dose: torch.Tensor) -> torch.Tensor:
        """Condition a cached [D,128] gallery on a batch of doses -> [B, D, 128]."""
        B = log_dose.shape[0]
        D = drug_proj.shape[0]
        dp = drug_proj.unsqueeze(0).expand(B, D, -1)                 # [B,D,128]
        # dose term per query, broadcast over all drugs in the gallery
        dose_term = self.bridge.dose_mlp(log_dose.unsqueeze(-1)).unsqueeze(1)  # [B,1,128]
        return torch.nn.functional.normalize(dp + dose_term, dim=-1)

    def forward(self, batch: DrugRankBatch) -> dict[str, torch.Tensor]:
        gap = self.encode_transition(batch)
        drug = self.encode_drug_idx(batch.drug_idx, batch.log_dose)
        out = {**gap, **drug}
        out["score"] = (gap["gap_emb"] * drug["drug_proj_cond"]).sum(-1)  # cosine (both unit norm)
        return out
