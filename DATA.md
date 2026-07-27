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

## Three further inputs, which this file used to omit

Added 2026-07-27. Without them, two of README's own "Reproduce the numbers" commands cannot run
from a fresh clone, and a reader could not tell that anything was missing.

- **ZhaoSims2021 patient glioblastoma**: the natural-heterogeneity benchmark, and the source of
  every two-gate number measured in real tissue (main-text Fig. 5d,e,f). Loader
  `src/data/load_zhao_gbm.py` reads `data/raw/zhao2021/ZhaoSims2021.h5ad` and caches
  `data/processed/zhao_gbm.npz`. Compartment labels are assigned by validated marker scoring inside
  that loader, which refuses to proceed if its validation check fails. Consumers:
  `analysis/natural/zhao_two_gates.py`, `zhao_threshold_sensitivity.py`, `zhao_premise_disjoint.py`.

  ```
  data/raw/zhao2021/ZhaoSims2021.h5ad
  ```

- **GDSC2 dose-response workbook**: the Class-C functional oracle (main-text Fig. 4h,i). Not
  redistributable here; download the release from the GDSC portal and place it at the one path both
  consumers read:

  ```
  results/upgrade/GDSC2_fitted_dose_response.xlsx      # and GDSC1_... for the drug match
  ```

  The verified release is `GDSC2_fitted_dose_response_27Oct23.xlsx` (release 8.5); rename it to the
  path above. `analysis/class_c/class_c_functional_oracle.py` raises with the download instructions
  if it is absent, and states which release its numbers were computed on.

- **Frangieh surface-protein modality**: the two protein oracles (main-text Fig. 4, oracle-shape
  result) use the CITE-seq protein matrix, not just the RNA tensor listed above. It is joined to the
  RNA matrix **by cell barcode**, which is why the protein analyses report 218,331 cells against the
  218,023 of the expression tensor: the two matrices as distributed differ in row count, and a
  positional concatenation silently pairs each cell's protein response with a different cell's RNA
  (Methods).

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
