"""Full-library drug gallery + MOA-aware matching context.

The gallery caches the base (dose-free) drug projections for all *candidate*
drugs (control excluded).  MatchingContext precomputes the annotation-index ->
library-position map and MOA co-membership lookups used by the InfoNCE loss and
by retrieval evaluation.
"""
from __future__ import annotations

import numpy as np
import torch


class MatchingContext:
    def __init__(self, ann_bundle, device: str = "cpu"):
        self.candidate_indices = torch.as_tensor(
            ann_bundle.candidate_indices, dtype=torch.long, device=device)   # [D]
        self.n_drugs = ann_bundle.n_drugs
        self.D = self.candidate_indices.numel()
        # annotation idx -> library position (-1 if not a candidate)
        a2l = torch.full((self.n_drugs,), -1, dtype=torch.long, device=device)
        a2l[self.candidate_indices] = torch.arange(self.D, device=device)
        self.ann_to_lib = a2l
        moa = torch.as_tensor(ann_bundle.moa_mask, dtype=torch.float32, device=device)
        self.moa_full = moa                                                  # [n_drugs, n_drugs]
        self.moa_lib = moa[:, self.candidate_indices]                        # [n_drugs, D]
        self.device = device

    def lib_pos(self, drug_idx: torch.Tensor) -> torch.Tensor:
        return self.ann_to_lib[drug_idx]

    def moa_same_lib(self, drug_idx: torch.Tensor) -> torch.Tensor:
        return self.moa_lib[drug_idx]                                        # [B, D]

    def moa_same_batch(self, drug_idx: torch.Tensor) -> torch.Tensor:
        return self.moa_full[drug_idx][:, drug_idx]                          # [B, B]


class DrugGallery:
    """Provides the [D,128] base gallery of candidate-drug projections."""

    def __init__(self, ctx: MatchingContext, refresh_every: int = 1):
        self.ctx = ctx
        self.refresh_every = max(1, refresh_every)
        self._cache: torch.Tensor | None = None
        self._logits: torch.Tensor | None = None

    def get(self, model, step: int) -> torch.Tensor:
        """Return base gallery [D,128].  Fresh (grad) if refresh_every==1, else
        a detached cache refreshed on step boundaries."""
        if self.refresh_every == 1:
            out = model.encode_all_drugs()
            return out["drug_proj"][self.ctx.candidate_indices]
        if self._cache is None or step % self.refresh_every == 0:
            with torch.no_grad():
                out = model.encode_all_drugs()
                self._cache = out["drug_proj"][self.ctx.candidate_indices].detach()
        return self._cache

    @torch.no_grad()
    def full_target_logits(self, model) -> torch.Tensor:
        return model.encode_all_drugs()["target_logits"]                     # [n_drugs, P]
