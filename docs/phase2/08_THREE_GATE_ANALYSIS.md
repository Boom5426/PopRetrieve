# 08. The three gates together

From `results/phase2_transition/synthesis/three_gate_grid.csv` and `per_query_joined.csv`.

Plan section 13 refuses to let the three gates be drawn separately and stop there. It fixes the
analysis in advance: differential response D on one axis, supervised recoverability `A_sup` on the
other, pre-specified quartiles, no threshold searched after seeing an outcome. The prediction under
test is its own:

> population gain should concentrate in queries where differential response is strong and
> recoverability is high.

3,620 queries carry both gates.

## The grid, with oracle population gain in each cell

`dMRR` is `energy` minus `mean_cosine`, averaged over the five seeds of each query.

| | A_sup Q1 (lowest) | A_sup Q2 | A_sup Q3 | A_sup Q4 (highest) |
|---|---:|---:|---:|---:|
| **D Q4 (highest)** | **+0.0851** (n=545) | +0.0308 (n=277) | -0.0009 (n=78) | **0.0000 (n=5)** |
| **D Q3** | +0.0752 (n=263) | +0.0299 (n=347) | +0.0138 (n=239) | +0.0018 (n=56) |
| **D Q2** | +0.0405 (n=101) | +0.0308 (n=228) | +0.0044 (n=353) | +0.0019 (n=223) |
| **D Q1 (lowest)** | +0.1425 (n=4) | +0.0453 (n=51) | +0.0110 (n=229) | +0.0026 (n=621) |

## The framework's own prediction fails

The predicted "population-benefit candidate regime" is the top-right cell: strong differential
response, high recoverability. **It contains 5 of 3,620 queries and its population gain is exactly
zero.** The cell next to it, D Q4 and A_sup Q3, holds 78 queries and its gain is -0.0009.

The gain is instead monotone in the *opposite* direction along the recoverability axis. Marginally:

| `A_sup` quartile | n | Oracle `mean_cosine` MRR | Oracle ΔMRR | `average_effect` ΔMRR | `ot_map` ΔMRR |
|---|---:|---:|---:|---:|---:|
| Q1 lowest | 913 | 0.8423 | **+0.0776** | -0.0229 | +0.0562 |
| Q2 | 903 | 0.9548 | +0.0313 | -0.0350 | +0.0274 |
| Q3 | 899 | 0.9885 | +0.0081 | -0.0556 | -0.0275 |
| Q4 highest | 905 | 0.9970 | +0.0024 | -0.0265 | -0.0329 |

Along the D axis the framework's direction does hold:

| D quartile | n | Oracle `mean_cosine` MRR | Oracle ΔMRR | `average_effect` ΔMRR | `ot_map` ΔMRR |
|---|---:|---:|---:|---:|---:|
| Q1 lowest | 905 | 0.9902 | +0.0078 | -0.0101 | -0.0078 |
| Q2 | 905 | 0.9773 | +0.0145 | -0.0265 | -0.0057 |
| Q3 | 905 | 0.9387 | +0.0371 | -0.0444 | +0.0153 |
| Q4 highest | 905 | 0.8753 | **+0.0606** | -0.0588 | +0.0221 |

## Why the two axes point in opposite directions, and what actually drives the gain

The two gates are not independent on this material. Spearman(D, `A_sup`) = **-0.760**. Both are
being driven by effect size, in opposite directions: a strong drug produces large, reliable state
responses that a probe separates easily (high `A_sup`) and whose cosine is high (low D), while a weak
drug produces small noisy responses that a probe cannot separate (low `A_sup`) and whose cosine is
low (high D). That is why the framework's own corner is nearly empty: strong differential response
and high recoverability almost never co-occur here.

Correlating the per-query oracle gain against three candidate explanations:

| Candidate explanation | Spearman with per-query oracle ΔMRR |
|---|---:|
| Headroom left by the mean route, `1 - MRR_mean_cosine` | +0.790 |
| Differential response D | +0.225 |
| Supervised recoverability `A_sup` | -0.320 |

> **Correction, 2026-09-02.** This section originally read the headroom correlation as the strongest
> single explanation of where population scoring pays. It is not an explanation at all. `H` and the
> gain share the term `MRR_mean` with opposite signs, and reciprocal rank is capped at 1, so a gain
> is arithmetically impossible where the mean route is already perfect. A null that reshuffles the
> population route's reciprocal ranks within each context, keeping both marginals and the ceiling,
> produces +0.786 [+0.767, +0.805]: the observed +0.790 lies inside it. The correct analysis
> conditions on the mean route's performance instead of subtracting it, and is in
> [P4](P4_BOTTLENECK_DECOMPOSITION.md). What survives from this paragraph is the ceiling fact
> itself: **3,110 of 3,992 queries have exactly zero headroom**, because the oracle mean route
> already ranks the true drug first at every seed. That is why so little is available to win.

Where the mean route already ranks the true drug first (its MRR is 0.997 in the top recoverability
quartile) there is nothing left to gain, and the population route gains nothing. Where the mean
route struggles (MRR 0.842 in the bottom quartile) the population route recovers part of the gap.
The grid's apparent dependence on D and on `A_sup` runs through that ceiling.

## What this means for the three-condition framework

The plan wrote the honest branch in advance: *if the bottom-right corner still shows no retrieval
gain, the three-condition framework needs revision and must not be forced into a positive reading.*
That is the branch the data took.

The framework is not refuted as a set of *necessary* conditions. Nothing here shows that a query
with no differential response can benefit from population scoring. What fails is its use as a
*locator*: the conditions do not identify where the benefit is, because on real material the two
measurable ones are strongly anti-correlated and both are proxies for effect size, while the actual
determinant of gain is how much the incumbent mean scorer has already got right.

Two consequences follow for the manuscript.

1. **`1 - cos` is the wrong operationalisation of differential response.** It is confounded with
   effect size and with cell count (Spearman -0.584 and -0.529, [05](05_DIFFERENTIAL_RESPONSE_AUDIT.md)).
   A version that is not a signal-to-noise measure in disguise is needed before D can be used to
   select queries.
2. **Whether the incumbent already decides correctly belongs in the framework as an explicit
   condition.** It is a property of the incumbent method, not of the biology, and on this benchmark
   it removes 78% of the queries from contention before any biology is consulted. A framework that
   omits it will keep pointing at queries where nothing can be won. Note that this is a ceiling
   constraint, not a predictor: see the correction above and
   [P4](P4_BOTTLENECK_DECOMPOSITION.md).
