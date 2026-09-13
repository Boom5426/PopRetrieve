# Final figure number ledger

Every number that a main-figure panel or its caption prints, with the file it is computed from,
the code that computes it, the estimator arm it belongs to, and every other place in the
manuscript that repeats it. The purpose is single: after the U-statistic reissue, no number may
appear in two places with two values, and no number may appear anywhere without a file behind it.

**Rules this table enforces.**

1. A value is listed at the precision it is DRAWN at. Where the caption and the panel print
   different precisions, both are given.
2. `Arm` is the estimator the source file was produced under. `U` is the unbiased U-statistic
   energy distance (`POPRETRIEVE_ESTIMATOR=u`), which is the manuscript's arm since 2026-09-03;
   `n/a` marks a quantity the estimator cannot reach (a cosine, a Spearman correlation between
   score columns, a cell count).
3. No number in this table was typed from a document. Each was read back out of the panel module
   or recomputed from the source file at the time this ledger was written.
4. Pre-repair values are recorded in the last column where the reissue moved them, so a reviewer
   comparing against an earlier draft can see what changed and by how much.

**Status.** All six main figures are complete and the whole deck builds CLEAN.

---

## Figure 1. Perturbation responses can be represented and evaluated at multiple information resolutions

Figure 1 is the only main figure that is almost entirely definitional, and after the 2026-09-03
cleanup that is enforced rather than intended: `fig1a.draw_1a` asserts that no text it drew
contains a digit, and panels b to f draw no measured value either. Two panels carry numbers, g
and h, and both read `results/exp06_theory_limits/`, re-run under the U arm on 2026-09-03 as part
of `analysis/estimator_audit/run_legacy_suite.sh` (line 58).

### The terminology this figure fixes, and why it is a number question

Until 2026-09-03 panels a, c and d drew a two-way fork, "mean route" against "population route",
and the manuscript called mean-signature retrieval the zero-variance limit of population
retrieval. Both statements silently identify the mean REPRESENTATION with the direction-only
SCORE. They are not the same object, and the paper's own measurement is what separates them:

| Step | Scores compared | Value | Source |
|---|---|---:|---|
| direction to + magnitude | `mean_l2` minus `mean_cosine` | **+0.3992** | Fig. 2a ledger row |
| + magnitude to + distribution | `global_energy` minus `mean_l2` | **+0.0480** | Fig. 2a ledger row |

A figure that draws two rungs where the data has three makes the larger of these two effects
impossible to state. Panel a now draws all three as one nested information axis, panel c writes
all three scores out, and panel d returns three verdicts instead of two.

### Panels b and c exchanged content on 2026-09-05

The Results cite the scoring-rule pair first and the shared-mean pair second, so panel c was being
cited before panel b. The two boxes are identical at 3.45 x 1.58 in, so the fix was to exchange
which draw function each slot calls: panel b is now "one pair of populations and the three scoring
rules" (`fig1c.py`) and panel c is "under drug B a resistant fifth does not move" (`fig1b.py`).
Row 1 therefore holds the representation and the rules that read it and row 2 the two shared-mean
cases, which is also the better grouping. The two Results citations became a,b and c,d, the second
of which no longer over-cites the scoring-rule panel for a claim about shared means. Everything
above this line that names panels b or c predates the swap.

### a to f. Nothing measured, and nothing printable

| Panel | Draws | Guard |
|---|---|---|
| a | representation fork, three scoring rules, nested information axis | `draw_1a` rejects any drawn text containing a digit; the three bar reaches must increase strictly and the last must equal the axis end |
| b | three lanes, 80/20 split, `R_MAJ_B` derived from the minority fraction | every cloud is translated onto its own drawn sample mean; the Drug B minority lands on the ghost to 1.1e-16 axes fractions |
| c | one pair of populations, three equations | the collapse must land within `MEAN_TOL_PT` = 0.10 pt of its column |
| d | three populations on one shared mean | `abs(cand_a.mean() - cand_b.mean()) < 1e-12`, and `_energy_1d(tgt, A) < _energy_1d(tgt, B)` on the cells actually drawn |
| e | two judging scenarios | schematic; no file |
| f | three evidence levels, two status columns | reads `manuscript/components/related_work_metric_audit_table.csv`; refuses to draw a headline class the ladder has no step for |

The one count panel f prints, **6 families surveyed**, is the audit table's row count less the
`PopRetrieve / distributional retrieval` row (7 rows, one excluded). It is read, never typed.

### g. The zero-variance limit

Source `results/exp06_theory_limits/degenerate_limit_synthetic.csv`, rows `prop1_spread`, drawn by
`figures/fig1/fig1g.py`. Arm: U.

| Quantity | File value | Drawn |
|---|---:|---|
| `energy` at `t_spread` = 0 | 98.50160217285156 | the curve's left endpoint, enlarged marker |
| `two_dmu` (constant) | 98.50164031982422 | the flat orange rule, "distance between means" |
| the printed identity | | `98.50 = 98.50`, both sides read from the file |
| `energy` at 0.5, 1.0 | 53.98805236816406, 34.111454010009766 | curve points under the two right-hand glyphs |

The two endpoint values agree to 3.8e-5 absolute, 3.9e-7 relative, which is float32 round-off in
the experiment and not a discrepancy in the identity; both print as 98.50 and the panel states the
agreement at that precision only. `two_dmu` is defined in `src/experiments/exp06_theory_limits.py`
line 64 as `2 * dmu` with `dmu = (muP - muT).norm()`, so the endpoint is twice the **Euclidean**
distance between the two means. That is the magnitude-aware mean score, not the cosine, and it is
the sentence the caption, the Results and the Methods were all corrected to say on 2026-09-03.

### h. The coverage temperature

Sources `results/exp06_theory_limits/beta_interpolation.csv` and `degenerate_limit_real.csv`,
drawn by `figures/fig1/fig1h.py`. Arm: U.

| Quantity | File value | Drawn |
|---|---:|---|
| four per-state distances | not stored; `STATES` in `fig1h.py` | 0.20, 0.55, 0.80, 1.30 |
| `mean` column | 0.7124999761581421 | low dashed rule, y tick `0.71` |
| `max` column | 1.2999999523162842 | high dashed rule, y tick `1.30` |
| middle frame | selected as the `beta` row furthest from both limits | `beta = 2` |
| `coverage_K1` vs `global_energy`, real file | 0.10994338989257812 in both | the K = 1 identity note |

`STATES` is not read from the file, because the file records only the aggregate. `_states()`
therefore checks it: its mean and max must equal the file's own `mean` and `max` columns, and its
log-sum-exp aggregate must reproduce every measured `D_beta` row. The panel raises rather than
draws if that ever stops holding.

### What left Figure 1 on 2026-09-03, and where it went

| Left | Was | Went to |
|---|---|---|
| panel a's four-candidate library and two ranked stacks | a ranking outcome on a definition panel | Fig. 1d's verdict (where the tie is provable by construction) and Fig. 1e's three candidate cards |
| "cosine" as the name of panel c's mean link | named a score where a representation was drawn | the link reads "means only"; the score names are the three equations below it |
| "Mean retrieval" / "Population retrieval" verdict rows in d | two rows for three scores | "directional mean", "magnitude-aware mean", "population", the names panel a gives the same three rules |
| "Coupled" / "Independent" lane names in e | "independent" reads as "neutral" | "Objective-aligned" / "Less score-aligned", with Fig. 4 cited in the caption |
| "more independent of the retrieval objective" axis label in f | same | "less coupled to the retrieval score", plus the axis-head gloss "less score-aligned != automatically neutral" |

### What changed in Figure 1 on 2026-09-04

One panel, and it is a layout fault rather than a claim: panel d's verdict was set as a name at
the left of the panel and a relation pinned to the panel's right edge, so the three rows carried
1.85, 1.58 and 1.26 in of empty paper between the two halves of each row, with no rule or leader
across it. At 7.2 pt that stops reading as three rows and starts reading as two unrelated lists,
which is the one thing a conclusion block must not do. The relation column is now measured from
the widest route name and set one gutter past it, the way panel a already sets its information
axis, and the largest ink gap in a row is 0.76 in. The verdict itself, its assertions and every
number in the figure are unchanged, and the other seven panels render pixel for pixel as before.

The three route names were also lower-cased, so Figure 1 names the three scoring rules once
rather than three ways ("directional mean" in a, "Directional mean" in d, s_dir in c).

A second pass the same day went panel by panel against four rules that transfer from outside the
deck: label a thing where it is drawn rather than in a key, use one grammar for one concept,
never let hue be the only channel, and let an axis range be set by its data. Three of the four
found nothing. Every panel draws only the colour roles fig1_style declares, with no unroled hex;
the two data panels' axis overhang is holding labels rather than sitting empty; and after d was
fixed no panel splits a row across empty paper. What the first rule found, and what changed:

| Panel | Was | Now |
|---|---|---|
| a | two column headers on one baseline, "Scoring rule" capitalised and "information retained" not | both lower case |
| c | four objects drawn, two named: the mean pair carried mu_Q and mu_d, the population pair carried nothing, and the third equation referred to a P_Q and a P_d that were nowhere on the drawing | the population pair is labelled P_Q and P_d, mirrored, at the same gap from the cells' own measured rim |
| e | "Retriever" and "Evaluator" capitalised beside "fixed ranking", which the code's own comment calls the same kind of label | all three lower case |
| g | the identity check printed "98.50 = 98.50", two identical numbers with no subject | "at lambda = 0, population distance = distance between means = 98.50", both sides named in the words already on the panel |

b, f and h were left alone: nothing in them failed a rule.

One gap was found, measured, and left open. Panel e's external judge is the only stage in the
figure without a name, and it does not fit. A label centred on its card may be 0.670 in wide
before it touches "fixed ranking"; "external evaluator" is 0.830, "external judge" is 0.660 and
leaves under a word space. Two lines are blocked from below, the row clearing the card by 0.144 in
against the 0.215 a second line needs. The naming stays in the caption, and fig1e records why, so
the next attempt starts from the stage pitch rather than from the type size.

### What changed in Figure 2 on 2026-09-04

The same four-rule pass Figure 1 got. Three of the four came back empty: no panel splits a row
across empty paper once the matrix and the value-track columns are excluded, the axis ranges on
every data panel are holding labels rather than sitting empty, and no series anywhere is separated
by hue alone (d's three cell lines share one blue and differ by marker and weight, f's matrix
carries tier in hue and magnitude in shade). What the first rule found:

