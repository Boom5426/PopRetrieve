> ⚠️ **SUPERSEDED IN PART, 2026-07-12.** This document predates an audit that retracted
> several numbers as artifacts of our own code, including the "5.1x structure collapse", the
> hand-entered divergence-gate positions (CD34+ was 0.95; it measures 0.186), the MoA-nDCG
> statistics computed over 165 undefined sentinel values, and the Class A/B contrast that
> compared two different scorers. **Read [CORRECTIONS.md](../CORRECTIONS.md) before using any
> number below.** Where this file and CORRECTIONS.md disagree, CORRECTIONS.md is right.
# DART figure deck: 6-figure Nature Methods style plan (merged with external review)

Editor pass 2026-07-12, merged with external NM-editor feedback (pasted-text-2026-07-12). Locked to
RESULTS_SPINE.md (claim -> Result -> figure). Plan first, build second. No em dashes. Every panel
source verified to column level. Panel counts: 5/6/6/7/7/6 = 37 main-text panels + a 4-figure
Extended Data set.

## What the external review changed (and what it did not)

ACCEPTED (the review was right):
- Panel density 5-7 per figure (NM norm 4-9); each figure a complete evidence unit
  (setup -> headline -> mechanism -> robustness), not one summary panel.
- Fig 5 REFRAME (the most valuable catch): plot the RELATIVE advantage DART-minus-mean vs
  identifiability, NOT absolute coverage MoA-nDCG. Better-separated queries are easier for ALL
  methods; the distributional advantage is near-zero. Show the zero honestly.
- Resistance coda LEAVES the main deck -> Extended Data Fig 8 (cleaner than an in-figure quarantine,
  and consistent with the manuscript demoting R6 to an R5 coda).
- New panels that repackage existing data: 3b dataset/cell-line heatmap, 4a paired A/B as the
  largest panel, 4c minority-coverage effect size (not just prose), 4g 37-task matrix, 5b
  predictor-specific gaps, 5d multi-metric diagnostics, 6a-6d HIR-Bench generator + boundary +
  info-conditions, and (initially) a 9-figure Extended Data framework, since trimmed to 4.
- New panel needing NEW compute: 5f identifiability phase diagram. COMPUTED 2026-07-12 (see below).

REJECTED / MODIFIED (editor override, with reason):
- Review wanted beta-interpolation + K=1 identity demoted to inset/Extended Data. DECLINED. C1
  unification is the load-bearing defense against "you beat a weak baseline"; we deliberately
  promoted exp06 theory from supplement to main Result 1. Keep 2a-2c in the main figure. Adopt the
  review's 2f metric-family hierarchy as a SUMMARY panel, not a replacement.
- Single-real-point energy=K=1 stays OUT of a headline claim (1 drug); synthetic multi-point curve
  carries it (2b/2c), real point marked. Agrees with review.

## Deck-level design (Nature Methods conventions, from figure-style skill)

- **Width.** Double-column 180 mm at 300 dpi (all figures 5-7 panels). Dense figures use 2-3 row
  grids with abutting subplots (wspace<=0.06) so each panel's data envelope stays >=75% (skill 3.5);
  never push data panels narrow to fit a schematic (skill 3.7). If legibility fails at 180 mm, the
  [SUPP-CAND] panels demote to Extended Data first.
- **Font ladder (exactly 3 sizes).** apply_figure_style(sizes=(8,7,6)): title/axis/series = 8;
  legend/annotation = 7; ticks = 6. Panel letters bold, top-left, outside axes, lowercase.
- **Palette threading (one binding, whole deck)** (skill 4.1-4.5):
  FOCAL blue #2166ac = distributional / DART / energy / coverage; COMP red #b2182b =
  mean-signature / CMap / collapse / null; META_GREY = context, reference lines, PCA/WTCS.
  CVD-safe, one alarm hue never a data color.
- **Titles are takeaways** (skill 2.4): plain-language claim, metric names on axes not titles.
- **Per panel:** n + unit of replication + test named (in panel if budget allows, else caption).
- **Source data:** one CSV per panel to figures/source_data/.
- **Render-then-verify** (skill 9): bbox overlap + per-panel crop perceptual check before save.

## New computation this pass: 5f identifiability phase diagram (DONE 2026-07-12)

