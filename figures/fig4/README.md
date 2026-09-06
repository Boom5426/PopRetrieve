# Figure 4: external evaluation is not automatically neutral, and heterogeneity is not reordering

One-line message: an external, unseen readout is not automatically a fair judge, and natural
heterogeneity that is real and recoverable can still leave candidate ordering intact. The figure
runs in three movements and does not return to any of them:

    a, b, c   EVALUATOR DEPENDENCE. Hold the rankings and the biological measurements fixed,
              change only the statistical form of an external protein evaluator, and the winner
              swaps. The magnitude control then shows that the swap is not distribution-specific.
    d         CONCEPTUAL BOUNDARY. A closed-form existence proof that settings where population
              structure changes the preferred candidate exist at all, and nothing more.
    e, f      NATURAL CONSTRAINT. Real tumour tissue contains recoverable response structure that
              unsupervised methods do not fully reach, and its two disjoint compartments still
              rank the same drug pairs the same way.

**SIX PANELS SINCE 2026-09-05, DOWN FROM SEVEN, AND 6.90 x 5.48 IN RATHER THAN 6.90 x 6.35.**
Two changes, made together.

The tumour-cohort schematic (`fig4_tissue.py`, the old d) left. It carried no data, and the Results
sentence that cited it already states its whole content: "each tumour was split by cell identity
into disjoint malignant and myeloid compartments that share no cells and received the same drug and
matched control". The caption states it again. `fig4_tissue.py` is kept on disk and imported by
nothing.

**The analytic boundary moved from last to fourth, because that is where the text cites it.** The
Results run design, reversal, magnitude control, then the boundary as the bridge into the tumour
section, then the two tumour panels. With the boundary drawn last, a reader was sent from panel c
to panel g and back to d. Nature asks for panels in citation order; Figure 3 was re-cut for the
same reason on 2026-09-04. Only one letter changes in the manuscript, g to d, because the two
tumour panels keep the letters they already had.

**The height came out, and the width could not.** Measured on the 2026-09-04 render, the two lower
rows carried 0.82 and 0.87 in of dead gutter while every row sat at its authored height. Two panels
per row cannot fill 6.90 in here: two of the six are aspect-locked squares, `fig4_nat` by an
explicit `set_aspect("equal")` and the boundary panel by being a unit square, and a square of side
h contributes h of width, so the panel beside it would have to run to about 5.5 - h inches to reach
the page edge. That is a 4 in bar chart at these heights. The gutter is structural, so the fix was
to take the height out rather than stretch the panels. Each row now stands at what its own tightest
panel was MEASURED to need, by bisecting that panel alone until its own assertions or
`check_overlaps.py` fired: 1.66 in (a), 1.05 in (neither binds) and 1.25 in (e). The figure prints
at 176 x 140 mm against 176 x 162 mm, its panels are unchanged, and no annotation was cut.

**SEVEN PANELS SINCE 2026-09-03, DOWN FROM NINE.** Four HIR-Bench panels and one natural-tissue
panel left. HIR-Bench had five of the nine panels in a figure about external evaluation, and a real
transition-to-intervention benchmark now exists elsewhere in the paper, so it keeps exactly one
panel here and keeps the one that is an existence proof rather than a measurement. The natural
panel that left drew a cosine between two compartment response directions, which is confounded with
effect size and signal-to-noise and therefore cannot carry the quantitative reading the main text
gave it. All five are now prose in Supplementary Notes 1 and 4; **no supplementary figure was
created**, because the SI has never carried one and two sentences in the manuscript say so.

**Authority.** [docs/phase2/FINAL_FIGURE_NUMBER_LEDGER.md](../../docs/phase2/FINAL_FIGURE_NUMBER_LEDGER.md)
is the authority for every number this figure draws, with its source file, its estimator arm and
the pre-repair value it replaced. `../../CORRECTIONS.md` is the authority for what has been
retracted. If this file disagrees with either, this file is the bug. Layout, canvas geometry and
the reasoning behind the restructure live in the `fig4_assemble.py` docstring.

