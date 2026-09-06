# Figure 1: Perturbation responses can be represented and evaluated at multiple information resolutions

One-line message: a single-cell response can be summarised at more than one resolution, and the
resolution a score reads is a separate choice from the summary it reads it off. Two drugs can share
a mean signature, direction and magnitude both, and still differ in their subpopulation response.
Whether that difference HELPS depends on the evaluator, which is the question the paper answers.
This figure sets the tension; it states no result and contains no Fig-4 collapse numbers.

Panels a-f are drawn from committed code (`fig1a.py` ... `fig1f.py`, composed by
`fig1_assemble.py`) and none of them reads from `results/`: all six are schematic, and the caption
says so. Panels g and h are the two exceptions and are MEASURED, drawn by `fig1g.py` and
`fig1h.py` off `results/exp06_theory_limits/`, which is re-run under the U arm by
`analysis/estimator_audit/run_legacy_suite.sh`. No AI-generated raster is placed in this figure;
see "Panel a provenance" below.

## The terminology rule this figure exists to fix (2026-09-03)

**A mean representation is not direction-only.** The mean vector mu carries a direction AND a
magnitude; it is the COSINE that discards the magnitude. So "direction-only" names a SCORING RULE
in this paper, the mean cosine, and never a representation. Two layers, kept apart everywhere:

| Layer | Values it takes |
|---|---|
| representation | mean `mu`, or the population `P` |
| scoring rule | `s_dir = cos(mu_Q, mu_d)`, `s_mag = -||mu_Q - mu_d||_2`, `s_pop = -D(P_Q, P_d)` |

The information those three read is nested, not parallel: direction < direction + magnitude <
direction + magnitude + population structure. The paper measures both steps, and they are very
unequal: `mean_l2` minus `mean_cosine` is **+0.399** in Hit@1 and `global_energy` minus `mean_l2`
is **+0.048** (Fig. 2a). A figure drawing two rungs where the data has three makes the larger of
those effects impossible to state, which is why panels a, c and d were rebuilt around it and why
the zero-variance sentence in the abstract, the Introduction, the Results and the Methods was
corrected in the same pass. The limit at lambda = 0 is `2||mu_Q - mu_d||`, so it is the
magnitude-aware mean score, not the cosine.

**No panel carries a title, and since 2026-09-01 no panel carries a phrase either.**
`figstyle.strip_titles` removed any rc title a panel script set, and it always did. What it could
not see was ink: seven panels drew a bold 8.5 pt phrase over themselves through a
`fig1_style.title()` helper, and `fig1_assemble` said in a comment that those phrases "are the
caption's own opening clauses". They were, three of them almost word for word, so the figure
asserted its conclusions twice, once where they could be qualified and once where they could not.

Six are gone: "same library, different ranking", "Means tie, distributions separate", "Better
representation, better decision?", "Evidence ladder", "Mean retrieval = zero-variance limit",
"Population scoring is a continuum". The helper is deleted rather than deprecated so no panel can
call it. One survived, the **same mean** label on the drug A/B panel (panel b then, panel c since 2026-09-05), and it survived as a PT_ANNOT label rather than a
PT_TITLE phrase because it NAMES the dashed rule it sits on, the way an axis label names an axis;
without it the reader meets an unexplained orange line.

`fig1_assemble._assert_no_titles` enforces this mechanically: **no panel may draw text above
7.2 pt**, and the build fails if one does. It is a size gate rather than a wording gate, because
no code can tell a claim from a label, but a claim that has to fit at 7.2 pt beside the marks it
describes has already lost the argument for being on the panel. Text that is entirely mathtext is
exempt: panel h sets its y axis to $D_\beta$ at PT_EQ = 9.3, the smallest nominal size whose 0.7x
subscript still clears this figure's 6.5 pt floor. Panel c composes its subscripts from two
artists instead and needs no exemption; panel a did the same until its 2026-09-03 rebuild and now
draws no subscript at all. A symbol is not a claim, and a conclusion sentence is never wrapped in
dollar signs.

## Panels

**SLOTS b AND c EXCHANGED THEIR CONTENT ON 2026-09-05.** Two reasons, pointing the same way. The
Results cite the scoring-rule pair first and the shared-mean pair second, so under the old
assignment panel c was cited before panel b, which Nature's panels-in-citation-order rule does not
allow; Figures 3 and 4 were re-cut for the same reason in the same week. And the grouping is
better: row 1 now holds the representation and the three rules that read it, row 2 the two cases
where the mean is the same and the populations are not, which is what each row argues. The two
boxes are identical at 3.45 x 1.58 in, so nothing was resized and nothing was redrawn. The module
names were left alone, as in `fig3_assemble` and `fig4_assemble`: **`fig1c.py` draws panel b and
`fig1b.py` draws panel c.** Statements further down this file that name a panel by letter were
written before the swap unless they say otherwise; the table just below is current.