| Panel | Was | Now |
|---|---|---|
| a | the value column set three decimals and the two step brackets set four, so "0.836" and "0.788" were shown beside "+0.0480"; the manuscript's own macros are three decimals, so one paper carried the same two quantities at two precisions | one VALUE_DP constant feeds both. The panel prints +0.048 and +0.399, which is what \HITSTEPDIST and \HITSTEPMAG print. The step is still computed unrounded |
| d | the composition strip called plot() with mfc set and color unset, so matplotlib handed its ten groups the default tab10 cycle. Nothing rendered wrong, mfc covered every one, but ten undeclared colours sat on visible artists | color=SHARED passed explicitly; the palette audit is clean |
| e | one STEM_TINT, mixed from POP, drew the tether to zero on BOTH rows, so the orange row's tether was blue on a panel whose whole key is orange-versus-blue | one tint per series, each derived from its own row's colour |

b, c and f were left alone. c is the panel the others should be read against: its three-way split
is labelled in ink with the colour carried by a strip under the axis, which is the deck rule
working.

**Open, and deck-wide rather than Figure 2's:** figstyle's presentation layer states that "every
label is INK or META" and that colour reaches the reader through marks, not letters. Four of the
six main figures break it, in 80 text artists: 20 in COMP_SOFT orange, which measures 2.23:1
against white, 24 in FOCAL_SOFT blue at 3.84:1, 3 in PURPLE_SOFT at 3.63:1 and 2 in GREEN_SOFT at
3.52:1, all of them at 6.5 or 7.2 pt and all under the 4.5:1 that small text is normally held to.
Figures 1 and 3 have none. Figure 2b and 2e each document why they chose colour: three markers
0.033 apart cannot bind three labels by proximity, and a two-series key has no other channel. Both
reasons are real, and the swatch that would replace the colour does not fit either place; 2e's
second key line clears the zero rule by 0.076 in and a swatch plus its gap needs about 0.12 in.
This is a policy call across four figures, not a Figure 2 patch, and it is left for a decision.

### What changed in Figure 3, and in the deck, on 2026-09-04

Figure 3's eleven panels through the same four rules. The colour-role rule found one thing and it
turned out not to be Figure 3's:

| Where | Was | Now |
|---|---|---|
| figstyle | ``ax.plot([x], [y], marker="o", mfc=SHARED)`` passes no colour, so matplotlib hands the artist the next tab10 entry. Figure 3 had accumulated sixteen such artists across panels a, b, g, i and j. Not one rendered: every one was covered by an explicit mfc and mec, which is why they survived | ``axes.prop_cycle`` is a single entry, INK. An unset colour is now a colour the deck owns. Proven inert: each figure was rendered twice in one process, once under the new cycle and once under the restored tab10, and all six rasters are identical |
| 3a | the two out-of-view notes at the ends of one row read "4% of this row beyond view, max +2.85" and "1% below, min -2.22". The second did not say below what, and dropped the qualifier the first was carrying on purpose | both read "n% of row above/below view", with the min or max. "this row" became "row" because the two full phrases set 1.55 and 1.59 in against 3.16 in of axes; the pair now sets 2.79 in |
| 3b | "21-27% exact ties" with an ASCII hyphen, where the manuscript sets its numeric ranges with an en dash (120--150, 34--35) | en dash |

The other three rules came back empty for Figure 3. Panel i's pale green is derived from EXT by the
same white blend that makes POP_WASH from POP, and the recipe is asserted against POP_WASH so the
two washes cannot drift; the axis ranges flagged in c, d and e are symmetric-about-zero half-plane
washes or are holding the per-row n labels, not empty; no panel separates a series by hue alone.

**Two things reported and left alone. The first was ACTED ON a day later; see the Figure 3 entry
below.** First, the panel letters run a b c g d e f h i j k: g sits at reading position four. Every
letter matches its caption entry, checked entry by entry, and c and d are vertically adjacent in
the left column so the caption's "c, d" pairing survives; but a reader scanning the figure meets g
fourth. Renaming would fix the order and break the pairing (c and d would become d and e), and
re-laying-out the two rows would change every panel's aspect. On 2026-09-05 the letters were
re-assigned anyway: the pairing cost is real and is paid, because the citation order is a
submission requirement and because the figure was also showing a stratification before the result
it stratifies. Second,
panel h sets "magnitude partialled out" in SUBTLE grey, which fig3_style defines as "units, n,
provenance; never a claim", on a row that carries +0.105 and a confidence interval. fig3h documents
the grey as marking a derived row rather than a method. Both are judgement calls, not defects.

### What changed in Figure 4 on 2026-09-04

Visual layer only; the figure stays frozen as analysis. Two changes, both in schematics, both
about a hue meaning two things at once.

| Panel | Was | Now |
|---|---|---|
| a | the two ranking names were set in POP blue and MEAN orange letters at 6.5 pt. Measured against white that is 3.84:1 and 2.23:1, both under the 4.5:1 small text is held to, and figstyle states that a label is INK or META and that colour reaches the reader through marks. Two rows below, the same panel already did it correctly: "evaluator as a mean" and "as a distribution" are ink inside a coloured box | a swatch in the family colour, the name in ink. The stub and its name are centred as one unit and the panel asserts the unit fits the box, so a rename cannot silently push it out |
| d | the two tissue compartments were drawn in POP blue and MEAN orange, which fig4_style defines as the population-level and mean-signature families. Malignant and myeloid are neither, and the collision was not idle: panel f plots cos(malignant) against cos(myeloid) with every point in POP blue, so the key carried one panel forward reads those points as the malignant compartment | both compartments neutral. Words, side-by-side position, and being the only two boxes holding a cell cloud already separate them three ways. A dead colour argument on the two question boxes, read by nothing, came out with it |

Panel b's nine rotated labels were measured and left: within a group the bar centres are 0.239 in
apart and a horizontal "+0.222" sets 0.298 in at 6.5 pt, so horizontal values would overlap. The
rotation is geometry, not carelessness. Panel e, whose bars are wider, sets its values horizontally
and only its names rotated, which is the pattern b would take if it ever gained width.

c, e, f and g were left alone. c separates its two forms by marker shape rather than hue, and e, f
and g draw only from declared roles.

After this pass the deck carries 47 text artists under 4.5:1, in Figures 2, 5 and 6; Figures 1, 3
and 4 carry none.

### What changed in Figure 5 on 2026-09-04

All thirteen of Figure 5's low-contrast text artists, and the rule they broke is now a helper
rather than a habit. figstyle states that a label is INK or META and that colour reaches the
reader through marks; Figure 5 was setting series names and value labels in COMP_SOFT (2.23:1
against white), FOCAL_SOFT (3.84:1), GREEN_SOFT (3.52:1) and TISSUE purple (3.63:1), all at 6.5 pt
against a 4.5:1 threshold.

The argument that settled it came from inside the figure. Panels g and h sit in one row and do the
same job, an audit of one statistic against another, and h was already labelling its values in ink
beside a coloured marker while g set the identical kind of label in the marker's colour. h loses
nothing. So the rule splits in two, and both halves are now in phase2_style:

  * a label that sits against its own marker inherits the hue from the mark and is set in ink.
    Applied to g's four values and f's two median labels.
  * a label with no marker beside it gets a swatch of its own and is then set in ink. Applied to
    g's two column keys and f's two series names, through the new phase2_style.key_label, which
    measures the name and places swatch and text as one unit so a rename moves them together.

| Panel | Was | Now |
|---|---|---|
| a | "target wanted state" in TISSUE purple beside a box already drawn with a TISSUE edge; the ranking's rank 1 in MEAN orange and rank 3 in POP blue | all ink. Blue was marking the true drug, but bold was marking it too and bold stayed. Orange was marking nothing: the schematic draws ONE scorer and ONE ranking, so there is no mean route for a mean-level hue to belong to, and it was sitting on a filler entry |
| f | two series names and two median values in their series colours | swatch and ink for the names, ink for the values on their own coloured rules |
| g | four values in their markers' colours, two keys in theirs | ink beside the markers, swatch and ink for the keys. g and h now read as the matched pair they are |

b, c, d, e and h were left alone. c already keys its two bars with a swatched legend and labels its
values in ink above them, which is the pattern the rest of the figure has now joined.

Panel a is drawn by phase2_task, which Figure 6 shares, so Figure 6 fell from 27 low-contrast
artists to 24 without being touched. The deck total is 31, all of it now in Figures 2 and 6.

### What changed in Figure 6 on 2026-09-04, and where the deck stands

All twenty-four of Figure 6's low-contrast text artists, under the rule Figure 5 established. Most
of them fell to the first half of it, "a label against its own mark is set in ink", because Figure
6 is a figure of bars and lines and almost every label on it sits on the thing it names.

| Panel | Was | Now |
|---|---|---|
| b | both endpoint values, both loss labels and both route names in their series colours | ink. Every one sits on or beside its own coloured line |
| c | the two half-plane headers in MEAN and POP letters | swatch and ink, through phase2_style.key_label. The data anchors are converted to axes coordinates here, since the helper works in those |
| e | "0, to float precision" on an orange arrow, "observed" on a purple rule | ink; the arrow and the rule were carrying the hue |
| g | ten counts in their bars' colours, two headers in theirs | ink for the counts, which sit at their own bar tips, and swatch plus ink for the headers, which have no mark |
| h | two values inside coloured boxes | ink; the box outline carries the colour |

One colour, not text: the forward-predictor box in the shared task drawing was filled with a typed
"#F4F8FC", a pale blue that is not a blend of POP (solving per channel gives 0.063, 0.057 and
0.048, so it was picked by eye) and would not have followed a recolour of the family. It is now
POP at 0.055 against white, which is #f5f8fc: one level from the old value on one channel, equal
on the other two.

The 26 wide text gaps the split-row check reports on this figure were all read and all rejected:
they are forest and bar rows where a y tick label sits at the left and its value at the marker or
the bar tip, with the bar, the interval or the axis spanning between them. The check was written
for Figure 1d, where two halves of one row were separated by nothing at all.

**Where the deck stands after this pass.** Two whole classes are closed. Default-colour-cycle
artists: 16 at the start, 0 now, prevented at the root by figstyle's single-entry prop_cycle rather
than patched per call site. Text under 4.5:1 against white: 49 at the start, 7 now, and all seven
are in Figure 2, where the swatch that would replace the colour was measured and does not fit;
2e's second key line clears the zero rule by 0.076 in and a swatch plus its gap needs 0.12.
Figures 1, 3, 4, 5 and 6 carry none.

