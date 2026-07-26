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

## BLOCKER: this deck is not synced to the manuscript, and must not be until it is re-cut

`manuscript/latex/figures/edfig{1..4}.pdf` are the **2026-07-12** build. Running `ed_panels.py`
today produces different files, and copying them over would be a **regression**, not an update.

The main deck (Figs 1-6) was re-authored at its printed width so that nominal size equals printed
size; see the geometry docstring in `fig6/fig6_assemble.py`. This deck never received that
treatment. Its canvases are declared in `FIGS` at 10.2-12.6 in against a 6.93 in (498.6 pt) SI
text block, so `\includegraphics[width=\textwidth]` scales them **down** and the type prints far
below the Nature Portfolio 5 pt floor:

| Fig | canvas | scale at `\textwidth` | min nominal | **printed** |
|-----|--------|----------------------|-------------|-------------|
| ED1 | 734.4 pt | 0.679 | 5.0 pt | **3.39 pt** |
| ED2 | 734.4 pt | 0.679 | 5.0 pt | **3.39 pt** |
| ED3 | 907.2 pt | 0.550 | 5.0 pt | **2.75 pt** |
| ED4 | 734.4 pt | 0.679 | 5.2 pt | **3.53 pt** |

These figures are also outside `build_all.py`, so no gate reports this: `FIGS` in `build_all.py`
covers only 1-6, and `assert_min_fontsize` measures the nominal size anyway, which is the exact
blind spot documented for the main deck.

Fixing it means re-authoring at 6.93 in, which is a re-layout and not a resize: at 0.68x canvas
the labels grow 1.47x relative to their panels and will collide, which is why the main deck's
re-cut rewrapped every label rather than shrinking type. Until that is done, the shipped SI keeps
the 07-12 build, and **two label edits made on 2026-07-26 (ED2c and ED4c, "DART - mean" ->
"distributional - mean", to match the relabelled main deck) are present in this source and not yet
visible in the SI PDF.**

## Files
- ed_panels.py (all draw functions), ed1..ed4 .{png,pdf}
- source data: ../source_data/ed*.csv
