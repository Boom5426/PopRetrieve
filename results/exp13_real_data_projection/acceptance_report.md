# exp13 Real-Data Projection — Acceptance Report

HIR-Bench boundary transferred by percentile: crossover_percentile = 0.389 (fit on 72 grid cells; DART wins in 55.6%). Real-data conflict threshold at that percentile = 0.1815.

Overall projection accuracy: **61.1%** (146/239 tasks)

## Primary acceptance test — projection vs. observed agreement

The projection would be *accepted* if the HIR-Bench regime prediction agreed with the method family that actually gives higher minority-state coverage on the real task, better than a trivial predictor does.

- observed-label distribution: {'mean_sufficient': np.int64(228), 'DART_recommended': np.int64(11)} (n=239)
- majority-class baseline (a constant predictor): **95.4%**
- projection accuracy: **61.1%**
| dataset | agreement | n | beats majority baseline |
|---|---|---|---|
| sciplex3_within_line | 0.31 | 90 | NO (baseline 0.99) |
| sciplex3_cross_line | 0.83 | 90 | NO (baseline 0.89) |
| cd34 | 0.25 | 12 | NO (baseline 1.00) |
| frangieh | 0.70 | 23 | NO (baseline 1.00) |
| sciplex3_predicted_mean | 1.00 | 24 | NO (baseline 1.00) |
| **overall** | **0.61** | 239 | **NO** (baseline 0.95) |

## Information-condition check (and what it does NOT show)

- predicted_mean → no-DART: 100%.
- **This is a tautology, not evidence.** `predict_regime` returns 'no_DART' unconditionally whenever `information_condition` is 'predicted_mean' or 'mean_only' (see predict_regime), so this rate is 100% by construction and can never be anything else. It restates the rule; it does not test it. The claim that mean-only predicted libraries offer no DART advantage rests on exp09, not on this line.

## Observed regime by dataset (data ground truth)

| dataset | observed DART-favoured | observed mean-sufficient | conflict (mean) | structure (mean) |
|---|---|---|---|---|
| sciplex3_within_line | 1 | 89 | 0.622 | 0.461 |
| sciplex3_cross_line | 10 | 80 | 0.130 | 0.581 |
| cd34 | 0 | 12 | 0.637 | 0.471 |
| frangieh | 0 | 23 | 0.597 | 0.385 |
| sciplex3_predicted_mean | 0 | 24 | 0.617 | 0.429 |

*Note:* the observed regime is defined by minority-state coverage (not energy regret), so it does not mechanically favour DART. Where the real data places a dataset in the low-conflict band (e.g. cross-line, CD34+), mean retrieval is genuinely sufficient — the projection reflects the data, not a prior expectation.