| Panel | Claim, which is the caption's to make | Type |
|-------|------------------------------|------|
| a | Representation and scoring rule are two layers; the information they retain is nested | schematic, seeded points, no number |
| b | One pair of populations, three scoring rules | schematic, seeded points |
| c | Same mean shift in direction and magnitude, opposite fate for a hidden minority | schematic, seeded points |
| d | Both mean scores tie, the population score separates | synthetic, seeded RandomState(3) |
| e | Objective-aligned evaluation can reward itself; less score-aligned is not neutral | schematic |
| f | All three evidence classes, reported here | schematic |
| g | The population representation contains its own mean as a zero-variance limit | measured, `exp06_theory_limits/degenerate_limit_synthetic.csv` |
| h | One temperature spans mean aggregation and worst case | measured, `exp06_theory_limits/beta_interpolation.csv` |

## Design notes

- **a** is the figure's definition panel and, since 2026-09-03, nothing else. It reads left to
  right in three columns, which is the order the sentence goes in: the source population in
  SHARED grey with two visible states, then the three scoring rules each beside the geometry it
  actually reads, then a matrix of what each one keeps. The glyphs are the argument in miniature,
  a unit arrow on a faint circle, the same arrow at its true length, and the cells with the
  centroid still on them, and rows one and two carry the SAME orange diamond, which is the
  panel's whole correction made without a word. The nesting is drawn rather than asserted:
  `_matrix` refuses to draw unless each row retains strictly more than the one above it and no
  row drops a property a weaker row keeps. The columns name properties and carry no quantity,
  because how much magnitude is worth is Fig. 2a's measurement, not a schematic's.
  **`draw_1a` rejects any drawn text containing a digit.** A definition panel states no quantity,
  and that is now a build failure rather than a convention. It is also why the middle rule is
  labelled "magnitude-aware mean" and not "mean L2": the digit would fail the build, and the
  caption names the norm instead.
  The four-candidate library and the two ranked stacks this panel drew until 2026-09-03 are gone:
  a ranking outcome on a definition panel invites the outcome to be read as evidence, and d owns
  the outcome on a construction where the tie is provable while e draws retrieval as a ranking
  handed to a judge. The matrix's left edge is set from the MEASURED width of the widest rule
  name, so renaming a rule moves the columns instead of printing them over the name.
- **a was re-cut on 2026-09-06** from a reference layout supplied as an image. Two things in that
  reference were deliberately not carried over. It presented the three rows as a hierarchy of
  response REPRESENTATIONS, with `mu/||mu||` as the first of them; the paper defines two
  representations, `mu` and `P`, the normalisation lives inside the cosine, and the Results call
  these three the scoring rules of Fig. 1a. And it coloured the source cells on a blue-to-orange
  response-magnitude ramp, which inside this figure reads as POP-to-MEAN, two frozen roles;
  cell-to-cell heterogeneity is carried by two states in one grey instead. What was carried over
  is the three-column reading, the per-rule geometry glyph and the retained/discarded matrix,
  which name the three properties as properties where the previous cut named them only as
  segments under an ordinal axis and had two readers take the segment widths for effect sizes.
- **b** shares row 1 with a. Everything sits on one shared response axis, so
  "identical mean shift" is geometry the reader can check rather than a caption assertion: both
  drugs' population-mean markers land on the same orange rule. Drug B's bulk overshoots (1.25 vs
  1.00) exactly because its 20% minority does not move, which is what holds the population mean
  fixed. Each lane is rigidly translated so its drawn population mean is exactly the intended one.
- **c** answers one question, "what statistic of these two populations enters the score?", and
  stops at the score. It draws no candidate library and no ranking; c is the operator and d is the
  consequence of the operator. Its DRAWING has two rows because there are two representations; its
  reference block has three lines because there are three scoring rules, and two of them read the
  same representation and therefore sit behind the same orange diamond. The mean row's link is
  labelled **means only**, not "cosine": a segment between two centroids is what both mean scores
  read, and which of them a reader is looking at is the angle it subtends or the length it has. Both rows plot
  THE SAME two point sets, sampled once at module scope, so the difference between the rows is the
  operator and not the data; the upper row's centroids are the actual means of those points. The
  filled, rounded, coloured cards this panel used to draw each rule in are gone: they were the main
  source of the figure's slide-deck look, and the rows are now separated by whitespace and one grey
  grouping rule.
- **d** is a labelled schematic, not a data panel. Both candidate clouds are rigidly translated
  onto the target's sample mean so the "shared mean" marker is exactly true, and the marginal
  density band carries the inequality (bimodal vs unimodal), which an overlaid scatter does not.
  It returns THREE verdicts, not two. Both mean rows tie, and they tie for a reason stronger than
  a drawing: A and B share a sample mean to 1e-12, so every score that reads only that mean is the
  same number for both, whatever it reads off it. The population row is checked the same way, by
  a one-dimensional energy distance computed on the cells the panel actually drew; if A ever stops
  being the closer population the panel raises instead of printing `A > B`.
