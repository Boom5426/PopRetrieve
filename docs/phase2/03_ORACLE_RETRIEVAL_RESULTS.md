# 03. Phase A: the oracle response-bank ceiling

Produced by [`analysis/phase2_transition/phase_a_oracle.py`](../../analysis/phase2_transition/phase_a_oracle.py)
on Tahoe-100M plate 3. Tables in `results/phase2_transition/phase_a/`.

**This is an information ceiling, not a deployment result.** Every candidate's response in the
held-out context is the observed one, taken from a library-prep half that shares no cell with the
query. No deployed system has that. Phase B removes it.

Scale: 44 contexts, 92 candidates, 3,992 eligible queries, 5 seeds, 19,960 scored rankings, 183
seconds on one RTX 4090. Candidate banks were 100 cells; 6.3% of the 20,240 bank slots had fewer
because the condition is small, and none had to fall back to using both halves.

## The headline

| Scorer | Route | MRR [95% CI] | Hit@1 | Hit@5 | Hit@10 |
|---|---|---|---|---|---|
| `mean_cosine` | mean | 0.9452 [0.9267, 0.9611] | 0.9156 | 0.9821 | 0.9924 |
| `mean_l2` | mean, diagnostic | 0.9653 [0.9517, 0.9770] | 0.9454 | 0.9891 | 0.9957 |
| **`energy`** | **population, primary** | **0.9755 [0.9659, 0.9839]** | **0.9604** | 0.9944 | 0.9982 |
| `energy_v_statistic` | population, manuscript estimator | 0.9659 [0.9516, 0.9789] | 0.9478 | 0.9881 | 0.9940 |
| `mmd` | population, secondary | 0.9754 [0.9658, 0.9838] | 0.9600 | 0.9942 | 0.9981 |
| `sliced_wasserstein` | population, secondary | 0.9222 [0.9023, 0.9402] | 0.8825 | 0.9741 | 0.9891 |

Intervals are percentile bootstrap over 2,000 replicates resampling whole cell lines, because
queries inside one context share a source population and an entire candidate bank and are not
independent.

**The answer to the Phase A question is yes, and it is small.** Population information improves
intervention selection when candidate outcomes are known perfectly: energy beats the mean route by
+0.0303 MRR [+0.0225, +0.0398] and +0.0448 Hit@1 [+0.0350, +0.0562], in the same direction in 44 of
44 contexts.

## Two thirds of that gain is magnitude, not population structure

The plan's mean route is the cosine of mean signatures, which discards response magnitude. The
energy distance does not. `mean_l2` is the same mean signatures compared by Euclidean distance: it
keeps magnitude and keeps nothing else about the population.

| Comparison | ΔMRR [95% CI] | ΔHit@1 [95% CI] |
|---|---|---|
| `energy` vs `mean_cosine` | +0.0303 [+0.0225, +0.0398] | +0.0448 [+0.0350, +0.0562] |
| `mean_l2` vs `mean_cosine` | +0.0201 [+0.0149, +0.0264] | +0.0299 [+0.0232, +0.0376] |
| **`energy` vs `mean_l2`** | **+0.0102 [+0.0065, +0.0145]** | **+0.0149 [+0.0100, +0.0207]** |
| `energy_v_statistic` vs `mean_l2` | +0.0006 [-0.0019, +0.0028] | +0.0024 [-0.0004, +0.0050] |

**66% of the population route's apparent advantage over the incumbent is recovered by a mean-only
scorer that keeps magnitude.** The genuinely distributional part is +0.0102 MRR. Its interval
excludes zero and it holds in 42 of 44 contexts, so it is real, but it is one third of the headline
number and must never be quoted as the whole of it.

The last row is sharper. Scored with the V-statistic energy distance, which is what
`src/retrieval/metrics.py` implements and therefore what the manuscript's numbers rest on, **the
population route has no measurable advantage over magnitude-aware mean matching at all**. The
U-statistic is unbiased at unequal sample sizes and the V-statistic is not; the 6.3% of banks
smaller than 100 cells are enough for that difference to consume the entire residual effect. This
is a property of the estimator, not of the biology.

## Where the gain is, and where it is not

- Rankings agree for 91.2% of query-seeds. The population route moves the true drug forward in
  7.3% and backward in 1.5%, mean Δrank +0.210 [+0.115, +0.333].
- Per query drug: 175 go from failing under `mean_cosine` to succeeding under `energy`, and 10 go
  the other way. Against `mean_l2` the counts are 72 and 5.
- 47 of 3,992 query drugs fail under both, so the residual hard set is small.
- Split by query size: at most 100 target cells (n = 1,078) gives MRRs of `mean_cosine` 0.889,
  `mean_l2` 0.854, `energy` 0.939; above 100 cells (n = 18,882) they are 0.948, 0.972, 0.978. The
  magnitude shortcut is what fails on small queries, because a mean estimated from few cells has an
  unreliable norm, while the full population comparison degrades much less.
- Sliced Wasserstein is worse than the mean route by -0.0230 MRR. "Population information helps" is
  not a property of distributional scoring in general: it is a property of the energy distance and
  of MMD, which behave almost identically here.

## Reading this against the plan's stopping rule

Plan section 15 asks whether the oracle population route shows a material gain. It does, so the
project does not stop at Case A. But the size of it sets a hard budget for everything downstream.
The mean route already reaches 0.945 MRR with perfect candidate outcomes, leaving 0.055 of headroom
in total, of which a predictor-free magnitude scorer takes 0.020 and genuine population structure
0.010. **Phase B cannot recover more than this, and any predicted-response result that appears to
exceed it should be treated as an artefact until explained.**

## Caveats that belong with these numbers

1. The absolute performance is high because the oracle task is close to matching a population to a
   held-out half of itself. That is what an oracle ceiling is, and it is why the number is a ceiling
   rather than a performance claim.
2. `MoA-nDCG@10` is not reported: plate 3 carries no MoA annotation. See
   [01](01_TRANSITION_TASK_FREEZE.md) section 12.
3. `mean_l2` is a diagnostic that decomposes the gap between the two frozen routes. It is not a
   third route, and the frozen comparison is unchanged.
