"""Collate a list of population-pair items into a padded ``DrugRankBatch``."""
from __future__ import annotations

import math

import torch

from .batch import DrugRankBatch


def _pad_stack(tensors: list[torch.Tensor]) -> tuple[torch.Tensor, torch.Tensor]:
    """Pad variable-length [Ni, G] tensors to [B, maxN, G] + bool mask [B, maxN]."""
    B = len(tensors)
    G = tensors[0].shape[1]
    maxN = max(t.shape[0] for t in tensors)
    out = tensors[0].new_zeros((B, maxN, G))
    mask = torch.zeros((B, maxN), dtype=torch.bool)
    for i, t in enumerate(tensors):
        n = t.shape[0]
        out[i, :n] = t
        mask[i, :n] = True
    return out, mask


def collate_population(items: list[dict]) -> DrugRankBatch:
    source, source_mask = _pad_stack([it["source_cells"] for it in items])
    target, target_mask = _pad_stack([it["target_cells"] for it in items])
    dose = torch.tensor([it["dose"] for it in items], dtype=torch.float32)
    return DrugRankBatch(
        source_cells=source,
        target_cells=target,
        source_mask=source_mask,
        target_mask=target_mask,
        drug_idx=torch.tensor([it["drug_idx"] for it in items], dtype=torch.long),
        dose=dose,
        log_dose=torch.log1p(dose),
        cell_line_idx=torch.tensor([it["cell_line_idx"] for it in items], dtype=torch.long),
        condition_keys=[it["condition_key"] for it in items],
    )
