# PopRetrieve

**Objective-aligned evaluation inflates distributional gains in single-cell drug retrieval.**

<p align="center">
  <img alt="tests" src="https://img.shields.io/badge/tests-99%20passed-brightgreen">
  <img alt="reproducibility" src="https://img.shields.io/badge/consistency%20recheck-35%2F35-brightgreen">
  <img alt="corrections" src="https://img.shields.io/badge/corrections-CORRECTIONS.md-orange">
  <img alt="python" src="https://img.shields.io/badge/python-3.11-blue">
  <img alt="license" src="https://img.shields.io/badge/license-MIT-blue">
  <img alt="status" src="https://img.shields.io/badge/status-research%20code-orange">
</p>

Code, data recipes and manuscript sources for a study of **how distribution-aware single-cell drug
retrieval is evaluated**. Given a query cell population and a library of candidate response
populations, a distributional score picks `argmin_d D(P_d, Q)` in distribution space rather than
matching mean signatures. This repository holds one such family of scores fixed, holds the queries
and the candidate rankings fixed, and **changes only the criterion that grades them**.

The result is the contribution. It is not a better drug-ranking method: the retrieval scores are
the *instrument*.

| when the rankings are graded by | the distributional score |
|---|---|
| its own distributional objective | **far ahead**: Hit@1 0.837 vs 0.388 for the mean-signature incumbent |
| mechanism-of-action recovery | **gone**: MoA-nDCG gain −0.037, and 41% of queries get *worse* |
| an external functional oracle (GDSC) | **wins**, ρ +0.276 vs +0.083, but a scalar comparing no distributions reaches +0.232 |
| the same proteins, same cells, scored as a *mean* | **loses**, +0.146 vs +0.242 |

Two external, blind, independent criteria built from identical material hand victory to opposite
methods, purely by their own statistical form.

- **Full results, with the counterexamples and the retraction notes:** [`docs/FINDINGS.md`](docs/FINDINGS.md)
- **Every number this project has revised or withdrawn:** [`CORRECTIONS.md`](CORRECTIONS.md)
- **The paper:** `manuscript/latex/PopRetrieve_manuscript.tex`

---

## Installation

```bash
git clone https://github.com/Boom5426/PopRetrieve.git && cd PopRetrieve
python -m venv .venv && source .venv/bin/activate      # Python 3.11
pip install -r requirements.txt
```

CUDA is optional; it accelerates the energy distance and nothing else.

Verify the install without any data:

```bash
python tests/run_tests.py        # 99 tests, no pytest required; `pytest tests/` also works
```

## Data

The processed single-cell tensors are large and **not tracked in git**. Put them under
`data/processed/`, or point `DIDR_DATA_ROOT` at wherever they already live:

```bash
export DIDR_DATA_ROOT=/abs/path/to/data
```

```
data/
  processed/
    sciplex3_all.pt      # SciPlex3: 276k cells x 2000 HVG, 188 drugs x 3 lines
    cd34_all.pt          # CD34+ HSPCs: 34k cells, 36 drugs, 4 natural lineages
    frangieh_hvg.npz     # Frangieh Perturb-CITE-seq: 218k cells, 248 KOs
  annotation/            # drug_order.json, drug_morgan_ecfp4.npy, moa_mask.npy, ...
```

[`DATA.md`](DATA.md) gives the source, accession and preprocessing command for each file. The test
suite runs without them; the experiments do not.

## Quickstart

Every long-running script honours `QUICK=1`, which cuts the seed counts and grid resolution. Use it
to confirm the pipeline works end to end before committing to a full run:

```bash
QUICK=1 bash scripts/run_all_core.sh          # core retrieval experiments, reduced seeds
QUICK=1 bash scripts/run_hir_benchmark.sh     # synthetic benchmark, ~40 s
```

`QUICK` results are **not** the paper's numbers and write to the same directories, so treat a quick
pass as a smoke test only. `run_hir_benchmark.sh` refuses to overwrite the tracked full results
unless you pass `ALLOW_QUICK_OVERWRITE=1`.

Override the interpreter anywhere with `PY=/path/to/python`.

## Reproducing the paper

Run these in order. Each writes to `results/` and prints where.

| # | what it reproduces | command | writes |
|---|---|---|---|
| 1 | core retrieval (exp01–07) and the consistency re-check | `bash scripts/run_all_core.sh` | `results/all_existing_results_recomputed.csv` |
| 2 | signature baselines, the Hit@1 table, predict-then-rank (exp08–11) | `bash scripts/run_all_baselines.sh` | `results/baseline_comparison_master.csv` |
| 3 | HIR-Bench, the synthetic benchmark (~60 min full) | `bash scripts/run_hir_benchmark.sh` | `results/exp11_hir_benchmark/` |
| 4 | gate diagnosis and true-divergence stratification (exp12, 16, 17) | `bash scripts/run_exp16_17.sh` | `results/exp16_17_verdict.md` |

Then the analyses that carry the individual claims:

| what it reproduces | command | writes |
|---|---|---|
| the external GDSC functional oracle, both constructions | `python analysis/class_c/class_c_functional_oracle.py` | `results/upgrade/class_c_functional_oracle.csv` |
| the oracle-shape reversal (the sharpest result) | `python analysis/class_c/oracle_shape_test.py` | `results/upgrade/oracle_shape_test.{csv,json}` |
| the surface-protein oracle | `python analysis/class_c/class_c_protein_oracle.py` | `results/upgrade/` |
| the two conditions in patient glioblastoma | `python analysis/natural/zhao_two_gates.py` | `results/zhao_gbm/zhao_two_gates.json` |
| the same premise on disjoint compartments | `python analysis/natural/zhao_premise_disjoint.py` | `results/zhao_gbm/` |
| every Tahoe-100M number quoted in the paper | `python analysis/tahoe_pilot/tahoe_summary_numbers.py` | `results/tahoe_pilot/manuscript_numbers.json` |
| the four-probe diagnostic verdicts | `PYTHONPATH=src python analysis/diagnostics/protocol_validation.py` | `results/upgrade/protocol_validation.json` |

