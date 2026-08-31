# Figure 2: cell populations carry retrievable information beyond mean signatures

One-line message: retaining within-population structure gives retrieval access to information that
a collapsed mean signature cannot reach. **Every criterion on this figure is objective-aligned
(Class A):** all of them reward correspondence between response populations, which is the
information population-level retrieval uses. The figure must NOT be read as independent
validation. What happens under criteria that do not share the retrieval objective is Figure 3.

## Panels

Read in four movements: how big, how general, can we predict it, is it one score or a family.

| Panel | What the reader should see in three seconds | Reads |
|---|---|---|
| a | "Every population scorer beats every mean scorer" | `results/exp08_signature_baselines/summary.csv` |
| b | "Large on both mixtures, reversed on Frangieh" | `results/exp08_signature_baselines/summary_by_task.csv` |
| c | "The gain survives partial observation" | `results/exp12_partial_observed_retrieval/per_query_scores.csv` |
| d | "Recommendation does not enrich the gain" | same per-query file |
| e | "K562 collapses; A549 and MCF7 do not" | `results/exp01_sciplex3_controlled/metrics_summary.csv` |
| f | "All five intervals clear zero" | same per-query file |
| g | "Score families agree within, not across" | `figures/source_data/ed1_metric_correlation.csv` |

Each phrase is drawn ink at 8.5 pt, not an rc title, and each is asserted against the data it
describes: if the data stopped supporting the sentence, the build breaks rather than the panel
quietly printing a false one. Panels e and f build their phrases from the drawn values.

## Verified numbers

- **a** macro-means over the 7 task x setting cells: energy 0.836905, PCA-dist 0.778175,
  coverage-mean 0.773413, coverage-worst 0.589286, PCA-mean 0.517857, CMap WTCS 0.463492,
  CMap cosine = mean cosine 0.388492. Difference energy minus mean cosine **+0.448413**, ratio
  2.154x. Note this is not 0.837 minus 0.388: subtracting the rounded values gives 0.449, and the
  panel prints the difference of the unrounded ones.
- **The separation is the panel's design.** The weakest population-level scorer (0.589) is above
  the strongest mean-level one (0.518), so sorting by value and grouping by representation give
  the same ladder. `fig2a` asserts it; if it ever failed, the two-colour scheme would be a claim
  the data no longer supports.
- **b** per task, energy vs mean/CMap cosine: controlled 0.8444 vs 0.2889 (+0.56), cross-line
  0.9157 vs 0.4176 (+0.50), Frangieh 0.5778 vs 0.6000 (-0.02). On Frangieh mean/CMap cosine is the
  best of all eight scorers. n = 90, 1080, 90.
- **c** regret reduction, coverage-worst against mean cosine, over ALL 765 partial-observed
  queries: median +0.11826, mean +0.25790, 72.0% improved, 20.8% worse, 7.2% exactly tied,
  Wilcoxon p = 1.568e-66.
- **d** recommended +0.11900 (n=621, 95% CI +0.099 to +0.139) against not recommended +0.12194
  (n=133, CI +0.061 to +0.177); difference -0.0029, CI -0.062 to +0.058, Mann-Whitney p = 0.967.
  Pooling the 11 mean-sufficient queries into the non-recommended arm gives +0.0048, CI -0.055 to
  +0.065, p = 0.807, so the null does not depend on which queries were set aside.
- **e** population advantage, energy Hit@1 minus mean-cosine Hit@1, at alpha 0.5 to 0.9:
  K562 +1.00 +0.90 +0.80 +0.50 +0.05 (the only monotone line, drop 0.95); A549 +0.40 +0.65 +0.70
  +0.65 +0.65; MCF7 +0.35 +0.65 +0.70 +0.90 +0.45. n = 20 seeds per point.
- **f** medians on the 621 gate-recommended queries, with seeded bootstrap 95% CIs: energy +0.0557
  [+0.037, +0.072], MMD +0.0604 [+0.042, +0.079], sliced-W +0.0591 [+0.040, +0.082], coverage-mean
  +0.0904 [+0.060, +0.109], coverage-worst +0.1190 [+0.099, +0.139]. All five exclude zero.