### Text-against-figure audit, 2026-09-04

A cross-check of the prose and the six legends against what the panels actually draw, run
mechanically where it could be: every drawn panel against every legend entry and every body
citation, every legend and body number against the printed numbers of the panel it names, every
\ref against its label, and the SI's notes and tables against what the manuscript asks for.

Three mismatches, all corrected:

| Where | Was | Now |
|---|---|---|
| Fig. 6h | drawn, and described in the legend, but never cited by letter anywhere in the body. Panels a to g were all cited | the sentence it quantifies, "The intervention task therefore states what population information is worth", now points to it |
| Fig. 3 legend preamble | "marker shape distinguishes cell lines", a figure-wide claim that is false for b. Panel b separates A549, K562 and MCF7 by line style, solid against (3.0, 1.5) against (0.8, 1.3), with its own in-panel key; only i uses marker shape | "cell lines are distinguished by line style in b and by marker shape in i" |
| Fig. 4 legend preamble | "Filled marks are scores that compare a response representation; open marks are controls that perform no retrieval", stated figure-wide. Panel e's own entry contradicts it with "Open bars, best unsupervised method; filled bars, supervised probe", and it is wrong for b as well: b's open bar is the response-magnitude scalar, which ranks candidates and only compares no distributions | the figure-wide sentence is gone, because this figure uses fill for two different local distinctions. e already declared its own; b now declares its own |

Verified clean and left alone: 46 of 46 drawn panels are described by their legend and cited by
the body; no legend entry names a panel that is not drawn; no body citation names a panel that is
not drawn; the six figures are first cited in order and each figure block sits after its first
citation; no legend or body number disagrees with the printed value of the panel it names, which
is the check that caught Figure 2a's four-decimal steps earlier in the day; the ten hard-typed
"Fig. N" strings are all inside %% comments and none reaches the page; the SI carries
Supplementary Notes 1 to 4 and Tables 1 to 4, which is exactly what the manuscript asks for, its
seven table environments being four numbered tables plus (b) and (c) continuations; and the
arithmetic ties, 3,110 + 882 = 3,992, 546 + 209 = 755, and 627 + 127 + 11 = 765 with the third
category printed on Fig. 3f.

Two things reported and deliberately not changed. Figure 3's letters still run a b c g d e f h i j
k, with g at reading position four; and Figures 2 and 3 are first met through a subordinate panel,
2f for the cosine equivalence and 3e for the diagnostic failure, where the other four figures are
first met through their a. Both are forward references that read correctly in place.

### Manuscript sentences this figure owns

Four, all corrected in the same pass and all saying the same thing: the abstract's zero-variance
sentence, the Introduction's, the Results paragraph at the head of the first subsection, and the
Methods paragraph "Connection between mean and population retrieval". Before the pass, the
Results paragraph asserted the limit and then opened the next paragraph with "This connection is
exact for the implemented mean-cosine baseline", which attaches the limit to the one mean score
that is **not** its endpoint. That sentence now reads "A second and separate equivalence concerns
the cosine rule itself", which is what the rest of that paragraph actually establishes.

---

## Figure 2. Response magnitude explains most retrievable information beyond directional signatures

Panels a, b and f read `results/exp08_signature_baselines/`, re-run on 2026-09-03 under the U
arm and with `mean_l2` added to `retrieval.rankers.SCORERS`. Panels c and e read
`results/exp12_partial_observed_retrieval/per_query_scores.csv`; panel d reads
`results/exp01_sciplex3_controlled/metrics_summary.csv`. Both were reissued under the U arm in the
same pass; the V-arm originals are in `results/_pre_ustat_backup/`.

### a. Hit@1 ladder, macro-average over 7 task-settings

Source `results/exp08_signature_baselines/summary.csv`, drawn by `figures/fig2/fig2a.py`.
Arm: U for the four population scorers and `pca_dist`; n/a for the four direction-only scorers and
for `mean_l2`, none of which touches an energy distance.

Pre-repair values are the same macro-average recomputed from
`results/_pre_magnitude_control_backup/summary.csv`, which is the V-arm eight-scorer run this
panel drew before 2026-09-03.

| Quantity | Drawn | Tier | Pre-repair (V) |
|---|---:|---|---:|
| `global_energy` | 0.836 | + distribution | 0.837 |
| `mean_l2` | 0.788 | + magnitude | not in the panel |
| `pca_dist` | 0.778 | population | 0.778 |
| `coverage_mean` | 0.749 | population | 0.773 |
| `coverage_worst` | 0.747 | population | 0.589 |
| `pca_mean` | 0.518 | direction | 0.518 |
| `cmap_wtcs` | 0.463 | direction | 0.463 |
| `cmap_cosine` | 0.388 | direction | 0.388 |
| `mean_cosine` | 0.388 | direction | 0.388 |
| magnitude step, `mean_l2` minus `mean_cosine` | **+0.3992** | | not measurable before |
| distribution step, `global_energy` minus `mean_l2` | **+0.0480** | | not measurable before |

### The macros this panel owns, and the prose that ignored them

Nine `\HIT*` macros carry these values in `PopRetrieve_manuscript.tex`. Until 2026-09-04 not one was
referenced in the body: the Results hand-typed every value, so `\HITENERGY` and `\HITENERGYW` kept
their V-arm readings (0.837 and 0.887) through the reissue while the caption said 0.836. Both the
prose and the caption now read the macros.

| Macro | Value | What it is |
|---|---:|---|
| `\HITMEAN` | 0.388 | `mean_cosine` macro-mean Hit@1 |
| `\HITMAG` | 0.788 | `mean_l2`, added 2026-09-04 |
| `\HITENERGY` | **0.836** | `global_energy` (V: 0.837) |
| `\HITSTEPMAG` | **+0.399** | `mean_l2` minus `mean_cosine`, added |
| `\HITSTEPDIST` | **+0.048** | `global_energy` minus `mean_l2`, added |
| `\HITPCADIST` / `\HITPCAMEAN` | 0.778 / 0.518 | PCA space |
| `\HITENERGYW` / `\HITMEANW` | **0.884** / 0.421 | query-weighted (V: 0.887) |
| `\HITWTCS` | 0.4635 | canonical L1000 WTCS |
| `\HITFRANGMEAN` / `\HITFRANGMAG` / `\HITFRANGENERGY` | 0.600 / **0.611** / 0.578 | Frangieh, panel b; the magnitude value added 2026-09-04 |

Magnitude is **89.3%** of the total `global_energy` minus `mean_cosine` gap. The Results prose
reported only the two ends of that gap until 2026-09-04 and so supported the reading this panel was
rebuilt to retire; see `POST_REPAIR_MASTER_RESULTS.md` A5f.

`coverage_worst` is the row the estimator moved, 0.589 to 0.747; `global_energy` and `pca_dist`
barely moved, and the four direction-only scorers cannot move, because none of them computes an
energy distance. That pattern is the structural prediction of
[P1](P1_ESTIMATOR_AUDIT.md) and is measured across the whole suite in [P2](P2_LEGACY_RERUN.md).

The panel's bracket labels print four decimals; the caption rounds to three (+0.399, +0.048).
Both are computed at draw time from the column above, never typed.

### b. The same ladder per task

Source `results/exp08_signature_baselines/summary_by_task.csv`, drawn by `figures/fig2/fig2b.py`.

| Task | n | direction | + magnitude | + distribution | steps |
|---|---:|---:|---:|---:|---|
| controlled mixture | 90 | 0.2889 | 0.8111 | 0.8444 | +0.52, +0.03 |
| cross-line mixture | 1,080 | 0.4176 | 0.8231 | 0.9130 | +0.41, +0.09 |
| Frangieh (natural) | 90 | 0.6000 | 0.6111 | 0.5778 | +0.01, **-0.03** |

The two step values per task are what the panel prints, at two decimals. On Frangieh the best of
all nine scorers is `mean_l2` at 0.6111, which the panel asserts at draw time.

### c. Paired outcome, coverage-worst against mean cosine

Source `results/exp12_partial_observed_retrieval/per_query_scores.csv`, paired on the six-column
query key; drawn by `figures/fig2/fig2c.py`. Arm: U. Pre-repair values are the same computation on
`results/_pre_ustat_backup/exp12_partial_observed_retrieval/per_query_scores.csv`.

| Quantity | Drawn / captioned | Pre-repair (V) |
|---|---:|---:|
| paired queries | 765 | 765 |
| median regret reduction | **+0.031** (exact +0.031056) | **+0.118** (+0.118263) |
| 95% bootstrap CI of that median (4,000 resamples, seed 0) | +0.017 to +0.049 | not reported |
| queries improved | **56%** (430 / 765, 56.21%) | **72%** (72.03%) |
| queries worsened | 36% (275 / 765, 35.95%) | 21% (20.78%) |
| queries tied exactly | 8% (60 / 765, 7.84%) | 7% (7.19%) |
| paired Wilcoxon P | 1.6e-12 | 1.6e-66 |
| mean regret reduction (caption only) | +0.132 | +0.258 (+0.257897) |
| observed range | -2.219 to +2.853 | -1.086 to +2.823 |
| incomplete-library subset: n | 165 | 165 |
| incomplete-library subset: median | +0.035 | +0.087 (+0.087204) |
| incomplete-library subset: improved | 60.0% | 68.5% |
| incomplete-library subset: P | 6.0e-05 | 9.7e-14 |

Manuscript macros: `\REGRETALL` +0.031, `\REGRETALLCI` +0.017 to +0.049, `\REGRETALLMEAN` +0.132,
`\REGRETALLFRAC` 56%, `\REGRETALLP` 1.6e-12. All five were reissued on 2026-09-03; the comment
above them in the preamble records the V values they replaced.

**Resolved 2026-09-03.** That Results sentence now reads its values from the macros above rather
than carrying its own copies, so the prose, the caption and the panel cannot disagree again. Its
claim was not rewritten: only the numbers moved, and the narrative rewrite is still the last step
of the reconstruction.

### d. Advantage against the minority-state fraction

Source `results/exp01_sciplex3_controlled/metrics_summary.csv`, drawn by `figures/fig2/fig2d.py`.
Quantity: `global_energy` Hit@1 minus `mean_cosine` Hit@1, 20 seeds per point, 400 cells per query.
Arm: U.

