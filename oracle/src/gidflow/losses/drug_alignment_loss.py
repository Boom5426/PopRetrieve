"""Losses for DrugRank-Flow.

- protein_space_bce : BCE(target_logits, DrugCentral protein targets), pos-weighted,
                      normalized per drug by its number of annotated targets, and
                      applied only to drugs that actually have annotations.
- recon_loss        : MSE(recon_delta, target_mean - source_mean)  (Phase 1 aux)
- FullLibraryInfoNCE: symmetric, MOA-aware, full-library contrastive matching
                      between gap_emb and dose-conditioned drug projections.
"""
from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


def protein_space_bce(target_logits: torch.Tensor, protein_labels: torch.Tensor,
                      annotated: torch.Tensor, pos_weight: float = 20.0) -> torch.Tensor:
    """
    target_logits  [B, P]
    protein_labels [B, P]  multi-hot (0/1)
    annotated      [B]     bool, True if the drug has >=1 known target
    Returns scalar mean BCE over annotated rows, normalized by #targets per row.
    """
    if annotated.sum() == 0:
        return target_logits.sum() * 0.0
    pw = torch.full((target_logits.shape[1],), pos_weight, device=target_logits.device)
    per_elem = F.binary_cross_entropy_with_logits(
        target_logits, protein_labels, pos_weight=pw, reduction="none")   # [B, P]
    # mean over proteins keeps the loss O(1) and well-scaled against InfoNCE;
    # pos_weight handles the positive/negative imbalance
    per_row = per_elem.mean(dim=1)[annotated]                             # [n_annotated]
    return per_row.mean()


def recon_loss(recon_delta: torch.Tensor, source_cells: torch.Tensor, target_cells: torch.Tensor,
               source_mask: torch.Tensor, target_mask: torch.Tensor) -> torch.Tensor:
    """MSE between predicted delta and (target_mean - source_mean) over cells."""
    sm = source_mask.unsqueeze(-1).float()
    tm = target_mask.unsqueeze(-1).float()
    src_mean = (source_cells * sm).sum(1) / sm.sum(1).clamp_min(1.0)
    tgt_mean = (target_cells * tm).sum(1) / tm.sum(1).clamp_min(1.0)
    delta = tgt_mean - src_mean                                           # [B, G]
    return F.mse_loss(recon_delta, delta)


class FullLibraryInfoNCE(nn.Module):
    """Symmetric InfoNCE with a full-library gallery and MOA-aware soft negatives.

    MoCo-style: the positive similarity uses the freshly-encoded (grad-carrying)
    true-drug projection, while negatives come from the (possibly cached) gallery.
    """

    def __init__(self, soft_weight: float = 0.3):
        super().__init__()
        self.soft_weight = soft_weight

    def forward(
        self,
        gap_emb: torch.Tensor,          # [B, 128]  transition embedding (unit norm)
        drug_proj_cond: torch.Tensor,   # [B, 128]  fresh true-drug proj (dose-cond, unit norm)
        gallery_cond: torch.Tensor,     # [B, D, 128] dose-conditioned library gallery
        lib_pos: torch.Tensor,          # [B]  column of the true drug in the gallery
        moa_same_lib: torch.Tensor,     # [B, D] 1.0 if gallery drug shares MOA w/ true drug
        moa_same_batch: torch.Tensor,   # [B, B] 1.0 if two queries' drugs share MOA
        temperature: float = 0.15,
    ) -> dict[str, torch.Tensor]:
        B, D, _ = gallery_cond.shape
        # === gap -> drug (full library) ===
        pos_logit = (gap_emb * drug_proj_cond).sum(-1) / temperature             # [B] fresh positive
        neg_logit = (gap_emb.unsqueeze(1) * gallery_cond).sum(-1) / temperature  # [B, D] negatives
        # weight: down-weight same-MOA negatives; zero-out the true drug's own column
        w = torch.where(moa_same_lib > 0,
                        torch.full_like(moa_same_lib, self.soft_weight),
                        torch.ones_like(moa_same_lib))
        w.scatter_(1, lib_pos.view(-1, 1), 0.0)                                  # exclude self from negs
        mx = torch.maximum(pos_logit, neg_logit.max(dim=1).values).detach()      # [B] stabilizer
        num = torch.exp(pos_logit - mx)
        den = num + (w * torch.exp(neg_logit - mx.unsqueeze(1))).sum(dim=1)
        g2d = -(torch.log(num.clamp_min(1e-12)) - torch.log(den.clamp_min(1e-12))).mean()

        # === drug -> gap (in-batch) ===
        d2g_logits = (drug_proj_cond @ gap_emb.t()) / temperature                # [B, B]
        pos_b = torch.arange(B, device=gap_emb.device)
        wb = torch.where(moa_same_batch > 0,
                         torch.full_like(moa_same_batch, self.soft_weight),
                         torch.ones_like(moa_same_batch))
        wb.scatter_(1, pos_b.view(-1, 1), 1.0)                                   # positive full weight
        mb = d2g_logits.max(dim=1, keepdim=True).values.detach()
        exb = torch.exp(d2g_logits - mb) * wb
        numb = exb.gather(1, pos_b.view(-1, 1)).squeeze(1)
        denb = exb.sum(dim=1)
        d2g = -(torch.log(numb.clamp_min(1e-12)) - torch.log(denb.clamp_min(1e-12))).mean()

        return {"infonce": 0.5 * (g2d + d2g), "g2d": g2d.detach(), "d2g": d2g.detach()}
