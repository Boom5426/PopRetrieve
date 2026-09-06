# P1. Estimator audit: what the V-statistic costs

Phase 1 of the post-Phase-II plan. Code: [`src/retrieval/metrics.py`](../../src/retrieval/metrics.py),
[`analysis/estimator_audit/estimator_bias_table.py`](../../analysis/estimator_audit/estimator_bias_table.py),
[`tests/test_estimator_bias.py`](../../tests/test_estimator_bias.py). Numbers in
`results/estimator_audit/`.

## What was implemented

Both estimators now exist under names that say which is which, and the old one is unchanged so
every published number still reproduces from an unedited call site.

| Name | Form | Bias | Status |
|---|---|---|---|
| `energy_distance`, alias `energy_distance_v` | self-pairs included | `+E|X-X'|/m + E|Y-Y'|/n` | unchanged; the published estimator |
| `energy_distance_u` | self-pairs excluded | unbiased at any m, n | new |
| `mmd_rbf`, alias `mmd_rbf_v` | self-pairs included | `+(1-Ek(X,X'))/m + (1-Ek(Y,Y'))/n` | unchanged; the published estimator |
| `mmd_rbf_u` | self-pairs excluded | unbiased at any m, n | new |
| `sliced_wasserstein` | quantile-matched | no U/V pair exists | unchanged |

`score_energy`, `score_mmd_rbf` and `score_coverage` take `estimator='u'|'v'`. The process-wide
default is read once from `POPRETRIEVE_ESTIMATOR` and prints a warning to stderr when it is not
`'v'`, so a whole legacy suite can be re-run under either estimator without editing thirty call
sites and without a run under the new estimator ever being mistaken for a published one.

**The default is still `'v'`.** That is a reproducibility decision, not an endorsement: an
unchanged script must keep producing the number it produced before. Everything below argues that
new work should pass `'u'`.

### The MMD question, answered

Plan section 1.3 asked which form the repository's MMD is, because energy and MMD agree to the
fourth decimal in Phase A (0.9754 against 0.9755) and swapping one bias for another would be no
progress. It is the **biased V-statistic**: `k(X,X).mean()` averages over all `m^2` pairs including
the `m` diagonal entries, and for any RBF kernel `k(x,x) = 1`. The bandwidth is the median
heuristic over the pooled sample, multi-bandwidth at scales 0.25, 1 and 4. `mmd_rbf_u` keeps the
kernel and the bandwidth identical and changes only which pairs are averaged, so the two differ in
the estimator and in nothing else.

## What the bias is worth, measured

Isotropic Gaussian data, so every population value is known exactly. 24 replicates per cell.

### The null, where the true value is zero

At 2,304 dimensions, `P` and `Q` drawn from the same distribution:

| n | `energy_u` | `energy_v` | `mmd_u` | `mmd_v` | `sliced_wasserstein` |
|---:|---:|---:|---:|---:|---:|
| 25 | -0.005 ± 0.011 | **5.423** | -0.00003 | 0.0489 | 0.320 |
| 50 | +0.012 ± 0.009 | 2.725 | +0.00007 | 0.0245 | 0.240 |
| 100 | +0.001 ± 0.004 | 1.359 | +0.00001 | 0.0122 | 0.177 |
| 200 | +0.001 ± 0.002 | 0.679 | +0.00001 | 0.0061 | 0.128 |
| 400 | -0.001 ± 0.001 | 0.338 | -0.00001 | 0.0031 | 0.093 |

The V-statistic's null value falls by a factor of 7.98 between n = 25 and n = 200, against the
factor of 8.00 that a pure `1/n` bias predicts. The U form is indistinguishable from zero at every
size. MMD shows the identical pattern at its own scale.

Sliced Wasserstein has no U/V repair available and its null still falls by a factor of 3.4 across
the same range. That is a reason to keep it a secondary scorer, and it is consistent with its being
the one population scorer that loses to the mean route in Phase A.

### Unequal sample sizes, which is the configuration the benchmark actually has

Query fixed at 200 cells; candidates of several sizes drawn from **the query's own distribution**,
so every candidate is equally correct and any spread across sizes is pure artefact. At 2,304
dimensions:

| candidate cells | `energy_u` | `energy_v` |
|---:|---:|---:|
| 25 | -0.007 ± 0.011 | 3.046 |
| 50 | -0.005 ± 0.004 | 1.691 |
| 100 | -0.003 ± 0.002 | 1.016 |
| 200 | +0.002 ± 0.002 | 0.681 |
| 400 | +0.001 ± 0.001 | 0.510 |

Shrinking a candidate from 400 cells to 50 moves the V-statistic by **+1.181** and the U-statistic
by **-0.006**, which is inside its own standard error.

**Calibrated against a real effect, that artefact is worth a mean shift of 0.184 standard
deviations**, and the figure is stable across dimensionality: 0.185 at 32 genes, 0.182 at 256,
0.184 at 2,304. A candidate with 50 cells is scored as though its response were displaced by a
fifth of a standard deviation. Nothing in the biology produced that.

### The second channel, which survives equal sample sizes

The bias decomposes as `E_V = E_U + within(X)/m + within(Y)/n`. The query term is the same for
every candidate and cancels from a ranking. **The candidate term does not**: even at equal `m` it
varies with each candidate's own dispersion, so the V form systematically prefers tighter
candidates. Measured at 2,304 dimensions with a 200-cell query and equal-size candidates:

| candidate cells | V minus U at candidate sd 1.0 | at sd 1.6 | difference |
|---:|---:|---:|---:|
| 100 | 1.018 | 1.425 | **0.407** |
| 200 | 0.679 | 0.882 | 0.204 |
| 400 | 0.509 | 0.611 | 0.102 |

For scale, the true signal between those two candidates is `E_U` = 0.002 against 4.634. So at
m = 400 the dispersion channel is 2.2% of the signal and at m = 100 it is 8.8%. It is small, it is
one-directional, and it means **"all candidates have the same number of cells" is not sufficient
for the estimator choice to be irrelevant.** Every affected result has to be re-run rather than
argued away, which is what Phase 2 does.

## Tests

`tests/test_estimator_bias.py` adds 8 tests covering the four scenarios the plan named: null
scaling, mean shift, variance shift and unequal sizes, plus the statement that the V bias is large
enough to **reorder two candidates**, not merely to move a value. The full suite is 107 passed, 0
failed, with the pre-existing 99 unchanged, which is the check that the published numbers still
reproduce.

## What this means for the manuscript

The bias is upward, of order 1/m, and it penalises candidates that are small or dispersed. Its
effect on a ranking is therefore not random: it is a systematic preference for large, tight
candidate populations, independent of whether they are the right answer.

Phase A already showed the consequence at full size. The population route's advantage over
magnitude-aware mean matching is +0.0102 MRR [+0.0065, +0.0145] under the U statistic and +0.0006
[-0.0019, +0.0028] under the V statistic: the estimator consumes the entire effect. Every other
population-scorer result in the manuscript is now re-run under both estimators; the table is
[P2_LEGACY_RERUN.md](P2_LEGACY_RERUN.md).