- **e** contrasts a closed loop (Class A: score and metric are one function, no way to lose)
  with an open chain that can end either way (Class B/C). Its lanes read **Objective-aligned
  evaluation** and **Less score-aligned evaluation**. They read "Coupled" and "Independent" until
  2026-09-03, and the second name was the problem: "independent" invites "therefore neutral,
  therefore the truth", and Figure 4 is the demonstration that it is not, two external protein
  evaluators built from the same cells preferring opposite retrieval scores on the same ranking. It has no boxes, no fills and no hue:
  the nodes sit directly on the canvas and the only strokes are the connectors, because the claim
  is a line SHAPE and the filled coloured cards it used to draw were the heaviest ink in the panel.
- **f** states this study's evidence coverage against the field audit. Two corrections were made
  here: the ladder used to put Class A at the top of an "evidence strength" arrow, which inverts
  the paper's own argument, and the status column used to read "this study: none" for Class C,
  which contradicts "We report PopRetrieve under all three classes". Class C is now at the top of
  an axis named for what actually increases, **less coupled to the retrieval score**, and the
  Class-C entry is marked reported-but-imported. That axis label said "more independent of the
  retrieval objective" until 2026-09-03; "independent" is an absolute and this axis has no
  absolute end, so the head of the arrow now carries the gloss `less score-aligned != automatically
  neutral`, which is the one inference a reader must not draw from the rise. Like e, it carries no fills and no hue: the tiers
  are separated by hairline rules, and the ordinal axis is encoded by a short vertical tick in a
  grey RAMP, which is the right encoding for an ordinal quantity where three unrelated hues were
  not.
- **g and h are the figure's only measured panels**, and they are here because each is the
  quantitative form of a claim a and c only draw. g measures the limit that makes a mean signature
  and a population the same object, the energy distance meeting the distance between means at
  lambda = 0 (98.50 against 98.50), so the mean REPRESENTATION is the zero-variance corner of the
  population representation rather than a rival to it. That endpoint is `2||mu_P - mu_T||`
  (`exp06_theory_limits.py` line 64), a Euclidean distance, so it is the magnitude-aware mean
  score and not the cosine; the panel's rule is labelled "distance between means" for that reason.
  h shows that c's resolutions are one score at two temperatures, D_beta running from the
  arithmetic mean over subpopulations (0.7125) to the worst-matched subpopulation (1.300), so
  "population" is itself a family and not one score. Both were drawn by `edfigs/ed_panels.py`
  (ED1b and ED1c there, main-text Fig. 2c and Fig. 2e before that) when the Extended Data deck
  existed; they now live in `fig1g.py` and `fig1h.py`, which read the same two CSVs.
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
- Palette semantics are the house ones, set in `fig1_style`: GREY context, FOCAL blue
  distributional, COMP orange mean/collapse, GREEN an evaluator the method never saw. PURPLE is
  not used. This paragraph used to claim that "colour appears only in a-d" and that e and f "are
  ink and grey", and neither was true of the code: panel e fills its retriever and evaluator
  circles in POP blue, its ranking cards in SHARED grey and its judge card in EXT green, and panel
  f washed its three platforms in POP, SHARED and EXT.
  **Panel e's fills are correct** and stay: a circle labelled "population distance" IS a
  population-level object, the ranking cards ARE shared machinery, and the judge IS an external
  evaluator, so all three uses are the vocabulary's own meanings.
  **Panel f's were not**, and were fixed on 2026-09-01. An evidence class is neither
  "population-level" nor "everything both routes have in common", so two of the three platforms
  gave established colours a second, contradictory meaning in the last panel a reader reaches. The
  ordinal axis is already carried by the staircase offset and by the labelled arrow, so hue was
  carrying only the false signal; the three platforms are now one neutral. See `CORRECTIONS.md` R57.
- **Bold is structural only.** Section labels, row identifiers and branch names are bold; every
  conclusion and every annotation is set plain. A bolded conclusion is emphasis, not information,
  and this figure previously had eight of them competing with the marks they described.
- Per deck rule 5, Fig 1 sets tension only: no +0.119, no collapse statistics.

## Print geometry, authored 1:1

The manuscript text block is 6.951 in and the figure enters with
`\includegraphics[width=\textwidth]`. The canvas is **6.90 x 7.92 in** and exports 176 x 201 mm,
so nominal point size is printed point size. The float budget is the 9.461 in text block less about
16/72 in of overhead, i.e. 9.238 in.

