"""Shared helpers: config loading, seeding, device, experiment construction."""
from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

import numpy as np
import torch
import yaml

from .data.processed import SciplexDataset
from .models.drug_rank_model import DrugRankModel
from .training.drug_gallery import MatchingContext


def load_config(path: str | Path) -> dict[str, Any]:
    with open(path) as f:
        return yaml.safe_load(f)


def set_seed(seed: int = 0) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def get_device(prefer: str = "cuda") -> torch.device:
    if prefer == "cuda" and torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


def build_data(cfg: dict) -> SciplexDataset:
    return SciplexDataset(
        processed_path=cfg["data"]["processed_path"],
        ann_dir=cfg["data"]["annotation_dir"],
        drug_features_path=cfg["data"].get("drug_features_path"),
    )


def build_model(cfg: dict, data: SciplexDataset) -> DrugRankModel:
    assert data.drug_features is not None, "drug_features not loaded; run build_drug_features.py"
    m = cfg["model"]
    return DrugRankModel(
        n_genes=data.n_genes,
        n_drugs=data.ann.n_drugs,
        n_proteins=data.ann.n_proteins,
        drug_features=data.drug_features,
        n_cell_lines=data.n_cell_lines,
        pop_hidden=m.get("pop_hidden", 512),
        pop_dim=m.get("pop_dim", 256),
        drug_hidden=m.get("drug_hidden", 512),
        drug_dim=m.get("drug_dim", 256),
        emb_dim=m.get("emb_dim", 128),
        dropout=m.get("dropout", 0.1),
    )


def build_matching(data: SciplexDataset, device: str = "cpu") -> MatchingContext:
    return MatchingContext(data.ann, device=device)