| alpha | 0.5 | 0.6 | 0.7 | 0.8 | 0.9 |
|---|---:|---:|---:|---:|---:|
| K562 | 1.00 | 0.90 | 0.80 | 0.50 | **0.00** |
| A549 | 0.40 | 0.65 | 0.70 | 0.65 | 0.65 |
| MCF7 | 0.35 | 0.65 | 0.70 | 0.90 | 0.45 |

The caption's "falls monotonically from +1.00 to 0.00 in K562" is the first row. Under the V arm
the K562 endpoint was +0.05; the shape of all three curves is otherwise unchanged.

### e. Median regret reduction against two references

Source `results/exp12_partial_observed_retrieval/per_query_scores.csv`, `DART_recommended` subset,
n = 627; drawn by `figures/fig2/fig2e.py`. Intervals are 95% percentile bootstrap of the median,
4,000 resamples, seed 0. Arm: U.

| Scorer | vs `mean_cosine` (direction only) | vs `mean_l2` (magnitude aware) |
|---|---|---|
| energy | +0.0591 [+0.0450, +0.0853] | **+0.0000 [+0.0000, +0.0000]** |
| MMD | +0.0647 [+0.0483, +0.0877] | **+0.0000 [+0.0000, +0.0000]** |
| sliced-W | +0.0670 [+0.0414, +0.0892] | **+0.0000 [-0.0000, +0.0000]** |
| coverage-mean | +0.0444 [+0.0236, +0.0647] | **-0.0304 [-0.0457, -0.0149]** |
| coverage-worst | +0.0319 [+0.0175, +0.0531] | **-0.0384 [-0.0520, -0.0277]** |

Caption range "+0.032 to +0.067" is the first column's five medians. The second column is the
panel's subject and is the reason panel c's advantage is captioned as modest: against a reference
that keeps response magnitude, three of the five scorers gain exactly nothing and two lose.

### f. Spearman correlation among scoring rules

Source `figures/source_data/ed1_metric_correlation.csv`, regenerated on 2026-09-03 by
`figures/source_data/build_metric_correlation.py` from
`results/exp08_signature_baselines/per_query_scores.csv`; drawn by `figures/fig2/fig2f.py`.
54,180 query-candidate scored pairs from 1,260 queries. Arm: n/a. This is a correlation between
score COLUMNS, and the estimator changes a column monotonically within a query, so the reissue
moves these values only through the score's own definition, not through the ranking.

Seven of the nine scorers in panel a; `pca_dist` and `pca_mean` are absent from the export and the
panel names them as absent on its own bottom line.

| Pair | rho |
|---|---:|
| `mean_cosine` / `cmap_cosine` | **1.000** (ringed; equals a diagonal cell to 1e-10) |
| `mean_cosine` / `cmap_wtcs` | 0.850 |
| `coverage_mean` / `coverage_worst` | **0.982** (ringed) |
| `global_energy` / `coverage_worst` | 0.905 |
| `global_energy` / `coverage_mean` | 0.894 |
| `mean_l2` / `global_energy` | **0.801** |
| `mean_l2` / `coverage_worst` | 0.685 |
| `mean_l2` / `coverage_mean` | 0.682 |
| `mean_l2` / `mean_cosine` | 0.198 |
| `mean_l2` / `cmap_cosine` | 0.198 |
| `mean_l2` / `cmap_wtcs` | 0.170 |
| direction x distribution, all nine pairs | max \|rho\| = **0.060** |

The 0.060 replaces the 0.076 the previous caption quoted. That value is the same nine-pair maximum
over the previous six-scorer export, recovered from `git show HEAD:figures/source_data/`; the two
are directly comparable because both cover the same nine direction-by-distribution pairs.

### What is NOT on Figure 2 any more, and where it went

| Retired | Reason | Where the evidence now lives |
|---|---|---|
| The family assertion in `fig2a` (every population scorer above every mean scorer) | False once a magnitude-aware mean scorer is in the panel: `mean_l2` at 0.788 beats three of the four population scorers | `docs/phase2/FIG2_MAGNITUDE_CONTROL_VERDICT.md` |
| The two family washes and family grouping in `fig2a` | Same finding: the axis the scorers separate on is what they KEEP | panel a's three tiers, panel f's tier ordering |
| The median RULE in `fig2c` | The U-arm median prints 0.86 pt from the zero rule against a 2.5 pt legibility floor | the paired-outcome composition, `docs/phase2/POST_REPAIR_MASTER_RESULTS.md` section A5 |
| The gate-diagnostic panel (old `d`) | Moved to Figure 3, where the diagnostic's failure is argued | Fig. 3d-f |


---

## Figure 3. The population advantage weakens, and can change direction, once the judge stops sharing the retrieval objective

Eleven panels in five rows, 6.90 x 7.89 in. **The panel letters were re-assigned on 2026-09-05**
so the panels are cited in order, which Nature asks for and which Figure 4 was re-cut for a day
earlier. The text runs a and b, then the 239-task minority-coverage result, then that result
STRATIFIED by divergence, then the two diagnostic panels; the figure ran the stratification first
and the result it stratifies fifth, so the reader met Fig. 3g third and the base number after its
own quartiles. The page now runs a b | c d | e f g | h i | j k, with the 239-task panel as c at
the 4.15 in box it was measured for and the four panels behind it each one letter later. Every
panel is drawn by its own unchanged draw function; only the letter-to-content assignment changed,
and figures/fig3/fig3_assemble.py's DRAW dict is the one place it is written down. The module
names were NOT renamed with the letters, following fig4_assemble: fig3g.py draws panel c.
**The rows were re-cut on 2026-09-04** so the page read in its own order: it used to run
a b | c g | d e f | h i | j k. **Row 3 was rebuilt on
2026-09-03** and three letters
changed meaning: the old d (gate enrichment) is now e, the old e and f are merged into one panel f,
and d is a new panel carrying the mechanism-recovery quartiles that were Figure 5 panel g. Panels
a, b, c and g to k keep their letters.

Sources, all under the U arm: a, b, f read
`results/exp12_partial_observed_retrieval/per_query_scores.csv`; d, e, g read
`results/exp16_gate_diagnosis/_merged_query_divergence.csv` (rebuilt 2026-09-03, see A5c);
c reads `results/exp13_real_data_projection/projection.csv`; h, i, j, k read the two Class-C views
under `figures/source_data/`, which are now MIRRORS of `results/upgrade/` and were resynced on
2026-09-03 after being stale since the U-arm install.

### a. The same advantage, judged twice (n = 600 leave-drug-out queries)

| Quantity | Response matching | Mechanism recovery | Pre-repair (V), response matching |
|---|---:|---:|---:|
| median | **+0.028** | **0.000** | +0.1288 |
| mean | +0.135 | -0.024 | +0.2752 |
| favour population | **55%** (55.2%) | **36%** (35.7%) | 73.0% |
| exact ties | 8% (7.5%) | 24% (23.5%) | 7.3% |
| paired Wilcoxon P | 2.7e-09 | 7.7e-03 (`\CLASSBP`) | 2.4e-54 |
| range | -2.219 to +2.853 | -0.681 to +0.631 | -1.086 to +2.823 |
| beyond the view | 4% right, 1% left | none | 4% right only |

The mechanism-recovery row barely moved: median still exactly 0.000, 34.2% to 35.7% favouring
population, its own Wilcoxon P from 2.5e-04 to 7.7e-03. `moa_ndcg` never passes through an energy
distance, so what moved is the retrieval, not the judging.

### b. The same comparison per cell line

A549, K562 and MCF7, n = 200 each, medians exactly 0.000 in all three; exact-tie fractions 22.5%,
26.5% and 21.5%, which the panel prints as the range 21 to 27 per cent. Drawn view +/- 0.701, from
1.03 times the largest absolute gain.

### c. Minority-state coverage gain across 239 real-data tasks

| dataset | n | mean | fraction positive | fraction tied |
|---|---:|---:|---:|---:|
| SciPlex3 cross-line (constructed) | 90 | +0.00368 | 0.167 | 0.800 |
| SciPlex3 predicted (constructed) | 24 | +0.00005 | 0.417 | 0.167 |
| SciPlex3 within-line | 90 | -0.00047 | 0.511 | 0.244 |
| Frangieh | 23 | -0.00076 | 0.304 | 0.087 |
| CD34+ | 12 | -0.00082 | 0.417 | 0.167 |
| all | 239 | **+0.00110** | | 102 tasks pick the same candidate |

Macro `\PROJMEAN` +0.0011, reissued from +0.0018.

### d, e. One divergence axis, two judges

Both cut quartiles on `true_divergence` over all 765 queries, so a row means the same stratum in
both panels. Means with 4,000-resample seeded bootstrap intervals.

| | c: minority-state coverage (n = 765) | d: MoA-nDCG (n = 600) |
|---|---|---|
| Q1 | **-0.0035** [-0.0076, +0.0001], n = 192 | **-0.0497** [-0.0755, -0.0227], n = 166, q = 0.002 |
| Q2 | +0.0038 [+0.0022, +0.0056], n = 191 | **-0.0391** [-0.0693, -0.0100], n = 150, q = 0.025 |
| Q3 | +0.0054 [+0.0037, +0.0073], n = 191 | -0.0158 [-0.0451, +0.0131], n = 141, q = 0.643 |
| Q4 | +0.0051 [+0.0033, +0.0072], n = 191 | +0.0142 [-0.0124, +0.0414], n = 143, q = 0.126 |
| Spearman rho | **+0.141**, p = 9.6e-05 | **+0.155**, p = 1.4e-04 |
| medians | 0.0000 / +0.0004 / +0.0012 / +0.0020 | -0.0062 / 0.0000 / 0.0000 / 0.0000 |

d's strata are uneven because mechanism recovery is only defined on the fully observed split; the
panel prints the four n. Its q values are Benjamini-Hochberg over the eight strata of
`results/exp17_true_divergence_subset/divergence_stratified.csv` and are quoted in the caption, not
drawn. Pre-repair, c read rho = +0.050 (p = 0.165) with all four quartiles positive, and d's Q4
read +0.003 at q = 0.57; see [POST_REPAIR_MASTER_RESULTS.md](POST_REPAIR_MASTER_RESULTS.md) A5c.

### f. Gate enrichment

