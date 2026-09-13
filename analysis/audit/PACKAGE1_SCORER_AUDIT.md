# PopRetrieve Package 1: scorer-definition audit

Status: implementation audit and targeted raw-vs-control-referenced sensitivity
completed. The full results are in
`analysis/audit/PACKAGE1_CONTROL_REFERENCE_SENSITIVITY.md` and the corresponding
machine-readable tables under `results/audit/package1_*`.

## Canonical contract

| scorer | input | matched-control reference | estimator/default |
|---|---|---|---|
| mean cosine | cell matrices; each matrix is reduced to its cell mean | subtract `control_P` from the candidate mean and `control_Q` from the query mean, when supplied; the two controls may differ | cosine similarity, no U/V statistic |
| mean L2 | cell matrices; each matrix is reduced to its cell mean | same separate subtraction as mean cosine; manuscript-facing calls now pass the candidate and query controls | negative Euclidean distance, no U/V statistic |
| global energy | raw normalized-expression cell matrices | no subtraction in `score_energy` or any manuscript ranker | U by default; `estimator='v'` is legacy-only |
| RBF MMD | raw normalized-expression cell matrices; pooled median-heuristic bandwidth and scales 0.25/1/4 | no subtraction | U by default; `estimator='v'` is legacy-only |
| sliced Wasserstein | raw normalized-expression cell matrices; 128 projections in the unified scorer | no subtraction | no U/V pair |
| coverage | cell matrices split into query-defined components, then energy/MMD/SW per component | no subtraction in the coverage path | U for energy/MMD base distances by default |

The phrase “control-referenced population distance” therefore denotes a
sensitivity arm (`P-control_P`, `Q-control_Q`), not the current manuscript
population implementation. It is translation-invariant only when the same
control is subtracted from both populations; candidate-specific controls can
change the referenced population comparison.

## Coverage assignment contract

* `score_labeled` (`src/retrieval/rankers.py`) uses the labels carried directly
  by `ContextMixtureTask`: `tlab` for the query and `plab` for each candidate.
  This is the cross-line and Frangieh constructed/labeled route.
* `score_controlled` currently retains target construction labels but does not
  retain candidate labels in `ControlledMixtureTask`; candidate cells are
  assigned to the nearest target-component mean by Euclidean distance in
  `src/retrieval/rankers.py::score_controlled`. This is distinct from the
  labeled route and must not be described as direct candidate-label scoring.
* Partial observation uses `src/experiments/exp12_partial_observed_retrieval.py::_assign_states`:
  query states are obtained by two-means clustering, and each candidate cell is
  assigned to the query centroid with the highest cosine similarity after row
  normalization. It is not Euclidean nearest-centroid assignment.
* The HIR helper uses the same cosine candidate assignment, whereas the
  synthetic phase-diagram helper uses Euclidean nearest-centroid assignment.
  These are separate legacy/diagnostic helpers and are not interchangeable
  descriptions of the partial-observation path.

## U/V execution contract

`src/retrieval/metrics.py` now sets `DEFAULT_ESTIMATOR='u'` when no environment
variable is present. Thus the manuscript-facing experiment scripts reproduce
the U-statistic results without an environment variable. The only supported
V reproduction is an explicitly labelled legacy run, for example:

```bash
PY=python3 POPRETRIEVE_ESTIMATOR=v bash analysis/estimator_audit/run_legacy_suite.sh
```

The canonical manuscript run is:

```bash
PY=python3 bash scripts/run_all_core.sh
PY=python3 bash scripts/run_all_baselines.sh
```

The U/V assignment for manuscript-facing code is:

