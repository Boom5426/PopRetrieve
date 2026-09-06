# Figure 2: response magnitude explains most retrievable information beyond directional signatures

One-line message: what a collapsed mean signature costs a retrieval scorer is mostly RESPONSE
MAGNITUDE, not population structure. A magnitude-aware mean scorer takes +0.399 of the +0.447 Hit@1
that separates a direction-only mean cosine from the energy distance; the distributional residue is
+0.048. **Every criterion on this figure is objective-aligned (Class A):** all of them reward
correspondence between response populations, which is the information population-level retrieval
uses. The figure must NOT be read as independent validation. What happens under criteria that do
not share the retrieval objective is Figure 3.

**The two-family reading this figure carried until 2026-09-03 is retired.** It rested on an
assertion in `fig2a` that every population-level scorer outranks every mean-level one, which is
false once a mean-level scorer that keeps magnitude is in the panel: `mean_l2` reaches 0.788 and
beats three of the four population scorers. The axis the scorers separate on is what they KEEP, so
the figure now argues three tiers, direction then magnitude then distribution. See
[docs/phase2/FIG2_MAGNITUDE_CONTROL_VERDICT.md](../../docs/phase2/FIG2_MAGNITUDE_CONTROL_VERDICT.md),
written before any panel was touched.

## Panels

Read in three rows: how big and how general, how much it is worth and where it holds, which
scorers and whether they are one score or a family. The one-movement-per-row reading this figure
had until 2026-09-01 went with the full-width hero; see the geometry note.

| Panel | What the reader should see in three seconds | Reads |
|---|---|---|
| a | one long step and one short one, bracketed, against a ladder of nine bars | `results/exp08_signature_baselines/summary.csv` |
| b | three small ladders, two steep at the first tread and one flat throughout | `results/exp08_signature_baselines/summary_by_task.csv` |
| c | a quantile curve hugging zero, with a wide blue segment on the axis below it | `results/exp12_partial_observed_retrieval/per_query_scores.csv` |
| d | one curve falling to the axis while two do not | `results/exp01_sciplex3_controlled/metrics_summary.csv` |
| e | orange intervals all clear of zero, blue ones sitting on it or left of it | `results/exp12_partial_observed_retrieval/per_query_scores.csv` |
| f | an orange block, a blue block, and a grey row that belongs to the blue one | `figures/source_data/ed1_metric_correlation.csv` |

## No panel states a conclusion

Every panel used to carry one bold phrase over itself, seven in all. They are gone, and
`fig2_style.title()` is deleted rather than deprecated so none can come back. Only four kinds of
text may appear on a panel: axis and group names, statistics (median, rho, P, n, and the values
being compared), a two or three word direction hint, and nothing else. Every deleted phrase's
content is already in the Fig. 2 caption.

`fig2_assemble._assert_no_titles` enforces this mechanically: **no panel may draw text above
7.2 pt**, and the build fails if one does. It is a size gate rather than a wording gate, because no
code can tell a claim from a label, but a claim that has to fit at 7.2 pt beside the marks it
describes has already lost the argument for being on the panel.

One casualty is worth naming. Panel a's headline step was set at 8.5 pt because it is the headline
number of the whole figure rather than a sentence. It is now 7.2 pt like every other statistic, and
stays prominent through weight, isolation in the right-hand block, and the brackets tying each step
to the two rows it compares. There are two brackets now rather than one, and their sizes are the
figure's argument: **+0.3992** for magnitude and **+0.0480** for distribution.

## Archetype and panel hierarchy

**Archetype: a quantitative grid, three rows of two.** Panel a is still the hero and still the
largest, but it is no longer a full-width row, and that change is the reason for everything else on
this page.

Measured 2026-09-03, share of total axes area:

| panel | share | axes | aspect |
|---|---|---|---|
| a | 22.9% | 2.95 x 1.94 in | 1.52:1 |
| b | 19.0% | 2.33 x 2.04 in | 1.14:1 |
| f | 15.8% | 2.60 x 1.52 in | 1.71:1 |
| e | 15.1% | 2.45 x 1.54 in | 1.59:1 |
| d | 14.6% | 3.23 x 1.13 in | 2.86:1 (plus a 0.34 in composition strip) |
| c | 12.6% | 2.03 x 1.55 in | 1.31:1 |

