> ⚠️ **SUPERSEDED IN PART, 2026-07-12.** This document predates an audit that retracted
> several numbers as artifacts of our own code, including the "5.1x structure collapse", the
> hand-entered divergence-gate positions (CD34+ was 0.95; it measures 0.186), the MoA-nDCG
> statistics computed over 165 undefined sentinel values, and the Class A/B contrast that
> compared two different scorers. **Read [CORRECTIONS.md](../../CORRECTIONS.md) before using any
> number below.** Where this file and CORRECTIONS.md disagree, CORRECTIONS.md is right.
# Figure 6: Structure preservation and identifiability constrain distribution-aware retrieval

One-line message: the collapse of the apparent distributional advantage (Fig 4) has a mechanism.
The predicted candidate populations retrieval must work on lose subpopulation structure (Gate 1),
and even in real data the subpopulations are not identifiable (Gate 2), so the advantage stays near
zero. A two-gate criterion, not a tuning failure.

## Panels (mechanism chain: predict -> preserve -> identify -> decide)

| Panel | Message | Type | Source | Status |
|-------|---------|------|--------|--------|
| a | Predict-then-rank: retrieval works on predicted or observed candidate populations | schematic | none | done |
| b | No predictor yields a positive DART-minus-mean nDCG gain (avg-effect -0.016, latent-linear, NN -0.071) | data | fig6b_predictor_gaps.csv | done |
| c | Predictors collapse subpopulation variance: real 0.046 vs predicted ~0.009 (5.1x) | data | fig6cd_structure_diagnostics.csv | done |
| d | Structure collapse across multiple diagnostics (predicted/real ratio heatmap) | data | fig6cd_structure_diagnostics.csv | done |
| e | 9 unsupervised methods on a controlled two-source mixture with KNOWN labels: best median ARI 0.106, none > 0.15 | data | fig6e_controlled_mixture_ari.csv | done |
| f | NEW identifiability phase diagram: at real separability (row 1.0) ARI ~0.07 at every budget; only larger separation lifts it | data | fig6f_phase_diagram_full.csv | done |
| g | REFRAME: DART-minus-mean advantage by divergence tertile near zero; trend rho +0.08 (p=0.046) collapses to rho -0.01 (p=0.90) under identifiability | data | fig6g_conditional_advantage.csv | done |

## Verified numbers

- 5b: nDCG@10 gain (DART energy minus mean cosine) avg-effect -0.016, nearest-neighbor -0.071, latent-linear (exp09 predict_then_rank/summary.csv).
- 5c/5d: subpop variance ratio real 0.046269 vs average_effect 0.009022 = 5.13x collapse (exp09 structure_diagnostics_summary.csv).
- 5e: best method KMeans-bestk4 median ARI 0.1055, max 0.1490; no method median exceeds 0.15 (controlled_mixture_ari.csv, 9 methods x 20 seeds).
- 5f: mean-ARI grid; real-data anchor separation_scale 1.0 row = {25:0.063, 50:0.079, 100:0.075, 200:0.068, 400:0.072}; separation 3.0 at n=400 = 0.643, 5.0 = 0.999 (identifiability_phase_diagram.csv, 600 rows).
- 5g: overall delta -0.0129; by tertile low -0.0387 mid -0.0172 high +0.0173; spearman(divergence, delta) rho +0.0817 p=0.0455; spearman(query_silhouette, delta) rho -0.0069 p=0.8995 (conditional_advantage_per_query.csv, 600 queries).

## Honesty notes (the load-bearing caveats)

- 5f: at HIGH separation, small budgets (n=25) score HIGHER ARI than large budgets, a small-sample
  KMeans artifact irrelevant to the real-data regime (row 1.0), where ARI is flat and low.
- 5g: this is the REFRAME the external review asked for. The panel deliberately shows a near-zero
  bar and the collapse of the weak positive trend under the TRUE identifiability variable
  (silhouette), consistent with the manuscript's "two-gate criterion confirmed, not rescued".
  Better-separated queries are easier for ALL methods, which is why the divergence trend is not a
  distributional advantage.
- 5e/5f use raw-space KMeans ARI against known source labels; ARI 0.5 is drawn as a reference line
  for "reliable recovery", not an accepted universal threshold.

## Files
- fig6a.py ... fig6g.py : per-panel draw functions (each runs standalone).
- fig6_assemble.py : 2-row 7-panel layout (top a-d, bottom e-g).
- fig6_two_gate.{png,pdf} : composite.

## Editor lens
Fig 5 kept at 7 panels per your approval. 5f and 5g are both new this pass; 5f (the phase diagram)
is the stronger keep because it converts "the gate is closed" into an information-limit statement.
