# 10. Final verdict

Plan section 17 allows this document to answer four questions and nothing else. Every number below
is derived in documents [02](02_DATA_ELIGIBILITY_AUDIT.md) to [09](09_ORACLE_TO_PREDICTION_DECOMPOSITION.md)
and reproducible from `results/phase2_transition/`.

Benchmark: Tahoe-100M plate 3, 44 held-out cell lines, a fixed 92-compound candidate library, 3,992
eligible queries, 5 seeds, leave-one-cell-line-out. Intervals are context-clustered bootstrap.

---

## 1. With candidate outcomes known perfectly, does population information improve source-to-target intervention retrieval?

**Yes, and by about a twentieth of the available headroom.**

Energy-distance retrieval reaches MRR 0.9755 [0.9659, 0.9839] against the mean route's 0.9452
[0.9267, 0.9611], a gain of +0.0303 [+0.0225, +0.0398], in the same direction in 44 of 44 contexts.

Two qualifications are part of the answer, not footnotes to it.

- **Two thirds of that gain is magnitude.** A mean-only scorer that compares the same mean
  signatures by Euclidean distance instead of cosine recovers +0.0201 of the +0.0303. The genuinely
  distributional residue is +0.0102 [+0.0065, +0.0145].
- **Under the manuscript's own estimator the residue vanishes.** With the V-statistic energy
  distance that `src/retrieval/metrics.py` implements, the population route beats magnitude-aware
  mean matching by +0.0006 [-0.0019, +0.0028].

As a decision: population information corrects a wrong top-1 in 5.6% of rankings and breaks a
correct one in 1.1%, a 5.2-to-one ratio.

## 2. After leakage-safe forward prediction, how much of that advantage survives?

**None of it. It reverses.**

| | Mean route | Population route |
|---|---:|---:|
| Oracle | 0.9452 | 0.9755 |
| Best predictor (`average_effect`) | **0.8876** | 0.8520 |

Deleting every observed candidate response in the held-out cell line costs the mean route 0.058 MRR
and the population route 0.124. Within the predictor, the population route is worse than the mean
route by -0.0356 MRR [-0.0620, -0.0115]. The same reversal holds for `linear_latent` and, at ten
times the amplitude, for both nearest-context predictors. The retained fraction of the oracle gain
is negative for all four.

The one exception is the only non-additive predictor. `ot_map` is the sole case where the population
route is not worse than its own mean route (+0.0027 [-0.0215, +0.0243]) and the sole case where it
beats magnitude-aware mean matching (+0.0110 [+0.0087, +0.0134]). Its absolute MRR is 0.665, a
quarter below `average_effect`'s, so no population-route system beats the best mean-route system at
any point in this benchmark.

**The best transition-retrieval system measured here is the context-averaged effect scored by mean
cosine: MRR 0.888, Hit@1 0.833, over 92 candidates, with no observed response from the held-out cell
line.**

## 3. Is the loss in differential response, recoverability, or decision relevance?

**Chiefly in decision relevance, then in the forward predictor. Recoverability is not the binding
constraint.**

- **Decision relevance is the largest term.** For 77% of queries the oracle population route and the
  oracle mean route return the same reciprocal rank, and for 81% the population route gains nothing
  at all, because the mean route already ranks the true drug first. The single
  strongest predictor of where a gain exists is not a biological gate at all: it is the headroom the
  incumbent scorer leaves, Spearman +0.783 against the per-query gain, versus +0.225 for differential
  response and -0.320 for recoverability.
- **The forward predictor destroys the remainder.** 546 of 3,992 queries have an oracle gain that
  `average_effect` fails to deliver, against 209 it delivers. Worse, the failure is not passive: no
  additive predictor produces any differential response at all (measured, exactly zero for 100% of
  3,581 drugs), so the population it hands the scorer has the vehicle's shape and a magnitude
  averaged over other cell lines. The distributional score then reads that fabricated shape as
  evidence.
