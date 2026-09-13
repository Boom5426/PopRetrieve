"""Population-pair dataset: samples (control pop, drug-treated pop) transitions."""
from __future__ import annotations

import math
from typing import Optional

import numpy as np
import torch
from torch.utils.data import Dataset

from .processed import SciplexDataset


def _sample_rows(pool: np.ndarray, n: int, rng: np.random.Generator) -> np.ndarray:
    if len(pool) == 0:
        raise ValueError("empty cell pool")
    replace = len(pool) < n
    return rng.choice(pool, size=n, replace=replace)


class PopulationPairDataset(Dataset):
    """One item per drug condition.  Source = matched cell-line control pool."""

    def __init__(
        self,
        data: SciplexDataset,
        condition_keys: list[str],
        n_source: int = 128,
        n_target: int = 128,
        deterministic: bool = False,
        seed: int = 0,
    ):
        self.data = data
        self.keys = list(condition_keys)
        self.n_source = n_source
        self.n_target = n_target
        self.deterministic = deterministic
        self.seed = seed
        # fallback source pool per cell line when a line has no control cells
        self._line_all: dict[str, np.ndarray] = {}
        cl = data.obs["cell_line"].astype(str).values
        for c in data.cell_lines:
            self._line_all[c] = np.where(cl == c)[0]

    def __len__(self) -> int:
        return len(self.keys)

    def _source_pool(self, cell_line: str) -> np.ndarray:
        pool = self.data.control_rows.get(cell_line, np.array([], dtype=np.int64))
        if len(pool) == 0:
            pool = self._line_all[cell_line]
        return pool

    def __getitem__(self, i: int) -> dict:
        cond = self.data.conditions[self.keys[i]]
        rng = (np.random.default_rng(self.seed + i)
               if self.deterministic else np.random.default_rng())
        src_rows = _sample_rows(self._source_pool(cond.cell_line), self.n_source, rng)
        tgt_rows = _sample_rows(cond.rows, self.n_target, rng)
        source = self.data.X[src_rows]        # [Ns, G]
        target = self.data.X[tgt_rows]        # [Nt, G]
        return {
            "source_cells": source,
            "target_cells": target,
            "drug_idx": cond.drug_idx,
            "dose": cond.dose,
            "cell_line_idx": cond.cell_line_idx,
            "condition_key": cond.key,
        }