The old page had a at 30.8 per cent on a full-width row and the other six between 8.7 and 18.6.
The spread is now 12.6 to 22.9, which is a flatter page, and that is the honest consequence of six
panels rather than seven: the hero can only be a hero by so much when five panels share the rest.
Row 2 grew 0.12 in on 2026-09-03 because panel f's matrix went from six scorers in two blocks to
seven in three, and its own cell-height assertion refused to draw at the old height.

## Verified numbers

Every value below is the U-statistic arm, read back out of the panel modules on 2026-09-03. The
per-number provenance table, with the V-arm values each one replaced, is
[docs/phase2/FINAL_FIGURE_NUMBER_LEDGER.md](../../docs/phase2/FINAL_FIGURE_NUMBER_LEDGER.md).

- **a** macro-means over the 7 task x setting cells: energy 0.835714, mean L2 0.787698,
  PCA-dist 0.778175, coverage-mean 0.748810, coverage-worst 0.746825, PCA-mean 0.517857,
  CMap WTCS 0.463492, CMap cosine = mean cosine 0.388492. The two drawn steps are
  **+0.399206** (mean L2 minus mean cosine) and **+0.048016** (energy minus mean L2). Their sum, +0.447222, is the old single "energy minus mean cosine"
  headline, and 89 per cent of it is the first step.
- **The old family separation is gone, and so is the assertion that protected it.** `mean_l2` is
  a mean-representation scorer at 0.788, above three of the four population scorers. What
  replaces it in `fig2a` is a tier assignment made by construction (a cosine discards magnitude
  whatever it scores) plus an assertion that PRIMARY holds exactly one scorer per tier.
- **b** per task, the three-tier ladder: controlled 0.2889 / 0.8111 / 0.8444 (steps +0.52, +0.03),
  cross-line 0.4176 / 0.8231 / 0.9130 (+0.41, +0.09), Frangieh 0.6000 / 0.6111 / 0.5778
  (+0.01, **-0.03**). On Frangieh the best of all nine scorers is `mean_l2`, not mean cosine, and
  the distributional step is negative. n = 90, 1080, 90.
- **c** regret reduction, coverage-worst against mean cosine, over ALL 765 partial-observed
  queries: median **+0.031056** (95% bootstrap CI +0.0168 to +0.0490), mean +0.132015,
  **56.2%** improved, 35.9% worse, 7.8% exactly tied, Wilcoxon p = 1.601e-12, range
  -2.2194 to +2.8529. On the 165 queries whose library is genuinely incomplete: median +0.034979,
  60.0% improved, p = 5.96e-05.
- **d** population advantage, energy Hit@1 minus mean-cosine Hit@1, at alpha 0.5 to 0.9:
  K562 +1.00 +0.90 +0.80 +0.50 **0.00** (the only monotone line); A549 +0.40 +0.65 +0.70
  +0.65 +0.65; MCF7 +0.35 +0.65 +0.70 +0.90 +0.45. n = 20 seeds per point. Only the K562
  endpoint moved under the estimator repair, from +0.05 to 0.00.
- **e** medians on the **627** gate-recommended queries, with seeded bootstrap 95% CIs, against
  TWO references. Against direction-only mean cosine: energy +0.0591 [+0.0450, +0.0853], MMD
  +0.0647 [+0.0483, +0.0877], sliced-W +0.0670 [+0.0414, +0.0892], coverage-mean +0.0444
  [+0.0236, +0.0647], coverage-worst +0.0319 [+0.0175, +0.0531]; all five exclude zero. Against
  magnitude-aware mean L2: energy, MMD and sliced-W are **exactly +0.0000**, coverage-mean
  **-0.0304** [-0.0457, -0.0149] and coverage-worst **-0.0384** [-0.0520, -0.0277].
- **f** seven scorers, 54,180 query-candidate pairs. Within the direction tier 1.000 / 0.850 /
  0.850; within the distribution tier 0.894 / 0.905 / 0.982; the nine direction-by-distribution
  pairs at |rho| <= **0.060**. The magnitude row is the finding: `mean_l2` correlates 0.198 /
  0.198 / 0.170 with the direction tier and **0.801 / 0.682 / 0.685** with the distribution tier.

## Honesty notes

