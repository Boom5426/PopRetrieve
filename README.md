<div align="center">

# When do single-cell response distributions improve drug retrieval?

### PopRetrieve: Population-response retrieval for single-cell perturbation data

<p>
  <img alt="Single-cell" src="https://img.shields.io/badge/scope-single--cell-7B61FF?logo=cell&logoColor=white">
  <img alt="Retrieval" src="https://img.shields.io/badge/task-drug%20retrieval-0F9D8A?logo=target&logoColor=white">
  <img alt="Python 3.10+" src="https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white">
  <a href="LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/license-MIT-2ea44f"></a>
  <a href="manuscript/PopRetrieve_manuscript.pdf"><img alt="Manuscript PDF" src="https://img.shields.io/badge/manuscript-PDF-B31B1B?logo=adobeacrobatreader&logoColor=white"></a>
  <a href="manuscript/PopRetrieve_SI.pdf"><img alt="Supplementary Information PDF" src="https://img.shields.io/badge/supplement-PDF-B31B1B?logo=adobeacrobatreader&logoColor=white"></a>
  <a href="https://huggingface.co/datasets/Boom5426/PopRetrieve"><img alt="Hugging Face dataset" src="https://img.shields.io/badge/data-Hugging%20Face-FFD21E?logo=huggingface&logoColor=black"></a>
</p>

<p><strong>A framework for testing when population response structure changes intervention ranking.</strong></p>

<p>
  <a href="https://boom5426.github.io/PopRetrieve/">🌐 Project page</a> ·
  <a href="#-installation">🚀 Install</a> ·
  <a href="#-data">🤗 Data</a> ·
  <a href="#-reproducing-released-experiments">🧪 Reproduce</a> ·
  <a href="manuscript/PopRetrieve_manuscript.pdf">📄 Paper</a> ·
  <a href="manuscript/PopRetrieve_SI.pdf">📎 Supplement</a> ·
  <a href="CITATION.cff">📚 Cite</a>
</p>

</div>

<p align="center">
  <img src="assets/fig1_overview.png" alt="PopRetrieve overview" width="920">
</p>

## ✨ Overview

PopRetrieve asks when full single-cell response distributions improve drug ranking beyond average responses. This repository provides retrieval metrics, mean baselines, controlled benchmarks and selected experiment drivers for the accompanying [manuscript](manuscript/PopRetrieve_manuscript.pdf) and [Supplementary Information](manuscript/PopRetrieve_SI.pdf).

The central comparison is a representation ladder: direction-only mean cosine, magnitude-aware mean L2 and population-level scores (energy distance, MMD, sliced Wasserstein and subpopulation coverage). The paper separates gains due to response magnitude from gains that require the full cellular response population.

In the manuscript, a magnitude-aware mean recovers most of the apparent gain over directional mean matching. The smaller contribution from cell-to-cell structure weakens under biological and functional evaluation. With observed responses in the target context, population retrieval adds a small gain; the predictors evaluated in the paper do not preserve that gain in a new context. The same held-out protein measurements can favour different RNA rankings depending on whether the evaluator uses mean or population responses.

<table>
  <tr>
    <td align="center" width="33%"><strong>📐 Scoring ladder</strong><br><sub>Direction, magnitude and population-response retrieval.</sub></td>
    <td align="center" width="33%"><strong>🧬 Evaluation ladder</strong><br><sub>Response matching, biological and functional evaluation, then prediction.</sub></td>
    <td align="center" width="33%"><strong>🔁 Reproducibility</strong><br><sub>Fixed configs, scripts, checked output snapshots and current PDFs.</sub></td>
  </tr>
</table>

## 🚀 Installation

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

## 🤗 Data

The processed datasets are hosted at [Hugging Face](https://huggingface.co/datasets/Boom5426/PopRetrieve). Download them with Git LFS and point PopRetrieve to the clone:

```bash
git lfs install
git clone https://huggingface.co/datasets/Boom5426/PopRetrieve popretrieve-data
export DIDR_DATA_ROOT="$PWD/popretrieve-data"
```

The release contains three core processed matrices and their annotation tables. See [`DATA.md`](DATA.md) for dataset details and the additional ZhaoSims2021, Tahoe-100M, GDSC2 and optional CIGS inputs.

## 🧪 Reproducing released experiments

Run commands from the repository root after downloading the required datasets. The scripts write into `results/`; use a separate checkout to preserve the included snapshots.

| Task | Command |
| --- | --- |
| 🧬 Core retrieval experiments | `bash scripts/run_all_core.sh` |
| 📊 Baseline and predict-then-rank experiments (requires optional CIGS inputs) | `bash scripts/run_all_baselines.sh` |
| 🧪 Synthetic HIR-Bench | `bash scripts/run_hir_benchmark.sh` |

Set `QUICK=1` for reduced smoke runs. Quick outputs are not the manuscript results.

Selected output snapshots and the scope of the released experiments are documented in [`results/README.md`](results/README.md).

## 🗂️ Repository layout

| Path | Contents |
| --- | --- |
| `src/` | Retrieval metrics, baselines, data loaders, benchmarks and experiment drivers |
| `configs/` | Dataset and experiment configurations |
| `scripts/` | Main reproduction entry points |
| `docs/` | Project website for GitHub Pages |
| `data/` | Location for external datasets |
| `results/` | Checked output snapshots and compact result summaries |
| `manuscript/` | Current manuscript and Supplementary Information PDFs |

Within `src/`, `popretrieve/` exposes the public API; `retrieval/`, `baselines/`, `benchmarks/`, `data/` and `experiments/` contain the implementations.

## 📚 Citation and license

The manuscript authors are listed in [`CITATION.cff`](CITATION.cff). PopRetrieve code is released under the MIT License. External datasets retain their original licenses.