| result path | estimator |
|---|---|
| `src/experiments/exp01`--`exp05`, `exp07`--`exp13`, `exp16`--`exp17` via `score_energy`, `score_mmd_rbf` or `score_coverage` | U default |
| `src/experiments/exp06_theory_limits.py` | explicit U |
| `analysis/phase2_transition/phase2_common.py` | explicit U for primary population scores; V only in the named diagnostic helper |
| PCA-latent Fig. 2a diagnostic | separate explicit V routine, as stated in the manuscript |
| `oracle/` scripts and `analysis/estimator_audit/` V arms | legacy reproduction/audit, not the canonical manuscript pipeline |
| sliced Wasserstein | no U/V choice |

## Targeted sensitivity table

The runnable analysis is
`analysis/audit/control_reference_sensitivity.py`. It covers only cross-context
settings where query and candidate controls differ: all three SciPlex3
cross-line pairs (the original alpha sweep) and the Frangieh IFNGR1 contrasts.
It writes:

* `<out>.csv`: per-setting, per-perturbation, per-seed Hit@1/MRR rows;
* `<out>_summary.csv`: raw and matched-control-referenced averages;
* `<out>_qualitative.csv`: whether the sign of population-minus-mean changes.

The completed run used the mounted processed inputs and the project environment:

```bash
DIDR_DATA_ROOT=/absolute/path/to/data \
  python \
  analysis/audit/control_reference_sensitivity.py \
  --out results/audit/package1_raw_vs_control.csv \
  --sciplex3 /absolute/path/to/data/processed/sciplex3_all.pt \
  --frangieh /absolute/path/to/data/processed/frangieh_hvg.npz \
  --dataset both --n-seeds 10 --n-drugs 15 --n-total 200 \
  --n-distractors 40 --frangieh-perturbation IFNGR1
```

The result is unchanged at the level of qualitative manuscript conclusions; the
small numerical differences are reported in the dedicated sensitivity report.

## Exact affected code locations

* `src/retrieval/metrics.py`: explicit `*_v` kernel names, canonical U aliases,
  `DEFAULT_ESTIMATOR`, `score_energy` documentation, and the U/V dispatch used
  by `_energy_dist`/`_base_dist`.
* `src/retrieval/rankers.py`: `score_metric_robustness` now calls explicit
  `energy_distance_u` and `mmd_rbf_u`; `score_labeled` is the direct-label path;
  `score_controlled` is the Euclidean inferred-label path.
* `src/retrieval/tasks.py`: `ContextMixtureTask.build` supplies direct query and
  candidate context labels; `ControlledMixtureTask.build` supplies target labels
  only, so its candidate assignment remains inferred rather than label-driven.
* `src/experiments/exp06_theory_limits.py`: all theory-anchor energy calls now
  name `energy_distance_u` explicitly.
* `src/experiments/exp11_hir_benchmark.py` and
  `src/experiments/exp12_partial_observed_retrieval.py`: mean L2 now receives
  the same matched controls as mean cosine; `_assign_labels`/`_assign_states`
  document the cosine-assignment helpers.
* `src/experiments/exp11_synthetic_phase_diagram.py`: the synthetic diagnostic's
  Euclidean inferred assignment is kept distinct from partial observation.
* `analysis/audit/control_reference_sensitivity.py`: targeted, non-manuscript
  sensitivity driver.
* `analysis/estimator_audit/estimator_bias_table.py`,
  `analysis/audit/diag_delta_vs_raw.py`, `analysis/audit/diag_subsample_power.py`
  and `tests/test_estimator_bias.py`: V-statistic calls are now explicitly named.

## Manuscript/SI definition corrections completed

1. Main Methods defines raw normalized-expression populations for population
   scorers and control-referenced means for mean scorers.
2. Main Methods and Supplementary Methods distinguish direct construction labels,
   inferred controlled-mixture labels and partial-observation cosine assignment.
3. Supplementary Table 1 and the implementation note state the U-statistic
   default and identify the PCA-latent V arm as a legacy diagnostic.

The manuscript retains the reported raw population-scoring path. The control-aware
comparison is reported as a targeted sensitivity, not substituted for the primary
analysis.
