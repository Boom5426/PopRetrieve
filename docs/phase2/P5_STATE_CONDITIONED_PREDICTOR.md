# P5. The one permitted non-additive predictor

`state_conditioned_average_effect`, implemented in
[`analysis/phase2_transition/phase_b_loco.py`](../../analysis/phase2_transition/phase_b_loco.py).
Results in `results/phase2_transition/phase_b_p5/`.

## What it is

The average-effect baseline estimated separately per cell-cycle state:

    delta_{d,s} = mean over the 43 training contexts of ( mu_{d,c',s} - mu_{0,c',s} )
    x_hat_i     = x_i + delta_{d, s(i)}

Each source cell is shifted by its own state's signature. It is the cheapest possible departure
from additivity: one extra grouping, no fitting, no new hyperparameter, and the same leave-one-cell-
line-out rule as every other predictor. A (line, drug, state) group with fewer than 20 cells is not
estimated and the pooled signature is used there instead; 11,916 of 12,275 groups clear that floor.

It is also the first predictor in this project that **can** produce a non-zero differential response
at all. The three additive ones produce exactly zero by construction ([05](05_DIFFERENTIAL_RESPONSE_AUDIT.md)).

## The two pre-frozen entry conditions

Both were fixed before the predictor was run.

### Condition 1: interaction fidelity, rho > 0 with a context-bootstrap CI excluding zero

Measured like for like: the predictor's own interaction magnitude `||r_1 - r_2||^2 / p` against the
observed cross-fitted `S_int` ([P3](P3_INTERACTION_STATISTIC.md)), 3,581 queries, 43 clusters.

| Predictor | rho | 95% CI | verdict |
|---|---:|---|---|
| **`state_conditioned_average_effect`** | **+0.606** | [+0.576, +0.639] | **pass** |
| `ot_map` | +0.571 | [+0.514, +0.626] | pass |
| `average_effect` | +0.076 | [-0.041, +0.194] | null, as it must be |

Calibration, on the scale-free share:

| Predictor | median predicted `S_int` | observed | median predicted share | observed share |
|---|---:|---:|---:|---:|
| `state_conditioned_average_effect` | 3.84e-05 | 1.38e-04 | **0.164** | **0.170** |
| `ot_map` | 9.16e-06 | 1.38e-04 | 0.078 | 0.170 |

The state-conditioned predictor under-predicts the absolute interaction 3.6-fold and gets the
**fraction** of the response that is state-dependent almost exactly right, 0.164 against 0.170.
`ot_map` under-predicts the magnitude 15-fold and the share 2.2-fold.

> **A first attempt at this test gave the opposite answer and was wrong.** Correlating the
> predictor's `1 - cos(r_1, r_2)` against the observed `S_int` returned rho = -0.259
> [-0.288, -0.229]. That comparison puts a cosine against a magnitude: a drug with a large, direction-
> consistent effect has a small `1 - cos` and a large `S_int`, so the two are anti-correlated for
> structural reasons that have nothing to do with fidelity. It is the same confound that retired the
> old Gate 1, reappearing one level up in the analysis. The like-for-like test above replaced it.

### Condition 2: the mean route must not degrade by more than 5% relative

Floor: MRR >= 0.843, from `average_effect`'s 0.8876.

| Predictor | mean-route MRR | verdict |
|---|---:|---|
| `state_conditioned_average_effect` | **0.8883** | **pass**, and marginally above the baseline |

## Retrieval result, 44 contexts, 92 candidates, 3,992 queries, 5 seeds

| Predictor | `mean_cosine` MRR | `energy` MRR | `energy` minus `mean_cosine` |
|---|---:|---:|---|
| `average_effect` | 0.8876 [0.8645, 0.9108] | 0.8520 | -0.0356 [-0.0620, -0.0115] |
| **`state_conditioned_average_effect`** | **0.8883 [0.8667, 0.9106]** | **0.8569** | **-0.0314 [-0.0584, -0.0076]** |
| `ot_map` | 0.6647 | 0.6674 | +0.0027 [-0.0215, +0.0243] |

Conditioning the average effect on cell-cycle state:

- raises the population route by **+0.0049 MRR** (0.8520 to 0.8569);
- raises the mean route by +0.0007, so it costs nothing;
- narrows the population route's deficit from -0.0356 to -0.0314, and **does not close it**: the
  interval still excludes zero.

## What this settles

**The predictor passes both gates and the gap survives.** A forward model that predicts the
drug-by-state interaction at rank correlation +0.61 and gets the interaction share calibrated to
within 4% still leaves distributional retrieval behind magnitude-aware mean matching on the same
predictions. Two thirds of the interaction magnitude is still missing (3.6-fold under-prediction),
so the door is not closed; but the +0.0049 that the first honest step towards non-additivity buys
should be measured against the -0.0314 that remains, and against the 0.0102 total that the oracle
says is available beyond magnitude in the first place ([03](03_ORACLE_RETRIEVAL_RESULTS.md)).

Phase 6, a cell-dependent residual predictor `x_hat_i = x_i + f(x_i, d)`, is the decision this
result hands back. It is not started.