It was 234 mm until 2026-09-01 and 219 mm until 2026-09-04. Both cuts are in the furniture rather
than the drawings, because the drawings will not take one: panels a, c and d are laid out in
absolute inches and points, so a shorter row clips them rather than compressing them, and a
asserts its own height to stop that happening silently. `LETTER_BLOCK` has gone 0.24 to 0.17 to
0.15 and `ROW_GAP` 0.30 to 0.22 to 0.11, both measured against the render: the white between the
last ink of one row and the letter of the next was 0.26 in on all three corridors. Rows 3 and 4
gave back the slack their tightest panel was measured to have, 0.08 and 0.15 in, the latter once
the g/h cartoon strip lost the 0.12 in of white above its marks.

The rows themselves gave back almost nothing, and that is a property of the panels rather than
carelessness: these are schematics whose type is absolute while their layout is fractional, so
shrinking a row compresses the drawing around text that does not shrink with it. Each row was cut
by less than its TIGHTEST panel's measured slack: 0.024 in spare in b, 0.023 in d, 0.042 in f,
0.014 in g, cut by 0.02, 0.02, 0.03 and 0.01. Measure scatter collections from their offsets when
checking this; `PathCollection.get_window_extent` does not report the drawn points, and reading it
made panel c look like it had 0.40 in of dead space at the top when it has 0.06.

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

**The panel no longer descends from that reference at all.** The 2026-09-03 rebuild replaced the
pipeline with the representation-and-scoring hierarchy, so the raster now documents an earlier
design of an earlier panel. It is kept for the same reason as before, so the panel's origin stays
auditable, and the three notes below are history rather than a description of what ships.

Three things changed in the first redraw, all deliberate. The reference put a second explanatory line
under each branch label ("one vector per perturbation", "cell-to-cell structure retained"); at
1.67 in of panel height those lines could only have been set below the floor, so they are in the
caption instead, which is where the repo's own rule sends them. The reference gave the two branches
visibly different clouds; the redraw gives them one shared query cloud, for the reason in the
design note above. And the reference drew the candidate library and the ranked list as separate
stages, which needs width this panel does not have; they are one ranked library column here.

## The a / c / d division of labour

These panels overlapped when a was added: a drew the pipeline with the fork between the two
representations, and c drew that same fork again, with its own query, its own candidate library
and its own ranked list. The overlap was removed by narrowing c rather than by deleting it, and
narrowed again on 2026-09-03 when a gave up its library and its ranked stacks. The division now:

- **a owns the vocabulary.** Two representations, three scoring rules, and the nesting of what
  they retain. No pair, no library, no ranking, no number.
- **c owns the operator.** One query-candidate pair, drawn twice, and the three scores written
  out on it. No library and no ranking.
- **d owns the consequence.** Two candidates for which the two mean scores are provably tied and
  the population score is not.

Nothing that appears in a appears again in c; in particular c must not regain a candidate library
or a ranked list, and a must not regain either.

## Agreement with the manuscript caption

The Figure 1 caption in `manuscript/latex/PopRetrieve_manuscript.tex` assigns all eight letters:
a = one population, the three scoring rules and the geometry each reads, with the
retained-information matrix, b = the
premise on one response coordinate, c = one pair of populations and the three scoring rules,
d = two candidate populations on a shared sample mean with three verdicts, e = objective-aligned
against less score-aligned evaluation, f = the three evidence classes on a coupling axis,
g = the zero-variance limit and what that endpoint actually is, h = the coverage temperature. If
the two ever disagree, the manuscript is the authority and this file is the bug.

The caption also carries the terminology rule in print: "Direction-only names the mean cosine
score throughout this paper and never a representation."

**No longer open.** This section used to record that the caption had six entries against the
figure's eight, and that g and h still needed theirs written. The caption has carried all eight
since the 2026-08-31 pass, including g's `98.50=98.50` at lambda = 0 and h's 0.7125 and 1.300
endpoints, and it names `exp06_theory_limits` as their source. It also used to point at a `TITLES`
dict in `fig1_assemble.py` as the thing to check the caption against; there is no such dict, and
after the phrase removal above there is nothing for one to hold.

## Files

- `fig1_style.py` : the frozen vocabulary. Four colours with one meaning each and one type ladder.
  There is no `title()` helper and there must not be one again; see the note at the foot of that
  file.
- `fig1a.py` ... `fig1h.py`, and `fig1_assemble.py`, which owns the inch ledger, the panel letters,
  the 6.5 pt floor gate and the 7.2 pt no-titles gate, plus the module-level `STEM`. The filename
  letter always equals the panel letter. An earlier version of this section said g and h had no
  modules and were drawn by `ed_panels.draw_ed1d/e` directly; both files exist and
  `fig1_assemble` imports `draw_1g` and `draw_1h` from them.
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
