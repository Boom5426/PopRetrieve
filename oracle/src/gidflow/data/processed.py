"""Loaders for the re-processed SciPlex3 tensor + drug annotation bundle.

The processed ``.pt`` (produced by ``scripts/prepare_sciplex3.py``) is a dict:

    X          np.ndarray [N, G] float32   log-normalized HVG expression
    gene_names list[str]  (len G)
    cell_lines list[str]
    doses      list[float]
    obs        pandas.DataFrame            per-cell metadata, index = cell barcode
                 required cols: perturbation, cell_line, dose_value, is_control
    meta       dict

The annotation bundle lives in ``data/annotation/`` and is drug-indexed by
``drug_order.json`` (189 entries: 188 drugs + 'control' at index 188).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import torch


def condition_key(perturbation: str, cell_line: str, dose_value: float) -> str:
    """Reconstruct the split key.  NOTE: perturbation is kept *raw* (trailing
    spaces preserved) so keys match the pre-computed split files exactly."""
    return f"{perturbation}_{cell_line}_{float(dose_value)}"


@dataclass
class Condition:
    key: str
    drug_name: str          # raw perturbation name
    drug_idx: int           # annotation index (row in drug_order)
    cell_line: str
    cell_line_idx: int
    dose: float
    rows: np.ndarray        # cell row indices into X
    n_cells: int


class AnnotationBundle:
    """Drug-indexed annotations (protein targets, MOA mask, names)."""

    def __init__(self, ann_dir: str | Path):
        ann = Path(ann_dir)
        self.drug_order: list[str] = json.load(open(ann / "drug_order.json"))
        self.n_drugs = len(self.drug_order)
        # normalized (stripped) name -> index, for matching raw perturbation names
        self.name_to_idx = {name.strip(): i for i, name in enumerate(self.drug_order)}
        self.protein_targets = np.load(ann / "drug_protein_targets.npy").astype(np.float32)  # [n_drugs, P]
        self.protein_vocab: list[str] = json.load(open(ann / "protein_target_vocab.json"))
        self.moa_mask = np.load(ann / "moa_mask.npy").astype(np.float32)                      # [n_drugs, n_drugs]
        self.master = pd.read_csv(ann / "drug_annotation_master.csv")
        # control index (drug with no treatment); excluded from candidate library
        self.control_idx = self.name_to_idx.get("control", None)
        assert self.protein_targets.shape[0] == self.n_drugs
        assert self.moa_mask.shape == (self.n_drugs, self.n_drugs)
        self.n_proteins = self.protein_targets.shape[1]

    def idx_for(self, raw_perturbation: str) -> Optional[int]:
        return self.name_to_idx.get(raw_perturbation.strip(), None)

    @property
    def candidate_indices(self) -> np.ndarray:
        """Drug indices usable as ranking candidates (excludes control)."""
        idx = np.arange(self.n_drugs)
        if self.control_idx is not None:
            idx = idx[idx != self.control_idx]
        return idx


class SciplexDataset:
    """Loads the processed tensor + annotations and builds the condition index."""

    def __init__(
        self,
        processed_path: str | Path,
        ann_dir: str | Path,
        drug_features_path: Optional[str | Path] = None,
        device: str = "cpu",
    ):
        blob = torch.load(processed_path, map_location="cpu", weights_only=False)
        self.X = torch.as_tensor(np.asarray(blob["X"]), dtype=torch.float32)      # [N, G] on CPU
        self.gene_names: list[str] = list(blob["gene_names"])
        self.n_genes = self.X.shape[1]
        obs: pd.DataFrame = blob["obs"].reset_index(drop=True)
        self.obs = obs
        self.cell_lines: list[str] = sorted(obs["cell_line"].astype(str).unique().tolist())
        self.cell_line_to_idx = {c: i for i, c in enumerate(self.cell_lines)}
        self.n_cell_lines = len(self.cell_lines)

        self.ann = AnnotationBundle(ann_dir)

        # --- split cells into control pools (per cell line) and drug conditions ---
        pert = obs["perturbation"].astype(str).values
        cl = obs["cell_line"].astype(str).values
        dose = obs["dose_value"].astype(float).values
        is_ctrl = obs["is_control"].astype(bool).values if "is_control" in obs else np.zeros(len(obs), bool)

        self.control_rows: dict[str, np.ndarray] = {}
        for c in self.cell_lines:
            self.control_rows[c] = np.where(is_ctrl & (cl == c))[0]

        # group drug (non-control) cells by condition key
        cond_rows: dict[str, list[int]] = {}
        for i in np.where(~is_ctrl)[0]:
            k = condition_key(pert[i], cl[i], dose[i])
            cond_rows.setdefault(k, []).append(i)

        self.conditions: dict[str, Condition] = {}
        for k, rows in cond_rows.items():
            rows = np.asarray(rows, dtype=np.int64)
            i0 = rows[0]
            didx = self.ann.idx_for(pert[i0])
            if didx is None:
                continue  # drug not in annotation index -> skip
            self.conditions[k] = Condition(
                key=k, drug_name=pert[i0], drug_idx=int(didx),
                cell_line=cl[i0], cell_line_idx=self.cell_line_to_idx[cl[i0]],
                dose=float(dose[i0]), rows=rows, n_cells=len(rows),
            )

        # optional cached Morgan features [n_drugs, fp_dim]
        self.drug_features = None
        if drug_features_path is not None and Path(drug_features_path).exists():
            self.drug_features = torch.as_tensor(
                np.load(drug_features_path).astype(np.float32))

    # -- convenience --
    def split_keys(self, split_path: str | Path, fold: str) -> list[str]:
        """Return condition keys for a split fold that actually exist in the data."""
        split = json.load(open(split_path))
        keys = split[fold]
        return [k for k in keys if k in self.conditions]

    def all_condition_keys(self) -> list[str]:
        return list(self.conditions.keys())

    def summary(self) -> str:
        n_ctrl = {c: len(r) for c, r in self.control_rows.items()}
        return (f"cells={self.X.shape[0]} genes={self.n_genes} "
                f"cell_lines={self.cell_lines} conditions={len(self.conditions)} "
                f"controls_per_line={n_ctrl} n_drugs_ann={self.ann.n_drugs} "
                f"n_proteins={self.ann.n_proteins}")
