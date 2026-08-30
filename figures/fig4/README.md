# Figure 4: The criterion decides the answer, from the inside and from the outside

One-line message: whether distribution-aware retrieval "wins" is a property of the criterion used
to judge it, and the same benchmark can be wrong in both directions at once. Row 1 measures that
from the inside, where a synthetic benchmark's latent utility oracle is known and circularity can
be quantified rather than argued. Row 2 measures it from the outside, by checking a benchmark we
constructed against tissue nobody assembled (patient glioblastoma), which corrected us twice.

Rows 3 and 4 were Extended Data until 2026-08-30 and are the audit of rows 1 and 2 respectively:
row 3 is HIR-Bench checked against itself, row 4 is the validation and threshold sweep of the
compartment calls every number in row 2 is computed within. They are placed in the columns of what
they audit, so no row is a miscellany.

**Authority.** The Figure 4 caption in `manuscript/latex/PopRetrieve_manuscript.tex` is the authority for
every number below, and `../../CORRECTIONS.md` for what has been retracted. If this file disagrees
with either, this file is the bug. Layout, canvas geometry and the reasoning behind each title live
in the `fig4_assemble.py` docstring; that is where those decisions are recorded, not here.

## Panels

Titles below are exactly the strings in `fig4_assemble.TITLES`, which is what the composite renders.
The panel modules deliberately do not set their own composite titles: a standalone claim that
differs from the printed claim is the defect this figure was audited for.

**Row 1, from the inside**: analytically, inside a synthetic benchmark, and between two real oracles.

| Panel | Rendered title | What it shows | Module | Source |
|-------|----------------|---------------|--------|--------|
| a | The mean suffices below $\alpha^*$ | HIR-Bench's analytic flip boundary $\alpha^* = B/(A+B)$, separating the regime in which the mean is a sufficient statistic (orange) from the one in which subpopulation structure can change the decision (blue). Closed form, not a fit. | `fig4b.py` | `results/exp11_hir_benchmark/theoretical_boundary.csv` |
| b | Objective alignment, measured | A 2x2: {observable at query time, oracle-derived} features x {28 label-determining parameter cells, 672 instances}. Observable features reach AUC 0.788 against a 0.643 majority-class rate; features derived from the benchmark's own latent utility matrix are at chance (0.400). Pseudo-replication inflates the circular set by $+0.240$ and the honest one by only $+0.048$. | `fig4f.py` | `results/exp11_hir_benchmark/phase_grid_predictability_2x2.csv` |
| c | The evaluator's shape picks the winner | Same cells, same 20 surface proteins, same two RNA rankings; the only thing that changes is whether the external protein criterion is computed as a mean or as a distribution. **The winner swaps**: mean incumbent $+0.242$ against $+0.146$ under the mean-shaped oracle, distributional $+0.529$ against $+0.334$ under the distribution-shaped one, in each of the three immune conditions. Hatched, the magnitude-matching control ($+0.125 \to +0.352$). | `fig4_shape.py` | `results/upgrade/oracle_shape_test.json` |

**Row 2, from the outside**: our constructed benchmark, checked against tissue nobody assembled
(ZhaoSims2021, ten glioblastoma patients).

| Panel | Rendered title | What it shows | Module | Source |
|-------|----------------|---------------|--------|--------|
| d | Recoverability in a tumour: an algorithmic limit | Gate 2 posed as the SAME drug-response question in both settings (36 splits, 4 patients). Pooling drugs into classes holds the constructed ceiling at 0.700 (grey, kept because deleting the number the paper previously reported would hide the correction); one drug against one drug, the same cells give 0.879 (gap $+0.007$). In a real tumour the information is present (ceiling **0.923**) and unsupervised clustering does not reach it (**0.777**, median paired gap **$+0.117$**, 95% CI $[+0.115, +0.135]$ by patient-level bootstrap). | `fig4_gate2.py` | `results/zhao_gbm/gate2_drug_response.json`, `results/zhao_gbm/gate2_uncertainty.json` |
| e | Divergence is overstated | Induced response cosine on natural tissue, median **0.566** over 17 patient-drug pairs, against **0.014--0.044** in our constructed mixtures: mixing cell lines overstates the divergence a distributional score can exploit by roughly an order of magnitude. | `fig4_nat.py` -> `../fig7/fig7_natural.py` | `results/zhao_gbm/gate1_natural.csv` |
| f | The mean ranks most of it | The Fig. 1a premise tested on real tumours: over 18 within-patient drug pairs, mean-signature similarity ranks malignant-compartment response similarity at Spearman $\rho = \mathbf{+0.878}$ when the mean contains 43\% of the malignant cells it is being used to rank, and $\mathbf{+0.835}$ in the disjoint form (ranking the malignant compartment by the *myeloid* one). The manuscript reports both and treats the disjoint value as the one its own argument permits; see CORRECTIONS.md R42. | `fig4_nat.py` -> `../fig7/fig7_natural.py` | `results/zhao_gbm/premise_mean_vs_compartment.csv` |

**Row 3, row 1 audited**: the boundary measured rather than derived, what losing the structure
costs a decision, and HIR-Bench's own quality control. Drawn by the modules of the retired Extended
Data Fig. 6, imported unchanged; note that those file names are off by one from their own function
names (`ed6_panel_c` defines `draw_ed6b`, and so on down the row).

