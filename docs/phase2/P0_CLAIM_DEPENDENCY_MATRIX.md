# P0. Claim dependency matrix

Built 2026-09-02, before any post-Phase-II edit to the manuscript. Its purpose is narrow and
mechanical: when a scorer, an estimator or a statistic changes, this file says which figure panels
and which Results sentences move with it, so a repair cannot be applied to one place and missed in
another.

Traced automatically from the code (panel script imports, `results_path` calls, scorer imports) and
checked by hand. Sources: `figures/*/fig*.py`, `src/experiments/`, `analysis/`,
`figures/sync_source_data.py`.

## The manuscript snapshot this matrix describes

Frozen in [`manuscript/snapshots/pre_phaseii/`](../../manuscript/snapshots/pre_phaseii/):
`MANUSCRIPT_PRE_PHASEII.{tex,pdf}`, `SI_PRE_PHASEII.{tex,pdf}`, `FIG1..5_PRE_PHASEII.pdf`. Nothing
in the snapshot is edited again; it exists so that any later claim of "this number changed" can be
checked against what the number actually was.

## Legend

**Estimator-sensitive** means the panel's numbers pass through `energy_distance`, `mmd_rbf` or
`coverage_aggregate`, and therefore change when the U-statistic replaces the V-statistic. *Direct*
means the producing script calls a population scorer; *inherited* means it reads a file that one
produced. Panels marked **no** compute only cosines, norms, probes or counts.

## Main figures

| Panel | Panel script | Result file | Producer | Population scorer | Estimator-sensitive |
|---|---|---|---|---|---|
| 1g | `fig1/fig1g.py` | `exp06_theory_limits/degenerate_limit_synthetic.csv` | `exp06_theory_limits.py` | `energy_distance`, `coverage_aggregate` | **yes, direct** |
| 1a-f, 1h | schematic / analytic | none | none | none | no |
| 2a | `fig2/fig2a.py` | `exp08_signature_baselines/summary.csv` | `exp08_signature_baselines.py` | `energy_distance` | **yes, direct** |
| 2b | `fig2/fig2b.py` | `exp08_signature_baselines/summary_by_task.csv` | `exp08_signature_baselines.py` | `energy_distance` | **yes, direct** |
| 2c | `fig2/fig2c.py` | `exp12_partial_observed_retrieval/per_query_scores.csv` | `exp12_partial_observed_retrieval.py` | all six scorers | **yes, direct** |
| 2d | `fig2/fig2d.py` | `exp01_sciplex3_controlled/metrics_summary.csv` | `exp01_sciplex3_controlled.py` | via `retrieval.rankers` | **yes, direct** |
| 2e | `fig2/fig2e.py` | `exp12_partial_observed_retrieval/per_query_scores.csv` | `exp12_partial_observed_retrieval.py` | all six scorers | **yes, direct** |
| 2f | `fig2/fig2f.py` | `source_data/ed1_metric_correlation.csv` | `exp12_partial_observed_retrieval.py` | all six scorers | **yes, inherited** |
| 3a, 3b | `fig3/fig3a.py`, `fig3b.py` | `exp12_partial_observed_retrieval/per_query_scores.csv` | `exp12_partial_observed_retrieval.py` | all six scorers | **yes, direct** |
| 3c, 3e, 3f | `fig3/fig3c.py`, `3e.py`, `3f.py` | `exp16_gate_diagnosis/_merged_query_divergence.csv` | `exp16_gate_diagnosis.py` | none of its own; reads exp12 | **yes, inherited** |
| 3d | `fig3/fig3d.py` | `exp12_partial_observed_retrieval/recommendation_vs_outcome.csv` | `exp12_partial_observed_retrieval.py` | all six scorers | **yes, direct** |
| 3g | `fig3/fig3g.py` | `exp13_real_data_projection/projection.csv` | `exp13_real_data_projection.py` | `score_energy` | **yes, direct** |
| 3h, 3i, 3j, 3k | `fig3/fig3h.py` .. `3k.py` | `source_data/fig3hi_class_c_*.csv` | `class_c_functional_oracle.py` | `score_energy` | **yes, direct, BLOCKED** |
| 4b | `fig4/fig4b.py` | `exp11_hir_benchmark/theoretical_boundary.csv` | `exp11_hir_benchmark.py` | all six scorers | **yes, direct** |
| 4f | `fig4/fig4f.py` | `exp11_hir_benchmark/phase_grid_predictability_2x2.csv` | `exp11_hir_benchmark.py` | all six scorers | **yes, direct** |
| 4 shape | `fig4/fig4_shape.py` | `upgrade/oracle_shape_test.json` | `class_c/oracle_shape_test.py` | `score_energy`, `energy_distance` | **yes, direct** |
| 4 gate2 | `fig4/fig4_gate2.py` | `zhao_gbm/gate2_drug_response.json`, `gate2_uncertainty.json` | `natural/gate2_drug_response.py` | none | no |
| 4d, 4e, 4f (premise) | `fig4/fig4_nat.py`, `fig7/fig7_natural.py` | `zhao_gbm/premise_mean_vs_compartment.csv` | `natural/zhao_premise_disjoint.py` | none | no |
| 5b | `fig5/fig5b.py` | `exp09_predict_then_rank/summary.csv` | `exp09_predict_then_rank.py` | `score_energy`, `score_coverage` | **yes, direct** |
| 5c, 5d | `fig5/fig5c.py`, `5d.py` | `exp09_structure_diagnostics/*.csv` | `exp09_structure_diagnostics.py` | `score_energy` | **yes, direct** |
| 5e, 5f | `fig5/fig5e.py`, `5f.py` | `upgrade/gate2_supervised_upper_bound.csv` | `identifiability/gate2_supervised_upper_bound.py` | none | no |
| 5g | `fig5/fig5g.py` | `exp17_true_divergence_subset/divergence_stratified.csv` | `exp17_true_divergence_subset.py` | none of its own; reads exp12 | **yes, inherited** |
| 5h-k (retired 2026-09-03) | was `fig5/fig5_two_gate.py`; those four Tahoe panels left the deck with the Phase-II rebuild and their content is in Supplementary Note 4 | `tahoe_pilot/*.csv` | `tahoe_pilot/tahoe_gate_pilot.py` | none | no |

