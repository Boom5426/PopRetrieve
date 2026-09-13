# PopRetrieve Package 2 — cluster-aware inference audit

Status: statistical repair completed from existing per-query result tables; no scorer or query construction was rerun.

## Input files

- `results/exp12_partial_observed_retrieval/per_query_scores.csv`
- `results/exp16_gate_diagnosis/_merged_query_divergence.csv`

## Dependence structure and confirmed counts

- Total query units: **765** = 600 leave-drug-out + 120 leave-MoA-out + 45 partial-library.
- Individual-drug formal universe: **720 queries, 143 query-drug clusters, 417 drug×cell-line contexts**.
- MoA-evaluable universe: **600 queries, 130 drug clusters**.
- `partial_library` has held-out drug value `batch`; it is descriptive only and excluded from primary cluster inference.
- Seeds, cell lines and library fractions remain repeated observations within query-drug clusters; cell lines are fixed contexts.

## Corrected result tables

- Source rows: `audit/package2_source_rows.csv`
- Query counts: `audit/package2_query_counts.csv`
- Cluster summaries: `audit/package2_cluster_summaries.csv`
- Divergence strata/rho: `audit/package2_divergence.csv`
- Diagnostic gate: `audit/package2_diagnostic_gate.csv`
- One-row-per-drug sensitivity: `audit/package2_drug_level_sensitivity.csv`

Primary inference uses 10,000 drug-cluster bootstrap resamples and percentile 95% CIs. Secondary paired tests, where valid, are Wilcoxon tests on one median effect per drug. Query-level P values are retained only as the old comparison and are not treated as confirmatory.

## Fig. 2c — response-matching regret

The all-query row is descriptive only: its `batch` label is not treated as a biological cluster. The formal row excludes all 45 pooled partial-library queries.

| scope | n | drugs | point | 95% interval | drug P | consequence |
| --- | --- | --- | --- | --- | --- | --- |
| all_eligible_descriptive | 765 | 144 | +0.0311 | query-descriptive [+0.0168, +0.0490] | NA | UNCHANGED |
| individual_drug_formal | 720 | 143 | +0.0304 | [+0.0155, +0.0495] | 1.19e-05 | UNCHANGED |

Formal result: median +0.0304, 95% drug-cluster CI [+0.0155, +0.0495], 720 queries and 143 drugs. The response-matching advantage remains supported.

## Fig. 2e — population scorers versus mean references

| scorer | reference | median | 95% cluster CI | n | drugs | consequence |
| --- | --- | --- | --- | --- | --- | --- |
| DART_energy | mean_cosine | +0.0600 | [+0.0416, +0.0889] | 584 | 141 | UNCHANGED |
| DART_mmd | mean_cosine | +0.0663 | [+0.0450, +0.0903] | 584 | 141 | UNCHANGED |
| DART_sliced_wasserstein | mean_cosine | +0.0676 | [+0.0403, +0.0924] | 584 | 141 | UNCHANGED |
| DART_coverage_mean | mean_cosine | +0.0447 | [+0.0198, +0.0648] | 584 | 141 | UNCHANGED |
| DART_coverage_worst | mean_cosine | +0.0304 | [+0.0164, +0.0539] | 584 | 141 | UNCHANGED |
| DART_energy | mean_l2 | +0.0000 | [+0.0000, +0.0000] | 584 | 141 | UNCHANGED |
| DART_mmd | mean_l2 | +0.0000 | [+0.0000, +0.0000] | 584 | 141 | UNCHANGED |
| DART_sliced_wasserstein | mean_l2 | +0.0000 | [-0.0013, +0.0000] | 584 | 141 | UNCHANGED |
| DART_coverage_mean | mean_l2 | -0.0324 | [-0.0520, -0.0172] | 584 | 141 | UNCHANGED |
| DART_coverage_worst | mean_l2 | -0.0438 | [-0.0603, -0.0307] | 584 | 141 | UNCHANGED |

Every population scorer remains positive versus direction-only mean cosine. Against magnitude-aware mean L2, energy/MMD/SW have no positive residual and coverage-mean/worst are negative. The comparison-dependent interpretation is unchanged.

## Fig. 3a–b — response matching and MoA recovery

