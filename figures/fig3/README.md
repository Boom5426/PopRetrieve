# Figure 3: the population advantage weakens, and can change direction, once the judge changes

One-line message: the Class-A advantage established in Figure 2 does not survive a change to
criteria that do not share the retrieval objective. Four numbers are this figure's skeleton, and
every other panel supports or qualifies one of them:

| | |
|---|---|
| **+0.028** | response matching: population retrieval wins, narrowly (a) |
| **0.000** | mechanism recovery, the SAME rankings: the advantage is gone (a, b) |
| **+0.265** | external functional similarity: a real population signal (h) |
| **+0.105** | what survives once the response-magnitude channel is partialled out (h, i) |

All four were reissued on 2026-09-03 under the unbiased U-statistic energy distance; the V-arm
values were +0.129, 0.000, +0.276 and +0.097. The first one lost three quarters of its size and
the third and fourth barely moved, which is the pattern the estimator audit predicts: the
external oracle comparison does not pass a candidate's cell count through an energy kernel and
the partial-observation retrieval does.

Panel letters and every number below match the Fig. 3 caption in
`manuscript/latex/PopRetrieve_manuscript.tex`, and the per-number provenance is in
[docs/phase2/FINAL_FIGURE_NUMBER_LEDGER.md](../../docs/phase2/FINAL_FIGURE_NUMBER_LEDGER.md). If a
number here and a number there ever disagree, the ledger is the authority and this file is the bug.

## Panels

| Row | Panel | What the reader sees | Reads |
|---|---|---|---|
| 1 | a | the advantage collapsing from +0.028 to 0 when only the judge changes | `results/exp12_partial_observed_retrieval/per_query_scores.csv` |
| 1 | b | three ECDFs stepping through zero, all three medians 0.000 | same |
| 2 | c | 239 tasks hugging zero, the largest mean on the smallest share | `results/exp13_real_data_projection/projection.csv` |
| 2 | d | one quartile below zero and three above, on the objective-aligned judge | `results/exp16_gate_diagnosis/_merged_query_divergence.csv` |
| 3 | e | the same four quartiles on a judge that never turns positive | `results/exp16_gate_diagnosis/_merged_query_divergence.csv` |
| 3 | f | two estimates with overlapping intervals, the declined one no worse | `results/exp12_partial_observed_retrieval/per_query_scores.csv` |
| 3 | g | a binned trend falling where it should rise, under a verdict strip that inherits the fall | `results/exp16_gate_diagnosis/_merged_query_divergence.csv` |
| 4 | h | energy above its incumbent, and an arc dropping it to +0.105 | `source_data/fig3hi_class_c_functional.csv` |
| 4 | i | a scatter split 62 / 40 by the diagonal, with one exact tie | same |
| 5 | j | two negative, one near zero, one strongly positive | `source_data/fig3hi_class_c_potency.csv` |
| 5 | k | a density piled up near +1 | same |

**THE LETTERS WERE RE-ASSIGNED ON 2026-09-05 SO THE PANELS ARE CITED IN ORDER.** The Results run a
and b, then the 239-task minority-coverage result, then that result STRATIFIED by divergence, then
the two diagnostic panels. The figure ran the stratification first and the result it stratifies
fifth, so a reader was sent to Fig. 3g third and met the base number after its own quartiles.
Nature also asks for panels in citation order, and Figure 4 was re-cut for that reason a day
earlier. The 239-task panel is now **c** and keeps the 4.15 in box it was measured for; the four
panels behind it are each one letter later. Nothing is redrawn: `fig3_assemble.DRAW` is the one
place the letter-to-content map lives, and the modules were deliberately NOT renamed with the
letters, so `fig3g.py` draws panel c. The one cost is that the two divergence-quartile panels, the
same drawing under two judges, are now the end of row 2 and the start of row 3 rather than side by
side; that is unavoidable, because 4.15 + 2.45 + 2.45 in does not fit a 6.90 in row.

**Row 5 was left alone on purpose.** The Results used to cite k before j. The figure's order there,
what the endpoint choice does and then the channel that explains it, is the right one, so the two
sentences in the Results were exchanged instead of the two panels.

**ROW 3 WAS REBUILT ON 2026-09-03 AND THREE LETTERS CHANGED MEANING**, under the letters of the
time: the old d (gate enrichment) became e; the old e and f became one panel, f, merged onto the
true-divergence axis they both drew; and d was new, carrying the mechanism-recovery quartiles that
were Figure 5 panel g. Under the 2026-09-05 assignment those three are f, g and e. The reason is in
`fig3_assemble.py`'s docstring: the objective-aligned quartile panel reversed under the repaired
estimator, so the figure could no longer argue that neither the axis nor the gate locates the gain,
and two of the three old panels were paying for one x axis twice.