**THE EXPLANATION THIS FIGURE RETIRED.** Until 2026-09-03 panel b's reversal was explained as
distribution-specific compatibility: a population-shaped evaluator rewarding a population-shaped
scorer. Under the V-statistic energy distance that reading had an eightfold gap behind it. Under
the unbiased U-statistic the gap is 1.2-fold, and panel c exists to draw that. The frozen wording
is in [POST_REPAIR_MASTER_RESULTS.md](../../docs/phase2/POST_REPAIR_MASTER_RESULTS.md) C1 and is
asserted, not merely written down: `fig4_shape.RESID_RATIO_MAX` and `fig4_residual.RATIO_MAX` both
stop the build if the two residuals separate again.

## Panels

| Row | Panel | What the reader sees | Reads |
|---|---|---|---|
| 1 | a | one experiment branching once, on the right-hand side only | `results/upgrade/oracle_shape_join_provenance.json` |
| 1 | b | two bar groups whose tallest bar changes colour between them | `results/upgrade/oracle_shape_test.json` |
| 2 | c | four pairs of markers that nearly coincide | same |
| 2 | d | a unit square cut by the identity line | `results/exp11_hir_benchmark/theoretical_boundary.csv` (provenance only) |
| 3 | e | a short gap on the left and a tall one on the right | `results/zhao_gbm/gate2_drug_response.json`, `gate2_uncertainty.json` |
| 3 | f | a cloud hugging the diagonal | `results/zhao_gbm/premise_mean_vs_compartment.csv` |

Rows 2 and 3 each end short of the right margin by 0.2 to 0.35 in, and that is the square panels
again: d and f can use no more than their row height whatever box they are given, so the width they
do not use has nothing to spend itself on. Filling those rows would mean a 4 in dot plot and a 4 in
bar chart. The height was taken out instead.

One of the six is a schematic that draws no result. It is not decoration: a is the control that
licenses b, and it was a clause in b's caption until it was given its own panel, which is where a
reader least expects to find the reason a result means anything. The second schematic, the tumour
cohort's, was removed on 2026-09-05 for the opposite reason: its content was already carried in
full by the sentence that cited it.

## Honesty notes (the load-bearing caveats)

- **e is scoped to the tumour on purpose.** The constructed arm in the same axes shows a gap of
  $+0.007$, i.e. there the limit is *not* algorithmic; an unscoped title would
  contradict one of its own two bar groups. The 0.692 quoted for this construct elsewhere is the
  earlier in-fold run (Fig. 5e), and the 0.964 once reported for natural tissue is **withdrawn**: it
  separated malignant from myeloid *control* cells, a cell-type rather than a drug-response
  partition (`CORRECTIONS.md` R18 and R21).
- **e's bounds are optimistic and the panel says so.** 30 of the 36 splits come from one patient
  (PW030) and 39.9% of cells are dropped by the compartment-assignment margin, so the discarded
  cells are by construction the hardest to place. The drug panels also differ between arms.
- **No $p$-value is given for f**, since 15 of the 18 pairs come from one patient. e and f are the
  arm on which both gates turn out to be OPEN and the distributional advantage still does not
  appear: the two gates are necessary, not sufficient.
- **b's 0.400-versus-0.5 gap is not itself interpretable.** The label is a deterministic step
  function of (alpha, conflict), so the 13,440 instances contain only 28 independent parameter cells
  and every held-out fold is single-class; no per-fold AUC distribution exists. The comparison that
  carries the claim is between the two feature sets and between the two CV units, not against 0.5.
- **c is the sharpest result here because no scorer can see either oracle.** The magnitude scalar is
  drawn as a third bar and is not decoration: an energy distance tracks a candidate's own response
  magnitude ($\rho = +0.791$), so a magnitude-to-magnitude channel could in principle have produced
  the swap with no distribution ever compared. It does not, quite; energy still leads it by $+0.177$
  under the distributional oracle against $+0.022$ under the mean-shaped one.
- **e and f are drawn by `fig7/fig7_natural.py`, not reimplemented here.** `fig4_nat.py` imports
  those two draw functions unchanged and only retunes annotation text, positions and font sizes for
  the 6.9 in canvas, each edit keyed to a substring of the original text so an upstream rewording
  fails the build instead of silently leaving a too-wide label on the page. There is exactly one
  copy of the plotting code.
