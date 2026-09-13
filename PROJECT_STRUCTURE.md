# Project structure

PopRetrieve has two public layers: an installable population-retrieval package and the reproducibility materials for the evaluation audit. The release follows the same separation used by the companion PertResolve repository: small, inspectable code and result artifacts live in Git, while large or restricted inputs are obtained separately.

```text
PopRetrieve/
├── src/                         # installable Python packages
│   ├── popretrieve/             # concise public namespace and API shims
│   ├── retrieval/               # metrics, rankers, evaluation, tasks, bootstrap
│   ├── baselines/               # mean/signature and predict-then-rank baselines
│   ├── benchmarks/              # HIR-Bench and oracle utilities
│   ├── data/                    # dataset containers and external-data loaders
│   ├── experiments/              # experiment and result-recomputation drivers
│   └── utils/                   # paths, IO, logging and random seeds
├── analysis/                    # claim-specific analyses and diagnostic controls
├── results/                     # checked summaries and figure-facing source tables
├── figures/                     # figure builders, style gates and panel source data
├── manuscript/                  # final PDFs, figure exports and figure-support tables
│   └── components/              # small figure-audit inputs used by Figure 1
├── oracle/                      # provenance-only original GID-Flow snapshot
├── scripts/                     # reproducibility entry points
├── examples/                    # repository-only runnable demonstration
├── tests/                       # numerical and repository-contract tests
├── configs/                     # dataset and experiment configuration files
├── docs/                        # findings and Phase-II audit records
├── DATA.md                     # external data, provenance and placement contract
├── pyproject.toml               # package metadata and optional dependencies
└── requirements.txt             # convenience install for older tooling
```

## Public package

The main public API is deliberately small:

```python
from popretrieve.metrics import (
    score_energy,
    score_mean_cosine,
    score_mean_l2,
    score_mmd_rbf,
    score_sliced_wasserstein,
)
```

The `retrieval.*` modules are the implementation surface used by the paper scripts. They remain top-level packages so existing experiment commands and tests keep their original imports. `popretrieve.*` provides a stable repository-facing entry point without duplicating the numerical implementation.

## Reproducibility boundary

The public checkout contains checked summaries and the per-query file required by the partial-observation analysis. Large raw dumps, model checkpoints, local logs, backups and GDSC workbooks are excluded. Every data-dependent loader accepts an explicit path or uses `DIDR_DATA_ROOT`; no machine-specific absolute path is required.

The final manuscript is distributed as a PDF artifact, matching the companion project's public-release convention. Figure sources are retained because the six main figures have explicit build and typography checks; LaTeX build intermediates and superseded manuscript drafts are not part of this public staging directory.
