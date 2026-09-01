# Figure 2: cell populations carry retrievable information beyond mean signatures

One-line message: retaining within-population structure gives retrieval access to information that
a collapsed mean signature cannot reach. **Every criterion on this figure is objective-aligned
(Class A):** all of them reward correspondence between response populations, which is the
information population-level retrieval uses. The figure must NOT be read as independent
validation. What happens under criteria that do not share the retrieval objective is Figure 3.

## Panels

Read in three rows: how big and how general, how much it is worth and where it holds, which
scorers and whether they are one score or a family. The one-movement-per-row reading this figure
had until 2026-09-01 went with the full-width hero; see the geometry note.

| Panel | What the reader should see in three seconds | Reads |
|---|---|---|
| a | four blue bars all longer than four orange, with a white channel between the bands | `results/exp08_signature_baselines/summary.csv` |
| b | two long paired jumps, then one that goes the other way | `results/exp08_signature_baselines/summary_by_task.csv` |
| c | a step curve lying almost entirely in the blue half-plane | `results/exp12_partial_observed_retrieval/per_query_scores.csv` |
| d | one curve falling to the axis while two do not | `results/exp01_sciplex3_controlled/metrics_summary.csv` |
| e | five intervals, none touching zero | `results/exp12_partial_observed_retrieval/per_query_scores.csv` |
| f | two saturated blocks on the diagonal, near-white everywhere else | `figures/source_data/ed1_metric_correlation.csv` |

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

One casualty is worth naming. Panel a's `+0.448 Hit@1` was set at 8.5 pt because it is the headline
number of the whole figure rather than a sentence. It is now 7.2 pt like every other statistic, and
stays prominent through weight, isolation in the right-hand block, and the bracket tying it to the
two rows it compares.

## Archetype and panel hierarchy

**Archetype: a quantitative grid, three rows of two.** Panel a is still the hero and still the
largest, but it is no longer a full-width row, and that change is the reason for everything else on
this page.

Measured 2026-09-01, share of total axes area:

| panel | share | axes | aspect |
|---|---|---|---|
| a | 24.1% | 2.95 x 1.94 in | 1.52:1 |
| b | 18.1% | 2.11 x 2.04 in | 1.03:1 |
| d | 15.3% | 3.23 x 1.13 in | 2.86:1 (plus a 0.34 in composition strip) |
| f | 14.7% | 2.49 x 1.40 in | 1.78:1 |
| e | 14.6% | 2.45 x 1.42 in | 1.73:1 |
| c | 13.2% | 2.03 x 1.55 in | 1.31:1 |

The old page had a at 30.8 per cent on a full-width row and the other six between 8.7 and 18.6.
The spread is now 13.2 to 24.1, which is a flatter page, and that is the honest consequence of six
panels rather than seven: the hero can only be a hero by so much when five panels share the rest.

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
- **d** population advantage, energy Hit@1 minus mean-cosine Hit@1, at alpha 0.5 to 0.9:
  K562 +1.00 +0.90 +0.80 +0.50 +0.05 (the only monotone line, drop 0.95); A549 +0.40 +0.65 +0.70
  +0.65 +0.65; MCF7 +0.35 +0.65 +0.70 +0.90 +0.45. n = 20 seeds per point.
- **e** medians on the 621 gate-recommended queries, with seeded bootstrap 95% CIs: energy +0.0557
  [+0.037, +0.072], MMD +0.0604 [+0.042, +0.079], sliced-W +0.0591 [+0.040, +0.082], coverage-mean
  +0.0904 [+0.060, +0.109], coverage-worst +0.1190 [+0.099, +0.139]. All five exclude zero.
- **f** within the mean family 1.0000 / 0.8501 / 0.8501, within the population family 0.8251 /
  0.7217 / 0.9749, and all nine cross-family pairs at |rho| <= 0.0757.

## Honesty notes

- **The whole figure is Class A.** The caption says so in its first sentence, and panel g's own
  note says its correlations describe scoring-rule similarity rather than retrieval performance.
- **b reports its own counterexample.** A colour-scaled heatmap renders the 0.578 / 0.600 reversal
  invisible; the paired markers and the signed gap cannot.
- **The two n differ on purpose.** c is all 765 partial-observed queries; e uses the 621
  gate-recommended subset. Each panel states its own n, because a silent mismatch would read as an
  error.

- **e's welfare proxy is worst-state energy**, and the two scorers furthest right are an energy
  score and a worst-case score, so the criterion's functional form is closest to the two winners.
  That alignment is the paper's subject, not a defect in the panel, and it is what Figure 3 tests.
- **d's alpha is a mixing proportion, not a similarity knob.** See CORRECTIONS.md R45: the
  manuscript described it as merging until 2026-08-31. It is not; the two response states are
  orthogonal throughout and what shrinks is the minority state, from 200 cells to 40.
- **The bootstrap bounds in e are seed-fixed, not seed-free.** `boot_median_ci` uses
  `seed=0` and `n_boot=4000`, so the panel, this file and the caption agree exactly and the
  figure reproduces. But with n = 133 the bootstrap median takes only about 38 distinct
  values, so the 2.5th percentile lands on one of two adjacent atoms depending on the seed:
  the non-recommended lower bound is +0.061 at seed 0 and +0.066 at seed 2. Quote these to
  three decimals at most, and never treat the last digit as measured. The medians and the
  rank-test p values are deterministic and carry no such caveat.
- **f's matrix has no generator.** See CORRECTIONS.md R46. It covers six of a's eight scorers; the
  two PCA baselines are absent from the export and the panel says so on its face rather than
  inventing them. It was panel g until 2026-09-01.
- **a's family separation is a property of the MACRO-MEAN, not of the seven cells.** Grouped and
  sorted at once, the panel is true of what it plots: the weakest population scorer (0.589) is
  above the strongest mean one (0.518). Per cell the separation holds in only 3 of the 7, and
  coverage-worst is beaten by PCA-mean or CMap WTCS in the other 4. The x axis label and the
  caption both scope the claim to the macro-average, and panel b carries the Frangieh reversal,
  so nothing on the page over-claims; but do not add per-cell dispersion to this panel without
  saying that, because the dots would break the grouping in four of seven columns.

## Print geometry, authored 1:1

The manuscript text block is 6.951 in and the figure enters with
`\includegraphics[width=\textwidth]`. The canvas is **6.90 x 7.57 in** and exports 176 x 193 mm, so
nominal point size is printed point size. The float budget is the 9.461 in text block less about
16/72 in of overhead, i.e. 9.238 in, leaving 1.65 in of headroom.

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
curve. The page is 193 mm rather than the 171 mm it would have been.

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
