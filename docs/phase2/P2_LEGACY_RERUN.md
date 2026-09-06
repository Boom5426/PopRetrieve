# P2. Every affected published result, recomputed under both estimators

Two complete runs of the legacy suite, identical in code, data and seeds, differing only in
`POPRETRIEVE_ESTIMATOR`. Driver:
[`analysis/estimator_audit/run_legacy_suite.sh`](../../analysis/estimator_audit/run_legacy_suite.sh);
comparison: [`compare_arms.py`](../../analysis/estimator_audit/compare_arms.py). Tables in
`results/estimator_audit/`.

**130 files, 872 numeric columns compared. 78 columns moved by more than 1%. 39 columns contain at
least one sign flip. No file was produced in one arm and not the other.**

One step failed identically in both arms: `analysis/predictors/exp_nonadditive_gate1.py` needs the
optional `scgen` package, which is not installed on the run machine. The failure is symmetric, so
it does not bias anything; that one analysis is simply not covered, and it is recorded here rather
than dropped.

## The finding in one line

**The estimator is irrelevant where every candidate has the same number of cells, and it matters a
great deal wherever candidates are compared through subpopulations.** That is exactly the structural
prediction from [P1](P1_ESTIMATOR_AUDIT.md), and it is now measured rather than argued.

## Global energy retrieval: unchanged

Where the task builds every candidate with the same cell count, the V bias is a near-constant
offset and cancels from the ranking.

| Result | V | U |
|---|---:|---:|
| exp04 CD34 `global_energy` Hit@1 | 0.3438 | **0.3438** |
| exp09 predict-then-rank MRR (pooled) | 0.82315 | **0.82315** |
| exp01 `global_energy` Hit@1 | 0.8933 | 0.8900 |

The first two are identical to every digit reported. This is the reassuring half of the audit.

## Coverage scorers: large moves, all in the same direction

`score_coverage` aggregates an energy distance over subpopulations, and subpopulations differ in
size across candidates by construction. This is where the O(1/m) bias bites.

| Result | V | U | change |
|---|---:|---:|---:|
| exp04 CD34 `coverage_worst` Hit@1 | 0.2049 | **0.4132** | +102% |
| exp04 CD34 `coverage_mean` Hit@1 | 0.3507 | **0.4271** | +22% |
| exp03 cross-line `coverage_worst` Hit@1 | 0.6636 | **0.8693** | +31% |
| exp11 phase diagram `adv_coverage_vs_mean` | 0.2384 | **0.4005** | +68% |
| exp01 `coverage_worst` Hit@1 | 0.6533 | 0.7300 | +12% |
| exp01 `coverage_mean` Hit@1 | 0.8567 | 0.7733 | -10% |

The V statistic was penalising candidates whose subpopulations are small, which is most of them
under a worst-subpopulation aggregator. `coverage_worst` was the scorer most damaged by it and it
gains the most from the repair.

**No conclusion reverses.** The CD34 negative control still shows `mean_cosine` (0.5139, unchanged
under either estimator because it is a cosine) beating every population scorer, so the honest
negative stays negative; it is simply less lopsided.

## Signature baselines and partial observation: small, consistent gains

| Result | V | U | change |
|---|---:|---:|---:|
| exp08 signature baselines MRR | 0.7619 | 0.7744 | +1.6% |
| exp08 Hit@1 | 0.5920 | 0.6085 | +2.8% |
| exp08 median rank proxy | 2.046 | 1.899 | -7.2% |
| exp12 partial-observation `target_mrr` | -0.3213 | -0.3181 | +1.0% |
| exp12 `decision_regret` | 0.3424 | 0.3382 | -1.2% |

All small, all favouring the repaired estimator, none large enough to move a claim.

## The external oracle results: numbers move, the verdict survives

`analysis/class_c/oracle_shape_test.py` is the sharpest result in the manuscript: two rankings swap
places when the external oracle is rebuilt from a mean to a distribution.

| Quantity | V | U |
|---|---:|---:|
| `energy_vs_oracleMEAN` | 0.1463 | 0.2222 |
| `energy_vs_oracleDIST` | 0.5291 | 0.3930 |
| `mean_vs_oracleMEAN` | 0.2421 | 0.2421 |
| `mean_vs_oracleDIST` | 0.3340 | 0.2299 |
| `magmatch_vs_oracleDIST` | 0.3523 | 0.2764 |
| winner under the mean oracle | mean | **mean** |
| winner under the distributional oracle | energy | **energy** |

**The reversal holds under both estimators.** What changes is its margin and, more importantly, the
magnitude-confound reading the script itself prints: under V, energy exceeds the magnitude-matched
scalar by 0.177 under the distributional oracle and by only 0.022 under the mean oracle; under U the
two gaps are 0.117 and 0.098. The repaired estimator makes the energy advantage look **less** like a
property of the distributional oracle specifically and more like a uniform magnitude channel. The
claim survives; the sentence explaining why it happens needs rewriting.

The protein oracle moves in the same way: `energy_rho` 0.1348 to 0.2195, with 148 of 659 per-query
values changing sign.

## The one result that degrades

| Result | V | U |
|---|---:|---:|
| exp13 real-data projection `prediction_correct` | 0.4519 | **0.3975** |

25 of 239 per-query predictions flip. The regime classifier is 12% less accurate under the
correct estimator. That is a real loss and it belongs in the manuscript as one.

**It is not a figure panel, and this document said it was.** No panel in the deck draws
`prediction_correct` or `HIR_predicted_regime`; a grep of `figures/` for either column returns
nothing. Fig. 3g reads the same `projection.csv` but plots the minority-state coverage gain, which
is a different column and a different claim. The classifier's accuracy is quantified in exactly one
place in the manuscript, Supplementary Note 1, and that is where the reissue lands. Corrected
2026-09-03.

## What this means for the manuscript

1. **Nothing has to be retracted.** Every qualitative conclusion checked here survives the estimator
   swap, including the negative control and the oracle-shape reversal.
2. **Numbers in coverage-scored panels must be reissued.** Fig. 2d, Fig. 5b and the exp01/exp03/exp04
   coverage rows move by 10 to 100 percent of their value. Quoting the V numbers after this audit
   would be quoting a known artefact.
3. **The `coverage_worst` aggregator was the main victim, and its published weakness was partly the
   estimator's doing.** Any sentence reading its low score as evidence about worst-subpopulation
   matching needs to be rechecked against 0.4132 rather than 0.2049.
4. **The oracle-shape explanation changes even though its verdict does not.** See above.
5. **The regime classifier gets worse.** Report it, in Supplementary Note 1, which is the only place it is quantified.

## Blocked, not skipped

Fig. 3h to 3k, the GDSC2 functional oracle, could not be re-run: the workbook is not
redistributable and is absent from both machines (`DATA.md`). Those four panels are
estimator-sensitive and their status under the U statistic is **unknown**, not unchanged.
