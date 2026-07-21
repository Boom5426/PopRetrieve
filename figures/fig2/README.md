# Figure 2: Mean retrieval is the variance-collapsed limit of distribution-aware retrieval

One-line message: mean-signature (CMap) retrieval is not a competing method but the
zero-variance degenerate member of the distributional family, so the comparison in later
figures is exact, not a strong-vs-weak-baseline setup.

## Panels

| Panel | Message | Type | Source data | Status |
|-------|---------|------|-------------|--------|
| a | Mean is the zero-variance limit of X = mu + lambda*eps | schematic (seed 0) | none | done |
| b | Scaling residual variance with the mean fixed | schematic (seed 1) | none | done |
| c | Energy retrieval collapses to the mean-distance floor as spread to 0 | data | source_data/fig2c_energy_collapse.csv | done |
| d | mean-cosine = CMap-cosine exactly (0.3885); WTCS 0.463 is the rank-based sibling | data | source_data/fig2d_operation_identity.csv | done |
| e | Coverage temperature beta spans mean-aggregation (0.7125) to worst-case (1.300); energy = coverage_{K=1} | data | source_data/fig2e_beta_spectrum.csv | done |
| f | Metric-family hierarchy and its limits | schematic | none | done |

## Verified numbers (traceable to source CSVs)

- 2c: energy 34.11 at spread 1.0 -> 98.50 at spread 0.0; mean-distance floor two_dmu = 98.50164 (exp06 degenerate_limit_synthetic.csv, prop1_spread).
- 2d: mean_cosine = cmap_cosine = 0.388492 (six-figure identity); cmap_wtcs = 0.463492 (exp08 summary.csv, 7-task mean Hit@1).
- 2e: D_beta 0.712500 (beta 1e-9, mean-agg) to 1.300000 (beta 1e9, worst-case); energy = coverage_{K=1} = 8.229259 (exp06 beta_interpolation.csv + degenerate_limit_synthetic.csv prop2_K1).

## Honesty notes

- 2b/2c residual-variance illustrations use synthetic gaussians (seeds fixed); they illustrate the
  algebra, they are not an experiment.
- The energy = coverage_{K=1} identity has one real drug on disk (Panobinostat, diff 0); the
  main-figure claim rests on the synthetic multi-point curve, real point noted in caption.

## Files

- fig2a.py ... fig2f.py : per-panel draw functions (each runs standalone: `python fig2c.py`).
- fig2_assemble.py : tiles a-f into fig2_unification.{png,pdf} (3x2 grid).
- fig2_unification.{png,pdf} : the composite.

## Editor lens

Panel e retains the beta-interpolation + K=1 identity in the MAIN figure (external review suggested
demoting to Extended Data; declined). C1 unification is the load-bearing defense against a
strong-vs-weak-baseline objection, so its quantitative evidence stays in the main deck.
