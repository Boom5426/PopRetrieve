# Figure 1: Distributional differences are visible, but their value depends on the evaluator

One-line message: two drugs can share a mean signature yet differ in their subpopulation response,
so distribution-aware retrieval can see structure mean-signature retrieval cannot. Whether that
structure HELPS depends on the evaluator, which is the question the paper answers. This figure sets
the tension; it contains NO Fig-4 collapse numbers.

Panels a-f are drawn from committed code (`fig1a.py` ... `fig1f.py`, composed by
`fig1_assemble.py`) and none of them reads from `results/`: all six are schematic, and the caption
says so. Panels g and h were added when the Extended Data deck was retired and are the two
exceptions: they are MEASURED, drawn by `figures/edfigs/ed_panels.py` off
`results/exp06_theory_limits/`. No AI-generated raster is placed in this figure; see "Panel a
provenance" below.

**No panel carries a title.** A Nature-family panel carries axis labels, tick labels, direct
labels on the marks and a key, and the explanation is the caption's job; `figstyle.strip_titles`
is called at the end of `build()` and removes any title a panel script sets, so the claims in the
table below reach the reader as the caption's entries, one per letter. The panel scripts keep their own
`set_title` calls, which is what labels a standalone `python fig1x.py` preview.

## Panels

| Panel | Claim (stated in the caption, NOT drawn on the panel) | Type |
|-------|------------------------------|------|
| a | One population, two representations, one ranking | schematic, seeded points |
| b | Same mean shift, opposite fate for a hidden minority | schematic, seeded points |
| c | The same pair, scored at two resolutions | schematic, seeded points |
| d | Means tie, distributions separate | synthetic, seeded RandomState(3) |
| e | Aligned evaluation can reward itself | schematic |
| f | All three evidence classes, reported here | schematic |
| g | Mean retrieval is the zero-variance limit of population retrieval | measured, `exp06_theory_limits/degenerate_limit_synthetic.csv` |
| h | One temperature spans mean aggregation and worst case | measured, `exp06_theory_limits/beta_interpolation.csv` |

## Design notes

- **a** is the pipeline the whole paper operates on. There is exactly ONE query cloud and both
  branches leave it: the difference the paper measures is in what each representation keeps, not
  in what it is given, so a separate cloud per branch would put the difference in the input. The
  collapse is drawn ON the upper branch, as a fan of thin leaders running from the query cells
  into a single orange dot, which is where the blue minority visibly disappears; the lower branch
  carries the population across intact. The candidate library and the ranked list are one object,
  a library column carrying rank numbers, and both branches point into it, because both rules rank
  the same library for the same query.
- **b** shares row 1 with a. Everything sits on one shared response axis, so
  "identical mean shift" is geometry the reader can check rather than a caption assertion: both
  drugs' population-mean markers land on the same orange rule. Drug B's bulk overshoots (1.25 vs
  1.00) exactly because its 20% minority does not move, which is what holds the population mean
  fixed. Each lane is rigidly translated so its drawn population mean is exactly the intended one.
- **c** answers one question, "what statistic of these two populations enters the score?", and
  stops at the score. It draws no candidate library and no ranking, because a already carries the
  pipeline end to end; c is the operator and d is the consequence of the operator. Both rows plot
  THE SAME two point sets, sampled once at module scope, so the difference between the rows is the
  operator and not the data; the upper row's centroids are the actual means of those points. The
  filled, rounded, coloured cards this panel used to draw each rule in are gone: they were the main
  source of the figure's slide-deck look, and the rows are now separated by whitespace and one grey
  grouping rule.
- **d** is a labelled schematic, not a data panel. Both candidate clouds are rigidly translated
  onto the target's sample mean so the "shared mean" marker is exactly true, and the marginal
  density band carries the inequality (bimodal vs unimodal), which an overlaid scatter does not.
