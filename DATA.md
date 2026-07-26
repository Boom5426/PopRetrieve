# Data

The processed single-cell tensors are **large and not tracked in git**. Place them
under `data/processed/` (or point `DIDR_DATA_ROOT` at wherever they live), then the
experiments in `scripts/run_all_core.sh` find them automatically.

```
data/
  processed/
    sciplex3_all.pt        # SciPlex3: 276k cells x 2000 HVG, 188 drugs x 3 lines (exp01/02/03/06)
    cd34_all.pt            # CD34+ HSPCs: 34k cells, 36 drugs, 4 natural lineages   (exp04)
    frangieh_hvg.npz       # Frangieh melanoma Perturb-CITE-seq: 218k cells, 248 KOs (exp05)
  annotation/              # drug_order.json, drug_morgan_ecfp4.npy, moa_mask.npy, ... (used by the oracle)
```

Point elsewhere without moving files:

```bash
export DIDR_DATA_ROOT=/abs/path/to/data
```

## Provenance / how the tensors were built

- **SciPlex3** — Srivatsan & Trapnell 2020 (`SrivatsanTrapnell2020_sciplex3.h5ad`), 2000
  HVG, log-normalized; three cell lines A549/K562/MCF7 with real DMSO controls.
- **CD34+** — GSE306429 (ILD1-011 CD34+); `layers['counts']` used as the raw counts
  layer (the demuxed `.X` is already log-normalized — do not double-normalize).
- **Frangieh** — scPerturb Zenodo `FrangiehIzar2021_RNA.h5ad`, 2000 HVG; immune
  conditions Control / IFNγ / Co-culture as the subpopulation axis.

The building scripts (`oracle/scripts/prepare_sciplex3.py`, `prepare_frangieh.py`) are
kept in `oracle/` for provenance. The self-contained loaders in `src/data/` read the
already-processed tensors directly.

> Note: `data/` on the original dev machine is a symlink to a shared data tree; that
> symlink is git-ignored. Clone users create their own `data/processed/`.

## Tahoe-100M (the unconstructed-heterogeneity check)

Used only by `analysis/tahoe_pilot/`, and only **plate 3**. No other result in this repository
depends on it, and no retrieval is run on it.

```
data/
  tahoe/
    plate3_filt_Vevo_Tahoe100M_WServicesFrom_ParseGigalab_preprocessed_cpu.h5ad
    metadata/sample_metadata.parquet          # optional, for the dose and plate audit
```

The preprocessed plate is 4,158,278 cells x 2,304 highly variable genes in log1p space, a complete
50 cell line x 93 compound grid at one dose per compound, with a `DMSO_TF` vehicle arm in every
line and a cell-cycle call on every cell. The scripts read it as it ships and refit nothing.

- **Source** — Zhang et al. 2025, *Tahoe-100M: a giga-scale single-cell perturbation atlas*,
  bioRxiv [10.1101/2025.02.20.639398](https://doi.org/10.1101/2025.02.20.639398). Released under
  **CC0** by Vevo Therapeutics and the Arc Institute; distributed through the Arc Virtual Cell
  Atlas and Hugging Face (`tahoebio/Tahoe-100M`).
- **Why this plate** — it is one of the smaller ones and still a complete grid, so it carries the
  full cell-line axis without the other thirteen plates. Using more plates would add compounds, not
  contexts.
