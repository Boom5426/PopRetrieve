"""Self-contained loader for CD34+ primary HSPCs (GSE306429).

Reads ``data/processed/cd34_all.pt`` (36 real drugs, 34k cells, 2000 HVG, 4 natural
lineages found unsupervised on DMSO). Same canonical schema as SciPlex3 but the
control label is ``'DMSO'`` (flagged by ``is_control``; dose is NaN for controls)
and there is a single cell line ``'CD34+'``. Context axis = ``cell_line``, but the
biological subpopulations here are DISCOVERED (PCA+KMeans on control cells) rather
than stored — see ``retrieval.tasks.NaturalSubpops``.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import torch

from data.population import Dataset
from utils.io import data_path


def load_cd34(processed_path: Optional[str | Path] = None) -> Dataset:
    path = Path(processed_path) if processed_path else data_path("processed", "cd34_all.pt")
    blob = torch.load(path, map_location="cpu", weights_only=False)
    X = np.asarray(blob["X"], dtype=np.float32)
    gene_names = list(blob["gene_names"])
    obs: pd.DataFrame = blob["obs"].reset_index(drop=True)
    return Dataset(X=X, obs=obs, gene_names=gene_names,
                   context_col="cell_line", pert_col="perturbation", name="cd34")
