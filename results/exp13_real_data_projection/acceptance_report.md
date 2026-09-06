# exp13 Real-Data Projection — Acceptance Report

HIR-Bench boundary transferred by percentile: crossover_percentile = 0.174 (fit on 4480 grid cells; PopRetrieve wins in 63.1%). Real-data conflict threshold at that percentile = 0.1232.

Overall projection accuracy: **39.7%** (95/239 tasks)

## Primary acceptance test — projection vs. observed agreement

The projection would be *accepted* if the HIR-Bench regime prediction agreed with the method family that actually gives higher minority-state coverage on the real task, better than a trivial predictor does.

- observed-label distribution: {'mean_sufficient': 229, 'DART_recommended': 10} (n=239)
- majority-class baseline (a constant predictor): **95.8%**
- projection accuracy: **39.7%**
| dataset | agreement | n | beats majority baseline |
|---|---|---|---|
| sciplex3_within_line | 0.29 | 90 | NO (baseline 1.00) |
| sciplex3_cross_line | 0.40 | 90 | NO (baseline 0.89) |
| cd34 | 0.33 | 12 | NO (baseline 1.00) |
| frangieh | 0.22 | 23 | NO (baseline 1.00) |
| sciplex3_predicted_mean | 1.00 | 24 | NO (baseline 1.00) |
| **overall** | **0.40** | 239 | **NO** (baseline 0.96) |

## Information-condition check (and what it does NOT show)

- predicted_mean → no_DART: 100%.
- **This is a tautology, not evidence.** `predict_regime` returns 'no_DART' unconditionally whenever `information_condition` is 'predicted_mean' or 'mean_only' (see predict_regime), so this rate is 100% by construction and can never be anything else. It restates the rule; it does not test it. The claim that mean-only predicted libraries offer no PopRetrieve advantage rests on exp09, not on this line.

## Observed regime by dataset (data ground truth)

| dataset | observed PopRetrieve-favoured | observed mean-sufficient | conflict (mean) | structure (mean) |
|---|---|---|---|---|
| sciplex3_within_line | 0 | 90 | 0.621 | 0.461 |
| sciplex3_cross_line | 10 | 80 | 0.130 | 0.594 |
| cd34 | 0 | 12 | 0.636 | 0.471 |
| frangieh | 0 | 23 | 0.669 | 0.441 |
| sciplex3_predicted_mean | 0 | 24 | 0.617 | 0.429 |

*Note:* the observed regime is defined by minority-state coverage (not energy regret), so it does not mechanically favour PopRetrieve. Where the real data places a dataset in the low-conflict band (e.g. cross-line, CD34+), mean retrieval is genuinely sufficient — the projection reflects the data, not a prior expectation.
