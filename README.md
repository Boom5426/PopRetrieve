<div align="center">

# PopRetrieve

### Objective-aligned evaluation inflates distributional gains in single-cell drug retrieval

<p>
  <img alt="Python 3.10+" src="https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white">
  <a href="LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/license-MIT-2ea44f"></a>
  <a href="manuscript/PopRetrieve_manuscript.pdf"><img alt="Manuscript PDF" src="https://img.shields.io/badge/manuscript-PDF-B31B1B?logo=adobeacrobatreader&logoColor=white"></a>
  <a href="https://huggingface.co/datasets/Boom5426/PopRetrieve"><img alt="Hugging Face dataset" src="https://img.shields.io/badge/data-Hugging%20Face-FFD21E?logo=huggingface&logoColor=black"></a>
</p>

<p><strong>Population-level retrieval metrics for single-cell perturbation response.</strong></p>

</div>

<p align="center">
  <img src="assets/fig1_overview.png" alt="PopRetrieve overview" width="920">
</p>

## Overview

PopRetrieve studies whether cell-population structure improves drug retrieval beyond mean-based signatures. It provides population retrieval metrics, baseline methods, synthetic benchmarks and experiment drivers used in the accompanying manuscript.

The main comparison includes mean cosine, mean L2, energy distance, MMD, sliced Wasserstein and subpopulation-coverage scores. All scorers return similarities, so larger values rank candidates higher.

## Installation

```bash
git clone https://github.com/Boom5426/PopRetrieve.git
cd PopRetrieve

python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

The public API is available from `popretrieve.metrics`:

```python
from popretrieve.metrics import score_energy, score_mean_cosine

energy_score = score_energy(candidate_cells, query_cells, max_cells=500, seed=7)
mean_score = score_mean_cosine(candidate_cells, query_cells)
```

Energy and MMD use the unbiased U-statistic by default. Set `POPRETRIEVE_ESTIMATOR=v` only when reproducing explicitly labelled legacy V-statistic outputs.

## Data

The processed datasets are hosted at [Hugging Face](https://huggingface.co/datasets/Boom5426/PopRetrieve). Download them with Git LFS and point PopRetrieve to the clone:

```bash
git lfs install
git clone https://huggingface.co/datasets/Boom5426/PopRetrieve popretrieve-data
export DIDR_DATA_ROOT="$PWD/popretrieve-data"
```

The release contains the three core processed matrices and the directly used annotation tables. CIGS-derived optional benchmark tables are not redistributed because their source does not state a clear redistribution license. Dataset schemas, provenance, checksums and this boundary are documented in [`DATA.md`](DATA.md) and the Hugging Face data card.

## Reproducing the main results

Run commands from the repository root. Full experiments require the corresponding external datasets.

| Task | Command |
| --- | --- |
| Core retrieval experiments | `bash scripts/run_all_core.sh` |
| Baseline and predict-then-rank experiments | `bash scripts/run_all_baselines.sh` |
| Synthetic HIR-Bench | `bash scripts/run_hir_benchmark.sh` |

Set `QUICK=1` for reduced smoke runs. Quick outputs are not the manuscript results.

Selected checked summaries are provided under [`results/`](results/). The latest manuscript and Supplementary Information are available as [`PopRetrieve_manuscript.pdf`](manuscript/PopRetrieve_manuscript.pdf) and [`PopRetrieve_SI.pdf`](manuscript/PopRetrieve_SI.pdf).

## Repository layout

| Path | Contents |
| --- | --- |
| `src/` | Retrieval metrics, baselines, data loaders, benchmarks and experiment drivers |
| `configs/` | Dataset and experiment configurations |
| `scripts/` | Main reproduction entry points |
| `data/` | Location for external datasets |
| `results/` | Selected headline result summaries |
| `manuscript/` | Final manuscript and Supplementary Information PDFs |

See [`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md) for package details.

## Citation and license

Citation metadata is provided in [`CITATION.cff`](CITATION.cff). PopRetrieve is released under the MIT License. External datasets retain their original licenses.
