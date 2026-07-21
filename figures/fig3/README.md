# Figure 3: Objective-aligned metrics reveal strong distributional signal (Class A)

One-line message: under objective-aligned evaluation, distribution-aware retrieval shows large,
consistent gains over mean-signature retrieval. This is genuine but Class A (the metric shares the
retrieval objective); the figure must NOT be read as independent validation, which Fig 4 addresses.

## Panels

| Panel | Message | Source | Status |
|-------|---------|--------|--------|
| a | Hit@1 ladder: energy 0.837 > ... > mean = CMap 0.388 | fig3a_hit1_ladder.csv | done |
| b | Advantage holds across controlled/crossline/frangieh (honest: CMap/mean win on frangieh 0.60) | fig3b_task_heatmap.csv | done |
| c | Per-query regret reduction ECDF: median +0.119, 72% of 621 queries improved, p=4e-56 | fig3c_regret_reduction.csv | done |
| d | Recommended (+0.113, n=621) vs non-recommended (+0.124, n=133): gate does NOT concentrate the gain | exp12 recommendation_vs_outcome.csv | done |
| e | alpha-crossover: energy beats mean; gap narrows as subpopulations merge (alpha to 0.9) | fig3e_alpha_crossover.csv | done |
| f | Every distributional metric shows the gain: energy +0.056, MMD +0.060, SW +0.059, cov-mean +0.090, cov-worst +0.119 | fig3f_classA_robustness.csv | done |

## Verified numbers
- 3a: energy 0.8369, pca_dist 0.7782, coverage_mean 0.7734, coverage_worst 0.5893, pca_mean 0.5179, cmap_wtcs 0.4635, cmap_cosine = mean_cosine 0.388492 (exp08 summary.csv, 7-task mean Hit@1).
- 3c/3d: regret reduction DART_coverage_worst vs mean_cosine, recommended subset: n=621, median +0.1190, mean +0.2677, frac>0 0.720, Wilcoxon p=4.255e-56 (exp12 per_query_scores.csv).
- 3d: recommendation_vs_outcome.csv medians, coverage_worst recommended +0.1133 (n=621) vs mean_or_no_call +0.1235 (n=133).
- 3e: exp01 K562 alpha=0.5 energy Hit@1 1.00 vs mean_cosine 0.00; gap narrows to 0.35 vs 0.30 at alpha=0.9 (metrics_summary.csv).
- 3f: all 5 DART metrics positive regret reduction, consistent direction (exp12 per_query_scores.csv, recommended subset).

## Honesty notes
- The whole figure is Class A: gains are measured with metrics that share the retrieval objective.
  Captions state this; the collapse under Class B/C metrics is Fig 4.
- 3b shows CMap/mean OUTPERFORMING on frangieh (0.60 vs energy 0.58); this is left visible, not hidden.
- 3c/3d: the Class-A positive is in decision REGRET, not MoA-nDCG (which is ~0 on the recommended
  subset); the panels plot regret reduction, not a MoA-nDCG gain, to avoid overclaiming.
- 3e uses the controlled alpha axis (subpopulation mixing), the one setting with a clean
  heterogeneity knob; per-query real-data divergence does NOT correlate with regret reduction
  (rho=-0.03, p=0.40), so that (absent) relationship is deliberately not drawn.

## Files
- fig3a.py ... fig3f.py, fig3_assemble.py, fig3_apparent_gains.{png,pdf}
