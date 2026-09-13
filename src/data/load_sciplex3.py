"""Self-contained loader for the re-processed SciPlex3 tensor.

Reads ``data/processed/sciplex3_all.pt`` (188 drugs x 3 cell lines, 276k cells,
2000 HVG). Canonical schema: dict with ``X``, ``gene_names``, ``obs`` (cols
perturbation / cell_line / dose_value / is_control), ``cell_lines``, ``doses``,
``meta``. Control cells carry ``perturbation == 'control'`` and ``is_control``.
Context axis = ``cell_line``.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import torch

from data.population import Dataset
from utils.io import data_path


def load_sciplex3(processed_path: Optional[str | Path] = None) -> Dataset:
    path = Path(processed_path) if processed_path else data_path("processed", "sciplex3_all.pt")
    blob = torch.load(path, map_location="cpu", weights_only=False)
    X = np.asarray(blob["X"], dtype=np.float32)
    gene_names = list(blob["gene_names"])
    obs: pd.DataFrame = blob["obs"].reset_index(drop=True)
    return Dataset(X=X, obs=obs, gene_names=gene_names,
                   context_col="cell_line", pert_col="perturbation", name="sciplex3")