- **g** within the mean family 1.0000 / 0.8501 / 0.8501, within the population family 0.8251 /
  0.7217 / 0.9749, and all nine cross-family pairs at |rho| <= 0.0757.

## Honesty notes

- **The whole figure is Class A.** The caption says so in its first sentence, and panel g's own
  note says its correlations describe scoring-rule similarity rather than retrieval performance.
- **b reports its own counterexample.** A colour-scaled heatmap renders the 0.578 / 0.600 reversal
  invisible; the paired markers and the signed gap cannot.
- **The three n differ on purpose.** c is all 765 partial-observed queries, d splits the same 765,
  f uses the 621 gate-recommended subset. Each panel states its own n, because a silent mismatch
  would read as an error.
- **d's test is anticonservative** (queries within a cell line share a candidate library), which
  for a NULL strengthens the conclusion rather than weakening it. Stated in the caption.
- **f's welfare proxy is worst-state energy**, and the two scorers furthest right are an energy
  score and a worst-case score, so the criterion's functional form is closest to the two winners.
  That alignment is the paper's subject, not a defect in the panel, and it is what Figure 3 tests.
- **e's alpha is a mixing proportion, not a similarity knob.** See CORRECTIONS.md R45: the
  manuscript described it as merging until 2026-08-31. It is not; the two response states are
  orthogonal throughout and what shrinks is the minority state, from 200 cells to 40.
- **The bootstrap bounds in d and f are seed-fixed, not seed-free.** `boot_median_ci` uses
  `seed=0` and `n_boot=4000`, so the panel, this file and the caption agree exactly and the
  figure reproduces. But with n = 133 the bootstrap median takes only about 38 distinct
  values, so the 2.5th percentile lands on one of two adjacent atoms depending on the seed:
  the non-recommended lower bound is +0.061 at seed 0 and +0.066 at seed 2. Quote these to
  three decimals at most, and never treat the last digit as measured. The medians and the
  rank-test p values are deterministic and carry no such caveat.
- **g's matrix has no generator.** See CORRECTIONS.md R46. It covers six of a's eight scorers; the
  two PCA baselines are absent from the export and the panel says so on its face rather than
  inventing them.

## Print geometry, authored 1:1

The manuscript text block is 6.951 in and the figure enters with
`\includegraphics[width=\textwidth]`. The canvas is **6.90 x 9.20 in** and exports 6.92 x 9.22, so
LaTeX scales it by 1.004 and nominal point size is printed point size. The float budget is the
9.461 in text block less about 16/72 in of overhead, i.e. 9.238 in, so the height has 0.018 in of
margin: **do not grow the canvas without re-checking `Float too large` in the build log.**

Layout is an explicit inch ledger in `fig2_assemble.py`: four rows, `a` alone at full width, then
`b|c`, `d|e`, `f|g`. It was three panels per row until 2026-08-31, which left each about 1.7 in
wide and forced six annotations down to 5.6 pt. Two per row buys the **6.5 pt floor** that
`fig2_assemble._assert_floor` now enforces, above the deck's 5 pt production limit, and mathtext
is measured at its effective 0.7x size.

## Files

- `fig2_style.py` : the frozen vocabulary. Two family colours, one type ladder, the shared scorer
  table, and `boot_median_ci` (seeded), which is where every interval in d and f comes from. Panels
  import from here and never re-declare a colour.
- `fig2a.py` ... `fig2g.py` : per-panel draw functions, each runnable standalone for a preview.
  `draw_2e` takes two axes (the curve and the composition strip above it); the rest take one.
- `fig2_assemble.py` : the inch ledger, the panel letters at 9.5 pt, and the 6.5 pt floor gate.
  Owns the module-level `STEM`, which `build_all.py` checks against its own `STEMS` dict.
- `fig2_temptation.{pdf,svg,png}` : the composite, and the only stem this figure is written under.
  `python figures/build_all.py --write` enforces the floor, writes these, and copies the PDF to
  `manuscript/latex/figures/fig2.pdf`, which is the file the manuscript compiles.
- `2a.png` ... `2g.png` : standalone per-panel previews, not inputs to the composite, and not
  guaranteed fresh.
