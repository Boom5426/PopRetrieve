# 07. Gate 3: decision relevance, read off the retrieval itself

From [`analysis/phase2_transition/phase_d_synthesis.py`](../../analysis/phase2_transition/phase_d_synthesis.py);
table in `results/phase2_transition/synthesis/gate3_decision_relevance.csv`.

Plan section 12 requires decision relevance to stop being a state-ordering correlation and become
the retrieval outcome itself. Holding the predictor fixed, for every (context, query drug, seed):

    delta_rank        rank under the mean route minus rank under the population route;
                      positive means population information moved the true drug forward
    Flip@1            the two routes name a different top-1 candidate
    CorrectedFlip@1   the population route's top-1 is the true drug and the mean route's is not
    ReverseFlip@1     the reverse

`ReverseFlip@1` is not in the plan. It is reported because `CorrectedFlip@1` alone is not
interpretable: a rule that reshuffles the top of the ranking at random produces corrected flips in
proportion to how often it flips at all, and only the balance against reverse flips says whether the
reshuffling was informative.

## Against the mean route (`energy` vs `mean_cosine`)

| Phase | Predictor | Δrank [95% CI] | Flip@1 | CorrectedFlip@1 | ReverseFlip@1 | Ratio |
|---|---|---|---:|---:|---:|---:|
| oracle | observed responses | **+0.210 [+0.115, +0.333]** | 0.083 | **0.0556** | 0.0108 | **5.2 : 1** |
| predicted | `average_effect` | -0.979 [-1.872, -0.325] | 0.157 | 0.0332 | 0.0748 | 0.44 : 1 |
| predicted | `linear_latent` | -0.980 [-1.880, -0.317] | 0.165 | 0.0369 | 0.0758 | 0.49 : 1 |
| predicted | `nearest_context` | -12.46 [-15.04, -9.78] | 0.667 | 0.0389 | 0.3582 | 0.11 : 1 |
| predicted | `nearest_context_cells` | -12.50 [-14.82, -10.16] | 0.690 | 0.0334 | 0.3747 | 0.09 : 1 |
| predicted | `ot_map` | -0.410 [-1.428, +0.391] | 0.340 | 0.0893 | 0.0864 | 1.03 : 1 |

## Against magnitude-aware mean matching (`energy` vs `mean_l2`)

| Phase | Predictor | Δrank [95% CI] | Flip@1 | CorrectedFlip@1 | ReverseFlip@1 | Ratio |
|---|---|---|---:|---:|---:|---:|
| oracle | observed responses | +0.079 [+0.039, +0.126] | 0.032 | 0.0198 | 0.0049 | 4.0 : 1 |
| predicted | `average_effect` | -0.077 [-0.150, -0.019] | 0.019 | 0.0050 | 0.0068 | 0.73 : 1 |
| predicted | `linear_latent` | -0.078 [-0.152, -0.019] | 0.021 | 0.0057 | 0.0068 | 0.84 : 1 |
| predicted | `nearest_context` | -0.202 [-0.255, -0.148] | 0.031 | 0.0028 | 0.0063 | 0.45 : 1 |
| predicted | `nearest_context_cells` | -0.409 [-1.009, +0.136] | 0.383 | 0.0405 | 0.0775 | 0.52 : 1 |
| predicted | **`ot_map`** | **+0.099 [+0.052, +0.145]** | 0.077 | **0.0260** | 0.0122 | **2.1 : 1** |

## What this says

**With observed candidate responses, decision relevance is real and small.** Population information
corrects a wrong top-1 decision in 5.6% of rankings and breaks a right one in 1.1%, a 5.2-to-one
ratio, with a mean forward movement of 0.21 rank positions out of 92. Measured against magnitude-
aware mean matching instead of cosine, both numbers fall by roughly two thirds and the ratio holds
at 4.0 to one. This is the first time in this project that decision relevance has been measured as
a decision rather than as a correlation, and it survives that change of measurement, at a third of
the size the cosine comparison suggests.

**With predicted candidate responses, decision relevance inverts for every additive predictor.**
`average_effect` flips the top-1 in 15.7% of rankings, and those flips break more correct decisions
(7.5%) than they fix (3.3%). A distributional score applied to an additively predicted population is
not neutral, it is actively harmful, because it reads a magnitude and a shape that the predictor
never had any basis to produce.

**`ot_map` is the single case where a predicted population supports decision relevance**, and only
against the magnitude-aware reference: +0.099 rank positions [+0.052, +0.145], corrected flips
outnumbering reverse flips 2.1 to 1. Against plain cosine it is a wash (1.03 to 1). Its absolute
retrieval quality remains a quarter below `average_effect`'s, so this is a positive signal inside a
system that is not competitive, not a working method.

## The honest summary of Gate 3

Decision relevance exists at the oracle, at about a fifth of a rank position and a 5.2-to-one flip
ratio. After leakage-safe prediction it is absent for the predictors that rank well and present only
for the one that ranks poorly. On this evidence Gate 3 is not the binding constraint at the oracle;
it becomes binding only after prediction, and it becomes binding through the forward model.
