> ⚠️ **SUPERSEDED IN PART, 2026-07-12.** This document predates an audit that retracted
> several numbers as artifacts of our own code, including the "5.1x structure collapse", the
> hand-entered divergence-gate positions (CD34+ was 0.95; it measures 0.186), the MoA-nDCG
> statistics computed over 165 undefined sentinel values, and the Class A/B contrast that
> compared two different scorers. **Read [CORRECTIONS.md](../../CORRECTIONS.md) before using any
> number below.** Where this file and CORRECTIONS.md disagree, CORRECTIONS.md is right.
> ⚠️ **SUPERSEDED, 2026-08-29.** The Extended Data deck is now three figures, not seven, built by
> [`ed_consolidated.py`](ed_consolidated.py); that file's docstring is the current map and names
> the five panels that were deleted rather than merged. Everything below describes the retired
> layout and is kept for provenance.

# Extended Data figures (ED1-ED4)

Trimmed from a 9-figure scope to 4 (user decision 2026-07-12). Each ED figure blocks one
anticipated reviewer attack; nothing is padding. Deleted from the earlier scope:
Fig 2 dataset decomposition (already main Fig 2b), HIR-Bench provenance/ablations (now Methods note + server README). Dataset
scale detail also lives in Supplementary Table 1.

**ED1 gained panels d and e on 2026-08-29**, when the main deck went from six figures to five.
The retired main-text figure argued that mean-signature retrieval is the zero-variance limit of
population retrieval. It carried no measured value from real cells: every claim on it was either
an algebraic identity proved in Methods or a definitional property of the coverage score, and
two of its six panels duplicated ED1b and ED1c. ED1c in particular is the STRONGER form of the
identity that figure spent a panel on: it shows mean cosine and CMap cosine agreeing at all
54,180 query-candidate scores (Spearman rho = 1.000 to ten decimal places), where the retired
panel showed three macro-means, and equal means do not establish an identity. Its two surviving
panels are ED1d (the lambda -> 0 collapse) and ED1e (the beta interpolation); its schematic
panels and its identity panel were dropped, not moved.

| Fig | Panels | Message | Blocks |
|-----|--------|---------|--------|
| ED1 | a dataset scale, b metric definitions, c metric correlation (54,180 queries), d lambda -> 0 collapse, e beta interpolation | mean-cosine == CMap-cosine (rho=1.00); energy/coverage form a separate near-orthogonal block; mean retrieval is the zero-variance endpoint (98.50 vs a 98.50 mean-distance endpoint) and beta spans 0.7125 to 1.300 | "non-standard data/metrics", "your score family is ad hoc" |
| ED2 | a Q4 power, b sample size for 80%, c null across divergence strata | objective-aligned metric fully powered (0.9999); objective-independent needs n=27,794; null holds everywhere | "the negative is underpowered" |
| ED3 | a 9-method ARI, b silhouette, c predictor collapse, d phase diagram | no clustering recovers subpops (best ARI 0.106); only separation not budget lifts ARI | "you clustered badly" |
| ED4 | a program enrichment, b AXL signal, c minority rescue | exploratory resistance signal (AXL r=0.134, IFN p=1.9e-6), minority rescue near null | (exploratory transparency) |

## Provenance notes
- ED4b uses PEARSON r (0.134) to match exp15 `corr_divergence_enrichment`, NOT Spearman
  (which gives 0.197 on the same data). The manuscript cites the Pearson value.
- ED1d/ED1e read results/exp06_theory_limits/ directly (degenerate_limit_synthetic.csv rows
  prop1_spread, and beta_interpolation.csv). Both are seeded synthetic constructions that
  verify a derivation, not measurements on cells, and the caption says so. The release
  mirrors are source_data/ed1d_energy_collapse.csv and ed1e_beta_spectrum.csv.
- ED2 power/stratified from exp17_true_divergence_subset (power_analysis.csv,
  divergence_stratified.csv).
- ED3 predictor collapse from exp09 structure diagnostics (real subpop_variance_ratio 0.046
  vs predictors ~0.009). Phase diagram from upgrade/identifiability_phase_diagram.csv.

## Print geometry: resolved 2026-08-28

These four figures used to be authored far wider than the page. `FIGS` declared canvases of
10.2-12.6 in against a 6.95 in SI text block, and each enters with
`\includegraphics[width=\textwidth]`, so LaTeX scaled them **down** and every nominal point size
shrank with it:

| Fig | old canvas | old scale | min nominal | old **printed** |
|-----|-----------|-----------|-------------|-----------------|
| ED1 | 10.2 in | 0.68 | 5.0 pt | **3.4 pt** |
| ED2 | 10.2 in | 0.68 | 5.0 pt | **3.4 pt** |
| ED3 | 12.6 in | 0.55 | 5.0 pt | **2.8 pt** |
| ED4 | 10.2 in | 0.68 | 5.2 pt | **3.5 pt** |

All four are now authored at 6.9 in, so the scale factor is 1.0 and nominal size is printed size.
Width had to be paid for: ED1, ED2 and ED4 keep one row and gained height, and ED3 became a 2 x 2
grid, because four panels across 6.9 in leaves 1.7 in each, narrower than several of that figure's
own axis labels.

`build_ed.py` now **gates** this. It reads each built PDF's media box and fails the build if a
canvas exceeds the text block, because that is the condition under which nominal size equals
printed size. The deck's other gate, `assert_min_fontsize`, measures nominal sizes and is blind to
the scale factor by construction, which is why nothing reported the defect for months.

The shipped `manuscript/latex/figures/edfig{1..4}.pdf` are synced to this source again, so the two
label edits made on 2026-07-26 (ED2c and ED4c, "PopRetrieve - mean" -> "distributional - mean")
are now visible in the SI.

## Files
- ed_panels.py (all draw functions), ed1..ed4 .{png,pdf}
- source data: ../source_data/ed*.csv