- **The whole figure is Class A.** The caption says so in its first sentence, and panel f's own
  note says its correlations describe scoring-rule similarity rather than retrieval performance.
- **b reports its own counterexample.** A colour-scaled heatmap renders the Frangieh reversal
  invisible; the paired markers and the signed steps cannot.
- **The two n differ on purpose.** c is all 765 partial-observed queries; e uses the 627
  gate-recommended subset. Each panel states its own n, because a silent mismatch would read as an
  error. That 627 was 621 before the estimator repair: the gate's verdict is computed from
  quantities that pass through the energy kernel, so six queries crossed its threshold.
- **e's welfare proxy is worst-state energy**, and the two scorers furthest right on its
  direction-only row are an energy score and a worst-case score, so the criterion's functional form
  is closest to the two winners. That alignment is the paper's subject, not a defect in the panel,
  and it is what Figure 3 tests. It is also why e's second reference matters: against a
  magnitude-aware mean, the same two scorers go NEGATIVE.
- **c is a modest advantage, and the panel is drawn for one.** Its composition changed on
  2026-09-03 because the median fell to a quarter of its published size and the old ECDF needed a
  median rule standing clear of a zero rule. The constant that refused that drawing,
  `MED_CLEAR_PT = 2.5`, was not lowered and the panel's scorer was not swapped; what changed is
  the chart. See `figures/fig2/fig2c.py` and
  [POST_REPAIR_MASTER_RESULTS.md](../../docs/phase2/POST_REPAIR_MASTER_RESULTS.md) section A5.
- **d's alpha is a mixing proportion, not a similarity knob.** See CORRECTIONS.md R45: the
  manuscript described it as merging until 2026-08-31. It is not; the two response states are
  orthogonal throughout and what shrinks is the minority state, from 200 cells to 40.
- **The bootstrap bounds are seed-fixed, not seed-free.** `boot_median_ci` uses `seed=0` and
  `n_boot=4000`, so the panels, this file and the caption agree exactly and the figure reproduces.
  Quote them to three decimals at most and never treat the last digit as measured. The medians and
  the rank-test p values are deterministic and carry no such caveat.
- **f now HAS a generator.** CORRECTIONS.md R46 recorded that its matrix was a hand-built export
  with no upstream parent. `figures/source_data/build_metric_correlation.py`, written 2026-09-03,
  regenerates it from `results/exp08_signature_baselines/per_query_scores.csv`; that is what let
  the magnitude control enter the panel at all, since the old export had no `mean_l2` column and
  no way to gain one. It covers seven of a's nine scorers; the two PCA baselines are absent from
  the export and the panel says so on its face rather than inventing them. It was panel g until
  2026-09-01.
- **a's tiers are a property of the MACRO-MEAN, not of the seven cells.** Per cell the magnitude
  step is large in six of seven and near zero on Frangieh; the distributional step is positive in
  five, exactly zero in one and negative in one. The x axis label and the caption both scope the
  claim to the macro-average, and panel b carries the per-cell picture, so nothing on the page
  over-claims; but do not add per-cell dispersion to panel a without saying that.

## Print geometry, authored 1:1

The manuscript text block is 6.951 in and the figure enters with
`\includegraphics[width=\textwidth]`. The canvas is **6.90 x 6.74 in** and exports 176 x 171 mm, so
nominal point size is printed point size. The float budget is the 9.461 in text block less about
16/72 in of overhead, i.e. 9.238 in, leaving 2.38 in of headroom.

It was 7.47 in until 2026-09-04. Three separate cuts, none of them to an axis that was carrying
anything: panel a's ladder ran at a 0.220 in row pitch for names that set 0.094 in and now runs at
0.180, which is the ratio the rest of the deck uses; panel f's note block went from three grey
lines to one, and the row dropped by exactly the 0.19 in that freed, so its matrix cell height is
unchanged; and panel c lost the second line under its x axis, which restated a sign convention the
panel already carries in its two end blocks. The two lines that left the panels are now in the
caption, which is where a legend and a caveat belong.

Layout is an explicit inch ledger in `fig2_assemble.py`: three rows of two, `a|b`, `c|d`, `e|f`.

### Why panel a stopped being a full-width row, 2026-09-01