- **e** contrasts a closed loop (Class A: score and metric are one function, no way to lose)
  with an open chain that can end either way (Class B/C). It has no boxes, no fills and no hue:
  the nodes sit directly on the canvas and the only strokes are the connectors, because the claim
  is a line SHAPE and the filled coloured cards it used to draw were the heaviest ink in the panel.
- **f** states this study's evidence coverage against the field audit. Two corrections were made
  here: the ladder used to put Class A at the top of an "evidence strength" arrow, which inverts
  the paper's own argument, and the status column used to read "this study: none" for Class C,
  which contradicts "We report PopRetrieve under all three classes". Class C is now at the top of
  an axis named for what actually increases (independence from the retrieval objective), and the
  Class-C entry is marked reported-but-imported. Like e, it carries no fills and no hue: the tiers
  are separated by hairline rules, and the ordinal axis is encoded by a short vertical tick in a
  grey RAMP, which is the right encoding for an ordinal quantity where three unrelated hues were
  not.
- **g and h are the figure's only measured panels**, and they are here because each is the
  quantitative form of a claim a and c only draw. g measures the limit that makes a mean signature
  and a population the same object, the energy distance meeting the mean-to-mean distance at
  lambda = 0 (98.50 against 98.50), so mean-signature retrieval is the zero-variance corner of the
  task in a rather than a rival to it. h shows that c's "two resolutions" are one score at two
  temperatures, D_beta running from the arithmetic mean over subpopulations (0.7125) to the
  worst-matched subpopulation (1.300). Both came from `edfigs/ed_panels.py` (ED1b and ED1c there,
  main-text Fig. 2c and Fig. 2e before that) and are still drawn by it, not copied here, so the
  four endpoint numbers have one source.
- **Row 1 is two panels wide, not two rows.** Giving a and b a full row each was tried and
  rejected on a measurement: at four rows the canvas needs 7.9 in, and pdflatex then reports
  `Float too large for page by 147.66pt` for this float, because the 681 pt text block has to hold
  the figure AND a six-entry caption. That constraint has since been lifted, since captions now set
  on a following page and the graphic owns 9.30 in on its own, which is what made room for the
  fourth row. The redesign it forced is kept rather than undone: a merged the library and the
  ranked list into one ranked column, and b wrapped its two right-flank minority labels onto two
  lines so they stopped overrunning the canvas. Both are recorded above and in the panel sources.
- **Row 4 starts one grid column in**, at columns 1-6 and 7-12. g and h are the only panels here
  with a y axis, one y apparatus measures about 0.35 in, and the left margin leaves 0.31 in; at
  columns 0-6 the y label of g would be drawn outside the canvas, and `pin_canvas` makes the
  exported page the union of canvas and ink, so that overhang would widen the PDF past the text
  block. Widening the left margin instead would narrow a, b, c, e and f by about 2 per cent each,
  which panel b cannot afford.
- Palette semantics are the house ones: GREY context, FOCAL blue distributional/PopRetrieve signal,
  COMP orange mean/collapse. No new hue family; GREEN and PURPLE are not used in this figure.
  **Colour appears only in a-d**, where those meanings apply. Panels e and f are about
  coupled-versus-independent evaluation and about evidence class, which are neither
  "distributional" nor "mean", so painting them blue and orange gave both hues a second,
  contradictory meaning inside one figure. They are ink and grey.
- **Bold is structural only.** Section labels, row identifiers and branch names are bold; every
  conclusion and every annotation is set plain. A bolded conclusion is emphasis, not information,
  and this figure previously had eight of them competing with the marks they described.
- Per deck rule 5, Fig 1 sets tension only: no +0.119, no collapse statistics.

## Panel a provenance

Panel a was designed as a generated concept image (`fig1a_reference.png`, GPT Image, 1448 x 1086
px) and then **redrawn in matplotlib**; the raster is a design reference, not a figure input, and
nothing in the build reads it. It is kept so the panel's origin stays auditable.