- Palette semantics are the deck's: blue distributional/PopRetrieve, orange mean/collapse, grey context,
  purple the natural-tissue arm. Green is *not* used in row 3: across the deck green marks readouts
  handed information the retrieval method does not have, and in panel e colour encodes the
  experimental arm, so both bars of every arm share one hue.

## What is NOT in this figure any more

HIR-Bench earned two panels of argument in the 2026-07-12 judgement and three more of audit when
the Extended Data deck was retired on 2026-08-30. On 2026-09-03 it earns one. The reason is not
that anything it showed was wrong; it is that a real transition-to-intervention benchmark now
exists in this paper, and a synthetic construction should not hold five of nine panels in the
figure about whether external evaluation can be trusted. What remains is the closed-form
existence proof, which is the one thing HIR-Bench can do that no measurement can.

Gone from the main figure, and where each went:

| Was | What it showed | Now |
|---|---|---|
| b | honest-vs-leaky classifier AUC, 2x2 | Supplementary Note 1, prose, with all four AUCs and both leakage deltas |
| e | induced response cosine, 17 patient-drug pairs, median 0.566 | Supplementary Note 4, prose, labelled descriptive and explicitly not a measure of differential-response strength |
| g | empirical energy-minus-mean phase grid, 36 cells | Supplementary Note 1, prose |
| h | decision regret by information condition | Supplementary Note 1, prose |
| i | three HIR-Bench sanity checks | Supplementary Note 1, prose, all three with their thresholds |

Two earlier removals still stand. The generative-model **schematic** read no result file and drew
no data. The failure-predictability **ROC curve** was replaced by the 2x2 that has now itself moved
to the SI; `fig4f_roc_curve.csv` and `fig4f_roc_summary.json` in this directory are its retired
source data. `fig4f.py` is still on disk and still builds standalone; it is simply no longer
imported by the assembler.

**No supplementary FIGURE was created for any of this.** `manuscript/latex/PopRetrieve_SI.tex` has
never contained a float, `figures/build_all.py` has no supplementary branch, and the SI binds
`\figurename` to "Extended Data Fig.", which is the wrong series. Both documents' panel accounting
was updated instead: nine of the former 21 Extended Data panels are in the main figures and twelve
are carried in prose.

## Files

- `fig4b.py`, `fig4f.py`, `fig4_shape.py`, `fig4_gate2.py`, `fig4_nat.py` : the panel modules for
  a, b, c, d, then e and f. The names are historical (`fig4b`/`fig4f` predate the re-lettering);
  the mapping above is the authoritative one and `fig4_assemble.py` states it too.
- g through m have NO module in this directory. They are imported from `../ed6/` and `../ed4/`,
  the same way e and f are imported from `../fig7/`, because a second copy of a draw function is a
  second thing to keep in step with the result files. The Extended Data deck being retired is not a
  reason to fork its panels into five main-figure directories.
- `fig4_assemble.py` : the 13-panel four-row layout, authored at the FINAL PRINTED width of 6.90 in so
  LaTeX applies no scaling and nominal point size == printed point size. Panel rectangles are in
  inches, not gridspec ratios. It owns `TITLES`, `ROW_LABELS` and the module-level `STEM`.
- `fig4_benchmarks.{pdf,svg,png}` : the composite, and the only stem this figure is written under.
  `python figures/build_all.py --write` enforces the 5 pt floor, writes these, and copies the PDF to
  `manuscript/latex/figures/fig4.pdf`, which is the file the manuscript compiles.
- Superseded artefacts kept in this directory, none of them an input to the current figure:
  `fig4_hir_bench.{png,pdf}` and `fig4_hir_bench_partial.png` (the old six-panel composite),
  `_fig5_partial.png`, `fig4f_roc_curve.csv` and `fig4f_roc_summary.json` (source data for the
  retired ROC panel), the `4b.png` / `4f.png` standalone previews, and `_stale/` (see
  `_stale/README.md`).