## Count

Of 40-odd panels across the five figures, **19 are estimator-sensitive**, 15 of them directly.
Four of the sensitive ones (3h to 3k) cannot be re-run: they need the GDSC2 workbook, which is not
redistributable and is absent from both machines (`DATA.md`). Those four are carried as **blocked**
in [P2_LEGACY_RERUN.md](P2_LEGACY_RERUN.md), not as unchanged.

## What else moves with each repair

Two repairs are in flight. This lists what each touches beyond the panels above.

### Repair 1: V-statistic to U-statistic energy and MMD

- Every macro in `PopRetrieve_manuscript.tex` whose value comes from a table in the "yes" rows.
- Supplementary Note 3's predictor table, which quotes induced-response cosines, not energies:
  **not affected**.
- The `coverage_aggregate` results (exp06, exp09, exp11, exp12), because coverage aggregates a base
  metric that is itself an energy distance.
- `docs/FINDINGS.md`, which quotes the same numbers.

### Repair 2: replacing Gate 1's `1 - cos` with a cross-fitted interaction statistic

- Fig. 5c and the `gate1_response_divergence` tables, which are `1 - cos` by construction.
- Fig. 4d and 4e, the patient-glioblastoma two-gate panels, which use the same statistic on tissue.
- The Phase-II Gate 1 audit, [05](05_DIFFERENTIAL_RESPONSE_AUDIT.md).
- Every Results sentence that calls a quantity "differential response" or "induced cosine".
- **Not** the retrieval results: the statistic is a stratifier and a diagnostic, never a scorer, so
  no ranking depends on it.

## Rule this file exists to enforce

A number quoted in the manuscript must be reachable from this table in one hop: panel to result
file to producing script. If it is not, it is either a hand-entered constant, which the source-data
manifest calls DERIVED and which has no generator, or it is unsourced. The audit that produced
[`CORRECTIONS.md`](../../CORRECTIONS.md) R65 found one of the latter; this matrix is how the next
one gets found before it is published rather than after.