Panel a was a full-width hero and its axes was 5.88 x 1.20 in, a **4.9:1 strip** whose longest bar
was 3.00 in of 6.9 pt ink, **44:1**. Worse, `xlim` ran to 1.656, so **2.33 in of the axes, 40 per
cent, sat beyond the data**, holding the value column, the headline block and the provenance key.

That width was spent, not wasted, which is why folding the annotation column back in does not fix
the panel: at full width the only alternative to dead space is a longer track and thinner bars. The
hero had to stop being full width, and that forces everything else, because **a full-width panel at
even the shortest row height here is 5.76 in^2 of axes against the narrowed hero's 5.72**. Once a is
not full width, nothing may be, and seven panels cannot tile two per row.

**The panel that left is the old d, the gate diagnostic, and it was not chosen for its size.**
Figure 3 panel d is the same measurement, and Figure 3's caption said so in those words, "The same
measurement as Fig. 2d". The null was already a main-text panel twice over, in the figure where the
diagnostic's failure is actually argued (Fig. 3d-f are "three independent ways the diagnostic
fails"). Its two load-bearing caveats, that the test is anticonservative and that pooling the 11
mean-sufficient queries does not change the verdict, moved into Fig. 3's caption entry with it. The
old e, f and g moved up one letter.

Panel a is now 2.95 x 1.94 in, **1.52:1**, with a row pitch of 15.8 pt against the old 9.8 and bars
0.101 in thick against 0.068. What it costs: the longest bar is 1.47 in rather than 3.00, and the
horizontal distance between the population floor (0.589) and the mean ceiling (0.518) is 0.124 in
rather than 0.253. The ratio the panel argues from is unchanged; the absolute separation is 3.2 mm
rather than 6.4.

**The value column stays outside the track.** Folding it inside the wash's Hit@1 = 1 ceiling would
buy a 2.10 in track instead of 1.75, i.e. 0.6 mm more separation, but `figstyle`'s presentation
layer states that value labels sit right-aligned past the end of the track and every other value
column in the deck does. 0.6 mm is not worth being the one panel that reads differently.

### The rows below grew, and why

Fixing a freed 1.01 in of page. Spending it on rows 1 and 2 rather than banking it fixed the same
defect one panel over: **d's curve was 3.23 x 0.66 in, 4.9:1**, the very proportion a was rebuilt
to escape. Its composition strip is a fixed 0.34 in, so every inch added to the row goes to the
curve. The page is 187 mm rather than the 171 mm it would have been.

### Three panels had furniture hung on axes fractions

`fig2a` lost this defect on 2026-08-31. `fig2b` and `fig2c` still had it and were found by this
change, because it is invisible until a box height moves:

- **b** dropped its group separator to `-0.40` and its n line to `-0.275` in AXES FRACTION, i.e.
  0.40 and 0.275 of the axes HEIGHT. When b went from a 1.08 in axes to 2.04 in, the separator fell
  0.816 in against a 0.50 in pad and hung **0.316 in into the row below**.
- **c** set its two x-label lines at `-0.19` and `-0.30`. At 1.55 in the second line fell 0.465 in
  and its descenders left the panel.

Both are now measured in inches and converted at draw time, preserving the printed drops they had
at their old heights. **No gate could see either**: `_assert_floor` and `_assert_no_titles` read
font sizes, not positions. `figures/check_overlaps.py` reads text-against-text, not text-against-box.

## Files

- `fig2_style.py` : the frozen vocabulary. Two family colours, one type ladder, the shared scorer
  table, and `boot_median_ci` (seeded), which is where every interval in d and f comes from. Panels
  import from here and never re-declare a colour.
- `fig2a.py` ... `fig2f.py` : per-panel draw functions, each runnable standalone for a preview.
  `draw_2d` takes two axes (the curve and the composition strip above it); the rest take one.
- `fig2_assemble.py` : the inch ledger, the panel letters at 9.5 pt, and the 6.5 pt floor gate.
  Owns the module-level `STEM`, which `build_all.py` checks against its own `STEMS` dict.
- `fig2_temptation.{pdf,svg,png}` : the composite, and the only stem this figure is written under.
  `python figures/build_all.py --write` enforces the floor, writes these, and copies the PDF to
  `manuscript/latex/figures/fig2.pdf`, which is the file the manuscript compiles.
- `2a.png` ... `2g.png` : standalone per-panel previews, not inputs to the composite, and not
  guaranteed fresh.
