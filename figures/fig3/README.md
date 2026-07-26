# Figure 3: Under objective-aligned metrics, distributional retrieval looks decisively stronger

One-line message: under objective-aligned (Class-A) evaluation, distribution-aware retrieval shows
large gains over mean-signature retrieval. This is genuine but Class A (the metric shares the
retrieval objective); the figure must NOT be read as independent validation, which Fig 4 addresses.

## Panels

| Panel | Panel title (must stay true of the manuscript) | Source | Status |
|-------|-----------------------------------------------|--------|--------|
| a | "Distributional scorers top the Hit@1 ladder": energy 0.837 > ... > mean = CMap 0.388 | exp08 summary.csv | done |
| b | "The advantage does not hold on Frangieh": mean/CMap 0.600 beats energy 0.578, and is the best of all eight scorers there | exp08 summary_by_task.csv | done |
| c | "72% of all 765 queries improve, median +0.118" | exp12 per_query_scores.csv | done |
| d | "The gate does not concentrate the gain": +0.119 (n=621) vs +0.122 (n=133) | exp12 recommendation_vs_outcome.csv | done |
| e | "Energy retrieval degrades as subpopulations merge" | fig3e_alpha_crossover.csv | done |
| f | "All five DART metrics gain under the Class-A metric" | fig3f_classA_robustness.csv | done |

## Verified numbers
- 3a: energy 0.8369, pca_dist 0.7782, coverage_mean 0.7734, coverage_worst 0.5893, pca_mean 0.5179,
  cmap_wtcs 0.4635, cmap_cosine = mean_cosine 0.388492 (exp08 summary.csv, unweighted mean over the
  7 task x setting cells). Query-weighted, the same two are 0.8865 and 0.4214, as the text says.
- 3b: per task, energy vs mean/CMap: controlled 0.844 vs 0.289 (+0.56), crossline 0.916 vs 0.418
  (+0.50), frangieh 0.578 vs 0.600 (-0.02). On Frangieh mean/CMap is the top of all eight scorers.
- 3c: regret reduction DART_coverage_worst vs mean_cosine over ALL 765 partial-observed queries:
  median +0.11826, mean +0.25790, frac>0 0.7203, frac<0 0.2078, Wilcoxon p = 1.568e-66. This is the
  number the manuscript quotes; the 621-query gate-recommended subset gives +0.11900 and p = 4.3e-56.
- 3d: recommendation_vs_outcome.csv medians, coverage_worst DART_recommended +0.11900 (n=621) vs
  mean_or_no_call +0.12194 (n=133). The remaining 11 of the 765 queries are gate "mean_sufficient"
  (median exactly 0.000); they are named on the panel and not plotted.
- 3e: exp01 controlled mixing sweep. Energy Hit@1 is monotone non-increasing in alpha for all three
  cell lines (K562 1.00 -> 0.35, A549 1.00 -> 0.85, MCF7 1.00 -> 0.75), which is what the panel
  title claims and what the panel asserts at draw time.
- 3f: all five DART metrics positive on the 621 gate-recommended queries: energy +0.056, MMD +0.060,
  sliced-W +0.059, coverage-mean +0.090, coverage-worst +0.119.

## Honesty notes
- The whole figure is Class A: gains are measured with metrics that share the retrieval objective.
  The caption states this; the collapse under Class B/C metrics is Fig 4.
- 3b is drawn as paired dots with a signed gap label rather than a heatmap, because a Blues heatmap
  renders the 0.578 / 0.600 reversal invisible. The counterexample is deliberately reported.
- 3c/3d: the Class-A positive is in decision REGRET, not MoA-nDCG (which is ~0 on the recommended
  subset); the panels plot regret reduction, not a MoA-nDCG gain, to avoid overclaiming.
- 3c plots all 765 queries, 3d and 3f the 621-query gate-recommended subset. Each panel states its
  own n, because the three n's differ for a reason and a silent mismatch would look like an error.
- 3e uses the controlled alpha axis (subpopulation mixing), the one setting with a clean
  heterogeneity knob; per-query real-data divergence does NOT correlate with regret reduction
  (rho=-0.03, p=0.40), so that (absent) relationship is deliberately not drawn.

## Open items for the author
- The manuscript caption for **e** says "the energy advantage narrows as subpopulations merge".
  That holds for K562 (energy-minus-mean gap 1.00 -> 0.05) but NOT for A549 (0.40 -> 0.65) or MCF7
  (0.35 -> 0.45). The panel title therefore claims only the part that is true of all three lines.
  Either soften the caption or restrict it to K562.
- The manuscript writes mean/CMap cosine as 0.389; the exact macro-mean is 0.388492, which rounds
  to 0.388. The panel prints 0.388.

## Print geometry (authored 1:1)
The manuscript text block is 6.93 in and the figure enters with `\includegraphics[width=\textwidth]`.
This composite was previously authored 11.0 x 5.7 in, so LaTeX shrank it 0.63x and the 6 pt panel
annotations printed at 3.8 pt, below the 5 pt Nature Portfolio floor. (`figstyle.save` only measures
NOMINAL point size, so it reported CLEAN while the printed page failed.) The canvas is now
6.9 x 5.8 in; the exported PDF is 6.836 x 5.596 in after the tight bounding box, so LaTeX scales it
by 1.014 and the 6 pt floor prints at 6.1 pt. Layout is an explicit inch ledger in
`fig3_assemble.py` (two rows of `[panel, gutter, panel, gutter, panel]`, `wspace=0`) because panels
a and f need ~0.62 in for their category labels, which a uniform 12-column gutter cannot give.

On-panel text that was cut to fit 1:1 (all of it survives in the caption or the Results text):
- 3a x label: "unweighted mean of 7 task x setting cells" -> "macro-mean of 7 cells".
- 3b x ticks: dropped the "SciPlex3" / "natural" provenance line; only `n` remains.
- 3c: dropped the trailing clause "pulled up by the right tail" from the Wilcoxon block.
- All six titles are wrapped to two lines; no wording changed, and no font size was lowered.

## Files
- fig3a.py ... fig3f.py : per-panel draw functions (each runs standalone). Each sets its own title,
  and `fig3_assemble.py` does NOT override them, so the string in the panel file is the string that
  prints.
- fig3_assemble.py : the two-row inch ledger described above; it owns the module-level `STEM`.
- fig3_temptation.{pdf,svg,png} : the composite, and the only stem this figure is written under.
  `python figures/build_all.py --write` enforces the 5 pt floor, writes these, and copies the PDF to
  manuscript/latex/figures/fig3.pdf, which is the file the manuscript compiles. The assemble used to
  write the same composite a second time as `fig3_apparent_gains.*`, so the figure sat on disk twice
  under two names with nothing to say which one the manuscript used; that duplicate stem is gone and
  build_all now fails if the two names drift apart again.
- 3a.png ... 3f.png are standalone per-panel previews, not inputs to the composite.
