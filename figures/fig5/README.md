# Figure 5: three requirements connect heterogeneity to a change in candidate ranking

One-line message: a distributional score can only beat a mean signature when the candidate
populations actually respond differently (differential response), when that difference can be
recovered from the observed population (recoverability), and when it is large enough to reorder
candidates (decision relevance). The figure measures the three on material we constructed, and
then measures them again on Tahoe-100M, which nobody constructed.

**Authority.** The Figure 5 caption in `manuscript/latex/PopRetrieve_manuscript.tex` is the
authority for every number below, and `../../CORRECTIONS.md` for what has been retracted. If this
file disagrees with either, this file is the bug. Panel geometry lives in `fig5_assemble.py`; the
colour and type vocabulary lives in `fig5_style.py`. Those docstrings, not this one, are where
layout and palette decisions are recorded.

## Panels

Eleven, a to k, read as: the three requirements, then each one measured, then all three measured
again at scale.

| Panel | What the reader should see in three seconds | Reads |
|---|---|---|
| a | a chain of four boxes, the last one dashed because it is proposed rather than measured | schematic |
| b | three predictor families straddling zero, two left and one right | `results/exp09_predict_then_rank/summary.csv` |
| c | a blue series flat across real and predicted, an orange one that is not | `results/exp09_structure_diagnostics/*.csv` |
| d | nine points on a log ratio axis, all near 1 except one predictor | `results/exp09_structure_diagnostics/exp09_structure_diagnostics_summary.csv` |
| e | seven lollipops from chance, and a short bracket between the best two | `results/upgrade/gate2_supervised_upper_bound.csv` |
| f | two curves that separate in the middle and rejoin at both ends | same file, separation ladder |
| g | four intervals, three below zero and one on it | `results/exp17_true_divergence_subset/divergence_stratified.csv` |
| h | a distribution piled up near 1, with the constructed anchor far to its left | `results/tahoe_pilot/gate1_per_condition.csv` |
| i | a cloud entirely above the diagonal | `results/tahoe_pilot/g2panel/gate2_clusterer_panel.csv` |
| j | two columns, both well above 0.5 | `results/tahoe_pilot/disjoint/*.csv` |
| k | a rising cloud, tight but not on a line | `gate1_per_condition.csv` + `gate3_disjoint_cellcycle_G1_vs_G2M.csv` |

## No panel states a conclusion

`fig5_assemble` used to carry a `TITLES` dict of fourteen conclusion sentences: "Gain is small and
sign-inconsistent", "Structure survives; divergence does not", "Where theory predicts gain, there
is none". They were never drawn on the composite, which calls `strip_titles`, but three panel
files still set one for their standalone run, so the standalone and the printed panel disagreed
about what the panel claimed. The dict and the three `set_title` calls are gone.

`fig5_assemble._assert_no_titles` enforces this mechanically: **no panel may draw text above
7.2 pt**, and the build fails if one does. It is a size gate rather than a wording gate, because
no code can tell a claim from a label, but a claim that has to fit at 7.2 pt beside the marks it
describes has already lost the argument for being on the panel.

## What left on 2026-09-01, and where it went

Three panels: median ARI across nine clustering configurations, per-population silhouette under a
raw k=2 partition, and the seed-averaged ARI grid over separation by cell budget. All three
measured recoverability of the constructed mixture, which is panel e's subject.

Unlike the panels cut from Figures 3 and 4, **no Supplementary Note carried their numbers**, so
Supplementary Note 2 gained "Unsupervised recovery of constructed two-state structure" *before*
they were removed. It carries all three: the nine configurations and their 0.037 to 0.106 range,
the SciPlex3 and Frangieh silhouette medians, and the finding that cell budget buys at most 0.02
of ARI while separation buys 0.93.

Removing them also repaired a citation. The Results sentence "This is an algebraic property of the
model class rather than a consequence of insufficient training" cited Fig. 5h-j, but those three
panels were clustering diagnostics and showed nothing about predictor algebra; the caption said so
itself ("h-j, Recoverability measured three further ways on the constructed mixture of e").
Supplementary Note 3 carries that claim and now carries it alone.

