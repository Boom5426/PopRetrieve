# Figure 2: Mean retrieval is the variance-collapsed limit of distribution-aware retrieval

One-line message: mean-signature (CMap) retrieval is not a competing method but the
zero-variance degenerate member of the distributional family, so the comparison in later
figures is exact, not a strong-vs-weak-baseline setup.

## Panels

| Panel | Message | Type | Source data | Status |
|-------|---------|------|-------------|--------|
| a | Two populations under X = mu + lambda*eps; at lambda -> 0 the population score becomes the mean-to-mean score | schematic (seed 0) | none | done |
| b | Scaling lambda changes only the residual; the sample mean is identical at every lambda | schematic (seed 1) | none | done |
| c | Energy distance meets the mean-distance floor (98.50) at lambda = 0 | data | source_data/fig2c_energy_collapse.csv | done |
| d | mean-cosine = CMap-cosine exactly (0.3885); WTCS 0.4635 is the rank-based sibling | data | source_data/fig2d_operation_identity.csv | done |
| e | Coverage temperature beta spans mean-aggregation (0.7125) to worst-case (1.300); energy = coverage_{K=1} | data | source_data/fig2e_beta_spectrum.csv | done |
| f | The family drawn as one axis of variance sensitivity, mean retrieval at its zero end | schematic | none | done |

The panels share one visual grammar so the argument reads as a chain: a defines lambda, b
isolates it, c measures the collapse along it, e shows the same collapse along beta, f is the
synthesis. Orange is reserved for mean / collapsed quantities and blue for distributional ones,
which is why the mean-cosine and CMap-cosine points in panel d are orange rather than blue.

## Verified numbers (traceable to source CSVs)

- 2c: energy 34.11 at spread 1.0 -> 98.50 at spread 0.0; mean-distance floor two_dmu = 98.50164 (exp06 degenerate_limit_synthetic.csv, prop1_spread).
- 2d: mean_cosine = cmap_cosine = 0.388492 (six-figure identity); cmap_wtcs = 0.463492 (exp08 summary.csv, 7-task mean Hit@1).
- 2e: D_beta 0.712500 (beta 1e-9, mean-agg) to 1.300000 (beta 1e9, worst-case); energy = coverage_{K=1} = 8.229259 (exp06 beta_interpolation.csv + degenerate_limit_synthetic.csv prop2_K1).

## Honesty notes

- 2a/2b residual-variance illustrations use seeded gaussians and re-centre the residual so the
  plotted sample mean is exactly mu at every lambda; they illustrate the algebra, they are not an
  experiment. Panel c is the measured version of the same statement.
- The energy = coverage_{K=1} identity has one real drug on disk (Panobinostat, 0.1099 vs 0.1099,
  diff 0, degenerate_limit_real.csv), and that is the instance the manuscript text quotes. Panel e
  annotates the SYNTHETIC instance (8.229 vs 8.229) and now says so in the annotation, so the two
  numbers cannot be confused. If the author prefers figure and text to quote the same instance,
  swap the panel-e annotation to the real drug; that is a content decision, not a styling one.
- Panel f deliberately does not draw a beta -> 0 edge into mean retrieval. beta -> 0 returns the
  mean-AGGREGATED coverage value (0.7125 in panel e), not the mean-signature score, so beta is
  drawn as the span within the coverage member and lambda -> 0 is the only collapse edge. The
  previous box-stack version drew beta -> 0 straight into "mean retrieval (CMap)", which conflated
  the two.
- Panel f also puts energy, MMD and sliced-Wasserstein on one rung. Nothing in the manuscript
  orders those three by variance sensitivity, so separate rungs would assert an unmeasured ranking.
- Panel d truncates the Hit@1 axis at 0.365 and marks the truncation with an axis-break glyph; the
  dotted row guides span the full axis so nothing in the panel encodes length.

## Files

- fig2a.py ... fig2f.py : per-panel draw functions (each runs standalone: `python fig2c.py`).
- fig2_assemble.py : tiles a-f into fig2_collapse.{png,pdf} on a 3-row x 12-column grid, split 7/5
  so the claim-carrying panels a, c, e hold the wide column. It owns the module-level `STEM`.
- fig2_collapse.{pdf,svg,png} : the composite, and the only stem this figure is written under.
  `python figures/build_all.py --write` enforces the 5 pt floor, writes these, and copies the PDF to
  manuscript/latex/figures/fig2.pdf, which is the file the manuscript compiles. The assemble used to
  write the same composite a second time as `fig2_unification.*`, so the figure sat on disk twice
  under two names with nothing to say which one the manuscript used; that duplicate stem is gone and
  build_all now fails if the two names drift apart again.
- 2a.png ... 2f.png are standalone per-panel previews, not inputs to the composite.

## Editor lens

Panel e retains the beta-interpolation + K=1 identity in the MAIN figure (external review suggested
demoting to Extended Data; declined). C1 unification is the load-bearing defense against a
strong-vs-weak-baseline objection, so its quantitative evidence stays in the main deck.
