"""Core data abstractions (plan §6).

A ``Population`` is a self-contained cell matrix + metadata (generalizing the old
``gidflow`` ``Condition``, which was only row indices into one big matrix, so it can
hold SciPlex3 / CD34 (.pt) and Frangieh (.npz) alike). ``RetrievalQuery`` bundles a
query population with its candidate populations and ground truth; ``RetrievalResult``
holds the scored / ranked output. ``Dataset`` is the loaded-dataset container that
the task builders slice to construct queries.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

import numpy as np
import pandas as pd


@dataclass
class Population:
    """A group of cells (cells × genes) with per-cell metadata.

    X    : np.ndarray [n_cells, n_genes]
    obs  : per-cell metadata (drug / condition / cell_line / subpopulation / replicate ...)
    var  : gene metadata (list of symbols or DataFrame)
    name : population identifier (condition-key style)
    """
    X: np.ndarray
    obs: Optional[pd.DataFrame] = None
    var: Any = None
    name: Optional[str] = None

    @property
    def n_cells(self) -> int:
        return int(self.X.shape[0])

    @property
    def n_genes(self) -> int:
        return int(self.X.shape[1])

    def mean(self) -> np.ndarray:
        return np.asarray(self.X).mean(0)

    def sample(self, n: int, rng: np.random.Generator) -> np.ndarray:
        """Draw ``n`` cells (with replacement iff the pool is smaller than n)."""
        X = np.asarray(self.X)
        idx = rng.choice(len(X), n, replace=len(X) < n)
        return X[idx].astype(np.float32)


@dataclass
class RetrievalQuery:
    query_id: str
    query_population: Population
    candidate_populations: dict[str, Population]
    ground_truth: Any                      # str | dict | pd.DataFrame
    metadata: dict = field(default_factory=dict)

    @property
    def candidate_names(self) -> list[str]:
        return list(self.candidate_populations)


@dataclass
class RetrievalResult:
    query_id: str
    scores: pd.DataFrame       # index = candidate name, columns = scorers
    metrics: pd.DataFrame      # per-scorer hit@k / rank of ground truth
    rankings: pd.DataFrame     # per-scorer descending candidate order


@dataclass
class Dataset:
    """Loaded single-cell dataset: a shared expression matrix + parallel metadata.

    ``context`` is the biological axis along which subpopulations / cell types split
    (cell_line for SciPlex3/CD34, immune condition for Frangieh). ``pert`` is the
    stripped perturbation label (drug or CRISPR KO). Task builders slice these to
    assemble ``RetrievalQuery`` objects.
    """
    X: np.ndarray
    obs: pd.DataFrame
    gene_names: list[str]
    context_col: str           # obs column naming the context axis
    pert_col: str = "perturbation"
    name: str = ""

    def __post_init__(self):
        self.X = np.asarray(self.X, dtype=np.float32)
        self.pert = self.obs[self.pert_col].astype(str).str.strip().to_numpy()
        self.context = self.obs[self.context_col].astype(str).to_numpy()
        if "is_control" in self.obs:
            self.is_control = self.obs["is_control"].astype(bool).to_numpy()
        else:
            self.is_control = np.zeros(len(self.obs), bool)
        self.contexts = sorted(pd.unique(self.context).tolist())

    # -- control pools --
    def control_rows(self, context: Optional[str] = None) -> np.ndarray:
        m = self.is_control
        if context is not None:
            m = m & (self.context == context)
        return np.flatnonzero(m)

    def control_mean(self, context: Optional[str] = None) -> np.ndarray:
        cr = self.control_rows(context)
        if len(cr) == 0:                       # fall back to grand mean
            return self.X.mean(0).astype(np.float32)
        return self.X[cr].mean(0).astype(np.float32)

    # -- treated pools --
    def treated_rows(self, context: str, drug: str,
                     dose: Optional[float] = None) -> np.ndarray:
        m = (self.context == context) & (self.pert == drug) & ~self.is_control
        if dose is not None:
            m = m & (self.obs["dose_value"].astype(float).to_numpy() == dose)
        return np.flatnonzero(m)

    def population(self, rows: np.ndarray, name: str = "") -> Population:
        return Population(self.X[rows], obs=self.obs.iloc[rows], var=self.gene_names,
                          name=name)

    def summary(self) -> str:
        n_ctrl = {c: len(self.control_rows(c)) for c in self.contexts}
        return (f"[{self.name}] cells={self.X.shape[0]} genes={self.X.shape[1]} "
                f"contexts={self.contexts} controls={n_ctrl} "
                f"perts={len(set(self.pert[~self.is_control]))}")
