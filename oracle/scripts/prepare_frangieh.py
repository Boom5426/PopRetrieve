#!/usr/bin/env python
"""Process FrangiehIzar2021 melanoma Perturb-CITE-seq into a 2000-HVG array for the
natural divergent-subpopulation anchor. Subpop axis = immune CONDITION
(Control / IFN-gamma / Co-culture); perturbation library = 248 CRISPR gene KOs
(+ non-targeting 'control'). Raw counts -> CP10k -> log1p -> HVG.

    python scripts/prepare_frangieh.py
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import scanpy as sc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="data/raw/frangieh2021/FrangiehIzar2021_RNA.h5ad")
    ap.add_argument("--output", default="data/processed/frangieh_hvg.npz")
    ap.add_argument("--n-hvgs", type=int, default=2000)
    ap.add_argument("--min-cells", type=int, default=50,
                    help="drop KOs with fewer than this many cells overall")
    args = ap.parse_args()

    print(f"[frangieh] reading {args.input} ...", flush=True)
    ad = sc.read_h5ad(args.input)
    cond = ad.obs["perturbation_2"].astype(str).str.strip()
    pert = ad.obs["perturbation"].astype(str).str.strip()
    keep_cond = cond.isin(["Control", "IFNγ", "Co-culture"]).to_numpy()
    keep_pert = (~pert.isin(["nan", "NaN", ""])).to_numpy()
    ad = ad[keep_cond & keep_pert].copy()
    print(f"[frangieh] cells after filter: {ad.n_obs}  conditions={sorted(cond.unique())}")

    sc.pp.normalize_total(ad, target_sum=1e4)
    sc.pp.log1p(ad)
    sc.pp.highly_variable_genes(ad, n_top_genes=args.n_hvgs, flavor="seurat")
    ad = ad[:, ad.var["highly_variable"]].copy()
    print(f"[frangieh] HVGs: {ad.n_vars}")

    X = ad.X.toarray().astype(np.float32) if hasattr(ad.X, "toarray") else np.asarray(ad.X, np.float32)
    condition = ad.obs["perturbation_2"].astype(str).str.strip().to_numpy()
    perturbation = ad.obs["perturbation"].astype(str).str.strip().to_numpy()
    is_control = (perturbation == "control")

    # drop KOs that are too rare overall (keep 'control')
    import pandas as pd
    vc = pd.Series(perturbation[~is_control]).value_counts()
    rare = set(vc[vc < args.min_cells].index)
    keep = np.array([p == "control" or p not in rare for p in perturbation])
    X, condition, perturbation, is_control = X[keep], condition[keep], perturbation[keep], is_control[keep]

    out = Path(args.output); out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out, X=X, condition=condition, perturbation=perturbation,
                        is_control=is_control, genes=ad.var_names.to_numpy())
    n_ko = len(set(perturbation[~is_control]))
    print(f"[frangieh] saved {out}  X={X.shape}  KOs={n_ko}  control_cells={int(is_control.sum())}")
    import collections
    print("[frangieh] cells per condition:",
          dict(collections.Counter(condition)))
    print("[frangieh] control cells per condition:",
          dict(collections.Counter(condition[is_control])))


if __name__ == "__main__":
    main()