`response_regret_difference` is population improvement; `moa_ndcg_difference` is population minus reference MoA-nDCG.

| metric | scorer | reference | median | 95% cluster CI | drug P | consequence |
| --- | --- | --- | --- | --- | --- | --- |
| response_regret_difference | DART_energy | mean_cosine | +0.0594 | [+0.0390, +0.0883] | 2.75e-12 | UNCHANGED |
| response_regret_difference | DART_mmd | mean_cosine | +0.0653 | [+0.0449, +0.0919] | 2.16e-13 | UNCHANGED |
| response_regret_difference | DART_sliced_wasserstein | mean_cosine | +0.0668 | [+0.0391, +0.0888] | 3.07e-10 | UNCHANGED |
| response_regret_difference | DART_coverage_mean | mean_cosine | +0.0413 | [+0.0159, +0.0620] | 0.000277 | UNCHANGED |
| response_regret_difference | DART_coverage_worst | mean_cosine | +0.0278 | [+0.0114, +0.0510] | 0.000391 | UNCHANGED |
| response_regret_difference | DART_energy | mean_l2 | +0.0000 | [+0.0000, +0.0000] | 0.0599 | UNCHANGED |
| response_regret_difference | DART_mmd | mean_l2 | +0.0000 | [+0.0000, +0.0000] | 0.0761 | UNCHANGED |
| response_regret_difference | DART_sliced_wasserstein | mean_l2 | +0.0000 | [-0.0016, +0.0000] | 0.000104 | UNCHANGED |
| response_regret_difference | DART_coverage_mean | mean_l2 | -0.0355 | [-0.0529, -0.0172] | 6.03e-13 | UNCHANGED |
| response_regret_difference | DART_coverage_worst | mean_l2 | -0.0476 | [-0.0614, -0.0326] | 2.98e-13 | UNCHANGED |
| moa_ndcg_difference | DART_energy | mean_cosine | +0.0000 | [+0.0000, +0.0000] | 0.904 | UNCHANGED |
| moa_ndcg_difference | DART_mmd | mean_cosine | +0.0000 | [+0.0000, +0.0000] | 0.647 | UNCHANGED |
| moa_ndcg_difference | DART_sliced_wasserstein | mean_cosine | +0.0000 | [+0.0000, +0.0000] | 0.562 | UNCHANGED |
| moa_ndcg_difference | DART_coverage_mean | mean_cosine | +0.0000 | [-0.0016, +0.0000] | 0.000529 | UNCHANGED |
| moa_ndcg_difference | DART_coverage_worst | mean_cosine | +0.0000 | [+0.0000, +0.0000] | 0.119 | WEAKEN CLAIM |
| moa_ndcg_difference | DART_energy | mean_l2 | +0.0000 | [+0.0000, +0.0000] | 0.436 | UNCHANGED |
| moa_ndcg_difference | DART_mmd | mean_l2 | +0.0000 | [+0.0000, +0.0000] | 0.977 | UNCHANGED |
| moa_ndcg_difference | DART_sliced_wasserstein | mean_l2 | +0.0000 | [+0.0000, +0.0000] | 0.957 | UNCHANGED |
| moa_ndcg_difference | DART_coverage_mean | mean_l2 | +0.0000 | [+0.0000, +0.0000] | 0.000756 | UNCHANGED |
| moa_ndcg_difference | DART_coverage_worst | mean_l2 | +0.0000 | [+0.0000, +0.0000] | 0.0813 | WEAKEN CLAIM |

Response-matching advantages remain positive versus mean cosine. MoA recovery does not show a positive population advantage. For coverage-worst versus mean cosine, the old query-level P=0.0077 becomes drug-level P=0.119; significance wording must be weakened, but the no-positive-MoA-advantage conclusion remains.

## Fig. 3d–f — current executable panel mapping

The executable maps minority coverage to Fig. 3c, MoA divergence to Fig. 3d, recommendation enrichment to Fig. 3e, and gate alignment to Fig. 3f. Both the requested analyses and these current code paths are retained.