The raster was not pasted in, and the reason is measured rather than stylistic. At the authored
6.9 in canvas the returned image is about 210 dpi, well under the line-art resolution Nature
Portfolio expects. Its 4:3 frame, dropped into a row whose panels are 1.67 in tall, shrinks to a
block occupying roughly a third of the width and leaves the rest empty. And its text is baked into
pixels, so `figstyle.assert_min_fontsize` cannot see it: the 5 pt production floor that gates every
other panel would have silently stopped applying to this one.

Three things changed in the redraw, all deliberate. The reference put a second explanatory line
under each branch label ("one vector per perturbation", "cell-to-cell structure retained"); at
1.67 in of panel height those lines could only have been set below the floor, so they are in the
caption instead, which is where the repo's own rule sends them. The reference gave the two branches
visibly different clouds; the redraw gives them one shared query cloud, for the reason in the
design note above. And the reference drew the candidate library and the ranked list as separate
stages, which needs width this panel does not have; they are one ranked library column here.

## The a / c division of labour

These two panels overlapped when a was added: a drew the pipeline with the fork between the two
representations, and c drew that same fork again, with its own query, its own candidate library
and its own ranked list. The overlap was removed by narrowing c rather than by deleting it. Panel
a owns the pipeline: query, the two representations, the library, the ranking. Panel c owns the
operator: one query-candidate pair, and the two statistics that can be taken of it, ending at a
score. Panel d then owns the consequence, two candidates for which the two statistics disagree.
Nothing that appears in a appears again in c; in particular c must not regain a candidate library
or a ranked list.

## Agreement with the manuscript caption

The Figure 1 caption in `manuscript/latex/PopRetrieve_manuscript.tex` assigns the first six
letters this figure draws: a = the retrieval pipeline and the representation fork, b = the premise
on one response coordinate, c = the inverse retrieval task and the two ways to score it, d = two
candidate populations on a shared sample mean, e = when an evaluator is independent, f = the three
evidence classes. If the two ever disagree, the manuscript is the authority and this file is the
bug.

**Open, and known:** the caption has six entries and the figure now has eight. g and h still need
their entries written, and they carry measured numbers, so the caption must also state the source
(`results/exp06_theory_limits/`) and the four endpoints (98.50 against 98.50 at lambda = 0; 0.7125
and 1.300 for D_beta). Their claims are in `TITLES` in `fig1_assemble.py`, which is what the
caption should be checked against.

## Files

- `fig1a.py` ... `fig1f.py`, `fig1_assemble.py` (which owns `TITLES`, the layout and the
  module-level `STEM`). The filename letter always equals the panel letter; when a panel is
  inserted or removed the modules are renamed with it. g and h break that rule on purpose: they
  have no `fig1g.py` or `fig1h.py`, because `fig1_assemble.py` imports
  `ed_panels.draw_ed1d` and `ed_panels.draw_ed1e` directly and a local copy would be a second
  place for their numbers to drift.
- `fig1_problem.{pdf,svg,png}` : the composite, and the only stem this figure is written under.
  `python figures/build_all.py --write` enforces the 5 pt floor, writes these, and copies the PDF to
  `manuscript/latex/figures/fig1.pdf`, which is the file the manuscript compiles. That copy is part
  of the build; it is no longer a manual step.
- `fig1a_reference.png` is the generated concept image panel a was redrawn from; see above.
- `fig1b_prompt.md` is a historical artefact from when panel b (then lettered a) was to be an AI
  image; panel b is matplotlib code and the prompt is unused.
- `1a.png` ... `1f.png` are standalone per-panel previews, not inputs to the composite.
  `fig1a.py`, `fig1b.py` and `fig1c.py` draw their previews on the SAME axes geometry the
  composite gives those panels (3.167 x 1.530 in for a and b, 3.724 x 1.580 in for c, no subplot
  margins; the heights recorded here were 1.670 and 1.733, which were the values of a canvas two
  revisions ago), because an x position tuned against a preview of a different width is wrong in the
  figure that ships, which is how the first draft of panel a overlapped its own footer and how
  panel c's row label was clipped. The other three previews still use matplotlib's default margins
  and are therefore approximate; treat the composite as the authority for spacing.
