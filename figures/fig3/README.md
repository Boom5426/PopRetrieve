# Figure 3: the apparent gains do not survive independent evaluation

One-line message: the Class-A advantage (Fig. 2) does not survive a change to metrics that do not
share the retrieval objective. The SAME queries flip sign from Class A to Class B, the
information-condition gate correlates the WRONG way with true divergence, the real-data coverage
advantage is statistically real but negligible and confined to constructed mixtures, and on the one
independent (Class C) oracle where the distributional score does win, a scalar comparing no
distributions reproduces most of the win.

Panel letters and every number below match the Fig. 3 caption in
`manuscript/latex/PopRetrieve_manuscript.tex`. If a number here and a number there ever disagree, the
manuscript is the authority and this file is the bug.

## Panels

| Panel | Message | Source | Status |
|-------|---------|--------|--------|
| a | Same 480 paired queries: Class A regret reduction median +0.129 (73%>0) vs Class B MoA-nDCG mean -0.037 (35%>0) | figures/source_data/fig3a_classA_vs_classB.csv | done |
| b | MoA-nDCG gain ECDF per cell line; median 0.000 in all three | figures/source_data/fig3a_classA_vs_classB.csv | done |
| c | Minority-coverage gain by divergence quartile: significant, and negligible | results/exp16_gate_diagnosis/_merged_query_divergence.csv | done |
| d | Recommended +0.119 (n=621) vs non-recommended +0.122 (n=133): the gate does not concentrate the gain | results/exp12_partial_observed_retrieval/recommendation_vs_outcome.csv | done |
| e | Gate structure-reliability vs true divergence, Spearman rho = -0.21 (WRONG sign) | results/exp16_gate_diagnosis/_merged_query_divergence.csv | done |
| f | Binary recommendation does not separate true divergence: Mann-Whitney p = 0.09 | results/exp16_gate_diagnosis/_merged_query_divergence.csv | done |
| g | All 239 real-data tasks, one dot per task: overall mean +0.0018, positive tail only in the constructed cross-line mixtures | results/exp13_real_data_projection/projection.csv | done |
| h | Class C functional oracle: energy +0.276 beats the mean incumbent +0.083, but a query-dependent magnitude scalar reaches +0.232 and the partial leaves +0.097 | figures/source_data/fig3hi_class_c_functional.csv | done |
| i | Per query, energy vs that scalar: energy better on 62 of 103 queries (nominal Wilcoxon p = 0.073, anticonservative) | figures/source_data/fig3hi_class_c_functional.csv | done |
| j | Achieved power in the highest divergence quartile: 1.00 for minority coverage, 0.06 for MoA-nDCG | results/exp17_true_divergence_subset/power_analysis.csv | done |
| k | Queries needed for 80% power: 45 (observed n=191) for minority coverage, 20,844 (observed n=143) for MoA-nDCG | results/exp17_true_divergence_subset/power_analysis.csv | done |
| l | The same four rankings scored against ABSOLUTE GDSC2 potency: energy -0.52 and raw mean cosine -0.53 change sign, control-subtracted mean cosine collapses to +0.10, response magnitude alone wins at +0.69 | figures/source_data/fig3hi_class_c_potency.csv | done |
| m | Spearman rho between the query-candidate energy distance and the candidate response magnitude, median +0.791 | figures/source_data/fig3hi_class_c_potency.csv | done |