- **Recoverability is high wherever it matters.** A linear probe separates treated from vehicle cells
  at 0.80 median accuracy, and above 0.8 for half of all queries, while k-means on the same cells
  sits at 0.555. The regime is overwhelmingly algorithm-limited, not information-limited.

## 4. Is there a reproducible, real population-sensitive intervention regime?

**Not one that the three-condition framework locates, and not one that beats the mean route.**

The framework predicts that benefit concentrates where differential response is strong and
recoverability is high. That cell of the pre-specified quartile grid holds **5 of 3,620 queries and
its population gain is exactly 0.0000**. The cell beside it holds 78 and gains -0.0009. The gain runs
in the opposite direction along the recoverability axis: +0.0776 in the lowest quartile, +0.0024 in
the highest.

The reason is that the two measurable gates are not independent on real material. Spearman(D,
`A_sup`) = -0.760, because both are driven by effect size in opposite directions, and because
`1 - cos` is confounded with effect size (-0.584) and with cell count (-0.529). A weak drug looks
differentially responding.

Rebuilding the statistic did not rescue the framework. A cross-fitted drug-by-state interaction that
passes five pre-specified checks and detects a constructed positive control at seven times the
endogenous level ([P3](P3_INTERACTION_STATISTIC.md)) still does not predict population gain once the
mean route's own performance is conditioned on: beta = +0.0011 [-0.0011, +0.0032], p = 0.33, and
negative when magnitude is controlled ([P4](P4_BOTTLENECK_DECOMPOSITION.md)). The one gate that does
point in the predicted direction is recoverability, at beta = +0.0084 [+0.0052, +0.0116].

What does reproduce is narrower and it is honest to state it as such: **at the oracle, distributional
retrieval adds +0.0102 MRR beyond magnitude-aware mean matching**, consistently across 44 contexts.
It is not localised by any biological gate measured here. After prediction, only a cell-dependent
transport map preserves any of it, and that map is not competitive in absolute terms.

---

## What follows, under the plan's own stopping rule

Plan section 15 defines three branches. The data fits none of them exactly, because it anticipated
that a predictor might lose the oracle gain but not that a predictor would invert it. The nearest
branch is Case B, prediction is the bottleneck, and the section's instruction there is that a
stronger non-additive predictor branch may open with the task unchanged. Three things qualify that
before anyone opens it.

1. **The prize is small and it is bounded.** The oracle leaves 0.055 MRR of total headroom above the
   mean route, of which 0.020 is magnitude and 0.010 is distributional. A perfect forward model
   scored distributionally cannot beat 0.9755, and the mean route already reaches 0.8876 without one.
2. **The next predictor must be measured on Gate 1 before it is measured on retrieval.** Every
   additive model produces exactly zero differential response, so it cannot pass. `ot_map`
   under-predicts the observed differential response 6.7-fold; `nearest_context_cells` over-predicts
   it 2.6-fold. Differential-response fidelity is the cheap decisive test and it should gate entry to
   the retrieval comparison, not follow it.
3. **Two measurement instruments need repair first.** The V-statistic energy distance is biased at
   unequal sample sizes and erases the entire distributional residue; the U-statistic form should
   replace it wherever this project scores populations of different sizes. And `1 - cos` should be
   replaced by a differential-response statistic that is not a signal-to-noise measure in disguise.

## What was not run, and why

- **SciPlex3 replication** (plan section 2). Not run. It is a legitimate replication of the task
  definition but it carries three cell lines, so leave-one-cell-line-out trains on two contexts and
  the context-clustered bootstrap has three clusters. It would not test the conclusions above at a
  useful resolution and it is not what the ten required documents are about.
- **`MoA-nDCG@10`** (plan section 11). Blocked, not skipped: plate 3's `obs` carries no MoA or target
  annotation, so the metric cannot be computed from the released file. It needs an external
  annotation with recorded provenance. The primary and secondary exact metrics are unaffected.
- **A 100-cell vehicle floor sensitivity** (freeze section 6). Pre-registered and not yet run; it
  would add 4 contexts and 147 queries. None of the conclusions above is close enough to a boundary
  for it to matter, so it is deferred rather than treated as a live alternative.