upgrade/identifiability_phase_diagram.csv (600 rows: 6 separations x 5 budgets x 20 seeds). Real
two-source mixture (K562 dose-10000 HDAC-target vs JAK-target cells, KNOWN labels), raw-space
KMeans k=2 ARI vs true labels. Separation axis rescales inter-source centroid distance; budget axis
is cells per source {25,50,100,200,400}. Mean-ARI grid:

```
                 cells_per_source: 25    50    100   200   400
separation 1.0 (REAL)              0.063 0.079 0.075 0.068 0.072
separation 1.5                     0.316 0.274 0.191 0.175 0.175
separation 2.0                     0.935 0.614 0.356 0.305 0.301
separation 3.0                     1.000 0.996 0.936 0.777 0.643
separation 5.0                     1.000 1.000 1.000 1.000 0.999
separation 8.0                     1.000 1.000 1.000 1.000 1.000
```

Verdict (this is the mechanism panel of the whole paper): at REAL separability (row 1.0), raising
the cell budget 16-fold (25->400) does NOT lift ARI (0.063->0.072, flat). Only enlarging source
separation does (1x->3x at n=400: ARI 0.072->0.643; 5x: 0.999). So Gate 2 closure is NOT "too few
cells" and NOT "weak algorithm": real data sits in a low-separability regime where even unlimited
cells cannot recover subpopulations. This upgrades "our method is weak" to an information-limit
statement. (Honest note: at high separation small budgets score higher ARI than large ones, a
small-sample KMeans artifact irrelevant to the real regime row.)

## Message arc (skill 7.5)

1. Fig 1 concept: subpop structure should matter, but the verdict depends on the evaluator (hook).
2. Fig 2 unification: mean IS distributional at zero variance (the comparison is fair).
3. Fig 3 apparent gains: under its own objective, distributional looks strong (the temptation).
4. Fig 4 collapse: the advantage is metric-class-dependent and vanishes independently (the knife).
5. Fig 5 two-gate: collapse has a cause; structure must be preserved AND identifiable (mechanism).
6. Fig 6 HIR-Bench: formalize the failure regimes with a known-oracle benchmark (controlled map).

---

## Figure 1: Distributional differences are visible, but their value depends on the evaluator (5 panels)
Status: NEW. 1a AI, 1b-1e code/schematic. NO Fig-4 numbers (tension only).

| Panel | Content | Source | Notes |
|-------|---------|--------|-------|
| 1a [core] | Biology: two drugs, similar mean signature, opposite subpopulation responses (one has a worsening resistant minority) | AI schematic (fig1/fig1a_prompt.md) | concept art; glyph/word consistent with data panels |
| 1b [core] | Inverse-retrieval task schematic: Q -> {P_d} -> s(P_d,Q) -> drug ranking, showing mean-signature vs distributional score paths | schematic | the task diagram the review flagged as missing; editors need it |
| 1c [core] | Toy 2D: candidates whose MEANS tie with the target but whose DISTRIBUTIONS differ; d_mean ties, d_dist separates | synthetic gaussians (labeled schematic) | coincident mean marker, two clouds; FOCAL vs COMP |
| 1d [core] | Evaluation coupling: retrieval objective / evaluation metric / external outcome as 3 nodes; coupled (energy->energy regret) vs independent (energy->MoA/viability) | schematic | defines the paper's core question directly |
| 1e [core] | Metric evidence ladder: Class A objective-aligned / B task-proximal / C externally-grounded, with 2-3 examples each, and this study's coverage (A full, B partial, C none) | schematic | shows we do not confuse evidence tiers; review's strongest Fig 1 add |

## Figure 2: Mean retrieval is the variance-collapsed limit of distribution-aware retrieval (6 panels)
Status: NEW (absorbs exp06 theory). Editor override: theory STAYS in main figure.