## Archetype and panel hierarchy

**Archetype: quantitative grid with two hero panels.** Declared here because the figure contract
requires it and this figure went a long time without one.

Row heights are set against the figure's own tiering, not by taste. Panels a, c, h and i carry the
argument; b, d, f and g explain why the biological gain is absent; e, j and k are diagnostics
answering anticipated objections. On 2026-08-31 that hierarchy was measured and found INVERTED:
the five tier-3 diagnostics averaged 6.6 per cent of panel area against 6.1 per cent for the four
tier-2 panels, and k and m were drawn as large as i. A page that gives its diagnostics discovery
weight tells the reader the wrong thing before they read a label.

Rows 1 and 4, which hold the four skeleton numbers, took the height; rows 5 and 6 gave it up. The
total is unchanged, so nothing outside those six numbers moved.

| tier | panels | share of panel area, each |
|---|---|---|
| 1, discovery | a, c, h, i | 13.8% |
| 2, why the gain is absent | b, d, f, g | 7.1% |
| 3, diagnostics | e, j, k | 5.5% |

## Audit findings NOT acted on

Recorded so they are decisions rather than oversights.

- **Panel letters are 9.5 pt against the 8 pt convention** for Nature-family panel labels. This
  deck sets its whole type ladder one step up (Figures 1, 2 and 3 all use 9.5), and changing one
  figure would break that consistency. Revisit deck-wide or not at all.
- **The caption is 631 words against a 300-word guideline.** All five figures are over. The
  guideline comes from a Nature Communications corpus; Nature main-text legends routinely run 400
  to 700. At eleven panels, 300 words is 27 words per panel including the figure title and every
  statistic, and the QA contract separately requires n, centre, spread and test to be IN the
  legend. The two rules conflict at this panel count, and the statistics won. Cut from 943 on
  2026-08-31; the remaining candidates were all honesty qualifications rather than prose.
- **POP blue and EXT green differ by 0.025 in relative luminance**, so they are indistinguishable
  in grayscale. Every panel that uses both (h, i, l) separates them by fill and position as well,
  which is what the grayscale rule actually requires, but the margin is thin: do not introduce a
  panel where blue and green appear as the same mark type.
- **No TIFF export.** `figstyle.save` writes PDF, SVG and PNG. These are vector line-art figures,
  for which Nature prefers vector; a 600 dpi TIFF of a 13-panel vector page would be large and
  worse. Add one only if the production workflow asks.
- **The legends carry no "Source data are provided as a Source Data file" line.** The Data
  availability section states that source-data tables underlying each figure panel are provided,
  so the substance is there; the per-legend boilerplate is venue-specific and can be added at
  submission.

## No panel states a conclusion

Every panel used to carry one bold sentence over itself, thirteen in all. They are gone, and
`fig3_style.title()` is deleted rather than deprecated so none can come back. Only four kinds of
text may appear on a panel: axis and group names, statistics (median, rho, P, n, and the values
being compared), a two or three word direction hint, and nothing else. Every deleted phrase now
opens its panel's entry in the Fig. 3 caption, where it costs no space and can be qualified.

`fig3_assemble._assert_no_titles` enforces this mechanically: **no panel may draw text above
7.2 pt**, and the build fails if one does. It is a size gate rather than a wording gate, because no
code can tell a claim from a label, but a claim that has to fit at 7.2 pt beside the marks it
describes has already lost the argument for being on the panel. Removing the thirteen sentences
returned 0.42 in of height to the six rows, which is most of what had made rows 5 and 6 cramped.

## Verified numbers

**They live in one place, and it is not this file.**
[docs/phase2/FINAL_FIGURE_NUMBER_LEDGER.md](../../docs/phase2/FINAL_FIGURE_NUMBER_LEDGER.md)
carries every number this figure draws or captions, panel by panel, with the file it comes from,
the estimator arm, and the pre-repair value it replaced. This section used to hold a second copy
and the copy went stale: on 2026-09-03 it still quoted the V-arm values for every panel, and for
h to k it quoted numbers that the panels' own source views had already been resynced away from.

Two facts about the numbers are worth stating here because they are properties of the FIGURE
rather than of any one panel.

- **Every panel is now the U arm.** The last two holdouts were the Class-C views under
  `figures/source_data/`, which `figures/sync_source_data.py` did not know about: they were
  labelled PRIMARY, were in none of its three tables, and so stayed on the July run while
  `results/upgrade/` moved. They are MIRRORS now and drift is a build failure.
