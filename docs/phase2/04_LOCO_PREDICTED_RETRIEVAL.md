# 04. Phase B: leave-one-cell-line-out predict-then-retrieve

Produced by [`analysis/phase2_transition/phase_b_loco.py`](../../analysis/phase2_transition/phase_b_loco.py).
Tables in `results/phase2_transition/phase_b/`.

Phase A gave every candidate its observed response in the held-out context. Phase B deletes all of
them. For each held-out cell line, a predictor is fitted on the other 43 usable contexts only, then
asked to imagine each of the 92 candidates' response in that line from its vehicle cells alone. The
retrieval rules, the query cells, the source cells and the sublibrary split are identical to Phase
A, because both phases draw them from generators keyed by purpose rather than by call order. The two
phases are therefore paired query by query.

Scale: 44 held-out contexts x 92 candidates x 3,992 queries x 5 seeds x 5 predictors, 688 seconds.

## Absolute performance, which the plan requires to be reported alongside any difference

| Predictor | `mean_cosine` MRR [95% CI] | `energy` MRR [95% CI] | `mean_cosine` Hit@1 | `energy` Hit@1 |
|---|---|---|---|---|
| **`average_effect`** | **0.8876 [0.8645, 0.9108]** | 0.8520 [0.8092, 0.8903] | **0.8329** | 0.7912 |
| `linear_latent` | 0.8766 [0.8526, 0.9012] | 0.8425 [0.7989, 0.8820] | 0.8175 | 0.7787 |
| `nearest_context` | 0.7274 [0.6836, 0.7708] | 0.4115 [0.3574, 0.4694] | 0.6234 | 0.3042 |
| `nearest_context_cells` | 0.7084 [0.6638, 0.7526] | 0.3686 [0.3229, 0.4200] | 0.5983 | 0.2570 |
| `ot_map` | 0.6647 [0.6292, 0.7011] | 0.6674 [0.6208, 0.7119] | 0.5398 | 0.5427 |

Two facts before any comparison of routes.

**Prediction is cheap on the mean route.** The best predictor, the plain context-averaged effect,
reaches 0.888 MRR against the oracle's 0.945. Deleting every observed candidate response in the
held-out cell line costs the mean route 0.058 MRR. A drug's average response over 43 other cell
lines is very nearly as good a query key as its observed response in the target line, which is a
direct measurement of how transferable mean signatures are.

**Prediction is expensive on the population route.** The same deletion costs the energy route
0.124 MRR, twice as much, and the ordering of the two routes reverses.

## The population route does not survive prediction

Paired within each predictor, on identical rankings:

| Predictor | `energy` vs `mean_cosine`, ΔMRR [95% CI] | `energy` vs `mean_l2`, ΔMRR [95% CI] |
|---|---|---|
| `average_effect` | **-0.0356 [-0.0620, -0.0115]** | -0.0020 [-0.0036, -0.0005] |
| `linear_latent` | -0.0341 [-0.0601, -0.0100] | -0.0016 [-0.0033, +0.0001] |
| `nearest_context` | -0.3159 [-0.3544, -0.2754] | -0.0032 [-0.0045, -0.0020] |
| `nearest_context_cells` | -0.3399 [-0.3736, -0.3027] | -0.0321 [-0.0501, -0.0151] |
| **`ot_map`** | +0.0027 [-0.0215, +0.0243] | **+0.0110 [+0.0087, +0.0134]** |

For the three additive predictors the population route is worse than the mean route, and the
interval excludes zero. The mechanism is visible in the second column: once magnitude is controlled
for by comparing against `mean_l2`, almost the entire deficit disappears. An additive predictor
emits one signature per drug and adds it to every source cell, so its candidate population is the
vehicle population rigidly translated. Its shape carries no information about the drug, and its
magnitude is the average over 43 other cell lines rather than the magnitude in this one. The energy
distance is sensitive to both; the cosine is sensitive to neither. What looks like a failure of
distributional scoring is a magnitude error inherited from the predictor.

`nearest_context` and `nearest_context_cells` lose 0.32 to 0.34 MRR on the population route, which
is the same effect at larger amplitude: a single donor cell line gives a much worse magnitude than
an average over 43.

**`ot_map` is the only predictor whose population route is not worse than its mean route**, and the
only one where the population route beats magnitude-aware mean matching (+0.0110 [+0.0087,
+0.0134]). It is also the only non-additive predictor in the set. That is consistent, and it is the
one positive signal in Phase B. It comes at a cost: `ot_map`'s absolute MRR is 0.667, a quarter
below `average_effect`'s 0.888, so at no point does the best population-route system beat the best
mean-route system.

## The best available system

The best transition-retrieval system measured here is **`average_effect` scored by
`mean_cosine`: MRR 0.888, Hit@1 0.833, Hit@10 0.980, over a 92-candidate library, with no
observed response from the held-out cell line**. Nothing involving population information beats it.

## Fit diagnostics

Per held-out context, over the 44 fits: the nearest training context has vehicle-mean cosine 0.44
to 0.81 (median 0.67); `linear_latent` keeps 504 to 512 components for 79.7% to 80.0% of training
variance; `ot_map`'s 50-component basis holds 33.9%; and its transport matrices sit a mean Frobenius
distance of 0.869 from the identity, so the map is genuinely cell-dependent rather than a disguised
translation. Fits take 1.3 seconds per context.

## What was fixed before these numbers were produced, and is recorded because it changed them

Two defects in the first `ot_map` implementation were found on a two-context smoke run and repaired
before the full run:

1. The predicted population was reconstructed inside the 50-dimensional latent subspace, which
   collapsed its spread and made the energy distance score a dimensionality artefact rather than the
   drug. It now applies the map as a latent edit, `x + P((A - I)z + b)`, keeping each source cell's
   component outside the subspace.
2. The treated latent covariance was pooled across training contexts after centring on each
   context's vehicle mean, so it absorbed between-context variation in the effect itself and
   inflated the predicted spread. Each cloud is now centred on its own condition mean before
   pooling, and the effect is carried separately as the mean latent shift.

With both defects present, `ot_map` scored 0.214 MRR under `energy` against 0.646 under
`mean_cosine`; with both repaired it scores 0.667 and 0.665. The repaired version is what is
reported. Neither change was made after seeing a full-run result.

## Caveat on `nearest_context_cells`

It is not in the plan's predictor table. It was added because three of the four named predictors are
additive, and an additive predictor cannot produce state-specific response by construction. A Phase
B consisting only of additive predictors plus one OT map would answer the phase's question partly by
construction rather than by measurement. It is labelled a diagnostic throughout and is not used to
support any claim about the named set.