| Panel | Content | Source | Notes |
|-------|---------|--------|-------|
| 2a [core] | Unified model X = mu + lambda*eps: lambda=0 mean-collapsed, lambda=1 observed; s_dist -> s_mean as lambda->0 | schematic + formula | small distribution insets, not full axes |
| 2b [core] | Variance-scaling illustration: same population, residual variance scaled lambda in {0,0.25,0.5,1}, MEAN fixed | synthetic | "not new data, only heterogeneity changes" |
| 2c [core] | Retrieval score vs lambda: mean score flat, distributional score varies, coincide at lambda=0 (the zero-variance claim, direct numerical check) | exp06 degenerate_limit_synthetic.csv (energy vs t_spread, converges to two_dmu floor) | the review's must-add; energy 34.1->98.5 as spread 1.0->0.0 toward mean floor 98.5 |
| 2d [core] | Operation identity: mean_cosine = cmap_cosine = 0.388492 exactly; WTCS 0.4635 is the rank-based sibling (related, not identical) | exp08 summary.csv | 3 lollipops + identity bracket; GREY WTCS |
| 2e [core] | beta-interpolation spectrum: D_beta 0.7125 (beta->0 mean-agg) to 1.300 (beta->inf worst-case); energy = K=1 coverage point on the same axis | exp06 beta_interpolation.csv (11) + degenerate_limit_synthetic.csv K=1 rows | the continuum made quantitative; real Panobinostat point marked, caption notes n=1 real |
| 2f [SUPP-CAND] | Metric-family hierarchy summary: mean / energy / MMD / SW / coverage / worst-case, arrows labeled zero-variance, K=1, beta->0, beta->inf | schematic | the review's 2f; concept summary, demote if dense |

## Figure 3: Objective-aligned metrics reveal strong distributional signal (6 panels)
Status: REBUILD from fig2_class_a_gains + expand. This gain is Class A (objective-aligned); the
figure must not imply independent validation.

| Panel | Content | Source | Notes |
|-------|---------|--------|-------|
| 3a [core] | Overall Hit@1 ladder: energy 0.837 top to mean=CMap 0.389 bottom (the gap) | exp08 summary.csv | FOCAL/COMP/GREY; 0.837 value-on-mark |
| 3b [core] | Hit@1 decomposed by dataset/cell-line/task (heatmap, scorer x task) | exp08 summary.csv (56 rows) | guards against K562 driving the mean alone; review's must-add |
| 3c [core] | Query-level paired advantage distribution (Delta objective-aligned utility, full ECDF/raincloud) | exp12 per_query_scores.csv | not just a mean |
| 3d [core] | Regret-reduction distribution +0.119 (coverage_worst on recommended), zero line + positive fraction + bootstrap CI | exp12 per_query_scores.csv (n=621) | median +0.119, Wilcoxon p=4.3e-56, 72% |
| 3e [core] | Gain vs heterogeneity: Delta Class-A score vs response divergence / subpop variance | exp01 + exp12 | shows the gain comes from distribution structure, not algorithm noise |
| 3f [SUPP-CAND] | Class-A metric robustness: energy/MMD/SW/coverage regret rank-consistency (all still Class A, labeled so) | exp08 summary.csv | answers "positive only because energy scored by energy?"; demote if dense |

## Figure 4: The apparent advantage does not transfer across metric classes (7 panels, the knife)
Status: KEEP fig3_metric_collapse core + expand. Densest figure (allowed). 4a is the largest panel.

| Panel | Content | Source | Notes |
|-------|---------|--------|-------|
| 4a [core] | Paired Class A (+0.119) vs Class B (-0.013) reversal, per query/aggregate; LARGEST panel | exp12/exp08 | the sign flip is the paper's headline |
| 4b [core] | MoA-nDCG query-level distribution (median, CI, positive fraction, per-cell-line), not just -0.013 | exp12 | full distribution behind the mean |
| 4c [core] | Minority-coverage effect size by divergence quartile: lowest +0.0009, highest +0.0018 (significant but negligible) | coverage_by_identifiability + exp12 | draw the negligibility, do not only say it |
| 4d [core] | Recommended (+0.119, n=621) vs non-recommended (+0.122, n=133) full distributions | exp12 recommendation_vs_outcome.csv | non-rec = mean_or_no_call only |
| 4e [core] | Gate axes vs true divergence: structure_reliability rho=-0.21 (wrong direction) and preference_conflict rho=+0.18 (too weak), two scatters | merged_query_divergence (765) | one axis wrong, one too weak |
| 4f [core] | Binary recommendation does not separate divergence: box by gate-recommended vs not, Mann-Whitney p=0.090 | merged_query_divergence | distinct from 4d: gate cannot distinguish divergence |
| 4g [core] | 37 real tasks as dataset x task matrix, color centered at 0, summary 0/37 dominant | exp13 projection.csv (37) | stronger than 37 grey dots |

## Figure 5: Structure preservation and identifiability constrain distribution-aware retrieval (7 panels)
Status: KEEP fig4_information_condition core + REFRAME 5g + NEW 5f. Full mechanism chain:
prediction -> structure preservation -> identifiability -> decision gain.