| Panel | Rendered title | What it shows | Module | Source |
|-------|----------------|---------------|--------|--------|
| g | The advantage is regime-dependent | Energy-minus-mean Hit@1 over the full HIR-Bench grid, 9 conflict $\lambda$ values x 4 minority fractions $\alpha$, on a signed $\pm 1$ scale. Panel a gives the flip boundary in closed form; g is the same boundary measured cell by cell, blue where the distributional score wins and orange where the mean does. | `../ed6/ed6_panel_c.py` | `results/exp11_synthetic_phase_diagram/dart_advantage_grid.csv` |
| h | Losing structure inflates regret | Best decision regret under the observed information condition against the predicted-mean one, for both welfare definitions: **0.11 to 0.45** under mean welfare and **0.29 to 0.96** under worst welfare. b measures how much of an evaluator is oracle-derived; h prices the same loss of structure as a decision cost, and the minority-sensitive welfare is where it costs most. | `../ed6/ed6_panel_d.py` | `results/exp11_hir_benchmark/method_dominance.csv` |
| i | The benchmark behaves as specified | The three sanity checks on one 0-1 track, each with its own threshold marked: no-conflict flip rate **0.000**, median boundary margin **0.272**, predicted-mean equality **0.056**. All three pass. A benchmark whose answer is designed in owes the reader this panel; without it, a and b have to be taken on trust. | `../ed6/ed6_panel_e.py` | `results/exp11_hir_benchmark/sanity_checks.csv` |

**Row 4, row 2 audited**: are the three compartments real, and does the assignment threshold change
any conclusion drawn inside them. All four come from one module and one sweep over ZhaoSims2021.

| Panel | Rendered title | What it shows | Module | Source |
|-------|----------------|---------------|--------|--------|
| j | The compartment calls match their markers | Mean marker-set expression for the three retained compartments against all three marker sets. The diagonal wins in every case (malignant **1.02** against 0.07 and 0.12; myeloid **1.53** against 0.12 and 0.17; oligodendrocyte **1.78** against 0.41 and 0.11). Every number in d, e and f is computed within these compartments, so this is the panel that says they exist. | `../ed4/ed4_zhao_robustness.py` | `results/zhao_gbm/compartment_validation.csv` |
| k | Retention falls with the threshold | Fraction of cells retained and fraction left unassigned as the marker floor and the margin move together from 0.10 to 0.50. The primary setting (0.25, marked) retains **0.601**; the sweep runs from 0.712 down to 0.418. This is where a reader sees what the discarded cells cost, which is the caveat d's own honesty note turns on. | `../ed4/ed4_zhao_robustness.py` | `results/zhao_gbm/zhao_threshold_sensitivity.csv` |
| l | Divergence is threshold-stable | Malignant-versus-myeloid induced-response cosine over the same sweep, **range 0.54 to 0.59**. e reports one such cosine and reads it as divergence being overstated; l shows that reading does not depend on where the threshold was set. | `../ed4/ed4_zhao_robustness.py` | `results/zhao_gbm/zhao_threshold_sensitivity.csv` |
| m | The recoverability gap persists | Supervised ceiling against best unsupervised recovery over the same sweep: the ceiling holds at 0.915-0.923 and the unsupervised best at 0.773-0.797, so the gap d reports is present at every threshold. d is this figure's one constructive claim; m is the check that it is not an artefact of the compartment call. | `../ed4/ed4_zhao_robustness.py` | `results/zhao_gbm/zhao_threshold_sensitivity.csv` |

## Honesty notes (the load-bearing caveats)

- **d is scoped to the tumour on purpose.** The two constructed arms in the same axes show gaps of
  $+0.007$ and $-0.002$, i.e. there the limit is *not* algorithmic; an unscoped title would
  contradict two of its own three bar groups. The 0.692 quoted for this construct elsewhere is the
  earlier in-fold run (Fig. 5e), and the 0.964 once reported for natural tissue is **withdrawn**: it
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
- **e and f are drawn by `fig7/fig7_natural.py`, not reimplemented here.** `fig4_nat.py` imports
  those two draw functions unchanged and only retunes annotation text, positions and font sizes for
  the 6.9 in canvas, each edit keyed to a substring of the original text so an upstream rewording
  fails the build instead of silently leaving a too-wide label on the page. There is exactly one
  copy of the plotting code.
- Palette semantics are the deck's: blue distributional/PopRetrieve, orange mean/collapse, grey context,
  purple the natural-tissue arm. Green is *not* used in row 2: across the deck green marks readouts
  handed information the retrieval method does not have, and in panel d colour encodes the
  experimental arm, so both bars of every arm share one hue.

## What is NOT in this figure any more

Earlier versions of this document described the six-panel HIR-Bench-only figure. Two of its panels
are still gone. The generative-model **schematic** read no result file and drew no data; panel a and
Supplementary Note 1 carry what it stated. The failure-predictability **ROC curve** was replaced by
the 2x2 in panel b, which reports the same experiment as an AUC per (feature set x CV unit) cell
rather than as one curve; `fig4f_roc_curve.csv` and `fig4f_roc_summary.json` in this directory are
its retired source data.

The other three came back on 2026-08-30 as g, h and i, when the Extended Data deck was retired.
That does not undo the 2026-07-12 judgement that HIR-Bench earns only two panels of ARGUMENT: a and
b are still the argument, and g, h and i are underneath them as its audit, which is a different job
and is why they sit in a separate row rather than being folded back into row 1.

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