| Group | n | median regret reduction | 95% bootstrap CI |
|---|---:|---:|---|
| recommended | 627 | +0.0319 | [+0.0175, +0.0531] |
| not recommended | 127 | +0.0402 | [-0.0188, +0.0582] |
| difference | | **-0.0083** | [-0.0322, +0.0555], Mann-Whitney p = 0.64 |
| pooled decline (138) | 138 | +0.0216 | [-0.0297, +0.0515], p = 0.53 |

The declined queries gain slightly MORE than the recommended ones. The difference interval is
wider than either median, so the panel measures a failure to detect enrichment, not a bounded
absence of it; the assertion that used to enforce the bound is kept and inverted. Macros
`\GATEDIFF` -0.008, `\GATEDIFFCI` -0.032 to +0.056, `\GATEDIFFP` 0.64.

### g. The diagnostic's own axis, continuous and thresholded

| Quantity | Value | Pre-repair (V) |
|---|---:|---:|
| Spearman rho, reliability vs true divergence (n = 765) | **-0.1885**, P = 1.5e-07 | -0.21, P = 3.8e-09 |
| binned conditional median, lowest to highest bin | 0.569 to 0.465 | 0.57 to 0.46 |
| recommended median divergence (n = 627) | 1.661 | 1.660 (n = 621) |
| declined median divergence (n = 127) | **1.683** | 1.689 (n = 133) |
| CLES, recommended vs declined | **0.427** [0.380, 0.475] | 0.41 |
| Mann-Whitney P | **0.0094** | 0.0011 |
| mean-sufficient (n = 11) median | 0.509 | 0.509 |
| pooled 138-query reading | CLES 0.472, P = 0.31 | P = 0.09 |

The P < 0.01 gate the panel asserts now clears by about a factor of two rather than ten.

### h, i, j, k. The external GDSC2 evaluation

Class C. `figures/source_data/fig3hi_class_c_functional.csv` mirrors
`results/upgrade/class_c_functional_oracle.csv` (U arm, installed 2026-09-03).
`figures/source_data/fig3hi_class_c_potency.csv` mirrors
`results/upgrade/class_c_magnitude_control_v2.csv`, **recovered** from the estimator audit rather
than re-run: see the note below. n = 103 queries throughout.

| Ranking | h: functional oracle, median rho | j: absolute potency, median rho |
|---|---:|---:|
| energy | **+0.2650** [+0.1930, +0.3659] | **-0.5059** |
| energy, magnitude partialled out | **+0.1053** [+0.0478, +0.1557] | not computed |
| mean cosine (control-subtracted) | +0.0826 [+0.0273, +0.1320] | +0.1049 |
| mean cosine, raw | +0.2413 [+0.1681, +0.3389] | -0.5334 |
| magnitude match (a scalar) | +0.2318 [+0.1065, +0.3573] | not computed |
| magnitude only, no retrieval | not drawn in h | +0.6918 |
| potency match (diagnostic only) | +0.3987 [+0.2316, +0.4572] | not computed |

Median per-query drop from partialling, +0.0416 [+0.0070, +0.1307].

**i**: energy beats the scalar on **62** of 103 queries, the scalar on **40**, with **1 exact tie**
(A549 / Fulvestrant, both 0.663436); paired Wilcoxon p = **0.054** (`\ENERGYWINSP`). Per cell line
18/34, 18/34, 26/35. The tie is new under the U arm and the panel used to REFUSE to draw when the
two half-planes did not partition the queries; it now names the tie.

**k**: per-query Spearman between the energy distance and the candidate's own response magnitude,
median **+0.780**, quartiles +0.493 and +0.958, 95 of 103 positive, **76** above +0.5, 8 at or
below zero, range -0.278 to +0.994.

### The one thing on Figure 3 that could NOT be re-run

`analysis/class_c/class_c_magnitude_control_v2.py` needs `data/processed/sciplex3_all.pt`, which
DATA.md documents as large and untracked and which is absent from this machine; no checkout of
this repository was reachable on the remote host either. Its U-arm output was therefore RECOVERED
from `results/estimator_audit/arm_comparison_full.csv`, which records every numeric cell of that
file under both arms, by `analysis/estimator_audit/recover_u_arm_output.py`.

That script does not write until it has rebuilt the OTHER arm from the same table and checked it
against the installed V-arm file: the round trip reproduced all 103 rows and all 8 numeric columns
to 4.4e-16, which is CSV printing precision. Only `energy_rho` (up to 0.138) and
`energydist_vs_candmag_rho` (up to 0.096) moved between arms; the five estimator-free columns are
identical to the last bit, which is the internal check that the pipeline changed nothing it should
not have. A reader who wants the file regenerated rather than recovered needs the SciPlex3 tensor.

### Eight macros this figure owns that the U-arm pass had missed

Found on 2026-09-03 while sweeping Figure 1's terminology through the Results, because the prose
printed a Class-A median of +0.129 where panel a draws +0.028. The `\REGRETALL` group of macros
was reissued under the U arm; the `\CLASS*` group directly beneath it, sharing the same source
file and the same 600 queries, was not, and the comment announcing the reissue sat above only the
first group. The Results paragraph carried hand-typed copies of the stale values rather than the
macros, so nothing compared the two.

All eight recomputed from `results/exp12_partial_observed_retrieval/per_query_scores.csv`,
`split_type == leave_drug_out`, `mean_cosine` against each population variant, n = 600 paired.

| Macro | V (in print until 2026-09-03) | U (now) |
|---|---:|---:|
| `\CLASSAMED` | +0.129 | **+0.028** |
| `\CLASSAMEAN` | +0.275 | **+0.135** |
| `\CLASSBMED` | 0.000 | 0.000 |
| `\CLASSBMEAN` | -0.037 | **-0.024** |
| `\CLASSBWORSE` | 41.3% | **40.8%** |
| `\CLASSBBETTER` | 34.2% | **35.7%** |
| `\CLASSBTIED` | 24.5% | **23.5%** |
| `\CLASSARANGE`, five-variant Class-A medians | +0.053 to +0.129 | **+0.028 to +0.067** |
| `\CLASSBRANGE`, five-variant Class-B means | -0.011 to -0.037 | **-0.011 to -0.033** |
| `\VARIANTCOUPLING`, Spearman over the five variants | -0.90 | **+0.60** |

Per variant, Class-A median then Class-B mean: energy +0.0594 / -0.0130, MMD +0.0653 / -0.0111,
sliced Wasserstein +0.0668 / -0.0160, coverage-mean +0.0413 / -0.0334, coverage-worst
+0.0278 / -0.0239. All five Class-B medians are exactly 0.000, which is why the B range is
summarised by means; the two statistics are labelled in the macro comments.

The direction of the claim does not change: response matching stays positive, mechanism recovery
stays at a median of exactly zero with a negative mean, and the paragraph's conclusion is
unaltered. The magnitude of the response-matching gain was overstated 4.6-fold. `\VARIANTCOUPLING`
does flip sign, which is why it is worth saying plainly that no sentence in the paper uses it:
at n = 5 it was never stable enough to argue from, and the macro is defined and unreferenced.
The Results paragraph now reads every one of these through its macro.


---

## Figure 4. External evaluation is not automatically neutral, and natural heterogeneity does not automatically imply decision reordering

**Six panels since 2026-09-05, down from seven, in rows of 2, 2 and 2, on a 6.90 x 5.48 in
canvas.** Three changes, made together.

The tumour-cohort schematic (old d) left: it drew no data, and the Results sentence citing it
already stated its whole content.

The analytic boundary moved from last to fourth, because that is the order the Results cite it in:
design, reversal, magnitude control, then the boundary as the bridge into the tumour section, then
the two tumour panels. With it drawn last a reader was sent from c to g and back to d. Only one
letter changes in the manuscript, g to d; the two tumour panels keep e and f.

The height came out. Measured on the 2026-09-04 render, the two lower rows carried 0.82 and 0.87 in
of dead gutter while every row sat at its authored height. Two panels per row cannot fill 6.90 in
here, because two of the six are aspect-locked squares and a square of side h contributes h of
width, so the panel beside it would have to run to about 5.5 - h inches to reach the page edge.
The gutter is structural, so the height came out instead of the panels being stretched: rows of
1.66, 1.05 and 1.25 in of axes, each bisected down until that row's tightest panel tripped its own
assertions or `check_overlaps.py`. One panel was changed to make that possible, and it is recorded
below. The figure prints at 176 x 140 mm against 176 x 162 mm.

**Seven panels since 2026-09-03, down from nine, in rows of 2, 3 and 2.** The horizontal split is
that revision's and is unchanged, so no surviving panel was re-tuned then. The vertical ledger was
re-cut on 2026-09-04: three rows of 1.68, 1.65 and 1.50 in of axes on a 6.90 x 6.38 in canvas,
down from a uniform 1.75 in on a 7.09 in canvas that this figure had inherited from the
thirteen-panel version. Each row now stands at what its own tightest panel was measured to need. Three panels are new (a, c, d), four moved letter
(b was c, e was d, f kept f, g was a), and five left the figure entirely.

### The one panel change the 2026-09-05 height cut required

The recoverability panel (e, the old f) set "best unsupervised" and "supervised ceiling" rotated
inside its two constructed bars. A label rotated into a bar runs ALONG the bar, so its printed
length is what has to fit between the chance rule and the bar top, and that length does not shrink
when the panel does. On one line "best unsupervised" measures 0.68 in, which put the panel's height
floor at 1.59 in and made it the tallest thing in the figure's lower half. Set on two lines the run
is 0.48 in and the floor is 1.20 in, measured by bisection.

No word was dropped. "best" and "ceiling" are the two words that stop the pair reading as two
competing methods, which is the misreading this panel and the deck's green EXT role both exist to
prevent, so shortening the labels was not available.

### What left, and where it went

| Was | What it drew | Now |
|---|---|---|
| b | honest-versus-leaky classifier AUC, 2x2 | Supplementary Note 1, prose |
| e | induced response cosine, 17 patient-drug pairs | Supplementary Note 4, prose, explicitly descriptive |
| g | empirical energy-minus-mean phase grid, 36 cells | Supplementary Note 1, prose |
| h | decision regret by information condition | Supplementary Note 1, prose |
| i | three HIR-Bench sanity checks | Supplementary Note 1, prose |