| Panel | Content | Source | Notes |
|-------|---------|--------|-------|
| 5a [core] | Predict-then-rank schematic: observed vs predicted candidate population -> DART/mean ranking | schematic | why predictor quality limits retrieval |
| 5b [core] | Predictor-specific retrieval gaps: average-effect -0.004, nearest-neighbor -0.097, latent-linear -0.029 | exp09 | forest-style; extensible to SOTA predictors later |
| 5c [core] | Subpopulation-variance preservation, per predictor: predicted/real ratio (real 0.046 vs predicted 0.009 = 5.1x collapse) | exp09 structure diagnostics | paired dots per predictor, not one bar |
| 5d [core] | Multi-dim structure diagnostics heatmap: predictor x {variance ratio, diversity, isotropy}, predicted/real | exp09_structure_diagnostics.csv (960) | collapse not reliant on one metric |
| 5e [core] | Identifiability recovery: 9 unsupervised methods on controlled two-source mixture with KNOWN source labels; seed points + median + null; best ARI 0.10, none >0.15 | upgrade/controlled_mixture_ari.csv | reworded per review (two-source w/ known labels, not "known bimodal"); ARI=0.5 shown as reference not "accepted threshold" |
| 5f [core] | NEW identifiability phase diagram: cells-per-source {25..400} x separation {1..8}, color ARI; real-data anchor at separation=1 (ARI ~0.07 flat in budget) | upgrade/identifiability_phase_diagram.csv (600) | THE mechanism panel: is it the algorithm or the data regime? Answer: data regime |
| 5g [core] | REFRAME: DART-minus-mean Delta MoA-nDCG vs identifiability (silhouette/divergence/tertile); near zero -> draw the zero | upgrade/conditional_advantage (600 queries) | "better-separated queries are easier overall but show no stable distributional advantage"; replaces absolute-coverage 5c |

## Figure 6: HIR-Bench formalizes when distributional retrieval can and cannot help (6 panels)
Status: NEW, code-direct. Resistance analysis MOVED OUT to Extended Data Fig 8.

| Panel | Content | Source | Notes |
|-------|---------|--------|-------|
| 6a [core] | HIR-Bench generative model: two subpops, candidate treatments, latent welfare (A,B), mixture alpha, conflict, information condition | schematic | entry point for the phase diagram |
| 6b [core] | Analytic boundary alpha* = B/(A+B) with a geometric decision interpretation (alpha < vs > alpha*) | exp11 theoretical_boundary.csv | show decision meaning, not just the formula |
| 6c [core] | Full phase diagram over (alpha, conflict/lambda), color = Delta latent welfare, analytic boundary overlaid | exp11 phase_diagram_source.csv (108) | diverging map centered at boundary (skill 4.4) |
| 6d [core] | Three information conditions side by side (observed / predicted_structure / predicted_mean): DART gain or failure rate | exp11 method_dominance.csv (16) | structure preservation shifts the applicable region |
| 6e [SUPP-CAND] | QC + transfer: no-conflict flip rate 0, median boundary margin 0.29, predicted_mean -> 100% no-DART | exp11 sanity_checks + uncertainty_band | compact quality-control panel |
| 6f [core] | Failure predictability: ROC AUC 0.645 (FULL 13,440-cell, NOT QUICK 0.5) + top-feature inset (top-k disagreement). Title: "moderately predictable" | exp11 phase_grid_predictability (FULL) | caption states FULL provenance; honest title, not "gate succeeds" |

---

## Extended Data (4 figures; each blocks one anticipated reviewer attack)

Trimmed from an earlier 9-figure scope (user decision 2026-07-12). Rationale: for an
audit paper with a negative core, a large Extended Data set reads as insecurity and gives
reviewers more surface to attack. Each ED figure must either block a predictable attack or
carry load-bearing reproducibility, nothing else. Deleted: beta-interpolation/K=1 detail
(already in main Fig 2e), Fig 3 dataset decomposition (already in main Fig 3b heatmap),
HIR-Bench provenance/ablations (now a Methods note + server README). Dataset scale detail
demotes to Supplementary Table 1.