## Verified numbers
- 4a: leave_drug_out subset, n=480 paired; Class A regret reduction median +0.1292 (73.1%>0); Class B MoA-nDCG gain mean -0.0369, median 0.0000 (35.0%>0); Class A max +2.82 (the panel view stops at +1.42 and says so).
- 4c: quartile MEANS +0.0042, +0.0050, +0.0062, +0.0056 (bars, with s.e.m.); quartile MEDIANS +0.0009, +0.0015, +0.0017, +0.0018 (dashes). The manuscript quotes the medians; the panel draws both, because the earlier "<0.002" caption was true of the medians only and was printed over the means.
- 4d: recommendation_vs_outcome.csv, DART_coverage_worst: recommended median +0.11900 (n=621), mean_or_no_call +0.12194 (n=133).
- 4e: structure_reliability vs true_divergence Spearman rho = -0.2110, p = 3.79e-09, n = 765 unique query keys (computed in the panel, not hard-coded).
- 4f: recommended median divergence 1.66 (n=621) vs not recommended 1.68 (n=144), Mann-Whitney p = 0.090 (computed in the panel).
- 4g: exp13 projection.csv, 239 tasks. Dataset means: SciPlex3 cross-line +0.00426 (n=90), SciPlex3 within-line +0.00038 (n=90), CD34+ +0.00027 (n=12), Frangieh +0.00042 (n=23), SciPlex3 predicted candidates +0.00003 (n=24); overall +0.0018. Two circled tasks (A549->MCF7 Abexinostat, Belinostat) are the only ones above the 0.01 threshold in 10 of 10 seed resamples.
- 3j/3k: exp17 power_analysis.csv, Q4 stratum. minority_state_coverage n=191, observed mean gap +0.005608, s.d. 0.013496, achieved power 0.99992, n for 80% power 45.5. moa_ndcg n=143, observed mean gap +0.003166, s.d. 0.16317, achieved power 0.0562, n for 80% power 20,844.3 (data_sufficient False). The two s.d. are the whole story: the same size of gap is decisive on one metric and invisible on the other because the MoA-nDCG gap is twelve times noisier.
- 3l/3m: fig3hi_class_c_potency.csv, the v2 analysis with the corrected energy sign. Medians against absolute GDSC2 AUC: energy -0.52, mean cosine raw -0.53, mean cosine control-subtracted +0.10, response magnitude alone +0.69. Energy distance vs candidate response magnitude, median rho +0.791.
- 4h/4i: 103 leave-one-drug-out queries, SciPlex3 x GDSC2 at 10 uM. Medians: energy +0.276, mean cosine control-subtracted +0.083, mean cosine raw +0.241, response-magnitude match +0.232, potency match +0.399, energy partialled on magnitude match +0.097. Energy better on 62 of 103 queries.

## Honesty notes
- This is the load-bearing negative. Every panel shows a DIFFERENT way the Class-A gain fails to
  transfer to oracle-independent evaluation. No panel is padding.
- 4a/4b: the flip is measured on the SAME queries, so it is not a population difference; it is the
  metric changing the verdict.
- 4c: the minority-coverage gain IS statistically significant (that is why it is not simply "zero"),
  and it is a fraction of a metric whose own values run 0.89 to 0.99; the panel states both.
- 4e: the negative correlation is the key. The gate axis moves opposite to the quantity it should
  track, so it cannot be a valid trust signal.
- 4g: the panel plots the distribution, never a count of "dominant" tasks. The conventional 0.01
  threshold sits inside the noise band of this difference, and the exp13 seed is not a replicate.
- 3j/3k: a power analysis in a MAIN figure normally reads as a sign that the headline result is
  thin, which is why these two sat in Extended Data. Here the headline result IS the null, so the
  power analysis is the evidence and not an apology for it. Panel k reports 20,844 rather than
  rounding to "roughly 20,000": the number is what makes the point, and 143 queries is what exists.
- 3l/3m: these two do not measure PopRetrieve. They measure the endpoint, and they are drawn beside
  h and i so the one external win in the study is read next to the endpoint choice that produced
  it. Row 5 is not evidence that retrieval fails under potency; a similarity retriever handed a
  weak query SHOULD return weak candidates.
- 3l: "every ranking inverts" is the phrasing ed5.py uses and it overstates panel l. Three of the
  four medians move the way the magnitude story predicts, but the control-subtracted mean cosine
  goes from +0.083 under functional similarity to +0.105 under potency, which is a collapse toward
  zero, not a sign change. The caption and the ledger above say sign change only of energy and raw
  mean cosine.
- 4h/4i: the oracle is drug-drug FUNCTIONAL SIMILARITY (GDSC2 dose-response AUC profile
  correlation, the three SciPlex3 lines held out), not measured potency. The absolute-potency
  comparison is the confounder audit in row 5 (panels l and m), and it is a control on row 3, not
  a competing result. Until 2026-07-26 the row-3 banner and the h/i titles still described that
  withdrawn potency framing and contradicted the bars beneath them; they now state what is plotted.

## Authored at print size (2026-07-26 re-cut, 2026-08-30 height re-cut)

