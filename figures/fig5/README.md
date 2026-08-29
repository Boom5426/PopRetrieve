# Figure 5: The information condition is a two-gate criterion

One-line message: the collapse of the apparent distributional advantage (Fig. 3) has a mechanism.
A distributional score can only exploit subpopulation structure that (Gate 1) actually responds
*differently* in the candidate populations handed to the retriever, and that (Gate 2) can be told
apart inside those populations at all. In the constructed cell-line data this figure uses, both
gates are closed, so the advantage stays near zero: a criterion, not a tuning failure.

**Authority.** The Figure 5 caption in `manuscript/latex/PopRetrieve_manuscript.tex` is the authority for
every number below, and `../../CORRECTIONS.md` for what has been retracted. If this file disagrees
with either, this file is the bug. Panel geometry and the reason each title is worded the way it is
are documented in `fig5_assemble.py`; that docstring, not this one, is the place layout decisions
are recorded.

## Panels (mechanism chain: predict -> preserve -> identify -> decide)

Titles below are exactly the strings in `fig5_assemble.TITLES`, which is what the composite
renders. A panel file that hard-codes a *different* title for its standalone run is a defect: the
standalone claim and the printed claim must be the same claim.

| Panel | Rendered title | What it shows | Source |
|-------|----------------|---------------|--------|
| a | Predict-then-rank, and the two gates | Design schematic: a held-out query scored against candidate populations that are either observed or produced by a perturbation predictor, and the two properties a candidate must have. No result is asserted. | schematic |
| b | Gain is small and sign-inconsistent | nDCG@10 gain (PopRetrieve energy minus mean cosine) per predictor family: $-0.071$ nearest-neighbour, $-0.016$ average-effect, $+0.027$ latent-linear. One task, so no dispersion is available; bars are coloured by sign. | `results/exp09_predict_then_rank/summary.csv` |
| c | Structure survives; divergence does not | Gate 1, both halves at once. Predicted candidates *retain* baseline subpopulation structure (variance ratio 0.142 against 0.138 real, left axis) but do not reproduce *divergence* (induced response cosine 0.19--0.37 predicted against 0.014 real, right axis). | `results/exp09_structure_diagnostics/{exp09_structure_diagnostics_summary,gate1_response_divergence_summary}.csv` |
| d | No predictor collapses structure | Three structure diagnostics x three predictors as predicted/real ratios on a log axis with the reference at 1, under the faithful (`cells`) synthesizer. | `results/exp09_structure_diagnostics/exp09_structure_diagnostics_summary.csv` |
| e | In this mixture, even the ceiling is only 0.692 | Gate 2 on a known bimodal mixture (K562, HDAC-class against JAK-class cells), every method scored in one unit as best-permutation accuracy against the true labels. Supervised ceiling 0.692, best unsupervised 0.674, gap 0.018. | `results/upgrade/gate2_supervised_upper_bound.csv` (real separation, s = 1.0) |
| f | The probe pulls away when structure is there | The positive control that licenses reading e: raise the separation between the two source states and the ceiling pulls away from clustering as it should ($+0.114$ at 1.5x, $+0.162$ at 2.0x, then both saturate). | `results/upgrade/gate2_supervised_upper_bound.csv` (separation ladder) |
| g | Where theory predicts gain, there is none | The conditional advantage a working information condition would produce, and its absence. PopRetrieve-minus-mean MoA-nDCG gain by *true* response-divergence quartile (means, s.e.m., Benjamini--Hochberg corrected). No stratum is positive; the lowest quartile is significantly negative (mean $-0.082$, $q = 5.8\times10^{-5}$, $n = 166$). | `results/exp17_true_divergence_subset/divergence_stratified.csv` |

## Honesty notes (the load-bearing caveats)

- **e is scoped to the constructed mixture on purpose, and its general reading is withdrawn.**
  The 0.692 ceiling is substantially an artefact of *pooling* several drugs into each class: split
  the same K562 cells one drug against one drug and the ceiling is 0.879 against 0.837
  unsupervised. Posed as that same drug-versus-drug question in a patient's tumour, the ceiling is
  0.923 and the best unsupervised method reaches 0.777 (median paired gap $+0.117$), so **in real
  tissue Gate 2 is an algorithmic bottleneck, not an informational one** (main-text Fig. 4d;
  `CORRECTIONS.md` R18 and R21). The panel title therefore names the mixture it measures. An
  earlier version of this withdrawal quoted a natural ceiling of 0.964 with Leiden at 0.949; that
  test separated malignant from myeloid *control* cells, a cell-type rather than a drug-response
  partition, and is itself withdrawn by R21. Do not reintroduce it.
- **b's title is a weaker claim than its predecessor, deliberately.** "No predictor gives a
  positive gain" was falsified by this figure's own source table: a reindex-key typo dropped the
  latent-linear predictor, whose gain is $+0.027$. The honest summary is that the gain is small and
  its *sign* is not consistent, and the panel now fails loudly rather than plotting NaN.
- **c and d retract the "5.1x structure collapse".** That number came from comparing a unimodal
  Gaussian synthesizer against a single-context reference rather than against the blended candidate
  a scorer actually ranks, so it measured the synthesizer, not the predictor. With the effect
  applied to real control cells, structure is preserved and it is *divergence* that is missing,
  which is the finding these two panels carry.
- **e and f share one source file and one protocol; f is not an independent result.** f exists so
  that "no gap in e" cannot be explained by an insensitive probe. Clusterers get best-permutation
  label matching for free and the transductive representation, which biases the comparison against
  the conclusion drawn; every supervised bar fits its representation inside the training fold, so
  no test information leaks into any of them.
- **g's highest-divergence quartile mean is $+0.003$**, not significant and with median exactly 0.
  The title claims the absence of the *predicted* gain, which is what the panel shows; it does not
  claim every bar is negative.
- Palette semantics are the deck's: blue distributional/PopRetrieve, orange mean/collapse, grey context,
  green for readouts handed information the retrieval method does not have (the supervised,
  label-given ceilings in e and f).

## What is NOT in this figure any more

Earlier versions of this document described panels that no longer exist, and the numbers went with
them. For the record, so nobody looks for them here: the nine-method adjusted-Rand-index comparison
(best median ARI 0.106) was replaced by e, which scores every method in one unit and adds the
supervised upper bound; the ARI phase diagram over (separation x cell budget) was replaced by f,
whose x axis is separation only, the cell-budget axis being flat and reported in Extended Data;
the predicted/real structure *heatmap* was replaced by d's ratio axis; and g is stratified by
**quartile**, not tertile, and read from `exp17` rather than re-derived here.

## Files

- `fig5a.py` ... `fig5g.py` : per-panel draw functions, each runnable standalone
  (`python fig5c.py`). The `__main__` block of each writes a scratch `6*.png` preview; the
  composite is not built from those PNGs.
- `fig5_assemble.py` : the 7-panel, 3-row layout (a|b|c / d|e / f|g), authored at the FINAL PRINTED
  width of 6.90 in so LaTeX applies no scaling and nominal point size == printed point size. Panel
  rectangles are given in inches, not gridspec ratios, because at this size the binding constraints
  (tick-label widths, y-label gutters) are absolute rather than proportional. It also owns `TITLES`
  and the module-level `STEM`.
- `fig5_two_gate.{pdf,svg,png}` : the composite, and the only stem this figure is written under.
  `python figures/build_all.py --write` enforces the 5 pt floor, writes these, and copies the PDF
  to `manuscript/latex/figures/fig5.pdf`, which is the file the manuscript compiles.
