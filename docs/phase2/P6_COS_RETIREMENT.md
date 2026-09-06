# P6. Retiring `1 - cos` across the manuscript

Step 3 of the post-Phase-II order: `grep -> classify -> rerun -> rewrite`. This document does the
first three. Every use of the retired statistic in the codebase is classified, the two load-bearing
measurements are recomputed against a reference they never had, and the sentences that have to
change are named.

## Why it is retired

`D = 1 - cos(r_1, r_2)` is confounded with effect size and with cell count: on 3,620 Tahoe
conditions it correlates **-0.694** with the response norm and **-0.425** with the number of treated
cells ([05](05_DIFFERENTIAL_RESPONSE_AUDIT.md)). Noise pushes the cosine down, so a weak drug scores
as strongly state-specific. Conditioned on the mean route's own performance it **anti**-predicts the
outcome it was introduced to predict (β = -0.0096, p = 0.009; [P4](P4_BOTTLENECK_DECOMPOSITION.md)).

The replacement is the cross-fitted interaction `S_int = <I_A, I_B>/p` with its scale-free share and
its reproducibility index `R_int` ([P3](P3_INTERACTION_STATISTIC.md)).

## The reference the published numbers never had

An additive predictor returns cosine exactly 1.000. That is algebra on a single mean per arm, with
no sampling error in it. A real measurement returns something below 1 whether or not there is a
state-specific response, because noise alone lowers a cosine. **Comparing the two is comparing a
noisy estimate against a noiseless constant, and the gap is overstated by an unknown amount.**

The missing reference is an **effect-size-matched additive null**: a synthetic treated arm built
from a disjoint half of the same control cells, shifted by that drug's own pooled response. Same
arms, same sizes, same noise, same effect magnitude, zero state-specific component. Whatever cosine
that returns is what "no interaction" looks like through the instrument.

Building it exposed a second trap worth recording. A first version of the null reused the *same*
cells for the treated and the control arm; a half of one arm and the complementary half of the other
then carry exactly opposite deviations from their shared mean, which makes the two cross-fit
estimates anticorrelated and drives `S_int` systematically negative. Real data never has that
structure, because treated and vehicle cells are different cells. The null has to reproduce the real
structure or it measures its own construction.

## Recomputation 1: within-context, SciPlex3 (Fig. 5c and the Discussion)

`analysis/predictors/gate1_within_context_interaction.py`, 36 drug-by-cell-line combinations across
K562, A549 and MCF7, same PCA plus k-means split of the control cells, same nearest-subpopulation
assignment of treated cells.

| | value |
|---|---:|
| published statistic, real cells | 0.216 (manuscript quotes 0.205) |
| **effect-size-matched additive null** | **0.379** |
| additive predictor, algebraic | 1.000 |
| fraction of drugs below their own null | 94.4% |
| **gap the manuscript reports** (1.000 - 0.216) | **0.784** |
| **gap that is real** (0.379 - 0.216) | **0.163** |

**79% of the apparent state-specific response in this construct is measurement noise.** The effect
is real, consistent in direction, and about five times smaller than the published framing implies.

The repaired statistic says the same thing: median `S_int` is 1.57e-04 against an additive-null
standard deviation of 4.04e-04, so the typical drug's interaction is **0.39 null standard
deviations**, and `R_int` is 0.045, meaning it barely reproduces across disjoint halves.

## Recomputation 2: patient glioblastoma (Fig. 4d, 4e)

`analysis/natural/zhao_gate1_interaction.py`, 17 patient-drug pairs across 9 patients, same
compartments and same compartment-matched controls.

| | value |
|---|---:|
| published statistic, median | **0.566** (reproduces the published 0.566) |
| **effect-size-matched additive null, median** | **0.955** |
| fraction of pairs below their own null | **100%** |
| gap the manuscript reports (1.000 - 0.566) | 0.434 |
| **gap that is real** (0.955 - 0.566) | **0.389** |
| median `S_int` | 8.96e-03, all positive |
| median `R_int` | **0.875** |
| median interaction share | 0.559 |

