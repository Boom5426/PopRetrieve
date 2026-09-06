# P4. Population-to-decision bottleneck decomposition

From [`analysis/phase2_transition/phase_e_bottleneck.py`](../../analysis/phase2_transition/phase_e_bottleneck.py);
tables in `results/phase2_transition/bottleneck/`.

This replaces the three-gate confirmation analysis and asks the sharper question:

> after controlling for how well the mean route already does, does a repaired, reproducible
> drug-by-state interaction explain population-specific decision gain?

Four quantities per query, on the 3,992 oracle queries:

| | | |
|---|---|---|
| `H` | headroom, `1 - RR_mean_cosine` | a property of the incumbent scorer |
| `interaction_share`, `S_int`, `R_int` | [P3](P3_INTERACTION_STATISTIC.md) | the repaired Gate 1 |
| `A_sup` | supervised recoverability | Gate 2, unchanged |
| `G` | `RR_population - RR_reference` | the decision gain |

## First, a correction to the headroom result

[08](08_THREE_GATE_ANALYSIS.md) reported Spearman(headroom, gain) = +0.783 and read it as the
strongest single explanation of where population scoring pays. **That reading was wrong, and this
document supersedes it.**

`H = 1 - RR_mean` and `G = RR_pop - RR_mean` share the term `RR_mean` with opposite signs, and `RR`
is capped at 1, so a positive gain is arithmetically impossible where the mean route is already
perfect. Both facts push the correlation up without any biology.

The null that measures how much: reshuffle the population route's reciprocal ranks **within each
context**, which destroys any real link between the two scorers while keeping both marginal
distributions, the ceiling and the clustering.

| | Spearman(H, G) |
|---|---:|
| observed | +0.790 |
| null, 200 within-context reshuffles | +0.786, 95% band [+0.767, +0.805] |

**The observed value sits inside the null band.** The headroom correlation carries essentially no
information. What it does record, correctly, is a ceiling fact: **3,110 of 3,992 queries have
exactly zero headroom**, because the oracle mean route already ranks the true drug first at every
seed. That is a real and important statement about the benchmark. It is not a discovered
relationship, and [08](08_THREE_GATE_ANALYSIS.md) and [10](10_FINAL_VERDICT.md) have been amended.

## The specification that is not a tautology

Regress the population route's own performance on the mean route's performance plus the candidate
explanators. The coefficient on a predictor then answers: given how well the mean route did, does
this variable predict how well the population route does? Ordinary least squares, predictors
standardised, cluster-robust standard errors at the cell line.

### Outcome: `RR_energy`, covariate `RR_mean_cosine` (n = 3,618; 44 clusters)

| Model | Term | β | 95% CI | p | R² |
|---|---|---:|---|---:|---:|
| mean route only | `RR_mean_cosine` | 0.0540 | [0.0487, 0.0593] | <1e-4 | 0.508 |
| plus interaction share | `interaction_share` | **0.0005** | [-0.0021, +0.0031] | 0.72 | 0.493 |
| plus recoverability | `interaction_share` | **0.0011** | [-0.0011, +0.0032] | 0.33 | 0.503 |
| | `A_sup` | **0.0084** | [+0.0052, +0.0116] | <1e-4 | |
| plus reproducibility | `R_int` | -0.0011 | [-0.0029, +0.0006] | 0.21 | 0.503 |
| the old statistic | `D_old` | **-0.0096** | [-0.0167, -0.0024] | 0.0087 | 0.516 |

### Magnitude-controlled: outcome `RR_energy`, covariate `RR_mean_l2`

| Term | β | 95% CI | p |
|---|---:|---|---:|
| `RR_mean_l2` | 0.0622 | [0.0577, 0.0667] | <1e-4 |
| `interaction_share` | **-0.0027** | [-0.0043, -0.0012] | 0.0006 |
| `A_sup` | **0.0033** | [+0.0013, +0.0054] | 0.0016 |

## What this says

**1. The repaired interaction does not locate population benefit.** `interaction_share` is
indistinguishable from zero in the headline specification (β = 0.0011, p = 0.33) and **negative**
once magnitude is controlled for (β = -0.0027, p = 0.0006). Adding it to a model that already knows
the mean route's performance moves R² by 0.001. `S_int` and `R_int` behave the same way. This is not
a power problem: 3,618 queries across 44 clustered contexts, with a statistic that passes five
pre-specified checks and detects a constructed positive control at seven times the endogenous level.

The interaction is real ([P3](P3_INTERACTION_STATISTIC.md): median permutation z = 3.64) and it does
not predict where distributional retrieval wins. Those are compatible: the interaction is small,
about a seventh of a constructed one, and the retrieval decision is dominated by whether the mean
signature already points at the right drug.

**2. The old statistic pointed the wrong way, and its apparent usefulness was borrowed.** `D_old`
enters the conditional model at **-0.0096** [-0.0167, -0.0024]. Its positive marginal correlation
with gain (+0.254) was mediated entirely by effect size: weak drugs score high on `D_old`, weak
drugs are the ones the mean route ranks badly, and the ceiling does the rest. Conditioning on the
mean route's performance reverses the sign. Any claim in the manuscript that high differential
response marks where population scoring helps rests on that mediation.

**3. Recoverability survives as the one positive locator.** `A_sup` is the only variable with a
positive, interval-excludes-zero coefficient in both specifications (+0.0084 headline, +0.0033
magnitude-controlled). It is small: a one standard deviation rise in supervised recoverability buys
0.008 of reciprocal rank. But it is the only one of the three gates that points where the framework
said it would.

## The revised bottleneck statement

The old chain was `differential response -> recoverability -> decision relevance`. On this evidence:

- **Differential response**, however it is measured, does not gate the benefit. The discredited
  version anti-predicts it; the repaired version does not predict it at all.
- **Recoverability** does, weakly and in the predicted direction.
- **Decision relevance** is where almost everything is lost, and the loss is not subtle: on 78% of
  queries the oracle mean route is already perfect, so there is no decision left to improve.
- **Faithful forward prediction** is the second loss, and it is a reversal rather than an
  attenuation ([09](09_ORACLE_TO_PREDICTION_DECOMPOSITION.md)).

The honest four-term chain the evidence supports is therefore

> **does the incumbent already decide correctly** -> **is the drug's effect recoverable in single
> cells** -> **does the forward model predict a population rather than inherit one** -> **does the
> decision change for the better**

with the first term dominant and the first term being a property of the baseline, not of the
biology. Whether a "population-specific signal" term belongs in front of it is exactly what this
document could not confirm: the signal exists and does not reach the decision.
