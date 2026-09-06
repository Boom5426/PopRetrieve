# Post-Phase-II verdict

The endpoint of the repair track. Five questions, five answers, nothing else. Every number is
derived in [P1](P1_ESTIMATOR_AUDIT.md) to [P5](P5_STATE_CONDITIONED_PREDICTOR.md) and reproducible
from `results/`.

---

## Q1. With the correct estimator, is there still beyond-magnitude information in the population?

**Yes, and it is small: +0.0102 MRR [+0.0065, +0.0145].**

At the oracle, on 3,992 queries over 44 held-out cell lines and a 92-compound library:

| Scorer | MRR |
|---|---:|
| `mean_cosine`, direction only | 0.9452 |
| `mean_l2`, direction plus magnitude | 0.9653 |
| `energy` (U-statistic), full population | 0.9755 |

The chain **direction -> magnitude -> distribution** splits the total +0.0303 as +0.0201 magnitude
and +0.0102 distribution. Under the manuscript's V-statistic the distributional term is +0.0006
[-0.0019, +0.0028], indistinguishable from zero: the estimator was consuming the whole of it.

The repair is real but narrow. Across the whole legacy suite the estimator swap changed nothing
where candidates are equal-sized (exp04 CD34 `global_energy` and exp09 MRR are identical to every
reported digit) and changed coverage-scored results by 10 to 100 percent, because coverage
aggregates over subpopulations of unequal size. **No published conclusion reverses**, including the
CD34 negative control and the oracle-shape reversal, but the coverage numbers and one regime
classifier must be reissued ([P2](P2_LEGACY_RERUN.md)).

## Q2. How large is that advantage in real intervention retrieval, at the oracle ceiling?

**About a fifth of a rank position out of 92, and a 5.2-to-1 flip ratio.**

Population information corrects a wrong top-1 in 5.6% of rankings and breaks a correct one in 1.1%.
Against magnitude-aware mean matching rather than cosine, those become 2.0% and 0.5%, still 4.0 to 1.

The ceiling above it is what bounds everything: **on 3,110 of 3,992 queries the oracle mean route is
already perfect at every seed**, so no decision is available to improve. This is the single largest
term in the whole analysis and it is a property of how good mean signatures already are, not of the
biology.

## Q3. Why does the advantage vanish, and reverse, after forward prediction?

**Because an additive predictor hands the distributional scorer a population it did not model.**

| | mean route | population route |
|---|---:|---:|
| oracle | 0.9452 | 0.9755 |
| best predictor (`average_effect`) | **0.8876** | 0.8520 |

Deleting every observed candidate response costs the mean route 0.058 MRR and the population route
0.124. Within the predictor the population route is worse by -0.0356 [-0.0620, -0.0115], and the
retained fraction of the oracle gain is **-1.17**: the gain does not attenuate, it inverts.

The mechanism is measured, not inferred. An additive predictor's candidate population is the
vehicle population rigidly translated, so its shape carries no information about the drug and its
magnitude is an average over 43 other cell lines. Its predicted differential response is zero to
within float32 round-off across all 19,044 predictor-drug-seed values. The energy distance is
sensitive to both shape and magnitude; the cosine is sensitive to neither. What looks like a failure
of distributional scoring is a magnitude error inherited from the predictor: comparing against
`mean_l2` instead of `mean_cosine` removes almost all of the deficit (-0.0020 instead of -0.0356).

## Q4. Does the repaired drug-by-state interaction explain population gain, independently of headroom?

**No.**

The old Gate 1 statistic had to go first: `1 - cos(r_1, r_2)` correlates -0.694 with the response
norm and -0.425 with cell count, so the weakest drugs scored as the most state-dependent. Its
replacement is a cross-fitted interaction, `S_int = <I_A, I_B>/p`, which is exactly zero in
expectation under the additive null. It passes all five pre-specified checks: the cell-count
correlation falls from -0.425 to +0.100, the magnitude relationship flips from mechanically negative
to +0.663, and a positive control built from the plate's own cells scores 7.2 times the endogenous
median ([P3](P3_INTERACTION_STATISTIC.md)).

