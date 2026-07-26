# Figure 5: The criterion decides the answer, from the inside and from the outside

One-line message: whether distribution-aware retrieval "wins" is a property of the criterion used
to judge it, and the same benchmark can be wrong in both directions at once. Row 1 measures that
from the inside, where a synthetic benchmark's latent utility oracle is known and circularity can
be quantified rather than argued. Row 2 measures it from the outside, by checking a benchmark we
constructed against tissue nobody assembled (patient glioblastoma), which corrected us twice.

**Authority.** The Figure 5 caption in `manuscript/latex/DART_manuscript.tex` is the authority for
every number below, and `../../CORRECTIONS.md` for what has been retracted. If this file disagrees
with either, this file is the bug. Layout, canvas geometry and the reasoning behind each title live
in the `fig5_assemble.py` docstring; that is where those decisions are recorded, not here.

## Panels

Titles below are exactly the strings in `fig5_assemble.TITLES`, which is what the composite renders.
The panel modules deliberately do not set their own composite titles: a standalone claim that
differs from the printed claim is the defect this figure was audited for.

**Row 1, from the inside**: analytically, inside a synthetic benchmark, and between two real oracles.

| Panel | Rendered title | What it shows | Module | Source |
|-------|----------------|---------------|--------|--------|
| a | The mean suffices below $\alpha^*$ | HIR-Bench's analytic flip boundary $\alpha^* = B/(A+B)$, separating the regime in which the mean is a sufficient statistic (orange) from the one in which subpopulation structure can change the decision (blue). Closed form, not a fit. | `fig5b.py` | `results/exp11_hir_benchmark/theoretical_boundary.csv` |
| b | Circularity, measured | A 2x2: {observable at query time, oracle-derived} features x {28 label-determining parameter cells, 672 instances}. Observable features reach AUC 0.788 against a 0.643 majority-class rate; features derived from the benchmark's own latent utility matrix are at chance (0.400). Pseudo-replication inflates the circular set by $+0.240$ and the honest one by only $+0.048$. | `fig5f.py` | `results/exp11_hir_benchmark/phase_grid_predictability_2x2.csv` |
| c | The oracle's shape picks the winner | Same cells, same 20 surface proteins, same two RNA rankings; the only thing that changes is whether the external protein criterion is computed as a mean or as a distribution. **The winner swaps**: mean incumbent $+0.242$ against $+0.146$ under the mean-shaped oracle, distributional $+0.529$ against $+0.334$ under the distribution-shaped one, in each of the three immune conditions. Hatched, the magnitude-matching control ($+0.125 \to +0.352$). | `fig5_shape.py` | `results/upgrade/oracle_shape_test.json` |

**Row 2, from the outside**: our constructed benchmark, checked against tissue nobody assembled
(ZhaoSims2021, ten glioblastoma patients).

| Panel | Rendered title | What it shows | Module | Source |
|-------|----------------|---------------|--------|--------|
| d | Gate 2 in a tumour: an algorithmic limit | Gate 2 posed as the SAME drug-response question in both settings (36 splits, 4 patients). Pooling drugs into classes holds the constructed ceiling at 0.700 (grey, kept because deleting the number the paper previously reported would hide the correction); one drug against one drug, the same cells give 0.879 (gap $+0.007$). In a real tumour the information is present (ceiling **0.923**) and unsupervised clustering does not reach it (**0.777**, median paired gap **$+0.117$**, 95% CI $[+0.115, +0.135]$ by patient-level bootstrap). | `fig5_gate2.py` | `results/zhao_gbm/gate2_drug_response.json`, `results/zhao_gbm/gate2_uncertainty.json` |
| e | Gate 1: divergence overstated | Induced response cosine on natural tissue, median **0.566** over 17 patient-drug pairs, against **0.014--0.044** in our constructed mixtures: mixing cell lines overstates the divergence a distributional score can exploit by roughly an order of magnitude. | `fig5_nat.py` -> `../fig7/fig7_natural.py` | `results/zhao_gbm/gate1_natural.csv` |
| f | The mean ranks most of it | The Fig. 1a premise tested on real tumours: over 18 within-patient drug pairs, mean-signature similarity ranks malignant-compartment response similarity at Spearman $\rho = \mathbf{+0.878}$. | `fig5_nat.py` -> `../fig7/fig7_natural.py` | `results/zhao_gbm/premise_mean_vs_compartment.csv` |

