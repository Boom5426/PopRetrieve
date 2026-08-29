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

## Verified numbers
- 4a: leave_drug_out subset, n=480 paired; Class A regret reduction median +0.1292 (73.1%>0); Class B MoA-nDCG gain mean -0.0369, median 0.0000 (35.0%>0); Class A max +2.82 (the panel view stops at +1.42 and says so).
- 4c: quartile MEANS +0.0042, +0.0050, +0.0062, +0.0056 (bars, with s.e.m.); quartile MEDIANS +0.0009, +0.0015, +0.0017, +0.0018 (dashes). The manuscript quotes the medians; the panel draws both, because the earlier "<0.002" caption was true of the medians only and was printed over the means.
- 4d: recommendation_vs_outcome.csv, DART_coverage_worst: recommended median +0.11900 (n=621), mean_or_no_call +0.12194 (n=133).
- 4e: structure_reliability vs true_divergence Spearman rho = -0.2110, p = 3.79e-09, n = 765 unique query keys (computed in the panel, not hard-coded).
- 4f: recommended median divergence 1.66 (n=621) vs not recommended 1.68 (n=144), Mann-Whitney p = 0.090 (computed in the panel).
- 4g: exp13 projection.csv, 239 tasks. Dataset means: SciPlex3 cross-line +0.00426 (n=90), SciPlex3 within-line +0.00038 (n=90), CD34+ +0.00027 (n=12), Frangieh +0.00042 (n=23), SciPlex3 predicted candidates +0.00003 (n=24); overall +0.0018. Two circled tasks (A549->MCF7 Abexinostat, Belinostat) are the only ones above the 0.01 threshold in 10 of 10 seed resamples.
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
- 4h/4i: the oracle is drug-drug FUNCTIONAL SIMILARITY (GDSC2 dose-response AUC profile
  correlation, the three SciPlex3 lines held out), not measured potency. The absolute-potency
  comparison is a confounder audit and lives in Extended Data. Until 2026-07-26 the row-3 banner
  and the h/i titles still described that withdrawn potency framing and contradicted the bars
  beneath them; they now state what is plotted.

## Authored at print size (2026-07-26 re-cut)

The figure enters the manuscript as `\includegraphics[width=\textwidth]` into a 6.93 in text block.
It used to be authored 11.7 in wide, so LaTeX scaled it by 0.59 on the page and its 5.6-8 pt source
text printed at 3.3-4.7 pt, under the 5 pt floor Nature Portfolio enforces at FINAL printed size.
`figures/build_all.py` measures NOMINAL point size, so it called the figure clean while the printed
page failed. The canvas is now **6.90 x 5.36 in**, the width it is printed at: the scale factor is
1.0 and nominal size is printed size. Panel geometry lives in `fig3_assemble.py` in INCHES, because
at 1:1 the room a y-axis label or a panel letter needs is a fixed physical quantity.

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
therefore printed) size 5.6 pt. Known residual: in panel a the stat blocks and the truncation note
sit over the Class-A violin's hairline upper tail, as they did before the re-cut.

## Files
- fig3a.py ... fig3i.py : per-panel draw functions (each runs standalone). `fig3_assemble.TITLES` is
  what the composite renders; where a panel file also sets a title it is the same claim, wrapped, and
  h and i import their titles from the panel modules (`TITLE_4H`, `TITLE_4I`) so there is one copy.
- fig3_assemble.py : the 9-panel, 3-row layout in inches; it owns `TITLES`, `ROW_LABELS` and the
  module-level `STEM`.
- fig3_collapse.{pdf,svg,png} : the composite, and the only stem this figure is written under.
  `python figures/build_all.py --write` enforces the 5 pt floor, writes these, and copies the PDF to
  manuscript/latex/figures/fig3.pdf, which is the file the manuscript compiles.
- 3a.png ... 3i.png are standalone per-panel previews, not inputs to the composite.
