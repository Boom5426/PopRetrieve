"""Self-contained loader for Frangieh melanoma Perturb-CITE-seq.

Reads ``data/processed/frangieh_hvg.npz`` (218k cells, 248 CRISPR KOs, 2000 HVG,
3 immune conditions Control / IFNγ / Co-culture). This is an ``.npz`` (NOT a .pt
with a DataFrame): parallel object arrays ``X``, ``condition``, ``perturbation``
(the CRISPR-KO gene), ``is_control`` (non-targeting guides), and gene symbols under
the key ``genes`` (NOT ``gene_names``). We synthesize an ``obs`` DataFrame so it
plugs into the shared ``Dataset``. Context axis = ``condition`` (the natural
subpopulation axis of a real tumor).
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from data.population import Dataset
from utils.io import data_path


def load_frangieh(npz_path: Optional[str | Path] = None) -> Dataset:
    path = Path(npz_path) if npz_path else data_path("processed", "frangieh_hvg.npz")
    d = np.load(path, allow_pickle=True)
    X = np.asarray(d["X"], dtype=np.float32)
    gene_names = list(d["genes"].astype(str))          # key is 'genes', not 'gene_names'
    obs = pd.DataFrame({
        "perturbation": d["perturbation"].astype(str),
        "condition": d["condition"].astype(str),
        "cell_line": "melanoma",                       # single system; condition is the axis
        "is_control": np.asarray(d["is_control"]).astype(bool),
    })
    return Dataset(X=X, obs=obs, gene_names=gene_names,
                   context_col="condition", pert_col="perturbation", name="frangieh")
