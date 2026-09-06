# Figure 5: the intervention oracle, and where its information goes

One-line message: with candidate responses observed, single-cell populations carry information
beyond the mean signature and it reaches a ranking decision; two thirds of it is response
magnitude rather than distribution, and almost all of what remains comes from the fifth of queries
where the mean route is not already perfect.

**Authority.** The Figure 5 caption in `manuscript/latex/PopRetrieve_manuscript.tex` is the
authority for every number below, and `../../CORRECTIONS.md` for what has been retracted. If this
file disagrees with either, this file is the bug. Panel geometry lives in `fig5_assemble.py`; the
colour and type vocabulary in `../phase2_style.py`; every number the panels draw is loaded by
`../phase2_data.py` and none is written into a panel by hand.

## The 2026-09-03 split, and what moved

This page used to carry the whole Phase-II result, the oracle measurement and what forward
prediction does to it, on one eight-panel page. The two halves answer different questions and were
competing for the same room, so they are now two figures:

| | candidate responses | question |
|---|---|---|
| Figure 5 | **observed** | what is population information worth, and does anything locate it |
| Figure 6 | **predicted** | what survives, and why not |

**No experiment was re-run for the split.** Both pages read the same Phase-II tree through
`../phase2_data.py`. Four panels moved to Figure 6 unchanged (the gain ladder, the predicted
interaction, the constructive test, the budget ledger) and four arrived here: the ceiling, the
headroom null, recoverability, and the interaction-statistic audit. All four are re-reads of files
that were already on disk.

The two task schematics are ONE function with ONE switch (`../phase2_task.py`). A reader comparing
the two pages has to be able to see that the experiment changed in exactly one station, and the
only way to guarantee that is for the two panels to be one drawing.

## Panels

Eight, a to h, read as: the task, what the ceiling is worth, whether it changes a decision, how
much room there was to begin with, whether the reported explanation of that room survives its own
null, and then the three gates: what recoverability is, whether the interaction statistic measures
interaction, and whether anything locates the gain at all.

| Panel | What the reader should see in three seconds | Reads |
|---|---|---|
| a | a left-to-right pipeline, with the target entering the ranking and not the model | schematic; no computed value |
| b | three points climbing, the second step half the size of the first | `phase_a/summary.csv` |
| c | a tall blue bar beside a short orange one, twice | `synthesis/gate3_decision_relevance.csv` |
| d | a huge n under a flat bar, a small n under a tall one | `bottleneck/bottleneck_per_query.csv` + `phase_a/delta_vs_reference.csv` |
| e | one open marker sitting inside a grey band | `bottleneck/summary.json` |
| f | two distributions, one against the chance rule and one far to its right | `phase_c/gate2_observed.csv` |
| g | two orange points left of zero, their blue partners at and beyond it | `gate1_interaction/checks.json` |
| h | four intervals, one clearly right of zero and one clearly left | `bottleneck/regression.csv` |

All paths are under `results/phase2_transition/`.

## The conventions this figure holds itself to

- **No panel states a conclusion.** `fig5_assemble._assert_no_titles` caps panel text at 7.2 pt,
  which is a size gate rather than a wording gate: a claim that has to fit at 7.2 pt beside the
  marks it describes is a caption sentence that has already lost the argument for being on the
  panel.
- **6.5 pt floor**, asserted by `_assert_floor` before the figure is returned. When it fires the
  fix is to cut the annotation into the caption, never to lower the size.
- **No mathtext in any panel.** A subscript prints at 0.7x nominal, so it clears the 6.5 pt floor
  only at 9.3 pt, which is above the 7.2 pt cap the same module applies.
- **Two panels per row.** At three across a box is 2.30 in and panel d's three-line tick labels
  alone need 2.0 in of it.
- **Every number comes from `results/`.** `../phase2_data.py` raises on a missing file or a
  missing key rather than returning a default, so a panel that cannot find its number fails the
  build instead of drawing a plausible one.
- **The task schematic prints no measured value.** `draw_task` raises if any digit it drew is not
  one of the two the task freeze fixes, the 92 compounds and the 43 fitted lines.

## Two panels that are a retraction, and one that is an identity

Panel **e** draws a number this project reported and has withdrawn. Spearman(headroom, gain) =
+0.79 was the strongest apparent explanation of where population scoring pays; a null that keeps
both marginals, the RR <= 1 ceiling and the clustering, and destroys only the pairing between the
two scorers, reproduces it at +0.786 [+0.767, +0.805]. The observed value is inside its own null,
so the panel draws it there. Its marker is deliberately NOT in POP blue: blue means population
retrieval throughout this deck, and the quantity is a property of a ceiling, not of a method.

Panel **g** is why panel h is worth reading. The statistic the interaction gate used to be built
on, `1 - cos(r_1, r_2)`, runs at -0.69 with response magnitude, so it scores the weakest drugs as
the most state-dependent. A gate built on it selects for weak signal. Its cross-fitted replacement
is zero in expectation under the additive null and runs at +0.66.

Panel **d** is an identity and not a comparison: the two groups are defined by the reference
route's own performance, so the split is arithmetic and no interval is drawn on it. `draw_5d`
asserts that the two group means, weighted by their own counts, reproduce the pooled value panel b
and the caption quote.

## Rebuilding

```bash
python figures/fig5/fig5_assemble.py     # panels + composite, gated
python figures/build_all.py --write      # the whole deck, and the copy the manuscript compiles
python figures/check_overlaps.py 5       # pairwise text overlap on the assembled page
```

Each panel also runs standalone (`python figures/fig5/fig5c.py`) and writes `5c.png` at roughly the
axes size it occupies in the composite, which is how a panel is reviewed at 1:1 before assembly.
