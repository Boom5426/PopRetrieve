# Data

Processed datasets are published at [Boom5426/PopRetrieve](https://huggingface.co/datasets/Boom5426/PopRetrieve). They are not duplicated in the GitHub repository.

```bash
git lfs install
git clone https://huggingface.co/datasets/Boom5426/PopRetrieve popretrieve-data
export DIDR_DATA_ROOT="$PWD/popretrieve-data"
```

By default, loaders otherwise read from `data/`. `DIDR_DATA_ROOT` may point to any directory with the layout below.

## Released layout

```text
popretrieve-data/
├── processed/
│   ├── sciplex3_all.pt
│   ├── cd34_all.pt
│   └── frangieh_hvg.npz
└── annotation/
    ├── drug_annotation_master.csv
    └── drugcentral_target_annotations.parquet
```

## Sources

- **SciPlex3:** Srivatsan et al. (2020), [GSE139944](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE139944), processed to 2,000 highly variable genes with A549, K562 and MCF7 controls.
- **CD34+ HSPCs:** [GSE306429](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE306429), using the raw-count layer before normalization.
- **Frangieh Perturb-CITE-seq:** Frangieh et al. (2021), [SCP1064](https://singlecell.broadinstitute.org/single_cell/study/SCP1064), processed to 2,000 highly variable genes.
- **Annotations:** SciPlex3 annotations enriched from ChEMBL, PubChem and DrugCentral.

SciPlex3 and Frangieh use the harmonized [scPerturb release](https://doi.org/10.5281/zenodo.13350497). Full schemas, transformations, SHA-256 checksums and source-specific license notices are in the Hugging Face data card.

## Optional CIGS benchmark

`src/experiments/exp10_pdgrapher_comparison.py` additionally expects:

```text
data/
├── annotation/drug_target_prior.parquet
└── benchmarks/
    ├── pdgrapher_closed_loop_benchmark.parquet
    └── response_rescue_labels_CIGS.parquet
```

These three CIGS-derived tables are intentionally not redistributed. The [CIGS website](https://cigs.iomicscloud.com/) provides its source data for download but does not currently state a clear redistribution license. Experiment 10 therefore remains optional and requires locally obtained inputs.

The core loaders are in `src/data/`. Missing inputs produce an explicit file-not-found error; no machine-specific path is embedded in the public code. External datasets retain their original terms; the repository's MIT license applies only to PopRetrieve code.