Four of the five were HIR-Bench, which had five synthetic panels against four real ones in a figure
about external evaluation. **No supplementary FIGURE was created.** The SI has never carried a
float, no script can build one, `\figurename` there is bound to "Extended Data Fig.", and two
sentences in the two documents assert that there are no Extended Data figures. Every demotion is a
move of content into an existing Supplementary Note, so those two sentences stay true; their panel
accounting was updated (nine of the former 21 ED panels in the main figures, twelve carried in
prose).

### a. The evaluator design (schematic, no result drawn)

Reads `results/upgrade/oracle_shape_join_provenance.json`. Named on the panel: 20 surface proteins,
218,331 cells, 659 query-candidate pairs. The panel asserts that the RNA file, the protein file and
their barcode join all hold the same 218,331 cells, which is what "in the same cells" rests on, and
refuses to draw any other digit.

### b. The winner reversal

Source `results/upgrade/oracle_shape_test.json`, drawn by `figures/fig4/fig4_shape.py`. Six bars,
Spearman rho against the protein evaluator, n = 659 query-candidate pairs. Arm: U.

| Ranking | evaluator as a mean | evaluator as a distribution | Pre-repair (V), mean form | Pre-repair (V), distribution form |
|---|---:|---:|---:|---:|
| energy distance | +0.222 | **+0.393** | +0.146 | +0.529 |
| mean cosine | **+0.242** | +0.230 | +0.242 | +0.334 |
| magnitude scalar (control, no retrieval) | +0.125 | +0.276 | +0.125 | +0.352 |
| winner | mean | energy | mean | energy |

**The reversal survives the estimator repair; the two mean-cosine and magnitude-scalar columns
under the mean-form evaluator are identical across arms by construction, because neither passes
through an energy distance.** What moved is every column that does.

Per condition, under the distribution-form evaluator energy leads in all three (Co-culture
+0.441 against +0.276, Control +0.332 against +0.120, IFNgamma +0.393 against +0.268). Under the
mean-form evaluator the mean leads in two of the three; in Control energy leads by +0.005, so the
WINNER SWAP itself occurs in two of three conditions, not three. The panel asserts that the stated
winner is the argmax of its own column.

### c. The magnitude residual under both evaluator forms

Same source, drawn by `figures/fig4/fig4_residual.py`. Energy minus the magnitude scalar, computed
from the two drawn correlations and cross-checked against the source file's own record of it.

| Row | n | mean form | distribution form | ratio | difference |
|---|---:|---:|---:|---:|---:|
| all conditions | 659 | +0.0976 | +0.1166 | **1.20** | 0.0191 |
| Co-culture | 219 | +0.1443 | +0.1547 | 1.07 | 0.0104 |
| Control | 213 | +0.1082 | +0.1142 | 1.06 | 0.0061 |
| IFNgamma | 227 | +0.0447 | +0.0821 | 1.84 | 0.0375 |

**Pre-repair the pooled pair was +0.0215 and +0.1768, a ratio of 8.2.** That eightfold gap is what
licensed the retired sentence, "population evaluators reward population scorers". At 1.20 it does
not, and the panel asserts a ceiling of 2.0 on every row so the old reading cannot return without
a build failure. See [POST_REPAIR_MASTER_RESULTS.md](POST_REPAIR_MASTER_RESULTS.md) C1.

### d. The analytic existence proof

`results/exp11_hir_benchmark/theoretical_boundary.csv` is read as a provenance check only; the
drawn curve is the identity line, because in (welfare ratio, minority fraction) coordinates
alpha* = B/(A+B) IS the identity. No value from the file reaches the page, and the equation is set
independently in Methods and in the HIR-Bench Supplementary Note.

### e. Recoverability

Source `results/zhao_gbm/gate2_drug_response.json`, intervals from `gate2_uncertainty.json`
(5,000 patient-level cluster-bootstrap resamples). Arm: n/a, no energy kernel is called.

| Arm | best unsupervised | supervised ceiling | gap | 95% CI | n splits |
|---|---:|---:|---:|---|---:|
| constructed, drug vs drug | 0.837 | 0.879 | +0.007 | -0.008 to +0.065 | 24 |
| natural tumour, drug vs drug | **0.777** | **0.923** | **+0.117** | +0.115 to +0.135 | 36 |

A third arm in the file, constructed class-vs-class, is not drawn: it has one split and a NaN
interval.

### f. Ordering conserved across disjoint compartments

Source `results/zhao_gbm/premise_mean_vs_compartment.csv`, 18 within-patient drug pairs from the
same 4 patients. Spearman rho between myeloid-response similarity and malignant-response
similarity = **+0.835** (`\PREMISEDISJOINT`, verified +0.8349). The overlapping mean-signature form,
`\PREMISEOVERLAP` +0.878 (verified +0.8782), moved from the Results into the Methods on 2026-09-06
and deliberately not drawn: the mean signature is the equal-weight average of the malignant and
myeloid compartment deltas (`zhao_two_gates.py:127-128`), so the malignant compartment it ranks is
half of it and part of that correlation is arithmetic. The earlier reason given here, "contains 43%
of the malignant cells it ranks", was wrong on both counts and is retracted in CORRECTIONS.md R75.
**No retrieval was performed on this cohort.**

### The tumour cohort schematic, panel d until 2026-09-05

Deleted with the panel. It drew no data: it restated in a flowchart the design that the
Results sentence citing it already states in full, and the caption states again. Its two
counts, 4 patients and 36 drug pairs for the recoverability panel against 18 for the
ordering panel, are asserted by those two panels' own draw functions and are quoted in
their caption entries. `figures/fig4/fig4_tissue.py` is kept on disk and imported by
nothing.

### Manuscript numbers this figure owns

`\PREMISEOVERLAP` +0.878 (now expanded in the Methods, not the Results) and `\PREMISEDISJOINT`
+0.835, both verified against the source. `\PREMISESHARE` was retired on 2026-09-06: see
CORRECTIONS.md R75. The six evaluator correlations and the two residuals are written into the Results prose
rather than into macros; they are listed above and nowhere else.


---

## Figures 5 and 6. The Phase-II intervention task, split on 2026-09-03

One experiment, two pages. Figure 5 runs it with candidate responses OBSERVED; Figure 6 replaces
that one station with a forward predictor and changes nothing else. **No experiment was re-run for
the split**: every panel on both pages reads `results/phase2_transition/` through
`figures/phase2_data.py`, and the two task schematics are one function with one switch
(`figures/phase2_task.py`).

Arm: U throughout. `phase_a/summary.csv` carries `energy` and `energy_v_statistic` as separate
rows, and every panel reads `energy`; the V row is 0.9659 against the U row's 0.9755, which is the
whole of the Phase-II estimator finding restated at the oracle.

The task: 3,992 queries, 44 held-out cell lines, a fixed 92-compound library, leave-one-cell-line-out,
5 seeds (19,960 query-seed pairs).

### Figure 5a and 6a. The task (schematic, no result drawn)

`figures/phase2_task.py`. The only digits either mode may print are the 92 compounds and the 43
fitted lines, and `draw_task` raises on any other digit in any text it drew.

### Figure 5b. The oracle ladder

Source `phase_a/summary.csv`. 95% bootstrap intervals over cell-line clusters.

| Scorer | Drawn MRR | 95% CI |
|---|---:|---|
| `mean_cosine`, direction only | **0.945** (0.945168) | 0.9267 to 0.9611 |
| `mean_l2`, + magnitude | **0.965** (0.965285) | 0.9517 to 0.9770 |
| `energy`, + distribution | **0.976** (0.975515) | 0.9659 to 0.9839 |
| magnitude step | **+0.0201** | |
| distribution step | **+0.0102** | |

The same three-rung ladder as Fig. 2a and drawn in the same three colours (orange, slate, blue),
which is why Fig. 1a's segments were changed to match on the same day.

### Figure 5c. Decision correction at the oracle

Source `synthesis/gate3_decision_relevance.csv`, rows `phase=oracle, predictor=oracle`.

| Reference | Corrected @1 | Broken @1 | Ratio |
|---|---:|---:|---:|
| `mean_cosine` (direction only) | **5.6%** (0.055561) [4.37, 6.91] | **1.1%** (0.010772) [0.81, 1.37] | **5.2 : 1** |
| `mean_l2` (magnitude aware) | **2.0%** (0.019840) [1.37, 2.68] | **0.5%** (0.004910) [0.34, 0.66] | **4.0 : 1** |

### Figure 5d. The ceiling

Source `bottleneck/bottleneck_per_query.csv`, columns `RR_ref_oracle_vs_cos` and
`G_oracle_vs_cos`; the pooled value is read from `phase_a/delta_vs_reference.csv` and asserted
equal to the mean of the drawn per-query gains.

| Group | n | Mean ΔMRR |
|---|---:|---:|
| mean route already perfect (`RR_ref` = 1 at every seed) | **3,110** | **−0.0036** |
| room to improve | **882** | **+0.1501** |
| all | **3,992** | **+0.0303** (0.030347) |

97.1% of the zero-headroom group has a gain of exactly 0.000; the other 2.9% is negative, because
a route that cannot beat a perfect reference can only lose to it. No interval is drawn: the split
is defined by the reference's own performance, so it is an identity and not a comparison.

### Figure 5e. The headroom correlation is inside its own null

Source `bottleneck/summary.json`, key `headroom_correlation_is_mechanical`.

| Quantity | Value |
|---|---:|
| observed Spearman, headroom vs gain | **+0.790** (0.789865) |
| null mean, 200 shuffles | **+0.786** (0.786022) |
| null 95% interval | **+0.767 to +0.805** |
| observed inside null | **true** (asserted by the panel) |

The null reshuffles the population route's reciprocal ranks within each context, keeping both
marginals, the RR <= 1 ceiling and the clustering. This retracts a relationship an earlier draft
reported as the strongest explanation of where population scoring pays.

### Figure 5f. Recoverability

Source `phase_c/gate2_observed.csv`, 3,992 rows over 44 cell lines and 92 drugs.

| Quantity | Median | Note |
|---|---:|---|
| `A_sup`, state labels given | **0.800** | a ceiling, drawn in EXT green; not a method |
| `A_unsup`, without labels | **0.555** | 29.6% of queries clear 0.6 |
| chance | 0.500 | balanced two-class problem |

### Figure 5g. The interaction statistic, retired and repaired

Source `gate1_interaction/checks.json`, `check5_effect_size_audit` and `check3_positive_control`.
n scored = 3,620 of 3,992.

