# Data

Large single-cell datasets are not stored in this repository. By default, loaders read from `data/`; set `DIDR_DATA_ROOT` to use another location.

```bash
export DIDR_DATA_ROOT=/absolute/path/to/data
```

## Expected layout

```text
data/
├── processed/
│   ├── sciplex3_all.pt
│   ├── cd34_all.pt
│   └── frangieh_hvg.npz
├── annotation/
│   ├── drug_annotation_master.csv
│   ├── drug_target_prior.parquet
│   └── drugcentral_target_annotations.parquet
└── benchmarks/
    ├── pdgrapher_closed_loop_benchmark.parquet
    └── response_rescue_labels_CIGS.parquet
```

## Sources

- **SciPlex3:** Srivatsan and Trapnell (2020), processed to 2,000 highly variable genes with A549, K562 and MCF7 controls.
- **CD34+ HSPCs:** GSE306429, using the raw-count layer before normalization.
- **Frangieh Perturb-CITE-seq:** Frangieh and Izar (2021), processed to 2,000 highly variable genes.
- **PDGrapher/CIGS tables:** optional precomputed benchmark inputs used by `src/experiments/exp10_pdgrapher_comparison.py`.

The core loaders are in `src/data/`. Missing inputs produce an explicit file-not-found error; no machine-specific path is embedded in the public code.
