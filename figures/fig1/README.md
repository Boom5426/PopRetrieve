# Figure 1: Distributional differences are visible, but their value depends on the evaluator

One-line message: two drugs can share a mean signature yet differ in their subpopulation response,
so distribution-aware retrieval can see structure mean-signature retrieval cannot. Whether that
structure HELPS depends on the evaluator, which is the question the paper answers. This figure sets
the tension; it contains NO Fig-4 collapse numbers.

All five panels are drawn from committed code (`fig1a.py` ... `fig1e.py`, composed by
`fig1_assemble.py`). None of them reads from `results/`; all five are schematic, and the caption
says so. There is no AI-generated panel in this figure any more.

## Panels

| Panel | Title (the claim it states) | Type |
|-------|------------------------------|------|
| a | Same mean shift, opposite fate for a hidden minority | schematic, seeded points |
| b | One query, one library, two ways to score | schematic |
| c | Means tie, distributions separate | synthetic, seeded RandomState(3) |
| d | A score that grades itself cannot lose | schematic |
| e | All three evidence classes, reported here | schematic |

## Design notes

- **a** is the dominant panel: it takes the full width of row 1 (b and c share row 2, d and e share
  row 3), because it is a horizontal three-lane diagram with side labels on both flanks and reads
  better wide than tall. Everything sits on one shared response axis,
  so "identical mean shift" is geometry the reader can check rather than a caption assertion: both
  drugs' population-mean markers land on the same orange rule. Drug B's bulk overshoots (1.25 vs
  1.00) exactly because its 20% minority does not move, which is what holds the population mean
  fixed. Each lane is rigidly translated so its drawn population mean is exactly the intended one.
- **c** is a labelled schematic, not a data panel. Both candidate clouds are rigidly translated
  onto the target's sample mean so the "shared mean" marker is exactly true, and the marginal
  density band carries the inequality (bimodal vs unimodal), which an overlaid scatter does not.
- **d** contrasts a closed loop (Class A: score and metric are one function, no way to lose)
  with an open chain that can end either way (Class B/C).
- **e** states this study's evidence coverage against the field audit. Two corrections were made
  here: the ladder used to put Class A at the top of an "evidence strength" arrow, which inverts
  the paper's own argument, and the status column used to read "this study: none" for Class C,
  which contradicts "We report JUDGE under all three classes". Class C is now at the top of an
  axis named for what actually increases (independence from the retrieval objective), and the
  Class-C entry is marked reported-but-imported.
- Palette semantics are the house ones: GREY context, FOCAL blue distributional/JUDGE signal,
  COMP orange mean/collapse. No new hue family; GREEN and PURPLE are not used in this figure.
- Per deck rule 5, Fig 1 sets tension only: no +0.119, no collapse statistics.

## Agreement with the manuscript caption

The Figure 1 caption in `manuscript/latex/DART_manuscript.tex` now assigns the same five letters
this figure draws: a = the premise on one response coordinate, b = the inverse retrieval task and
the two ways to score it, c = two candidate populations on a shared sample mean, d = when an
evaluator is independent, e = the three evidence classes. An earlier version of this file recorded a
letter mismatch (the caption had no entry for the evaluator-independence panel); the caption was
updated and the mismatch is closed. If the two ever disagree again, the manuscript is the authority
and this file is the bug.

## Files

- `fig1a.py` ... `fig1e.py`, `fig1_assemble.py` (which owns `TITLES`, the layout and the
  module-level `STEM`).
- `fig1_problem.{pdf,svg,png}` : the composite, and the only stem this figure is written under.
  `python figures/build_all.py --write` enforces the 5 pt floor, writes these, and copies the PDF to
  `manuscript/latex/figures/fig1.pdf`, which is the file the manuscript compiles. That copy is part
  of the build; it is no longer a manual step.
- `fig1a_prompt.md` is a historical artefact from when panel a was to be an AI image; panel a is
  now matplotlib code and the prompt is unused.
- `1a.png` ... `1e.png` are standalone per-panel previews, not inputs to the composite.