- **One file was recovered rather than re-run.** `class_c_magnitude_control_v2` needs a SciPlex3
  tensor that is not on this machine, so its U-arm output was rebuilt from the estimator audit's
  cell-by-cell comparison table by `analysis/estimator_audit/recover_u_arm_output.py`, which
  refuses to write unless rebuilding the other arm reproduces the installed file exactly. It did,
  to 4.4e-16 over 103 rows and 8 columns.

## Print geometry, authored 1:1

The figure enters the manuscript as `\includegraphics[width=\textwidth]` into a 6.951 in text
block. The canvas is **6.90 x 7.89 in** and exports 6.95 x 7.94 (176 x 202 mm), so LaTeX scales it by
1.001 and nominal point size is printed point size. The float budget is the 9.461 in text block less about
16/72 in of overhead, i.e. 9.238 in. The canvas grew from 7.67 to 8.22 in on 2026-09-03 when row 3 was rebuilt,
came back to 7.91 on 2026-09-04 and to 7.89 on 2026-09-05; the build log was re-checked each time: no `Float too large`, no
overfull vbox. **Do not grow it further without re-checking both.** The caption is on the following page and is
itself near the limit; it overflowed at 991 words and fits at about 945.

Layout is an explicit inch ledger in `fig3_assemble.py`: five rows, `a|b`, `c|d`, `e|f|g`, `h|i`,
`j|k`, with unequal widths inside a row because the panels are unequal.

### Why the rows were re-cut, twice

On **2026-09-04** the page read `a b | c g | d e f | h i | j k`, so a reader met g fourth. The fix
then was positional: g moved into the second half of row 2, whose box is 2.75 to 6.90 in and
therefore the same box it had in row 1 to the hundredth, so it was redrawn at its own width with
its x limit, its summary column and its two visibility assertions untouched. It was not given the
narrow half, because its summary column is absolute rather than fractional (a 0.24 in task-split
bar and a 0.38 in mean value at 6.8 pt), so at 2.40 in that column would be 0.33 in and the values
would have to shrink.

On **2026-09-05** the letters themselves moved, because position was only half the problem: the
page read alphabetically but the Results did not cite it alphabetically, and the figure was
showing a stratification before the result it stratifies. The 239-task panel took the first half
of row 2 at the same 4.15 in width, and the four panels behind it each moved one letter later.
Row 3 now holds three panels at 1.32 in and row 2 two at 1.42 in, which is the previous pair of
row heights exchanged; the diagnostic cloud gives up 0.30 in of width and 0.10 in of height and
was re-measured on the render. The figure is 0.02 in shorter than before.

**The two power panels left the page on 2026-08-31.** They showed achieved power and the queries
needed for 80 per cent power in the highest response-divergence quartile, and they answered the one
objection this paper's central negative result invites. They are third-tier diagnostics and they
cost a whole row on a page whose argument is rows 1 to 4, so their numbers moved to Supplementary
Note 2 in full and the Results now cite that Note. Removing them shortened the canvas from 9.20 to
7.96 in and lifted panel a from 15.6 to 17.5 per cent of panel area without resizing anything else;
the surviving `l` and `m` were relabelled `j` and `k`. See CORRECTIONS.md R51.

**Eleven panels on one page is still tight.** Row 5 gives its panels 0.54 in of axes height, and
row 3 gives 0.58 in. The response to that is to cut annotation into
the caption; `fig3_assemble._assert_floor` enforces a **6.5 pt** floor, above the deck's 5 pt
production limit, and measures mathtext at its effective 0.7x size.

## Files

- `fig3_style.py` : the frozen vocabulary. The sign rule, the type ladder, `CELL_MARKER`,
  `sign_field`, and the seeded `boot_ci` that every interval in the figure comes from.
- `fig3a.py` ... `fig3k.py` : per-panel draw functions, each `draw_3X(ax)`, each runnable
  standalone for a preview. Panels j to m were drawn by `edfigs/ed_panels.py` and `ed5/ed5.py`
  until 2026-08-31; they are re-authored here because those modules set type under this figure's
  floor, and are no longer imported by any main figure.
- `fig3_assemble.py` : the inch ledger, 9.5 pt panel letters, and the 6.5 pt floor gate. Owns
  `STEM`, which `build_all.py` checks against its own `STEMS` dict.
- `fig3_collapse.{pdf,svg,png}` : the composite. `python figures/build_all.py --write` enforces
  the floor, writes these, and copies the PDF to `manuscript/figures/fig3.pdf`.
- `3a.png` ... `3m.png` : standalone previews, not inputs to the composite, not guaranteed fresh.
