#!/usr/bin/env python
"""Re-process raw SciPlex3 (scPerturb h5ad) into the DrugRank-Flow tensor.

Memory-safe: reads the backed CSR matrix in CONTIGUOUS blocks (fast for CSR),
selects HVGs on a subsample, and only ever materializes the [N, 2000] HVG dense
matrix — never the full [N, 110983] dense. Peak RAM ~3-4 GB on a 14 GB box.

Keeps all 3 cell lines + real DMSO controls (is_control) + real gene symbols.

    python scripts/prepare_sciplex3.py \
        --input data/raw/SrivatsanTrapnell2020_sciplex3.h5ad \
        --output data/processed/sciplex3_all.pt \
        --annotation-dir data/annotation \
        --n-hvgs 2000 --max-cells-per-cond 120 --max-control-cells 3000
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.sparse as sp

CTRL_NAMES = ["control", "vehicle", "dmso"]


def pick_col(cols, candidates):
    for c in candidates:
        if c in cols:
            return c
    raise KeyError(f"none of {candidates} in {list(cols)}")


def load_rows_chunked(adata_b, idx_sorted, chunk=40000, gene_idx=None, layer=None):
    """Load rows `idx_sorted` (sorted, into full matrix) via contiguous block reads.
    If gene_idx is given, subset columns immediately. Returns (X, rowsum_all_genes).
    X is dense float32 if gene_idx else sparse csr. If `layer` is set, read raw counts
    from adata_b.layers[layer] instead of .X (for already-normalized h5ads)."""
    n = adata_b.shape[0]
    parts, rowsums = [], []
    ptr = 0
    src = adata_b.layers[layer] if layer is not None else adata_b.X
    for start in range(0, n, chunk):
        end = min(start + chunk, n)
        # which requested rows fall in this block?
        while ptr < len(idx_sorted) and idx_sorted[ptr] < end:
            ptr += 1  # advance; we slice below by mask instead
        m = (idx_sorted >= start) & (idx_sorted < end)
        if not m.any():
            continue
        local = idx_sorted[m] - start
        Xb = src[start:end]
        Xb = Xb.tocsr() if sp.issparse(Xb) else sp.csr_matrix(np.asarray(Xb))
        sub = Xb[local]
        rowsums.append(np.asarray(sub.sum(1)).ravel())
        if gene_idx is not None:
            parts.append(np.asarray(sub[:, gene_idx].todense(), dtype=np.float32))
        else:
            parts.append(sub)
    rowsum = np.concatenate(rowsums)
    if gene_idx is not None:
        return np.concatenate(parts, axis=0), rowsum
    return sp.vstack(parts).tocsr(), rowsum


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", default="data/processed/sciplex3_all.pt")
    ap.add_argument("--annotation-dir", default="data/annotation")
    ap.add_argument("--n-hvgs", type=int, default=2000)
    ap.add_argument("--max-cells-per-cond", type=int, default=120)
    ap.add_argument("--max-control-cells", type=int, default=3000)
    ap.add_argument("--hvg-subsample", type=int, default=60000)
    ap.add_argument("--target-sum", type=float, default=1e4)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--counts-layer", default=None,
                    help="read raw counts from .layers[KEY] instead of .X (pre-normalized h5ads, e.g. GSE306429)")
    ap.add_argument("--keep-all", action="store_true",
                    help="keep ALL perturbations & cell lines present (for datasets without a "
                         "predefined drug_order, e.g. GSE306429). Default filters to drug_order.")
    ap.add_argument("--cell-lines", default=None,
                    help="comma-separated cell lines to keep; default = SciPlex3 trio unless --keep-all")
    args = ap.parse_args()
    rng = np.random.default_rng(args.seed)

    import scanpy as sc

    print(f"[prep] reading (backed) {args.input} ...", flush=True)
    adata_b = sc.read_h5ad(args.input, backed="r")
    print(f"[prep] raw: {adata_b.shape}", flush=True)
    obs = adata_b.obs
    c_pert = pick_col(obs.columns, ["perturbation", "compound_name", "product_name", "treatment", "drug"])
    c_line = pick_col(obs.columns, ["cell_line", "cell_id", "cell_type", "celltype"])
    c_dose = pick_col(obs.columns, ["dose_value", "dose_uM", "dose", "concentration"])
    c_time = next((c for c in ["time", "timepoint_hr", "time_value", "timepoint"] if c in obs.columns), None)
    print(f"[prep] cols: pert={c_pert} line={c_line} dose={c_dose} time={c_time}", flush=True)

    pr = obs[c_pert].astype(str).values
    ps = np.char.strip(pr.astype(str))
    cl = obs[c_line].astype(str).values
    dose = pd.to_numeric(obs[c_dose], errors="coerce").values
    isc = np.isin(np.char.lower(ps.astype(str)), CTRL_NAMES)
    dose = np.where(isc & np.isnan(dose), 0.0, dose)   # controls often carry no dose

    if args.cell_lines:
        lines = [c.strip() for c in args.cell_lines.split(",")]
    elif args.keep_all:
        lines = sorted(pd.unique(cl).tolist())
    else:
        lines = ["A549", "K562", "MCF7"]
    valid_line = np.isin(cl, lines)

    if args.keep_all:
        keep_pert = ps != "nan"                      # keep every real perturbation
    else:
        keep_names = {n.strip() for n in json.load(open(Path(args.annotation_dir) / "drug_order.json"))}
        keep_pert = np.isin(ps, list(keep_names))
    keep_mask = (keep_pert | isc) & valid_line & ~np.isnan(dose)
    if c_time is not None:
        t = pd.to_numeric(obs[c_time], errors="coerce").values
        use_t = 24.0 if np.nansum(t == 24.0) > 0 else float(pd.Series(t).mode().iloc[0])
        keep_mask &= (t == use_t)
        print(f"[prep] time filter -> {use_t}", flush=True)
    print(f"[prep] cells passing filter: {int(keep_mask.sum())}", flush=True)

    # ---- downsample per condition / control pool from OBS ----
    idx_all = np.where(keep_mask)[0]
    keep_idx = []
    for c in lines:
        ci = idx_all[isc[idx_all] & (cl[idx_all] == c)]
        if len(ci) > args.max_control_cells:
            ci = rng.choice(ci, args.max_control_cells, replace=False)
        keep_idx.extend(ci.tolist())
    dpos = idx_all[~isc[idx_all]]
    keydf = pd.DataFrame({"i": dpos, "k": [f"{pr[i]}_{cl[i]}_{float(dose[i])}" for i in dpos]})
    for _, grp in keydf.groupby("k"):
        ii = grp["i"].values
        if len(ii) > args.max_cells_per_cond:
            ii = rng.choice(ii, args.max_cells_per_cond, replace=False)
        keep_idx.extend(ii.tolist())
    keep_idx = np.array(sorted(keep_idx))
    print(f"[prep] downsampled to {len(keep_idx)} cells", flush=True)

    # ---- HVG selection on a subsample (full-gene) ----
    sub = keep_idx if len(keep_idx) <= args.hvg_subsample else np.sort(
        rng.choice(keep_idx, args.hvg_subsample, replace=False))
    print(f"[prep] HVG selection on {len(sub)} subsample cells ...", flush=True)
    Xsub, _ = load_rows_chunked(adata_b, sub, gene_idx=None, layer=args.counts_layer)
    import anndata as ad
    asub = ad.AnnData(X=Xsub, var=pd.DataFrame(index=adata_b.var_names.copy()))
    sc.pp.normalize_total(asub, target_sum=args.target_sum)
    sc.pp.log1p(asub)
    sc.pp.highly_variable_genes(asub, n_top_genes=args.n_hvgs, flavor="seurat")
    gene_mask = asub.var["highly_variable"].values
    gene_idx = np.where(gene_mask)[0]
    gene_names = adata_b.var_names[gene_idx].astype(str).tolist()
    del Xsub, asub
    print(f"[prep] selected {len(gene_idx)} HVGs (e.g. {gene_names[:5]})", flush=True)

    # ---- full load, HVG columns only, normalize with all-gene size factors ----
    print(f"[prep] loading {len(keep_idx)} cells x {len(gene_idx)} HVGs ...", flush=True)
    Xhvg, rowsum = load_rows_chunked(adata_b, keep_idx, gene_idx=gene_idx, layer=args.counts_layer)
    rowsum = np.clip(rowsum, 1.0, None)
    Xhvg = Xhvg / rowsum[:, None] * args.target_sum
    np.log1p(Xhvg, out=Xhvg)
    Xhvg = Xhvg.astype(np.float32)

    # ---- finalize obs ----
    ob = obs.iloc[keep_idx]
    prk = ob[c_pert].astype(str).values
    clk = ob[c_line].astype(str).values
    dsk = pd.to_numeric(ob[c_dose], errors="coerce").values
    isck = np.isin(np.char.lower(np.char.strip(prk.astype(str))), CTRL_NAMES)
    new_obs = pd.DataFrame({"perturbation": prk, "cell_line": clk,
                            "dose_value": dsk, "is_control": isck})
    for extra in ["target", "pathway", "pathway_level_1", "pathway_level_2"]:
        if extra in ob.columns:
            new_obs[extra] = ob[extra].astype(str).values

    import torch
    blob = {"X": Xhvg, "gene_names": gene_names,
            "cell_lines": sorted(pd.unique(clk).tolist()),
            "doses": sorted(pd.unique(dsk[~isck]).tolist()),
            "obs": new_obs.reset_index(drop=True),
            "meta": {"n_hvgs": args.n_hvgs, "target_sum": args.target_sum,
                     "source": "SrivatsanTrapnell2020_sciplex3"}}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    torch.save(blob, args.output)

    n_ctrl = {c: int((isck & (clk == c)).sum()) for c in blob["cell_lines"]}
    n_cond = new_obs[~isck].groupby(["perturbation", "cell_line", "dose_value"]).ngroups
    print("=" * 60, flush=True)
    print(f"[prep] cells={Xhvg.shape[0]} genes={Xhvg.shape[1]} lines={blob['cell_lines']} "
          f"doses={blob['doses']}", flush=True)
    print(f"[prep] control cells/line={n_ctrl}", flush=True)
    print(f"[prep] drug conditions={n_cond} "
          f"drugs={len(set(np.char.strip(prk.astype(str))[~isck]))}", flush=True)
    print(f"[prep] saved -> {args.output} ({Xhvg.nbytes/1e9:.2f} GB)", flush=True)


if __name__ == "__main__":
    main()