| panel | stratum | mean | median | 95% cluster CI | n | drugs | BH q | consequence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Fig3c/current-divergence-coverage | Q1 | -0.0035 | +0.0000 | [-0.0091, +0.0013] | 190 | 71 | 0.442 | NUMERIC UPDATE ONLY |
| Fig3c/current-divergence-coverage | Q2 | +0.0030 | +0.0002 | [+0.0017, +0.0045] | 181 | 91 | 0.0144 | NUMERIC UPDATE ONLY |
| Fig3c/current-divergence-coverage | Q3 | +0.0038 | +0.0008 | [+0.0025, +0.0052] | 174 | 87 | 0.00102 | NUMERIC UPDATE ONLY |
| Fig3c/current-divergence-coverage | Q4 | +0.0036 | +0.0015 | [+0.0021, +0.0052] | 175 | 78 | 0.00102 | NUMERIC UPDATE ONLY |
| Fig3d/current-divergence-MoA | Q1 | -0.0497 | -0.0062 | [-0.0849, -0.0168] | 166 | 64 | 0.14 | NUMERIC UPDATE ONLY |
| Fig3d/current-divergence-MoA | Q2 | -0.0391 | +0.0000 | [-0.0733, -0.0048] | 150 | 82 | 0.14 | NUMERIC UPDATE ONLY |
| Fig3d/current-divergence-MoA | Q3 | -0.0158 | +0.0000 | [-0.0447, +0.0114] | 141 | 76 | 0.74 | NUMERIC UPDATE ONLY |
| Fig3d/current-divergence-MoA | Q4 | +0.0142 | +0.0000 | [-0.0165, +0.0425] | 143 | 73 | 0.601 | NUMERIC UPDATE ONLY |

Cluster-bootstrap Spearman: coverage divergence rho=+0.1152 (95% CI [+0.0147, +0.2143], 720 queries/143 drugs); MoA divergence rho=+0.1548 (95% CI [+0.0722, +0.2349], 600 queries/130 drugs).

| panel | effect/rho | 95% cluster CI | n | drugs | old P | consequence |
| --- | --- | --- | --- | --- | --- | --- |
| Fig3e/current-diagnostic-gate-enrichment | -0.0109 | [-0.0355, +0.0498] | 709 | 141 | 0.793 | UNCHANGED |
| Fig3f/current-gate-alignment | -0.2247 | [-0.3144, -0.1289] | 720 | 143 | 1.08e-09 | UNCHANGED |

The diagnostic enrichment effect is recommended minus no-call median regret gain = -0.0109 (95% cluster CI [-0.0355, +0.0498]; 584 versus 125 queries; 141 drugs), so the diagnostic does not reliably enrich for population-beneficial queries. Gate-alignment reliability versus divergence remains negative, rho=-0.2247 (95% CI [-0.3144, -0.1289]).

## Old versus corrected inference

See `package2_old_vs_new.csv` for the complete machine-readable table, including old query-level point/CI/P, corrected point/cluster CI/drug-level P, sample sizes, direction flags, and manuscript consequence categories.

## Pooled-query versus one-row-per-drug sensitivity

The primary sign flags are in `package2_cluster_summaries.csv`. 14 summary rows have a point-estimate sign difference between pooled rows and one-row-per-drug medians; these are concentrated in zero-inflated MoA-nDCG or low-divergence strata. The headline Fig. 2c formal effect remains positive in both analyses (+0.0304 pooled-query median versus +0.0444 one-row-per-drug median).