## Honesty notes (the load-bearing caveats)

- **d is scoped to the tumour on purpose.** The two constructed arms in the same axes show gaps of
  $+0.007$ and $-0.002$, i.e. there the limit is *not* algorithmic; an unscoped title would
  contradict two of its own three bar groups. The 0.692 quoted for this construct elsewhere is the
  earlier in-fold run (Fig. 6e), and the 0.964 once reported for natural tissue is **withdrawn**: it
  separated malignant from myeloid *control* cells, a cell-type rather than a drug-response
  partition (`CORRECTIONS.md` R18 and R21).
- **d's bounds are optimistic and the panel says so.** 30 of the 36 splits come from one patient
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
- **e and f are drawn by `fig7/fig7_natural.py`, not reimplemented here.** `fig5_nat.py` imports
  those two draw functions unchanged and only retunes annotation text, positions and font sizes for
  the 6.9 in canvas, each edit keyed to a substring of the original text so an upstream rewording
  fails the build instead of silently leaving a too-wide label on the page. There is exactly one
  copy of the plotting code.
- Palette semantics are the deck's: blue distributional/JUDGE, orange mean/collapse, grey context,
  purple the natural-tissue arm. Green is *not* used in row 2: across the deck green marks readouts
  handed information the retrieval method does not have, and in panel d colour encodes the
  experimental arm, so both bars of every arm share one hue.

## What is NOT in this figure any more

Earlier versions of this document described the six-panel HIR-Bench-only figure, and none of those
panels is here. For the record, so nobody looks for them in this directory: the generative-model
schematic, the (alpha x conflict) Hit@1 phase grid, the boundary-margin comparison and the benchmark
sanity checks all moved to Extended Data, and the failure-predictability **ROC curve** was replaced
by the 2x2 in panel b, which reports the same experiment as an AUC per (feature set x CV unit) cell
rather than as one curve. HIR-Bench keeps two main-text panels, a and b, because its phase boundary
is designed in and its transfer to real data fails; the analytic condition and the circularity
measurement are the parts that earn the space.

## Files

- `fig5b.py`, `fig5f.py`, `fig5_shape.py`, `fig5_gate2.py`, `fig5_nat.py` : the panel modules, in
  panel order a, b, c, d, then e and f. The names are historical (`fig5b`/`fig5f` predate the
  re-lettering); the mapping above is the authoritative one and `fig5_assemble.py` states it too.
- `fig5_assemble.py` : the 6-panel two-row layout, authored at the FINAL PRINTED width of 6.90 in so
  LaTeX applies no scaling and nominal point size == printed point size. Panel rectangles are in
  inches, not gridspec ratios. It owns `TITLES`, `ROW_LABELS` and the module-level `STEM`.
- `fig5_benchmarks.{pdf,svg,png}` : the composite, and the only stem this figure is written under.
  `python figures/build_all.py --write` enforces the 5 pt floor, writes these, and copies the PDF to
  `manuscript/latex/figures/fig5.pdf`, which is the file the manuscript compiles.
- Superseded artefacts kept in this directory, none of them an input to the current figure:
  `fig5_hir_bench.{png,pdf}` and `fig5_hir_bench_partial.png` (the old six-panel composite),
  `_fig5_partial.png`, `fig5f_roc_curve.csv` and `fig5f_roc_summary.json` (source data for the
  retired ROC panel), the `5b.png` / `5f.png` standalone previews, and `_stale/` (see
  `_stale/README.md`).