| Spearman ρ with | `D_old` = 1 − cos (retired) | `S_int` cross-fitted (used) |
|---|---:|---:|
| response magnitude | **−0.694** | **+0.663** |
| cells per arm | **−0.425** | **+0.100** |

Positive control built from the plate's own cells: `S_int` median **7.22x** the endogenous median,
n = 176. 94.6% of endogenous `S_int` values are positive.

The two rows are not read the same way, and the caption says so: on response magnitude a NEGATIVE
correlation is disqualifying, because it inverts the quantity; on cells per arm the target is zero.

### Figure 5h. Does anything locate the gain

Source `bottleneck/regression.csv`, outcome `RR_pop_oracle_vs_cos`, with the mean route's own
reciprocal rank as a covariate. n = 3,618 queries in 44 cell-line clusters (3,620 for `D_old`).

| Term | β | 95% CI | p |
|---|---:|---|---:|
| interaction share | +0.0015 | −0.0009 to +0.0039 | 0.21 |
| recoverability (`A_sup`) | **+0.0091** | +0.0060 to +0.0121 | 3.8e-09 |
| reproducibility (`R_int`) | −0.0011 | −0.0029 to +0.0006 | 0.21 |
| 1 − cos (retired) | **−0.0096** | −0.0167 to −0.0024 | 0.0087 |

These are the `conditional: plus interaction reproducibility` and `conditional: the old statistic`
model rows. `docs/phase2/POP_RETRIEVE_POST_PHASEII_VERDICT.md` quotes a different specification
(+0.0011 and +0.0084, magnitude-controlled); the panel and this table are the conditional model,
and the two must not be quoted interchangeably.

### Figure 6b. Where the loss falls

Sources `phase_a/summary.csv` and `phase_b/summary.csv`, predictor `average_effect`. The loss is
computed in `phase2_data.route_loss`, not read: no result file records it, and subtracting two
summary files inside a panel is how a number gets typed by hand.

| Route | Oracle | Predicted | Loss |
|---|---:|---:|---:|
| mean (`mean_cosine`) | 0.9452 | **0.8876** [0.8645, 0.9108] | **0.058** |
| population (`energy`) | 0.9755 | **0.8520** [0.8092, 0.8903] | **0.124** |

### Figure 6c. The gain ladder

Sources `phase_a`, `phase_b` and `phase_b_p5` `delta_vs_reference.csv`, `energy` against
`mean_cosine`.

| Row | ΔMRR | 95% CI |
|---|---:|---|
| oracle (observed) | **+0.0303** | +0.0225 to +0.0398 |
| average effect | **−0.0356** | −0.0620 to −0.0115 |
| state-cond. average effect | −0.0314 | −0.0584 to −0.0076 |
| linear latent | −0.0341 | −0.0601 to −0.0100 |
| OT map | +0.0027 | −0.0215 to +0.0243 |
| nearest context | −0.3159 | −0.3544 to −0.2754 |
| nearest context, cells | −0.3399 | −0.3737 to −0.3027 |

Retained fraction of the oracle gain (`synthesis/oracle_to_prediction.csv`): **−1.17** for
`average_effect`, −1.13 linear latent, +0.09 OT map, −10.41 and −11.20 for the two nearest-context
predictors. Negative means the gain inverts rather than attenuates.

### Figure 6d. The deficit is a magnitude error

Source `phase_b/delta_vs_reference.csv`, predictor `average_effect`, n = 19,960 query-seed pairs.

| Comparison | ΔMRR | 95% CI |
|---|---:|---|
| population vs direction-only | **−0.0356** | −0.0620 to −0.0115 |
| magnitude-aware vs direction-only | **−0.0335** | −0.0588 to −0.0105 |
| population vs magnitude-aware | **−0.0020** | −0.0036 to −0.0005 |

`draw_6d` asserts both halves of the reading: the first two within a factor of two of each other,
the third at least five times smaller than the first.

### Figure 6e. The interaction each predictor generates

Source `phase_b_p5/gate1_predicted.csv.gz` (19,044 rows per predictor) and
`gate1_interaction/interaction_per_query.csv` for the observed value. Drawn in units of 1e-4.

| Predictor | Median predicted `S_int` | Drawn |
|---|---:|---|
| average effect | 3.4e-15 (max 1.8e-14) | an arrow off the axis, "0, to float precision" |
| OT map | 9.24e-06 | 0.092 |
| state-cond. average effect | 3.90e-05 | 0.39 |
| observed, cross-fitted | 1.375e-04 | the dashed rule |

### Figure 6f. The constructive test

Source `phase_b_p5/summary.csv`.

| Predictor | Mean route | Population route |
|---|---:|---:|
| average effect | 0.8876 [0.8645, 0.9108] | 0.8520 [0.8092, 0.8903] |
| state-cond. average effect | **0.8883** [0.8667, 0.9106] | **0.8569** [0.8152, 0.8933] |

Mean accuracy preserved, interaction fidelity real for the first time (panel e), gap not closed.

### Figure 6g. The attrition, counted

Source `synthesis/oracle_to_prediction.csv`. The denominator is the **755** queries on which the
oracle population route had any gain; it is a property of the oracle, is identical down all five
rows, and `draw_6g` asserts that rather than assuming it.

| Predictor | oracle gain lost (case II) | kept (case III) | appeared (case IV) |
|---|---:|---:|---:|
| average effect | **546** | **209** | 343 |
| linear latent | 527 | 228 | 388 |
| OT map | 305 | **450** | **1,165** |
| nearest context | 523 | 232 | 320 |
| nearest context, cells | 576 | 179 | 258 |

Case IV is in the caption and not on the panel: different denominator, and the OT map's 1,165 is a
symptom of a mean route that reaches only 0.665, which Figure 5e rules out as evidence.

### Figure 6h. The budget

Reads the same accessors as 5b, 5c and 6c, so the ledger cannot disagree with the panels it
summarises. Rows one and two are MRR at the oracle and are drawn to scale; rows three and four are
a rate and a signed gain and are drawn as gates with no width.

### What left these two pages on 2026-09-03, and where it went

| Left | Was | Went to |
|---|---|---|
| the eleven-panel Figure 5 caption in the manuscript | describing panels a to k while the built figure had eight | replaced; it had been stale since the Phase-II rebuild and is recorded in `POST_REPAIR_MASTER_RESULTS.md` A5e |
| the Results subsection "When can population-level information improve drug retrieval?" | cited Fig. 5b, c, d, e, f and h to k, none of which existed | rewritten around the two new figures; the constructed-mixture and Tahoe measurements it carried are kept as prose with Supplementary Note pointers |
| `fig5b_predictor_gaps.csv`, `fig5cd_structure_diagnostics.csv` | source-data views of panels the Phase-II rebuild removed | `figures/source_data/_stale/` |
| `figures/fig5/fig5_style.py`, `figures/fig5/fig5_data.py` | one figure's private modules, now read by two | `figures/phase2_style.py`, `figures/phase2_data.py` |

## Main-SI synchronization and claim freeze, 2026-09-04

Two review passes, applied together. Nothing was committed.

### Missed U-statistic reissues, now closed

The 2026-09-03 repair reissued every value that passes through an energy kernel, but the sweep
was driven by "which scripts call the kernel" rather than "which numbers move". Three consumers
were downstream of a kernel without calling one, and all three kept V-arm values:

| Value | V (in print) | U (source) | Where it was printed |
|---|---:|---:|---|
| `\ENERGYFUNC` | +0.276 | **+0.265** | Results R5, Supplementary Table 4 |
| `\ENERGYPARTIAL` | +0.097 | **+0.105** | Results R5, Supplementary Table 4 |
| `\ENERGYUNCEN` | +0.0967 | **+0.0902** | Supplementary Table 4 |
| `\ENERGYCANDMAG` | +0.791 | **+0.780** | Results R5 (Fig. 3k already drew +0.780) |
| SI decline counts | 133 / 11 | **127 / 11** | Supplementary Note 2 |
| SI pooled decline check | +0.005, p = 0.81 | **+0.022, p = 0.53** | Supplementary Note 2 |
| SI pooled divergence test | p = 0.09, D = 0.154, p = 0.007 | **p = 0.31, D = 0.146, p = 0.015** | Supplementary Note 2 |
| SI divergence association | rho = 0.14, top stratum +0.02 | **rho = 0.15, +0.014** | Supplementary Note 2 |
| SI Q4 power | +0.0056 / +0.0032, n@80% 45 / 20,844 | **+0.0051 / +0.0142, 56 / 1,110** | Supplementary Note 2 |

`results/upgrade/class_c_functional_oracle.csv` differs from its pre-U backup in exactly three
columns, which are exactly the three `\ENERGY*` macros above. Every other Class-C ranking compares
mean vectors or scalars and cannot move; all seven were checked and the other four agree.

One SI claim changed direction rather than only digits: the top divergence quartile's MoA gain now
reverses in **two** of three cell lines, not one, and the paragraph prints the per-line means.

### Fig. 5f was described as the wrong measurement

The Results and the Fig. 5f caption both said the panel recovers "the cellular state that carries
the drug-by-state interaction". It does not. `analysis/phase2_transition/phase_c_gates.py` states in
its own header that the state partition cannot be used here, because cell-cycle phase is called from
expression and recovering it from expression would be circular, so Gate 2 is scored on **treated
versus vehicle** instead: 300 of a query drug's treated cells against 300 vehicle cells of the same
line. The 0.800 / 0.555 medians are that problem, not a state-recovery problem.

Consequences applied: the panel and the surviving Fig. 5h explanator are now **response
detectability**; the drug-versus-drug problems (constructed HDAC/JAK mixtures, Fig. 4e glioblastoma
splits, Tahoe drug pairs) are **response-identity recoverability**; and the Methods say that neither
is the recovery of a cell state, with the circularity argument given.

### Other corrections

- Methods named **five** predictors; `phase_b_loco.PREDICTORS` runs **six** and Fig. 6c draws six.
  `nearest_context_cells` is now defined, and the six are grouped by additivity (3 additive, 3 not).
- The Tahoe OT map was called "non-parametric". It is a Gaussian (Bures) map in a 50-component
  training PCA basis. The Sinkhorn map of Supplementary Note 3 is a different, SciPlex3 experiment.
