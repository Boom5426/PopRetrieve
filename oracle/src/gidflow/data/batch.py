"""Core batch object for population-level drug-rank transitions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

import torch


@dataclass
class DrugRankBatch:
    """A batch of (source population -> target population) transitions.

    Shapes:
        source_cells [B, Ns, G]   control / source population cells
        target_cells [B, Nt, G]   drug-treated / target population cells
        source_mask  [B, Ns]      True = valid cell (used for masked pooling)
        target_mask  [B, Nt]      True = valid cell
        drug_idx     [B]          annotation index (row in drug_order / target matrix)
        dose         [B]          raw dose (nM)
        log_dose     [B]          log1p(dose) conditioning feature
        cell_line_idx[B]          0..(n_cell_lines-1)
    """

    source_cells: torch.Tensor
    target_cells: torch.Tensor
    source_mask: torch.Tensor
    target_mask: torch.Tensor
    drug_idx: torch.Tensor
    dose: torch.Tensor
    log_dose: torch.Tensor
    cell_line_idx: torch.Tensor
    condition_keys: list[str] = field(default_factory=list)
    metadata: Optional[dict[str, Any]] = None

    def to(self, device: torch.device | str) -> "DrugRankBatch":
        return DrugRankBatch(
            source_cells=self.source_cells.to(device),
            target_cells=self.target_cells.to(device),
            source_mask=self.source_mask.to(device),
            target_mask=self.target_mask.to(device),
            drug_idx=self.drug_idx.to(device),
            dose=self.dose.to(device),
            log_dose=self.log_dose.to(device),
            cell_line_idx=self.cell_line_idx.to(device),
            condition_keys=self.condition_keys,
            metadata=self.metadata,
        )

    @property
    def batch_size(self) -> int:
        return self.source_cells.shape[0]

    @property
    def n_genes(self) -> int:
        return self.source_cells.shape[-1]
