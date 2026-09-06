# Figure 6: the prediction bottleneck

One-line message: the oracle advantage of Figure 5 does not survive forward prediction, it inverts
rather than attenuates, and the deficit is a magnitude error inherited from the predictor rather
than a failure of distributional scoring.

**Authority.** The Figure 6 caption in `manuscript/latex/PopRetrieve_manuscript.tex` is the
authority for every number below. If this file disagrees, this file is the bug. Panel geometry
lives in `fig6_assemble.py`; the colour and type vocabulary in `../phase2_style.py`; every number
is loaded by `../phase2_data.py` and none is written into a panel by hand.

## Why this page exists separately from Figure 5

Until 2026-09-03 both halves of the Phase-II result shared one eight-panel page. Figure 5 keeps the
oracle, with candidate responses OBSERVED. This page changes exactly one thing about that
experiment, the third station of the task, and measures what happens.

**No experiment was re-run for the split.** Panels e, f and h were on the previous page unchanged;
b, d and g are new re-reads of files already on disk. Panel a is the same drawing as Figure 5
panel a, from the same function with one station switched (`../phase2_task.py`), so the one change
is visible rather than asserted.

## Panels

| Panel | What the reader should see in three seconds | Reads |
|---|---|---|
| a | the same pipeline as Figure 5a with one box replaced | schematic; no computed value |
| b | two lines falling and crossing | `phase_a/summary.csv` + `phase_b/summary.csv` |
| c | one point right of zero at the top, everything below it left of zero | `phase_a` + `phase_b` + `phase_b_p5` `delta_vs_reference.csv` |
| d | two intervals of the same length, and a third far shorter | `phase_b/delta_vs_reference.csv` |
| e | one bar absent, two short, and a dashed line well to their right | `phase_b_p5/gate1_predicted.csv.gz`, `gate1_interaction/interaction_per_query.csv` |
| f | two pairs of bars, the orange taller in both | `phase_b_p5/summary.csv` |
| g | orange arms longer than blue ones in four rows of five | `synthesis/oracle_to_prediction.csv` |
| h | two filled bars, the second a third of the first, then two outlined gates | the same files as Figure 5b and 5c, through `../phase2_data.py` |

All paths are under `results/phase2_transition/`.

## The panel this page was built around

Panel **d** is the correction. Read alone, panel c says the population route loses 0.0356 MRR to
direction-only mean matching once candidates are predicted, and that reads as a failure of
distributional scoring. On the SAME predictions and the same 19,960 query-seed pairs, the
magnitude-aware mean loses 0.0335 of the same deficit although it reads no distribution at all,
and what is left once magnitude is controlled is 0.0020.

So the deficit is inherited. An additive predictor's candidate population is the vehicle
population rigidly translated by an effect averaged over 43 other cell lines: its magnitude is
wrong and its shape carries nothing about the drug. A scorer that reads magnitude pays for that
error; a cosine does not. `draw_6d` asserts both halves of that reading on the drawn values, that
the first two deficits are within a factor of two of each other and that the third is at least
five times smaller, so the caption cannot outlive the numbers.

Panel **e**'s leftmost entry is an arrow leaving the axis rather than a bar at the smallest tick.
An additive predictor's interaction is zero by algebra, measured at a maximum of 1.8e-14 across
19,044 cell-line, drug and seed combinations, which is float round-off; a bar clamped to the axis floor would
read as small rather than absent.

Panel **g** deliberately does not draw case IV, a gain appearing where the oracle had none. It has
a different denominator, and for the OT map it is 1,165 queries, which would be the largest bar on
the page. It is not the strongest result on it: the OT map's mean route reaches 0.665 against the
oracle's 0.945, and by Figure 5e that room alone manufactures the pattern. The counts are in the
caption.

## The conventions this figure holds itself to

The same as Figure 5: no panel states a conclusion (7.2 pt cap), a 6.5 pt floor asserted before
the figure is returned, no mathtext in any panel, two panels per row, and every number read from
`results/` through an accessor that raises rather than defaulting.

## Rebuilding

```bash
python figures/fig6/fig6_assemble.py     # panels + composite, gated
python figures/build_all.py --write      # the whole deck, and the copy the manuscript compiles
python figures/check_overlaps.py 6       # pairwise text overlap on the assembled page
```
