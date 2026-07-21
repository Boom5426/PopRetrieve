# Figure 4: Oracle-independent metrics collapse the apparent gains (the knife)

One-line message: the Class-A advantage (Fig 3) does not survive a change to metrics that do not
share the retrieval objective. The SAME recommended queries flip sign, the information-condition
gate correlates the WRONG way with true divergence, and 0/37 real tasks are DART-dominant.

## Panels

| Panel | Message | Source | Status |
|-------|---------|--------|--------|
| a | Same recommended queries: Class A regret +0.129 (73%>0) vs Class B MoA-nDCG mean -0.037 (35%>0) | fig4a_classA_vs_classB.csv | done |
| b | MoA-nDCG gain ECDF per cell line, all center on zero | fig4a_classA_vs_classB.csv | done |
| c | Minority-coverage gain by divergence quartile: significant but negligible (<0.002 in Q4 gap) | fig4ef_gate_divergence.csv | done |
| d | Recommended (+0.113, n=621) vs non-recommended (+0.124, n=133): the gate does not concentrate the gain | fig4d_recommendation_vs_outcome.csv | done |
| e | Gate structure-reliability vs true divergence rho=-0.21 (WRONG sign) | fig4ef_gate_divergence.csv | done |
| f | Binary recommendation does not separate true divergence: Mann-Whitney p=0.09 | fig4ef_gate_divergence.csv | done |
| g | 37 real tasks across 5 dataset regimes, all best method = mean_sufficient (0/37 DART-dominant) | fig4g_exp13_projection.csv | done |

## Verified numbers
- 4a: leave_drug_out recommended subset, n=480 paired; Class A regret reduction median +0.1292 (73.1%>0); Class B MoA-nDCG gain mean -0.0369, median 0.0000 (35.0%>0).
- 4d: recommendation_vs_outcome.csv, coverage_worst recommended median +0.1133 (n=621), mean_or_no_call +0.1235 (n=133), mean_ndcg_gain -0.0285 both.
- 4e: structure_reliability vs true_divergence rho=-0.2110 p=3.789e-09; preference_conflict rho=+0.1825 p=3.717e-07 (n=765 -> 735 unique query keys).
- 4f: recommended median divergence 1.660 vs non-rec 1.680, Mann-Whitney p=0.0902.
- 4g: exp13 projection.csv, 37 tasks, observed_best_method all mean_sufficient, 0/37 DART-dominant.

## Honesty notes
- This is the load-bearing negative. Every panel shows a DIFFERENT way the Class-A gain fails to
  transfer to oracle-independent evaluation. No panel is padding.
- 4c: the minority-coverage gain IS statistically significant (that is why it is not simply "zero"),
  but its magnitude is <0.002, i.e. practically negligible; the panel states both.
- 4a/4b: the flip is measured on the SAME queries, so it is not a population difference; it is the
  metric changing the verdict.
- 4e: the negative correlation is the key, the gate axis moves opposite to the quantity it should
  track, so it cannot be a valid trust signal.

## Files
- fig4a.py ... fig4g.py, fig4_assemble.py, fig4_collapse.{png,pdf}