The four Tahoe-100M panels stayed and became h to k. Their numbers ARE duplicated in Supplementary
Note 4, so they were the cheaper cut in content terms; they were kept anyway, because they are the
answer to the objection that a negative result about mixtures we built is a fact about our
mixtures, and a reader who accepts that objection stops reading before the Supplementary
Information.

## Archetype and panel hierarchy

**Archetype: a mechanism chain measured twice.** There is no single hero and there should not be:
the figure's claim is that three requirements must hold together, so no one of them can carry it.

Measured after the row heights were set, panel area as a share of total axes area:

| tier | panels | share, each |
|---|---|---|
| 1, the requirements measured | e 16.1, g 15.7, f 12.2 | 12 to 16% |
| 2, the chain and its mechanism | c 9.9, a 9.5, d 9.1, b 8.0 | 8 to 10% |
| 3, the same three at scale | h 5.7, i 5.3, k 4.4, j 4.1 | 4 to 6% |

The first cut of the ledger had **e largest at 17.8 per cent, and e is the panel whose general
reading this paper withdraws** (see the honesty notes below), while a, the schematic the whole
figure is organised around, was 8.9. Row 1 gave height back to rows 0 and 2. e is still the single
largest, at 16.1 against g's 15.7, and that is a content constraint rather than a claim: it scores
seven methods in one unit, and seven two-line categorical labels need 3.39 in whatever the panel
is worth.

## Verified numbers

- **b** nDCG@10 gain, distributional minus mean: nearest-neighbour -0.071, average-effect -0.016,
  latent-linear +0.027. One task, so no dispersion is available and the bars are coloured by sign.
- **c** subpopulation variance ratio 0.142 predicted against 0.138 real (structure IS preserved);
  induced response cosine 0.19 to 0.37 predicted against 0.014 real (divergence is NOT).
- **d** ratios of predicted to real under the faithful `cells` synthesizer. Average-effect and
  nearest-neighbour reproduce subpopulation variance, response diversity and isotropy to within
  4 per cent (1.03, 1.04, 0.99 and 1.03, 1.02, 0.99); the linear-latent model gives 3.35, 2.39
  and 0.78.
- **e and f** are **medians** over seeds, not means, and the distinction is load-bearing: the mean
  ceiling at real separation is 0.690 and the median is 0.692. At separation 1.0, ceiling 0.692,
  best unsupervised 0.674 (Leiden), gap +0.018. Ladder gaps: +0.018, +0.114, +0.161, +0.034,
  +0.000, +0.000 at 1.0, 1.5, 2.0, 3.0, 5.0 and 8.0 times real separation.
- **g** MoA-nDCG gain by true response-divergence quartile: Q1 -0.082 (n=166, q=5.8e-5), Q2 -0.041
  (n=150, q=0.073), Q3 -0.020 (n=141, q=0.57), Q4 +0.003 (n=143, q=0.57). Benjamini-Hochberg.
- **h** median induced response cosine 0.739 over 3,630 evaluable conditions; the constructed
  mixtures sit at 0.014, which fewer than 0.11 per cent of conditions reach.
- **i** supervised ceiling 0.853 against best unsupervised 0.611 over 960 drug pairs and 48 cell
  lines, median paired gap 0.157, positive in all 48.
- **j** median disjoint state-ordering Spearman 0.841 under the cell-cycle partition (44 contexts,
  none below 0.5) and 0.778 under the control-derived partition (45 contexts, two below 0.5).
  Patient tissue computed the same way is 0.835.
- **k** Spearman rho +0.62 over 44 cell lines.

## Honesty notes (the load-bearing caveats)

- **e is scoped to the constructed mixture, and its general reading is withdrawn.** The 0.692
  ceiling is substantially an artefact of *pooling* several drugs into each class: split the same
  K562 cells one drug against one drug and the ceiling is 0.879. Posed as that same drug-versus-drug
  question in a patient's tumour, the ceiling is 0.923 against 0.777 unsupervised, so **in real
  tissue Gate 2 is an algorithmic bottleneck, not an informational one** (Fig. 4d; `CORRECTIONS.md`
  R18 and R21). An earlier version of this withdrawal quoted a natural ceiling of 0.964 with Leiden
  at 0.949; that test separated malignant from myeloid *control* cells, a cell-type rather than a
  drug-response partition, and is itself withdrawn by R21. Do not reintroduce it.