| ED Fig | Content | Blocks the attack | Source |
|--------|---------|-------------------|--------|
| ED 1 | Reproducibility basis: dataset ladder + DART metric definitions + metric correlation matrix (merged old ED1+ED2) | "your data/metrics are non-standard" | fig1_E_dataset_ladder + exp08 per_query_scores |
| ED 2 | Class B negative robustness: full statistics + power analysis + bootstrap CIs | "the null is just underpowered" (most important for a negative paper) | exp16/exp17 power_analysis |
| ED 3 | Identifiability robustness: 9 clustering methods x k/space sensitivity + predictor structure-collapse diagnostics (merged old ED6+ED7) | "you just clustered badly; another method would find the subpops" | upgrade/kmeans_quality + subpop_identifiability + exp09 structure diagnostics |
| ED 4 | Resistance exploratory: Frangieh contexts, AXL/mesenchymal +0.134 p=0.003, IFN p=1.9e-6, antigen-presentation p=0.04, minority-rescue near null | transparent home for the exploratory signal (kept out of main deck) | exp15 enrichment_summary + divergence_marker_enrichment |

Supplementary Table 1: dataset scale, preprocessing, query construction (SciPlex3/Frangieh/CD34) + configs.

## Consistency rules (whole deck)

1. Palette bound once (FOCAL distributional, COMP mean/collapse, GREY context).
2. Every headline number traces to reference/manuscript_evidence_table.md. Traps: HIR AUC 0.645 FULL
   not 0.5 QUICK; +0.119 = coverage_worst MEDIAN on recommended; non-rec +0.122 = mean_or_no_call
   only; 5f real-data anchor = separation_scale 1.0 row.
3. A conclusion appears at most twice per figure (aggregate + decomposition), never 4 chart types of
   one number (review's redundancy rule).
4. mean=CMap=0.389 identity: Fig 2d (structure) and Fig 3a (ladder floor) are DIFFERENT uses.
5. Fig 1 sets tension only, no Fig 4 collapse numbers.
6. Class A gains (Fig 3) never captioned as independent validation.

## code-direct vs AI split

- AI: Fig 1a only (biological schematic). Prompt to figures/fig1/fig1a_prompt.md.
- Schematic (code/vector, no AI): 1b, 1c, 1d, 1e, 2a, 2b, 2f, 5a, 6a, 6b.
- Data panels (code-direct): all remaining, code kept in figures/figN/.
- Reuse+renumber: Fig 4 core (=current fig3_metric_collapse), Fig 5 a-e (=current
  fig4_information_condition, + new 5f/5g). Fig 3 rebuilds from fig2_class_a_gains.

## Execution order (after sign-off)

1. Fig 2 (theory anchor) + Fig 5f/5g (the new mechanism panels, data now in hand).
2. Fig 6 (HIR-Bench) + Fig 1 schematics (1b-1e).
3. Fig 3 rebuild + Fig 4 expand.
4. Fig 1a AI prompt handed to you; drop returned image into fig1/.
5. Per-figure README (message + panel table + verified numbers + source CSV) per AllelePerturb
   template; extract each panel's code into figures/figN/.
6. Extended Data figures ED1-ED4 (trimmed from 9; see ED section).

## Open decisions for you

- ED framework: TRIMMED to 4 figures (user decision 2026-07-12), each blocking one reviewer attack.
- Fig 5 is now 7 panels with 5f+5g both new; if too dense, 5f phase diagram or 5b predictor-gaps is
  the demote candidate (5f is the stronger keep).
- Any panel you want promoted from [SUPP-CAND] to core, or cut.


## Style update (2026-07-12): Nature Methods house style adopted

All six figures now use the shared house config in `figstyle.py`, matching the AllelePerturb
manuscript template:
- Palette: FOCAL #5185C0 (distributional/DART), COMP #E99D4E (mean/collapse), GREY #7A7A7A (context),
  INK #1A1A1A axes. Soft Okabe-Ito set, not the earlier saturated #2166ac/#b2182b diverging pair.
- Signed-advantage heatmaps (4g, 5d, 6c) use the house orange-white-blue diverging map (DIVMAP),
  blue = DART-positive.
- Titles: regular descriptive phrases (what the panel shows), not bold declarative sentences.
- Geometry: true print size, 183 mm double-column (7.2 in), 6-7 pt type, 0.5 pt spines.
- Deliverable: editable-text vector PDF (fonttype 42) + high-dpi PNG.

One edit in `figstyle.py` recolours the whole deck. Each panel file also carries the palette inline
so it stays standalone-runnable.