Note what step 1's consistency re-check is and is not: `recompute_all.py` re-reads the cached
experiment CSVs against the constants in `src/experiments/common.py` and confirms 35/35 headline
numbers. It **runs no experiment**. The experiments are the four scripts above it.

### Figures and the manuscript

```bash
bash scripts/run_all_figures.sh                 # Figs 1-6 + Extended Data 1-7 -> manuscript/latex/figures/
cd manuscript/latex && make && make si          # both PDFs
```

Every headline number in the manuscript is quoted through a LaTeX macro whose value is produced by
one of the scripts above, so a doubted number is rechecked by re-running that script rather than by
trusting the text.

## Using the diagnostic on your own method

The reusable part of this repository is
[`analysis/diagnostics/dart_diagnostic.py`](analysis/diagnostics/dart_diagnostic.py): four probes
that separate a **real** null result from an **implementation artifact**. It depends only on numpy,
scipy and scikit-learn, and operates on cell x gene matrices already in memory.

```python
from dart_diagnostic import (
    translation_invariance_probe,   # is raw-vs-delta an unfair comparison?
    subsampling_power_probe,        # is the null just low power at this cell budget?
    metric_blindspot_probe,         # does the metric measure what it claims?
    magnitude_confound_probe,       # is the positive result just response magnitude?
)
```

Each returns a verdict dict. `protocol_validation.py` runs all four on this project's data and
checks they reproduce the reported verdicts, which doubles as a worked example.

If you take nothing else from here, take the four controls in
[`docs/FINDINGS.md`](docs/FINDINGS.md#the-four-controls-if-you-read-nothing-else). Each of them
caught an error of ours.

## Repository layout

| path | what is in it |
|---|---|
| `src/` | retrieval scores, baselines, data loaders, the HIR-Bench generator, the experiment drivers |
| `oracle/` | the mixture-construction and evaluation scripts behind the controlled experiments |
| `analysis/` | the analyses that carry the paper's claims, one directory per question |
| `results/` | per-experiment summary tables; the large per-query dumps are gitignored |
| `figures/` | one directory per figure, each panel a standalone script, plus `build_all.py` |
| `manuscript/latex/` | manuscript and Supplementary Information sources, and their Makefile |
| `scripts/` | the run-everything shell entry points used above |
| `tests/` | 99 tests, including the ones that pin the algebraic claims |
| `docs/FINDINGS.md` | the detailed results |
| `CORRECTIONS.md` | every number this project has retracted or revised, and why |

Inside `analysis/`, one directory per question:

| directory | question it answers |
|---|---|
| `class_c/` | does the gain survive an external functional oracle, and is it distributional? |
| `natural/` | do the conditions hold in patient tissue rather than in mixtures we built? |
| `tahoe_pilot/` | do they hold at scale in unconstructed, non-tissue material? |
| `identifiability/` | is the subpopulation structure recoverable at all? |
| `predictors/` | do generated candidate populations carry differential response? |
| `hir_bench/` | is retrieval failure predictable, and from features a method can actually see? |
| `audit/` | the field-level evaluation audit behind Supplementary Table 2 |
| `diagnostics/` | the four-probe protocol as a runnable check |

## Reproducibility notes

- **`CORRECTIONS.md` is part of the deliverable**, not an appendix. Forty-five entries covering
  thirty-nine distinct corrections, each recording what a number was, what it is now, and why it
  changed. Several retract mechanisms the earlier drafts asserted.
- **Algebraic claims are pinned by tests, not by runs.** An additive predictor induces exactly zero
  response divergence; that is asserted to `1.000000` in the test suite rather than measured.
- **Numbers quoted in more than one place are LaTeX macros defined once**, so the text, a figure
  caption and the Methods cannot drift apart.
- **Figures rebuild from committed code.** `figures/build_all.py` fails the build if any rendered
  text is authored below the 5 pt floor. That gate reads nominal point sizes and knows nothing
  about the manuscript's column width, so a figure authored wider than the text block is scaled
  down by LaTeX and can print below 5 pt while the gate still reports CLEAN. The five main figures
  are authored at the printed width, so their scale factor is 1.00; the Extended Data figures have
  their own driver, `figures/build_ed.py`, which enforces the same width.
- **A missing input raises**, rather than being replaced by a plausible default. That rule exists
  because it was once broken; see `CORRECTIONS.md`.

## A note on the name

This project was called **DART** while it was still written as a method paper, and is now
**PopRetrieve**, which is not an acronym. The rename follows a repositioning: what is released is
an evaluation framework, not a proposed drug-ranking method.

**Identifiers inside `results/` and `src/` still carry the `DART_` prefix, and that is deliberate.**
Method keys such as `DART_energy` and `DART_coverage_worst`, and the gate's regime label `no_DART`,
are the keys under which every published number was computed and stored. Renaming them would mean
regenerating every results table and breaking the correspondence between the numbers in the paper
and the files you can check them against. The historical drafts under `manuscript/_archive/` are
left alone for the same reason.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). In short: the test suite must pass, every reported number
must stay reproducible, and negative results stay in view.

## Citing

The manuscript is in preparation. Until it is posted, cite this repository and the commit you used
(see [`CITATION.cff`](CITATION.cff)). The dataset citations are in the manuscript's Data
availability section and in [`DATA.md`](DATA.md).

## License

MIT, see [`LICENSE`](LICENSE). The datasets are covered by their own licences and are not
redistributed here.