The figure enters the manuscript as `\includegraphics[width=\textwidth]` into a 6.93 in text block.
It used to be authored 11.7 in wide, so LaTeX scaled it by 0.59 on the page and its 5.6-8 pt source
text printed at 3.3-4.7 pt, under the 5 pt floor Nature Portfolio enforces at FINAL printed size.
`figures/build_all.py` measures NOMINAL point size, so it called the figure clean while the printed
page failed. The canvas is now **6.90 x 8.59 in**, the width it is printed at: the scale factor is
1.0 and nominal size is printed size. Panel geometry lives in `fig3_assemble.py` in INCHES, because
at 1:1 the room a y-axis label or a panel letter needs is a fixed physical quantity.

Height grew from 4.83 to 8.59 in on 2026-08-30, when the caption moved to the page following the
figure and freed the graphic from its roughly 5 in cap; the ceiling is 9.30 in. The width did not
move and cannot: it is the only number that sets printed point size. `build()` now also calls
`figstyle.pin_canvas`, so the exported media box is the authored canvas (6.92 in with
`savefig.pad_inches`) instead of whatever the ink happened to span, which was 6.878 in.

No data value, statistic, panel or panel letter changed. What changed is geometry, plus on-panel
prose that the Fig. 3 caption already carries:

| Panel | Cut or moved | Where it now lives |
|-------|--------------|--------------------|
| a | summary blocks moved from beside the violins to above them; view opened to $+1.8$, left spine still stops at the plotted $+1.42$ | on panel |
| b | per-line n moved out of the key labels into the median note (key order); key to the upper left, note to the lower right | on panel |
| c | four-line key rewrapped; head-room opened to 0.0135 | on panel |
| e | note moved out of a bolted-on right-hand strip (`xlim` ran to 2.62 with data ending at 1.90) into the data-free band above the cloud; x axis cropped to the data | on panel, shortened |
| f | view opened to 2.22 so the test statistic clears the two median labels | on panel |
| g | second x-label line ("all 239 tasks; overall mean ...; circled, above 0.01 in 10 of 10 seeds") | Fig. 3 caption; diamond key kept on panel |
| h | two-line gloss on the dotted remainder; x-label line 2 (GDSC2 provenance) | caption + row-3 banner; the number $+0.097$ stays on panel |
| i | "the scalar is better here" (it lay across the cloud); win count moved from an in-axes label into the title, **computed** from the source table | caption; title carries 62 of 103 |

QA at print size: zero text-text bbox collisions, nothing outside the canvas, smallest nominal (and
therefore printed) size 5.2 pt, both instances inherited from the adopted panels: panel j's
"80% power" note (`ed_panels.draw_ed2a`) and panel l's three-marker key (`ed5.draw_a`). The floor
is 5 pt and `figstyle.save` refuses to write below it.
Known residuals:

- panel a: the stat blocks and the truncation note sit over the Class-A violin's hairline upper
  tail, as they did before the re-cut.
- panel k: "observed n=191" and "45" clear each other by 0.53 pt. Both y positions are computed
  from the data inside `ed_panels.draw_ed2b`, so the only lever this file has is row height, and
  the clearance scales with it: 1.6 pt at axh 1.55, 3.8 pt at 2.03, 4.4 pt at the 2.19 the
  Extended Data version had. Recovering 4 pt costs the whole remaining height budget and makes two
  two-bar panels the largest thing on the page, so the row stays at 1.32 in. The glyphs do not
  touch even though the boxes nearly do.

## Files
- fig3a.py ... fig3i.py : per-panel draw functions for a-i (each runs standalone). `fig3_assemble.TITLES` is
  what the composite renders; where a panel file also sets a title it is the same claim, wrapped, and
  h and i import their titles from the panel modules (`TITLE_4H`, `TITLE_4I`) so there is one copy.
- fig3_assemble.py : the 13-panel, 5-row layout in inches; it owns `TITLES`, `ROW_LABELS` and the
  module-level `STEM`. Panels j-m have no fig3\*.py of their own: they are imported from
  `figures/edfigs/ed_panels.py` (j, k) and `figures/ed5/ed5.py` (l, m), which is where the retired
  Extended Data deck drew them, so the panel here and the analysis it came from cannot drift.
- fig3_collapse.{pdf,svg,png} : the composite, and the only stem this figure is written under.
  `python figures/build_all.py --write` enforces the 5 pt floor, writes these, and copies the PDF to
  manuscript/latex/figures/fig3.pdf, which is the file the manuscript compiles.
- 3a.png ... 3i.png are standalone per-panel previews, not inputs to the composite.