- **e and f share one source file and one protocol; f is not an independent result.** f exists so
  that "no gap in e" cannot be blamed on an insensitive probe. Clusterers get best-permutation
  label matching for free and the transductive representation, which biases the comparison against
  the conclusion drawn; every supervised bar fits its representation inside the training fold, so
  no test information leaks into any of them.
- **k no longer reports an R-squared, and the removal is a correction rather than a trim.** The
  panel and the caption printed "R^2 = 0.38", which was the square of *Spearman's* rho. It sat
  beside a least-squares line whose actual R-squared is Pearson's, **0.606**, so the printed value
  understated the drawn line by 0.22 while looking like the line's own statistic. Rho is the right
  statistic for a monotone-association claim and it stays. See `CORRECTIONS.md` R54.
- **c and d retract the "5.1x structure collapse".** That number compared a unimodal Gaussian
  synthesizer against a single-context reference rather than against the blended candidate a
  scorer actually ranks, so it measured the synthesizer, not the predictor.
- **g's highest-divergence quartile mean is +0.003**, not significant and with median exactly 0.
  The figure claims the absence of the *predicted* gain, not that every bar is negative.
- **No retrieval was run on Tahoe-100M.** Panels h to k constrain the conditions under which
  population-level retrieval could help; they do not measure retrieval.
- **The three n in the Tahoe block differ on purpose**: 3,630 conditions in h, 960 drug pairs
  across 48 lines in i, 44 and 45 contexts in j, 44 lines in k. Each panel states its own.

## Print geometry, authored 1:1

The manuscript text block is 6.951 in and the figure enters with
`\includegraphics[width=\textwidth]`. The canvas is **6.90 x 8.11 in** and exports 6.92 x 8.13 (176 x 207 mm),
so LaTeX applies no meaningful rescale and nominal point size is printed point size. The float
budget is the 9.461 in text block less about 16/72 in of overhead, i.e. 9.238 in, leaving 1.03 in
of headroom; it was 0.02 in before this figure came down from 234 mm.

Layout is an explicit inch ledger in `fig5_assemble.py`: four rows, `a|b|c`, `d|e`, `f|g`, then the
four Tahoe panels across. Left pads are the **measured** furniture of each panel plus 0.22 in for
the letter, not a common value, because at eleven panels an over-wide pad is axes width thrown
away.

Row 3 is four-across on measurement rather than preference. At 1.09 in of axes the four Tahoe
panels need 6.99 in of slot against the 6.90 in available, an excess of about three characters of
label at 6.5 pt; splitting them two-by-two costs a whole row and puts the page back at 226 mm.
The excess was paid by reworking the panels, not by shrinking type: panel i's four hand-staggered
in-place labels became a key in the triangle below the diagonal, which is empty by construction
because a supervised ceiling cannot be beaten by the unsupervised method it upper-bounds.

**The 6.5 pt floor** is enforced by `fig5_assemble._assert_floor`, above the deck's 5 pt production
limit, with mathtext measured at its effective 0.7x size. Before this pass the figure carried
**239 text artists below 6.5 pt and 33 at exactly 5.0 pt**, and all fourteen of its panels failed.
The ladder is now four sizes: 6.5, 6.8, 7.2 and the 9.5 pt panel letters.

## Files

- `fig5_style.py` : the frozen vocabulary. Four colours with one meaning each, one type ladder.
  Panels import from here and never re-declare a colour or a size.
- `fig5a.py` ... `fig5g.py` : per-panel draw functions, each runnable standalone for a preview.
- `../ed7/ed7_tahoe.py` : `draw_a` to `draw_d`, which are panels h to k. They live there because
  that module still assembles a standalone preview of the four; Figure 5 is their only gated
  consumer, so they take their type ladder and their palette from `fig5_style`.
- `fig5_assemble.py` : the inch ledger, the panel letters at 9.5 pt, the 6.5 pt floor gate and the
  7.2 pt no-titles gate. Owns the module-level `STEM`, which `build_all.py` checks.
- `fig5_two_gate.{pdf,svg,png}` : the composite, and the only stem this figure is written under.
  `python figures/build_all.py --write` enforces the floor, writes these, and copies the PDF to
  `manuscript/latex/figures/fig5.pdf`, which is the file the manuscript compiles.
