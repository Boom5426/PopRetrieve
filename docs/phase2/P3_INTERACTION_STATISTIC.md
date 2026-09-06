# P3. Gate 1 rebuilt: a cross-fitted drug-by-state interaction

Code: [`src/retrieval/interaction.py`](../../src/retrieval/interaction.py),
[`tests/test_interaction_statistic.py`](../../tests/test_interaction_statistic.py),
[`analysis/phase2_transition/gate1_interaction.py`](../../analysis/phase2_transition/gate1_interaction.py).
Results: `results/phase2_transition/gate1_interaction/`.

## Why the old statistic was retired

Gate 1 measured differential response as `D = 1 - cos(r_G1, r_G2M)`. Measured on 3,620 Tahoe query
conditions it correlates **-0.694** with the response norm and **-0.425** with the number of treated
cells: when both state responses are small, their angle is set by sampling noise, so a weak drug
scores as strongly state-dependent. The statistic was a signal-to-noise measure wearing a
pharmacological label.

## What replaces it

The question is whether the interaction vector `I = r_1 - r_2` is non-zero. Its norm is unusable
directly for the same reason as before, so `I` is estimated twice on disjoint halves of **all four
arms**, the vehicle arms included, and the two estimates are multiplied:

| Quantity | Definition | Reads as |
|---|---|---|
| `S_int` | `<I_A, I_B> / p` | interaction strength, in squared expression units |
| `S_main` | `<M_A, M_B> / p`, `M = (r_1 + r_2)/2` | the state-independent part, same construction |
| `interaction_share` | `S_int / (S_int + S_main)` | scale-free: what fraction of the response is state-dependent |
| `R_int` | `cos(I_A, I_B)` | is the interaction reproducible at all? |

Under the additive null `E[I] = 0` and the two halves are independent, so `E[S_int] = 0` **exactly**.
Noise no longer buys interaction: it makes `I_A` and `I_B` point in unrelated directions.

Splitting the vehicle arms matters. Sharing one vehicle mean between the halves would put the same
control noise into both estimates and correlate them under the null, which is the bias the whole
construction exists to avoid.

`interaction_share` exists because `S_int` is on a squared-response scale and so grows with effect
size. Its denominator is cross-fitted too, so unlike a division by `||r||` it does not put a
noise-inflated single-sample quantity underneath, which is the exact mechanism that sank `1 - cos`.

## The five pre-specified checks

Three are synthetic and run in the test suite; two need real material and run on Tahoe.

| # | Check | Result |
|---|---|---|
| 1 | additive null gives `S_int` = 0 | **pass**: mean over 24 worlds within 4 standard errors of zero, with the additive effect set 3x larger than the noise |
| 2 | state-label permutation returns to the null | **pass**: a real interaction gives z > 3 against its own permutation null; an additive drug gives \|z\| < 3 |
| 3 | constructed positive control | **pass**, see below |
| 4 | no systematic drift with cell count | **pass**: `S_int` flat across n = 50, 100, 200, 400 while `1 - cos` more than doubles from n = 400 to n = 50 |
| 5 | effect-size audit | **pass**, see below |

Two further tests assert that `interaction_share` is scale-free (doubling effect and interaction
together leaves it unchanged; raising only the interaction raises it) and that it is near zero for
an additive drug. Suite total after this phase: 114 passed, 0 failed.

### Check 3: a positive control built from the plate itself

Tahoe has no constructed mixture, so 176 synthetic conditions were built from its own cells: G1
cells from drug A, G2M cells from drug B, against the same vehicle arms and at the same arm sizes.
Their interaction is real and large by construction.

| | Real query conditions (n = 3,620) | Synthetic interacting (n = 176) | Ratio |
|---|---:|---:|---:|
| median `S_int` | 1.37e-04 | 9.93e-04 | **7.2x** |
| median `R_int` | 0.169 | 0.568 | 3.4x |
| median `D_old` | 0.306 | 0.784 | 2.6x |

### Check 5: the effect-size audit

| Correlate | old `D` | new `S_int` |
|---|---:|---:|
| number of treated cells | **-0.425** | **+0.100** |
| mean response norm | **-0.694** | +0.663 |

The cell-count confound is gone and the magnitude relationship has flipped from mechanically
negative to positive, which is the direction biology would predict: a drug with a larger effect has
more room to have a state-dependent one. The plan allowed a positive relationship and forbade the
inversion, and that is what the data show.

The two statistics rank drugs almost oppositely: Spearman(`S_int`, `D_old`) = **-0.333**.

## What the plate actually contains

| Quantity | Median | 5th to 95th percentile |
|---|---:|---|
| `S_int` | 1.37e-04 | -1.83e-06 to 6.77e-04 |
| `R_int` | 0.169 | |
| `D_old` | 0.306 | |

94.6% of queries have a positive `S_int`, which is what an unbiased statistic should show when most
conditions carry some real interaction and roughly the remainder are null. Against a
state-label permutation null run on 365 of the queries, the median z is **3.64**, 69.6% exceed z = 2
and 72.6% reach p < 0.1 at the 20-permutation resolution.

So a drug-by-state interaction is genuinely present in most conditions and it is roughly seven times
smaller than a constructed one. Cell-cycle state modulates drug response on this plate; it does so
weakly.

## What this does not settle

That the statistic is sound says nothing about whether it locates population-scoring benefit. That
is [P4](P4_BOTTLENECK_DECOMPOSITION.md), and the answer there is no.
