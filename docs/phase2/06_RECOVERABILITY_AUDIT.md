# 06. Gate 2: recoverability, measured on the retrieval task

From [`analysis/phase2_transition/phase_c_gates.py`](../../analysis/phase2_transition/phase_c_gates.py);
table in `results/phase2_transition/phase_c/gate2_observed.csv`. All 3,992 queries scored.

## What is being recovered, and why it is not the Gate 1 partition

Gate 1's partition is cell-cycle phase, which is itself scored from expression. Asking a probe to
recover it from expression is partly circular, and that circularity is one of the failure modes this
project exists to criticise; it is why `analysis/tahoe_pilot/tahoe_gate_pilot.py` scored Gate 2 on
drug identity instead. This audit keeps that choice and asks the per-query form of it:

> can a probe tell a cell that saw drug `q` in context `c` from a vehicle cell of context `c`?

The label is external. It is which well the cell came from, not a property computed from the
expression values the probe reads. It is also the quantity a population-aware retriever actually
depends on: if a drug's effect is not recoverable in single cells, no distributional score can use
it.

    A_sup    5-fold cross-validated logistic probe (C = 1), out-of-fold accuracy
    A_unsup  k-means with k = 2 on the same cells, best-permutation accuracy
    G        A_sup - A_unsup

Both arms are balanced and capped at 300 cells, so chance is 0.5 by construction. Label matching is
free for the unsupervised arm, following the manuscript.

## Result

| Quantity | Median | Mean | IQR |
|---|---:|---:|---|
| `A_sup` | 0.8000 | 0.8068 | 0.7267 to 0.8950 |
| `A_unsup` | 0.5550 | 0.5987 | 0.5233 to 0.6200 |
| `G` | 0.2050 | 0.2081 | 0.1450 to 0.2700 |

`A_sup` exceeds 0.8 for 49.7% of queries. `A_unsup` exceeds 0.8 for 9.3%. The minimum `A_sup` is
0.504, the maximum 1.000; `A_unsup` bottoms out at exactly 0.500, which is the floor a balanced
best-permutation accuracy can reach.

## Reading it with the plan's own two labels

Plan section 12 asks that each query be called information-limited or algorithm-limited.

- **Algorithm-limited** (`A_sup` high, `A_unsup` low) is the dominant regime. For half of all
  queries a linear probe separates treated from vehicle cells at 80% or better while k-means, given
  the same cells, sits near chance. The drug's effect is present in single cells and unsupervised
  structure does not find it.
- **Information-limited** (`A_sup` low) is the rest. The lower quartile of `A_sup` is below 0.727,
  and at the bottom of the range a supervised probe is barely above chance, which means the drug
  leaves almost no single-cell trace in that context.

The gap `G` is remarkably stable, median 0.205 with an interquartile range of 0.125, so the amount
of information that supervision recovers and clustering does not is close to constant across a very
wide range of drugs and cell lines.

## The consequence for the three-gate framework

`A_sup` is strongly negatively correlated with Gate 1's D (Spearman -0.760, see
[05](05_DIFFERENTIAL_RESPONSE_AUDIT.md)). The two gates are not independent axes on this material:
the queries with the highest measured differential response are largely the queries whose effect is
least recoverable, because both statistics are being driven by effect size in opposite directions.
The joint analysis in [08](08_THREE_GATE_ANALYSIS.md) has to be read with that in front of it, and
it is the reason the framework's own predicted regime turns out to be nearly empty.