**90% of the apparent compartment-specific response in patient tissue is real.** `R_int` of 0.875
means the interaction vector reproduces almost perfectly across disjoint halves of the same cells.

## The contrast this creates, which is better than the claim it replaces

| Setting | published cosine | matched null | real fraction of the gap | `R_int` |
|---|---:|---:|---:|---:|
| SciPlex3, within-context constructed subpopulations | 0.216 | 0.379 | **21%** | 0.045 |
| Tahoe-100M, cell-cycle states, 3,620 conditions | 0.740 | (median permutation z = 3.64) | majority real | 0.169 |
| **Patient glioblastoma, natural compartments** | **0.566** | **0.955** | **90%** | **0.875** |

The differential response that the manuscript's constructed within-context measurement reports is
mostly noise; the one it measures in patient tissue is almost entirely real and highly reproducible.
That is a stronger result than the current text, not a weaker one: it says the phenomenon is a
property of real tissue heterogeneity rather than of a k-means split of a cell line.

## Classification of every use in the codebase

### Class 3, gate terminology, delete

- `analysis/tahoe_pilot/tahoe_gate_pilot.py`, `tahoe_summary_numbers.py`: `induced_cosine_G1_vs_G2M`
  as "Gate 1 differential response". The quantity may stay as a descriptive column; the framing goes.
- Manuscript lines 469 (the three-requirement statement), 479 (Tahoe), 1119 (Methods,
  "Within-context definition of differential response"), 1627.
- Every occurrence of the reading "high `1 - cos` = strong differential response".

### Class 2, stratifier or biological variable, must be replaced

- `analysis/predictors/gate1_within_context.py`: the 0.205 and the 30-combination mean. Replaced by
  recomputation 1 above.
- `analysis/natural/zhao_two_gates.py`, `zhao_threshold_sensitivity.py`: the 0.566. Replaced by
  recomputation 2 above.
- `src/experiments/exp09_structure_diagnostics.py`: `gate1_response_divergence`, which feeds Fig. 5c.
- `figures/ed4/ed4_zhao_robustness.py`, `figures/ed7/ed7_tahoe.py`: axis labels reading
  "differential response".
- Fig. 5g's divergence stratification uses `cross_cos`, a **cross-context** response cosine rather
  than the within-context state cosine. It is a different statistic with a different confound
  profile and is **not** covered by this retirement; it needs its own check.

### Class 1, descriptive, keep and relabel

- The predictor induced-response cosines (1.000, 0.972, 0.900, and the second-reference column
  1.000, 0.190, 0.404, 0.380). For a predictor these are exact algebra with no sampling noise, so
  the confound does not apply. They must be relabelled from "differential response" to **"departure
  from additivity"**, and they must stop being compared directly against the real-cell value, which
  is a noisy estimate on a different footing. The honest comparison for the real cells is against
  the matched null, above.
- `src/baselines/nonadditive_predictors.py` docstrings: descriptive, relabel only.

## Sentences that have to be rewritten, not renumbered

1. Manuscript line 473: "Real treated cells ... produced markedly different response directions,
   with a mean induced-response cosine of 0.205 ... By contrast, the additive average-effect and
   linear-latent predictors returned a cosine of 1.000 by construction." The contrast as written
   attributes 0.795 of gap to biology; 79% of it is noise. The sentence needs the matched null.
2. Manuscript line 469: the three-requirement framework statement. Superseded by
   [P4](P4_BOTTLENECK_DECOMPOSITION.md).
3. Manuscript line 479: the Tahoe median cosine of 0.739 as evidence about differential response
   strength. Replace with the interaction statistic and its permutation null.
4. Manuscript line 517 (Discussion): "reproduce how perturbation effects vary across cellular
   states" is still correct; the magnitude attached to it is not.

## What is not affected

No retrieval result depends on this statistic. It is a stratifier and a diagnostic, never a scorer,
so no ranking, no MRR and no flip count changes. The retirement is a claim-level repair, not a
numerical one, except for the two recomputed values above.