- The Methods paragraph "Predict-then-rank evaluation" claimed to specify **Fig. 6c** while
  describing the SciPlex3 720-query nDCG@10 run. It is now marked SI-only and points at
  Supplementary Note 3 / Table 3.
- Supplementary Table 3's continuation held a checklist of fields to fill in ("Drug-effect
  estimation set, context handling, cell cap, and exact construction") for three of five predictors.
  Filled from the code that produced the run.
- Figs. 5e, 5f and 5h had no Methods at all. Added: headroom and its permutation null, the
  detectability probe, and the conditional bottleneck regression.
- The Fig. 4b caption called 659 **queries** "query--candidate pairs". The statistic is a per-query
  Spearman across candidates, then a median over queries.
- Frangieh: 218,023 (2,000-HVG retrieval matrix) and 218,331 (unfiltered barcode intersection) are
  two matrices, and the Methods now say so instead of leaving the reader with a contradiction.
- The Fig. 3i caption's second clause was unfinished ("and the scalar on 40").
- The SI title was the pre-2026-09 main title.
- `\MAINRECOVER` pointed at Fig. 5e. That panel is now the headroom null, Fig. 5f is detectability,
  and the constructed-mixture result has no panel; the SI carries its values directly.

### Framing

Four stages, frozen in the Introduction and used in the Results and Discussion: the response must
differ between cellular states, be detectable in single cells, be large enough to change the top-1
choice, and survive forward prediction. The Discussion opens by answering the title's question as a
conjunction, and states that no observable tested predicts query-level benefit.

Downgraded overclaims: the Tahoe task is **intervention identification**, not intervention design
(the target is one library compound's own observed response); "most of the signal is magnitude"
became "most of the gap is recovered by a magnitude-sensitive mean score"; "the advantage inverts"
became "does not survive, and becomes negative for the mean-accurate predictors tested"; "best
predictor" became "primary average-effect predictor"; "first to generate real interaction" became
"first to satisfy both entry conditions at once"; "external protein evaluators" became a held-out
protein modality, with "external" pinned to mean outside the retrieval objective; "239 real-data
tasks" became "239 task instances spanning natural and constructed settings"; "Class-A" became
"response-matching".

### De-audit

Six Results passages compressed with every number retained in its own caption: the diagnostic's two
failure modes, the GDSC2 significance caveat, the headroom null's construction, the retirement of
1 - cos, the retained fraction -1.17, and the gains-where-the-oracle-had-none counts. Seven Methods
passages lost the forensic voice, including the SHA-256 task-freeze note and the repeated
"not representative benchmarks of the broader virtual-cell model class".

### Verification

Manuscript 47 pages, SI 15 pages, 0 errors, 0 undefined references, 0 em dashes in either, 0
overfull hboxes in the SI. All 46 panels cited. 28 macros defined in both documents agree. 31
headline values checked against their source files: 0 mismatches.

**Open:** the abstract is 358 words (270 before this pass), over every Nature-family limit.

### Second de-audit pass, 2026-09-04

Five further relocations. No number left the paper; each moved to the place that owns it.

- **Discussion opening.** Four consecutive negative diagnostics (the gate, divergence, the
  interaction statistic, the HIR-Bench boundary) opened the section and read as an account of what
  could not be done. Replaced by three sentences naming the two binding constraints, one at the
  oracle and one in deployment. Each diagnostic is still reported where it is measured.
- **Fig. 3e,f in the Results** is now one sentence. The difference, its interval, the rank test and
  the divergence medians are all in the Fig. 3 caption already.
- **The naive cosine is no longer "retired".** `phase2_data.TERM_LABEL`, `phase2_data.STAT_LABEL`
  and `fig5g.STAT_KEY` said "1 - cos (retired)" and "cross-fitted (used)", which narrates method
  development on the page. Now "naive cosine" and "cross-fitted interaction"; deck rebuilt and
  synced, 6/6 CLEAN. The Results sentence is one clause and the four correlations stay in the
  Fig. 5g caption.
- **Supplementary Note 2** lost the sentence recording when two panels were moved out of the main
  text, and the script path behind the power calculation. **Supplementary Table 3** lost
  `loco=False in the run provenance`.
- **The SciPlex3 predict-then-rank specification actually moved.** Marking it
  "Supplementary Information only" while leaving it in the main Methods was a label, not a move;
  the block is now a paragraph of Supplementary Note 3.

Verification after the pass: manuscript 46 pages, SI 16 pages, 0 errors, 0 undefined references,
0 em dashes, all 46 panels cited, 29 headline values checked against source, 0 mismatches. The only
repository paths left in the manuscript are the two in Code availability, where they belong.

### Claim-scope pass, 2026-09-04

Five corrections, two of them to statements that were internally contradictory.

**The energy distance carries a factor of two, and the paper said "equals".** Methods were already
right: for two point masses the energy distance is exactly `2||mu_Q - mu_d||`. The Abstract,
Introduction, Results and the Fig. 1g panel all said the zero-variance limit *is* the Euclidean
distance between means. `results/exp06_theory_limits/degenerate_limit_synthetic.csv` settles it: the
column is named `two_dmu`, its value is 98.50, and the energy curve reaches 98.5016 at
`t_spread = 0`. So the numbers were right and only the word "equals" was wrong. All four statements
now say proportional, with the constant given; the panel rule is labelled `2 x distance between
means` and its annotation matches. The constant is fixed in lambda and cannot reorder candidates,
which is stated where the claim is made.

**"Detectable without labels" was not what was shown.** The explanator that survives the Fig. 5h
regression is `A_sup`, the five-fold cross-validated logistic probe, which is the *supervised* arm;
`A_unsup` is the k-means arm and is not in the model. The Abstract, Introduction and Discussion all
described the surviving stage as detectability "without labels", which the evidence does not
support. The stage is now **measurable at single-cell resolution**: the supervised 0.800 is an
information ceiling saying the response is present in the cells, and the unsupervised 0.555 says
plain two-way clustering does not extract it. The Results, the Fig. 5f caption and the Methods
vocabulary block all now name which arm is carried forward. This is the second defect found in the
same panel, after its description as state recovery.

**The four stages are no longer a strict necessary conjunction.** A response population can exceed
its mean through variance, multimodality, tail structure or gene covariance, and a distributional
score can separate candidates on any of those. Two drugs with identical means and identical
per-state means can still differ in modality. The stages are now four **bottlenecks**, explicitly
scoped to the state-dependent mechanism this study examines, and both the Introduction and the
Discussion say that they do not speak to gains arising some other way.

**Decision relevance is no longer defined as changing the top-1.** MRR is the primary outcome and
Hit@1 secondary, so a scorer moving the true drug from rank 30 to rank 3 was valuable by the
benchmark and irrelevant by the definition. The stage now reads "alter candidate ordering enough to
move the decision criterion of interest", with MRR named as the continuous measure and the
corrected/broken top-1 counts as the stricter one.

**The +0.399 step is reported as a score, not as a causal decomposition.** Mean cosine to mean L2
changes both what is read (direction, then direction and magnitude) and the geometry used to read it
(angular, then Euclidean), so the step is not the isolated contribution of magnitude. The section
heading, the Results sentence, the Fig. 2a caption, the Fig. 5b caption and the Fig. 5 Results
sentence now all report it as the step to the magnitude-sensitive mean score.

Verification: manuscript 47 pages, SI 16 pages, 0 errors, 0 undefined references, 0 em dashes, all
46 panels cited, deck rebuilt 6/6 CLEAN and synced, 29 headline values checked against source with
0 mismatches. The two surviving uses of "without labels" are the disclaimer in the Results and the
supervised-minus-unsupervised definition in Methods, where the phrase is correct.


---

## Deck compaction pass, 2026-09-04

Every main figure was too tall for its ink, and one of them read out of order. Nothing plotted
changed and no annotation was resized; what left the page is white, two lines of caption material,
and plotting area that was not carrying anything.

| Fig | Height before | after | What came out |
|-----|---------------|-------|----------------|
| 1 | 8.60 in / 219 mm | 7.92 in / 201 mm | `LETTER_BLOCK` 0.17 to 0.15, `ROW_GAP` 0.22 to 0.11, `PAD_BOT` 0.10 to 0.04, the g/h cartoon strip 0.78 to 0.66, and the measured slack in rows 3 and 4. Rows 1 and 2 gave nothing: a, c and d are laid out in absolute inches and points, so a shorter row clips them. |
| 2 | 7.47 in / 190 mm | 6.74 in / 171 mm | Panel a's ladder pitch 0.220 to 0.180 in for names that set 0.094; panel f's note block 3 grey lines to 1; panel c's second x-axis line, which restated a sign convention the panel already carries twice. `ROW_GAP` 0.16 to 0.10. |
| 3 | 8.22 in / 209 mm | 7.91 in / 201 mm | The reorder above, which cost 0.01 in, plus `ROW_GAP` 0.16 to 0.09 and `PAD_BOT` 0.08 to 0.04. This figure's bottom pads have no slack and did not move. |
| 4 | 7.09 in / 180 mm | 6.38 in / 162 mm | The uniform 1.75 in row height, replaced by 1.68 / 1.65 / 1.50, each lowered until a draw-time check or `check_overlaps.py` fired and then stepped back. |
| 5 | 7.50 in / 191 mm | 6.58 in / 167 mm | Bottom pads that reserved 0.28 to 0.49 in for an x apparatus measuring 0.28, and for the schematic none at all; then rows 3 and 4, four panels of two to four categorical rows each sitting in 1.06 to 1.12 in of axes. |
| 6 | 7.70 in / 196 mm | 6.82 in / 173 mm | The same two, on the ledger this figure inherited from Figure 5 when they split. |

The manuscript goes from 42 to 36 pages on the same text.

**One real bug surfaced and was fixed at its source.** Four panels (5f, 5g, 6c, 6g) declared their
own axes size as a pair of constants copied from their figure's inch ledger, and used it to turn a
printed point size into an axes fraction when placing a series key. Nothing checked the copy, so
the first row-height change put Figure 5f's "labels given" key on top of the n annotation above the
panel. `phase2_style.key_label` now measures the axes it is drawing into, and the four constants
are deleted rather than updated.

Verification: `figures/build_all.py --write` reports 6/6 CLEAN against the 6.5 pt floor and syncs
all six to `manuscript/figures/`; `figures/check_overlaps.py` reports 0 collisions on all
six; the manuscript compiles with 0 errors, 0 undefined references, no `Float too large` and no
overfull vbox.
