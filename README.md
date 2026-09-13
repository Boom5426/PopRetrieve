<div align="center">

# PopRetrieve

### Objective-aligned evaluation inflates distributional gains in single-cell drug retrieval

<p>
  <a href="https://github.com/Boom5426/PopRetrieve/actions/workflows/tests.yml"><img alt="Tests" src="https://github.com/Boom5426/PopRetrieve/actions/workflows/tests.yml/badge.svg"></a>
  <img alt="Python 3.10+" src="https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white">
  <a href="LICENSE"><img alt="MIT License" src="https://img.shields.io/badge/license-MIT-2ea44f"></a>
  <a href="manuscript/PopRetrieve_manuscript.pdf"><img alt="Manuscript PDF" src="https://img.shields.io/badge/manuscript-PDF-B31B1B?logo=adobeacrobatreader&logoColor=white"></a>
</p>

<p>
  <strong>Audit whether single-cell population information improves drug retrieval for the decision that the evaluation is meant to support.</strong>
</p>

</div>

<p align="center">
  <img src="assets/fig1_overview.png" alt="PopRetrieve overview figure" width="920">
</p>

<p align="center"><em>Figure 1. PopRetrieve separates direction, response magnitude and full population structure before asking which information changes a retrieval decision. <a href="manuscript/figures/fig1.pdf">Open the vector PDF.</a></em></p>

> The same retrieval ranking can look far ahead under an objective-aligned distributional score and disappear under a more independent judge. PopRetrieve makes that dependence measurable.

## What is PopRetrieve?

PopRetrieve is a research codebase for population-to-population drug retrieval and for auditing how that retrieval is evaluated. Given a query cell population (Q) and candidate response populations ({P_d}), a population score ranks candidates using information beyond a single mean signature. The repository compares those rankings with mean-cosine, magnitude-aware mean-L2, energy, MMD, sliced-Wasserstein and subpopulation-coverage scores.

The study is an evaluation framework, not a validated therapeutic recommender. It keeps the query construction and candidate rankings fixed while changing the criterion used to grade them. The release includes the numerical kernels, baseline predictors, synthetic HIR-Bench, analysis scripts, checked result tables, final manuscript PDFs and the latest figure files.

### Main findings

| Question | Release-level answer |
| --- | --- |
| Does a population score improve response matching when candidate responses are observed? | Yes, but most of the gain over direction-only matching is recovered by a mean-based magnitude control. |
| Does that gain transfer to mechanism recovery and external functional criteria? | It weakens, disappears or changes direction as the judge becomes more independent. |
| Does forward prediction preserve the advantage? | Not for the additive predictors tested here; the oracle advantage can reverse after prediction. |
| Is this a therapeutic recommendation system? | No. The distributional retrieval scores are the instrument used to audit objective–utility mismatch. |

## Quick start

The public package and synthetic benchmark do not require the large single-cell tensors.

```bash
git clone https://github.com/Boom5426/PopRetrieve.git
cd PopRetrieve

python -m venv .venv
source .venv/bin/activate                 # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"

# 116 repository tests
pytest -q

# Small deterministic population-retrieval example
python examples/run_retrieval_demo.py
```

The core public namespace is `popretrieve.metrics`; the lower-level modules remain available under `retrieval`, `baselines`, `benchmarks`, `data` and `utils` for compatibility with the experiment scripts.

```python
from popretrieve.metrics import score_energy, score_mean_cosine

energy_score = score_energy(candidate_cells, query_cells, max_cells=500, seed=7)
mean_score = score_mean_cosine(candidate_cells, query_cells)
```

All retrieval scorers return similarities, so larger values rank candidates higher. The energy and MMD wrappers use the unbiased U-statistic by default. Set `POPRETRIEVE_ESTIMATOR=v` only when reproducing the explicitly labelled legacy V-statistic outputs.

## Data

Large processed tensors are not tracked in Git. Put them under `data/` or point `DIDR_DATA_ROOT` to an existing data directory:

```bash
export DIDR_DATA_ROOT=/absolute/path/to/data
```

The expected inputs and provenance are documented in [`DATA.md`](DATA.md). They include SciPlex3, CD34+ HSPCs, Frangieh Perturb-CITE-seq, ZhaoSims2021 glioblastoma and the optional Tahoe-100M plate. GDSC dose-response workbooks are external inputs and are deliberately not redistributed.

The tests and `examples/run_retrieval_demo.py` run without these datasets. The data-dependent experiments do not.

## Reproduce the study

Run the commands from a clean checkout or write outputs to a scratch copy of `results/`; long-running scripts may regenerate result files.

| What | Command | Main output |
| --- | --- | --- |
| Core retrieval experiments | `bash scripts/run_all_core.sh` | `results/all_existing_results_recomputed.csv` |
| Signature baselines and predict-then-rank | `bash scripts/run_all_baselines.sh` | `results/exp08_signature_baselines/`, `results/exp09_predict_then_rank/` |
| Synthetic HIR-Bench | `bash scripts/run_hir_benchmark.sh` | `results/exp11_hir_benchmark/` |
| Phase-II gate and transition analyses | `bash scripts/run_exp16_17.sh` | `results/exp16_17_verdict.md`, `results/phase2_transition/` |
| Four-probe diagnostic | `PYTHONPATH=src python analysis/diagnostics/protocol_validation.py` | `results/upgrade/protocol_validation.json` |

`QUICK=1` is supported by the long-running drivers as a smoke test. Quick outputs are not paper numbers and must not replace the checked result tables.

The repository's detailed interpretation is in [`docs/FINDINGS.md`](docs/FINDINGS.md). [`CORRECTIONS.md`](CORRECTIONS.md) records revised and retracted numbers; read it before quoting any older analysis note.

## Figures and manuscript

The final manuscript and Supplementary Information are available as [`manuscript/PopRetrieve_manuscript.pdf`](manuscript/PopRetrieve_manuscript.pdf) and [`manuscript/PopRetrieve_SI.pdf`](manuscript/PopRetrieve_SI.pdf). The latest final figure composites and panel exports are in [`manuscript/figures/`](manuscript/figures/).

Figure-generation sources are in [`figures/`](figures/). To rebuild the six main figure PDFs and synchronise them to the public manuscript-figure directory:

```bash
python figures/build_all.py                 # typography/build checks
python figures/build_all.py --write         # export and update manuscript/figures/figN.pdf
python figures/check_overlaps.py 1          # optional panel-overlap check
```

The figure sources read checked result tables and per-panel source data; missing inputs raise instead of being replaced by defaults. The large atlas inputs remain external.

## Repository map

| Path | Contents |
| --- | --- |
| `src/` | Installable retrieval kernels, rankers, data abstractions, predictors, benchmark generators and experiment drivers |
| `analysis/` | Claim-specific analyses, diagnostics, natural-tissue checks and estimator audits |
| `results/` | Reproducibility tables and checked summaries; heavy raw/intermediate dumps are excluded |
| `figures/` | Figure builders, typography gates and per-panel source data |
| `manuscript/` | Final manuscript/SI PDFs and latest final figure exports |
| `oracle/` | Read-only provenance snapshot of the original GID-Flow implementation |
| `scripts/` | Reproduction entry points |
| `tests/` | Repository and numerical-contract tests |
| `docs/` | Findings and Phase-II protocol/audit records |

See [`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md) for the release topology and the boundary between public artifacts and external inputs.

## Citation and license

Please cite the repository and the commit used; metadata is in [`CITATION.cff`](CITATION.cff). PopRetrieve is released under the MIT License. Datasets and external workbooks retain their own licenses and are not redistributed here.
