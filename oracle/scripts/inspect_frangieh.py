#!/usr/bin/env python
"""Inspect FrangiehIzar2021 Perturb-CITE-seq (melanoma) to decide if/how it fits the
'divergent-subpopulation' anchor: what perturbation library, what natural subpop axes
(immune condition control/IFNg/co-culture, or resistance-program states), cell counts,
normalization state, control/non-targeting label.

    python scripts/inspect_frangieh.py
"""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np
import scanpy as sc

PATH = sys.argv[1] if len(sys.argv) > 1 else "data/raw/frangieh2021/FrangiehIzar2021_RNA.h5ad"
KEYS = ["pert", "guide", "target", "gene", "condition", "cond", "state", "program",
        "control", "ntc", "sgrna", "grna", "treatment", "ifn", "co_culture", "mixscape"]

ad = sc.read_h5ad(PATH, backed="r")
print(f"=== {Path(PATH).name} ===")
print(ad)
print("\n--- obs columns ---")
print(ad.obs.columns.tolist())
print("\n--- perturbation/condition-like columns ---")
hits = [c for c in ad.obs.columns if any(k in c.lower() for k in KEYS)]
print(hits)

for c in hits:
    try:
        vc = ad.obs[c].value_counts(dropna=False)
    except Exception:                                     # noqa: BLE001
        continue
    print(f"\n[{c}]  ({ad.obs[c].nunique(dropna=True)} unique)")
    print(vc.head(15).to_string())

# X normalization state (raw counts vs log-normalized)
try:
    Xs = ad.X[:2000] if ad.isbacked else ad.X[:2000]
    Xs = Xs.toarray() if hasattr(Xs, "toarray") else np.asarray(Xs)
    print(f"\n--- X sample stats --- max={Xs.max():.3f} min={Xs.min():.3f} "
          f"integer={np.allclose(Xs, np.round(Xs))} "
          f"layers={list(ad.layers.keys())}")
except Exception as ex:                                   # noqa: BLE001
    print("X stat check skipped:", ex)
print("\nvar head:")
print(ad.var.head())