It still does not locate population benefit. Conditioning on the mean route's own performance,
which is the specification that avoids the tautology in `gain = RR_pop - RR_mean`:

| Term | β | 95% CI | p |
|---|---:|---|---:|
| `interaction_share` | +0.0011 | [-0.0011, +0.0032] | 0.33 |
| `interaction_share`, magnitude-controlled | **-0.0027** | [-0.0043, -0.0012] | 0.0006 |
| `A_sup`, recoverability | **+0.0084** | [+0.0052, +0.0116] | <1e-4 |
| `D_old`, the retired statistic | **-0.0096** | [-0.0167, -0.0024] | 0.0087 |

Two corrections to earlier drafts belong here.

**The headroom result was a ceiling artefact.** Spearman(headroom, gain) = +0.790 was reported as the
strongest explanation of where population scoring pays. A null that reshuffles the population
route's reciprocal ranks within each context, keeping both marginals and the `RR <= 1` ceiling,
reproduces it at +0.786 [+0.767, +0.805]. The observed value is inside the null. What survives is
the ceiling fact in Q2, not a relationship.

**The old statistic's apparent usefulness was borrowed.** Its +0.254 marginal correlation with gain
runs entirely through effect size: weak drugs score high on `D_old`, weak drugs are the ones the mean
route ranks badly, and the ceiling does the rest. Conditioned on the mean route's performance it
reverses sign.

Of the three gates, **only recoverability points where the framework said it would**, and it buys
0.008 of reciprocal rank per standard deviation.

## Q5. Is there a predictor that keeps both mean accuracy and population fidelity?

**Partly. The first honest attempt passes both gates and does not close the gap.**

`state_conditioned_average_effect` estimates the average effect separately per cell-cycle state. It
is one extra grouping and no new hyperparameter.

| Pre-frozen entry condition | Result | Verdict |
|---|---|---|
| interaction fidelity rho > 0, CI excludes 0 | **+0.606** [+0.576, +0.639] | pass |
| mean-route MRR >= 0.843 | **0.8883** | pass |

It predicts the **fraction** of the response that is state-dependent almost exactly (0.164 against an
observed 0.170) while under-predicting the absolute interaction 3.6-fold. On retrieval it raises the
population route from 0.8520 to 0.8569 and the mean route from 0.8876 to 0.8883, narrowing the
population deficit from -0.0356 to **-0.0314 [-0.0584, -0.0076]**, which still excludes zero.

So: mean accuracy is preserved, interaction fidelity is real for the first time, and distributional
retrieval still loses to magnitude-aware mean matching on the same predictions.

---

## What follows

The measured budget is the thing to keep in view. The oracle leaves 0.055 MRR above the mean route
in total; 0.020 of it is magnitude, available to a scorer that needs no predictor at all; 0.010 is
distribution. Against that, `average_effect` scored by `mean_cosine` already reaches 0.8876 with no
observed response from the held-out cell line, and every population route tried so far sits below it.

Three things follow, in order.

1. **Reissue the affected numbers before writing anything.** The coverage rows across exp01, exp03,
   exp04 and exp11, the oracle-shape magnitude-confound sentence, and the regime classifier's accuracy
   (Supplementary Note 1; it is not a figure panel)
   (0.4519 to 0.3975). Four GDSC2 panels are **blocked, not unchanged**: their status under the
   correct estimator is unknown.
2. **Retire `1 - cos` wherever it appears**, including Fig. 5c and the patient-glioblastoma panels,
   and re-derive anything that used it as a stratifier. It anti-predicts the outcome it was
   introduced to predict.
3. **Phase 6 is a decision, not a default.** A cell-dependent residual predictor
   `x_hat_i = x_i + f(x_i, d)` is the natural next step and it is not started. The case for it is
   that two thirds of the interaction magnitude is still unpredicted; the case against it is that
   the entire prize beyond magnitude is 0.010 MRR, and the last predictor to pass both gates bought
   0.005 of it while remaining 0.031 behind the incumbent. Training it should be conditional on
   deciding that 0.010 is worth a manuscript claim.