| panel | metric | scope | cluster point | drug-row point | direction |
| --- | --- | --- | --- | --- | --- |
| Fig2e | response_regret_difference | recommended_individual_formal | +0.0000 | -0.0008 | includes_zero |
| Fig3a-b | response_regret_difference | leave_drug_out/DART_energy/mean_l2 | -0.0168 | +0.0000 | negative |
| Fig3a-b | response_regret_difference | leave_drug_out/DART_mmd/mean_l2 | -0.0161 | +0.0000 | negative |
| Fig3a-b | response_regret_difference | leave_drug_out/DART_sliced_wasserstein/mean_l2 | -0.0330 | +0.0000 | negative |
| Fig3a-b | moa_ndcg_difference | leave_drug_out/DART_energy/mean_cosine | -0.0130 | +0.0000 | includes_zero |
| Fig3a-b | moa_ndcg_difference | leave_drug_out/DART_mmd/mean_cosine | -0.0111 | +0.0000 | includes_zero |
| Fig3a-b | moa_ndcg_difference | leave_drug_out/DART_sliced_wasserstein/mean_cosine | -0.0160 | +0.0000 | includes_zero |
| Fig3a-b | moa_ndcg_difference | leave_drug_out/DART_coverage_mean/mean_cosine | -0.0334 | +0.0000 | negative |
| Fig3a-b | moa_ndcg_difference | leave_drug_out/DART_coverage_worst/mean_cosine | -0.0239 | +0.0000 | negative |
| Fig3a-b | moa_ndcg_difference | leave_drug_out/DART_energy/mean_l2 | -0.0017 | +0.0000 | includes_zero |
| Fig3a-b | moa_ndcg_difference | leave_drug_out/DART_mmd/mean_l2 | +0.0003 | +0.0000 | includes_zero |
| Fig3a-b | moa_ndcg_difference | leave_drug_out/DART_sliced_wasserstein/mean_l2 | -0.0046 | +0.0000 | includes_zero |
| Fig3a-b | moa_ndcg_difference | leave_drug_out/DART_coverage_mean/mean_l2 | -0.0220 | +0.0000 | negative |
| Fig3a-b | moa_ndcg_difference | leave_drug_out/DART_coverage_worst/mean_l2 | -0.0125 | +0.0000 | includes_zero |

## Panel mapping note

The current executable figure code labels the divergence panels as Fig. 3c (minority coverage) and Fig. 3d (MoA-nDCG), the recommendation-outcome diagnostic as Fig. 3e, and the gate-alignment diagnostic as Fig. 3f. This differs from the shorthand panel numbering in the audit request; both current code paths are included and no split was silently reinterpreted.

## Manuscript consequence

Categories in the machine-readable table are `UNCHANGED`, `NUMERIC UPDATE ONLY`, and `WEAKEN CLAIM`. No row supports `SCIENTIFIC CONCLUSION CHANGED` or `REMOVE INFERENTIAL CLAIM` for the central information-attrition story. The `WEAKEN CLAIM` rows are significance statements whose query-level P values do not survive drug-level clustering; their effect direction does not become a positive population advantage.

## Manuscript/SI sentence inventory (not edited)

- `manuscript/latex/PopRetrieve_manuscript.md:144-147`: the +0.119, n=621, query-level Wilcoxon sentence is not the current U-source-table result. Replace its denominator, effect summary and uncertainty after the scorer-definition audit is incorporated; Package 2 establishes the cluster-aware numbers but does not rewrite this claim.
- `manuscript/latex/PopRetrieve_manuscript.md:174-186`: replace confirmatory query-level gate P values and the 621/133-era diagnostic framing with the current U-source counts (627 recommended, 127 mean-or-no-call, 11 mean-sufficient) and the drug-cluster enrichment CI; retain the null-enrichment interpretation.
- `manuscript/latex/PopRetrieve_manuscript.md:290-296` and `manuscript/latex/PopRetrieve_SI.tex:239-245`: replace query-level divergence P values/intervals with the cluster-bootstrap rho and quartile intervals; retain that divergence does not establish a positive MoA-recovery advantage in the highest quartile.
- `manuscript/latex/PopRetrieve_manuscript.md:576-579`: add the partial-observation inferential unit (query drug), exclusion of pooled partial-library rows from formal inference, drug-cluster bootstrap, and drug-level paired test; query-level Wilcoxon/Mann–Whitney P values are descriptive/legacy only.
- `manuscript/latex/PopRetrieve_SI.tex:284-291`: retain the 127 plus 11 diagnostic labels, but replace query-level interval language with the cluster-aware enrichment result and state that the comparison is not evidence of reliable enrichment.
- `manuscript/latex/PopRetrieve_SI.tex:769-779`: retain the 765/600 denominators, but state their split composition explicitly (600 leave-drug-out, 120 leave-MoA-out, 45 partial-library; 600 MoA-evaluable rows correspond to leave-drug-out) and identify 143 individual query-drug clusters (130 for MoA-evaluable rows).

No manuscript/SI text was edited. Package status: **PASS WITH TEXT REVISION**. Uncertainty and selected significance wording must be updated, but the central effect directions and evaluation-dependent interpretation remain.
