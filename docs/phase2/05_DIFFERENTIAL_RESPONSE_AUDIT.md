# 05. Gate 1: differential response, measured on the retrieval task

Observed values from [`analysis/phase2_transition/phase_c_gates.py`](../../analysis/phase2_transition/phase_c_gates.py)
(`results/phase2_transition/phase_c/gate1_observed.csv`); predicted values from Phase B
(`results/phase2_transition/phase_b/gate1_predicted.csv`); the comparison in
`results/phase2_transition/synthesis/gate1_fidelity.csv`.

## Definition

Two cellular states are fixed in advance as the cell-cycle calls that ship with the plate, G1 and
G2M, with S dropped as intermediate. For a query condition,

    r_state = mean(treated cells in that state) - mean(vehicle cells of the same context in that state)
    D       = 1 - cos(r_G1, r_G2M)

Each state's response is referred to its own state-matched vehicle mean, which is correction R30 in
CORRECTIONS.md: a pooled baseline leaves the difference between the two vehicle states inside the
responses and inflates D.

Scored for 3,620 of 3,992 queries. The 372 exclusions all have fewer than 50 treated cells in one
state arm; no vehicle arm failed.

## Observed differential response

| Quantity | Value |
|---|---:|
| Median D | 0.2602 |
| Median induced cosine `cos(r_G1, r_G2M)` | 0.7398 |
| Interquartile range of D | 0.1634 to 0.3997 |
| Range | 0.0200 to 1.0471 |

Cell-cycle state responses in real, unconstructed cell lines are mostly aligned. The median cosine
of 0.74 sits far above the 0.014 to 0.044 the manuscript reports for constructed cross-line
mixtures, which is expected: those mixtures were built to be divergent, and these subpopulations
were not built at all.

## D is confounded with effect size, which limits what it can be used for

| Correlate of D | Spearman |
|---|---:|
| Mean response norm `(||r_G1|| + ||r_G2M||)/2` | **-0.584** |
| Number of treated cells | -0.529 |
| Supervised recoverability `A_sup` (Gate 2) | **-0.760** |

Stratifying by response magnitude makes the size of the problem plain:

| Response-norm quartile | n | Median D | Median norm | Median A_sup |
|---|---:|---:|---:|---:|
| Q1, weakest | 905 | 0.3654 | 0.9356 | 0.7050 |
| Q2 | 905 | 0.3285 | 1.2234 | 0.7633 |
| Q3 | 905 | 0.2407 | 1.5664 | 0.8367 |
| Q4, strongest | 905 | 0.1352 | 2.2547 | 0.9367 |

**A weak drug looks differentially responding.** When both state responses are small, their cosine
is dominated by sampling noise, the cosine falls, and D rises. The drugs with the highest measured
differential response are systematically the drugs with the weakest and least reliably measured
effects. `1 - cos` is therefore not a clean measure of state-specific pharmacology on this material;
it is partly a signal-to-noise measure. Any downstream analysis that treats high D as "this drug
acts differently on different cell states" inherits that confound, and section 8 shows it does.

This is a property of the statistic, not of this dataset in particular, and it applies to the same
statistic wherever the manuscript uses it.

## Differential-response fidelity: can a predictor reproduce D?

| Predictor | Median observed D | Median predicted D | Max abs predicted D | Fraction with predicted D = 0 | Spearman observed vs predicted |
|---|---:|---:|---:|---:|---:|
| `average_effect` | 0.2600 | 3.0e-10 | 1.5e-07 | **100%** | -0.033 |
| `linear_latent` | 0.2600 | 1.3e-10 | 1.3e-07 | **100%** | +0.005 |
| `nearest_context` | 0.2600 | -1.1e-09 | 1.3e-07 | **100%** | +0.003 |
| `ot_map` | 0.2600 | 0.0389 | 0.4820 | 0% | +0.395 |
| `nearest_context_cells` | 0.2613 | 0.6863 | 1.3104 | 0% | +0.637 |

The three additive predictors produce no differential response at all: across all 19,044
(context, seed, drug) values the largest absolute predicted D is 2.5e-07, which is float32
round-off against an observed median of 0.260. This is computed, not assumed: the predicted response
of a state is the mean predicted cell of that state minus the mean source cell of that state, and
for a predictor that adds one vector to every cell those two differences are the same vector. The
manuscript states this as a property; here it is measured on 3,581 drugs in 44 contexts and holds to
seven decimal places.

The two non-additive predictors do produce a differential response and neither reproduces the
observed one. `ot_map` under-predicts it 6.7-fold (0.039 against 0.260) while
correlating with it at +0.395. `nearest_context_cells` over-predicts it by a factor of 2.6 (0.686
against 0.261) with a higher rank correlation, +0.637, because transplanting another cell line's
treated cells transplants that line's state structure along with the drug's.

**No predictor in the frozen set reproduces the observed differential response.** The best of them
recovers the ordering moderately and the magnitude not at all. Gate 1 is therefore not passed by any
predictor available here, which is a precondition for anything a distributional retriever could
exploit downstream.
