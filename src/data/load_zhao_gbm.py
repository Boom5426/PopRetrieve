"""ZhaoSims2021: patient-derived glioblastoma slices. NATURAL heterogeneity, not constructed.

WHY THIS DATASET, AND WHAT IT IS NOT
------------------------------------
Every positive real-data result in this study lives in cell-line mixtures that WE constructed
(SciPlex3 A549+K562 etc.). That is a fair objection: a minority subpopulation we assembled by
pipetting two cell lines together is not evidence that anything works on the heterogeneity a
tumour actually has. This dataset is the answer to that objection, and it is used for exactly
one purpose.

ZhaoSims2021 is acute-slice culture and surgical biopsy from 10 glioblastoma patients, treated
with drugs. Within a single patient's slice there are malignant cells, tumour-associated
myeloid cells, T cells, oligodendrocytes and endothelium, co-existing as they do in the
patient. That heterogeneity is NATURAL: we did not build it, and the minority subpopulation is
a real cell type with a real, different response to a drug.

**IT IS NOT A RETRIEVAL BENCHMARK, AND WE DO NOT USE IT AS ONE.** The drug panel is 6 compounds,
and only ONE patient (PW030) received all six; the rest received one or two (etoposide and/or
panobinostat). A leave-one-drug-out retrieval would therefore run on a single patient against
five candidates. Reporting Hit@1 from that would be an anecdote dressed as a benchmark, and this
paper is in part about not doing that. We use it to test the TWO GATES on natural heterogeneity:

  Gate 1  do naturally co-existing cell types respond in DIFFERENT directions to the same drug?
          (induced response cosine between malignant and immune compartments)
  Gate 2  is that natural structure RECOVERABLE, and is the supervised ceiling higher than the
          0.69 we measured on the constructed HDAC-versus-JAK mixture?

The second is the sharper test. If real tumour subpopulations are far more separable than our
constructed ones, then Gate 2 opens on natural data, and the question becomes whether a
distributional score finally pays off. If it does not pay off even then, the negative result is
much stronger than anything the constructed mixtures could establish.

CELL TYPING, AND WHY IT IS NOT A BARE ARGMAX
-------------------------------------------
The published obs carries celltype = 'unknown' for every cell, so compartments are assigned by
canonical marker score. Marker assignment is a labelling of the data, not a model fit on it, and
the labels are never shown to any retrieval score or to any clustering method: they exist only
to evaluate whether those methods recover them.

The first version of this loader took the argmax of five marker z-scores. That FORCES every cell
into some compartment, including cells that express none of the markers, and it produced two
compartments that do not survive their own validation: cells labelled "tcell" (22% of the
dataset) had a mean CD3D/CD3E/CD2 expression of 0.080, LOWER than their malignant-marker score
of 0.141, and "endothel" cells expressed myeloid markers more strongly than endothelial ones.
They were not T cells and not endothelium; they were unidentifiable cells swept into whichever
class the argmax had left over. Building a "natural heterogeneity" result on a fabricated T-cell
compartment would be worse than having no natural dataset at all.

A cell is therefore assigned to a compartment only if it (i) scores highest for that
compartment, (ii) clears an absolute expression floor on that compartment's key markers, and
(iii) beats the runner-up compartment by a margin. Everything else is labelled ``unassigned``
and is EXCLUDED, not reassigned. Only the three compartments that pass validation are used:
malignant glioma cells, tumour-associated myeloid cells, and oligodendrocytes. The validation
table is written alongside the data so the labelling can be checked rather than trusted.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[2]
RAW = REPO / "data" / "raw" / "zhao2021" / "ZhaoSims2021.h5ad"
PROC = REPO / "data" / "processed" / "zhao_gbm.npz"

N_HVG = 2000
MIN_CELLS_PER_GROUP = 50

# Only the compartments that survive validation (see module docstring). "tcell" and "endothel"
# were assigned by an earlier argmax rule and did NOT express their own markers; they are gone.
MARKERS = {
    "malignant": ["SOX2", "EGFR", "PDGFRA", "OLIG1", "OLIG2", "GFAP", "AQP4"],
    "myeloid":   ["PTPRC", "CD14", "AIF1", "CSF1R", "ITGAM", "C1QA", "C1QB"],
    "oligo":     ["MBP", "PLP1", "MOG", "MAG"],
}
# the genes a cell must actually express to be called this type, and the floor it must clear
KEY_MARKERS = {
    "malignant": ["SOX2", "OLIG2", "EGFR"],
    "myeloid":   ["CD14", "CSF1R", "C1QB", "AIF1"],
    "oligo":     ["MBP", "PLP1"],
}
EXPR_FLOOR = 0.25        # mean log-normalized expression of the key markers
MARGIN_FLOOR = 0.25      # z-score margin over the runner-up compartment


def _score(Xl: np.ndarray, gene_idx: dict, names: list) -> np.ndarray:
    """Mean z-scored expression of a marker set: a labelling rule, not a fitted model."""
    cols = [gene_idx[g] for g in names if g in gene_idx]
    if not cols:
        return np.zeros(Xl.shape[0], dtype=np.float32)
    S = Xl[:, cols]
    mu, sd = S.mean(0, keepdims=True), S.std(0, keepdims=True) + 1e-8
    return ((S - mu) / sd).mean(1).astype(np.float32)


def _raw_mean(Xl: np.ndarray, gene_idx: dict, names: list) -> np.ndarray:
    """Mean log-normalized expression (not z-scored): the absolute floor a call must clear."""
    cols = [gene_idx[g] for g in names if g in gene_idx]
    return Xl[:, cols].mean(1).astype(np.float32) if cols else np.zeros(len(Xl), np.float32)


def build(force: bool = False) -> Path:
    """Normalize, log1p, HVG-select, and assign compartments by marker score."""
    if PROC.exists() and not force:
        return PROC
    import anndata as ad
    import scanpy as sc

    a = ad.read_h5ad(RAW)
    a.var_names = [str(v).upper() for v in a.var_names]
    a.var_names_make_unique()

    sc.pp.filter_cells(a, min_genes=200)
    sc.pp.normalize_total(a, target_sum=1e4)
    sc.pp.log1p(a)

    # compartments are scored on the FULL log-normalized matrix, before HVG selection, so the
    # labelling never depends on a gene set chosen for downstream variance
    gene_idx = {g: i for i, g in enumerate(a.var_names)}
    Xl = a.X.toarray() if hasattr(a.X, "toarray") else np.asarray(a.X)
    names = list(MARKERS)
    scores = np.vstack([_score(Xl, gene_idx, m) for m in MARKERS.values()]).T
    keyexp = np.vstack([_raw_mean(Xl, gene_idx, KEY_MARKERS[n]) for n in names]).T

    top = scores.argmax(1)
    margin = scores.max(1) - np.sort(scores, axis=1)[:, -2]
    own_expr = keyexp[np.arange(len(top)), top]

    # A cell is called ONLY if it wins, clears the absolute expression floor for the class it
    # won, and beats the runner-up by a margin. Otherwise it is 'unassigned' and is dropped.
    # It is never swept into a leftover class, which is what fabricated the T-cell compartment.
    called = (own_expr >= EXPR_FLOOR) & (margin >= MARGIN_FLOOR)
    labels = np.where(called, np.array(names)[top], "unassigned")

    # validation table: does each called compartment actually express its OWN key markers most?
    val = []
    for i, n in enumerate(names):
        m = labels == n
        if m.sum() == 0:
            continue
        row = {"compartment": n, "n_cells": int(m.sum())}
        for j, k in enumerate(names):
            row[f"expr_{k}"] = float(keyexp[m, j].mean())
        row["passes"] = bool(np.argmax([row[f"expr_{k}"] for k in names]) == i)
        val.append(row)
    val = pd.DataFrame(val)
    if not val.passes.all():
        raise RuntimeError(
            "compartment validation FAILED: a called compartment does not express its own key "
            f"markers most strongly. Refusing to write labels that are not what they claim.\n"
            f"{val.to_string(index=False)}")
    val["frac_unassigned"] = float((labels == "unassigned").mean())
    (REPO / "results" / "zhao_gbm").mkdir(parents=True, exist_ok=True)
    val.to_csv(REPO / "results" / "zhao_gbm" / "compartment_validation.csv", index=False)
    print(f"[zhao] compartment validation PASSED; "
          f"{(labels=='unassigned').mean():.1%} of cells unassigned and dropped")
    print(val.to_string(index=False))

    sc.pp.highly_variable_genes(a, n_top_genes=N_HVG, flavor="seurat")
    a = a[:, a.var.highly_variable].copy()
    X = (a.X.toarray() if hasattr(a.X, "toarray") else np.asarray(a.X)).astype(np.float32)

    o = a.obs
    pert = o["perturbation"].astype(str).values
    keep = labels != "unassigned"          # dropped, not reassigned
    np.savez_compressed(
        PROC, X=X[keep],
        patient=o["sample"].astype(str).values[keep],
        perturbation=pert[keep],
        is_control=(pert[keep] == "control"),
        compartment=labels[keep],
        compartment_margin=margin[keep],
        genes=np.array(a.var_names, dtype=object),
    )
    return PROC


class ZhaoGBM:
    """Loader with the same surface the retrieval code expects, plus natural compartments."""

    def __init__(self, path: Optional[Path] = None):
        d = np.load(path or PROC, allow_pickle=True)
        self.X = d["X"]
        self.patient = d["patient"]
        self.pert = d["perturbation"]
        self.is_control = d["is_control"]
        self.compartment = d["compartment"]
        self.compartment_margin = d["compartment_margin"]
        self.genes = d["genes"]

    @property
    def patients(self):
        return sorted(set(self.patient.tolist()))

    def rows(self, patient=None, drug=None, compartment=None, control=None) -> np.ndarray:
        m = np.ones(len(self.X), dtype=bool)
        if patient is not None:
            m &= self.patient == patient
        if drug is not None:
            m &= self.pert == drug
        if compartment is not None:
            m &= self.compartment == compartment
        if control is not None:
            m &= self.is_control == control
        return np.where(m)[0]

    def usable(self, min_cells: int = MIN_CELLS_PER_GROUP) -> pd.DataFrame:
        """(patient, drug, compartment) cells, so the caller can see what is actually testable."""
        df = pd.DataFrame({"patient": self.patient, "drug": self.pert,
                           "compartment": self.compartment})
        t = df.value_counts().reset_index(name="n")
        return t[t.n >= min_cells].sort_values(["patient", "drug", "compartment"])

    def summary(self) -> str:
        u, c = np.unique(self.compartment, return_counts=True)
        comp = ", ".join(f"{a} {b}" for a, b in zip(u, c))
        return (f"ZhaoGBM: {self.X.shape[0]} cells x {self.X.shape[1]} HVG | "
                f"{len(self.patients)} patients | compartments: {comp}")


def load_zhao_gbm() -> ZhaoGBM:
    build()
    return ZhaoGBM()


if __name__ == "__main__":
    d = load_zhao_gbm()
    print(d.summary())
    print()
    print(d.usable().to_string(index=False))
