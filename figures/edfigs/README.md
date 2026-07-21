> ⚠️ **SUPERSEDED IN PART, 2026-07-12.** This document predates an audit that retracted
> several numbers as artifacts of our own code, including the "5.1x structure collapse", the
> hand-entered divergence-gate positions (CD34+ was 0.95; it measures 0.186), the MoA-nDCG
> statistics computed over 165 undefined sentinel values, and the Class A/B contrast that
> compared two different scorers. **Read [CORRECTIONS.md](../../CORRECTIONS.md) before using any
> number below.** Where this file and CORRECTIONS.md disagree, CORRECTIONS.md is right.
# Extended Data figures (ED1-ED4)

Trimmed from a 9-figure scope to 4 (user decision 2026-07-12). Each ED figure blocks one
anticipated reviewer attack; nothing is padding. Deleted from the earlier scope:
beta-interpolation/K=1 detail (already main Fig 2e), Fig 3 dataset decomposition (already
main Fig 3b), HIR-Bench provenance/ablations (now Methods note + server README). Dataset
scale detail also lives in Supplementary Table 1.

| Fig | Panels | Message | Blocks |
|-----|--------|---------|--------|
| ED1 | a dataset scale, b metric definitions, c metric correlation (54,180 queries) | mean-cosine == CMap-cosine (rho=1.00); energy/coverage form a separate near-orthogonal block | "non-standard data/metrics" |
| ED2 | a Q4 power, b sample size for 80%, c null across divergence strata | objective-aligned metric fully powered (0.9999); objective-independent needs n=27,794; null holds everywhere | "the negative is underpowered" |
| ED3 | a 9-method ARI, b silhouette, c predictor collapse, d phase diagram | no clustering recovers subpops (best ARI 0.106); only separation not budget lifts ARI | "you clustered badly" |
| ED4 | a program enrichment, b AXL signal, c minority rescue | exploratory resistance signal (AXL r=0.134, IFN p=1.9e-6), minority rescue near null | (exploratory transparency) |

## Provenance notes
- ED4b uses PEARSON r (0.134) to match exp15 `corr_divergence_enrichment`, NOT Spearman
  (which gives 0.197 on the same data). The manuscript cites the Pearson value.
- ED2 power/stratified from exp17_true_divergence_subset (power_analysis.csv,
  divergence_stratified.csv).
- ED3 predictor collapse from exp09 structure diagnostics (real subpop_variance_ratio 0.046
  vs predictors ~0.009). Phase diagram from upgrade/identifiability_phase_diagram.csv.

## Files
- ed_panels.py (all draw functions), ed1..ed4 .{png,pdf}
- source data: ../source_data/ed*.csv
