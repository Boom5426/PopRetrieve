# Project structure

PopRetrieve is distributed as a compact installable package. Large datasets and regenerable intermediate outputs are kept outside Git.

```text
PopRetrieve/
├── src/
│   ├── popretrieve/       # public API
│   ├── retrieval/         # metrics, rankers and evaluation utilities
│   ├── baselines/         # mean/signature and prediction baselines
│   ├── benchmarks/        # synthetic benchmark utilities
│   ├── data/              # dataset loaders and population containers
│   ├── experiments/       # experiment drivers
│   └── utils/             # IO, logging and random seeds
├── configs/               # experiment configurations
├── scripts/               # main reproduction commands
├── data/                  # external data location
├── results/               # selected checked summaries
├── manuscript/            # final manuscript and SI PDFs
├── README.md
├── DATA.md
└── pyproject.toml
```

The stable public imports are exposed through `popretrieve.*`. Existing experiment drivers continue to use the lower-level `retrieval`, `baselines`, `benchmarks`, `data` and `utils` packages.

The repository excludes raw single-cell tensors, model checkpoints, local logs, large per-query outputs and superseded manuscript material. Data-dependent commands use an explicit input path or `DIDR_DATA_ROOT`.
