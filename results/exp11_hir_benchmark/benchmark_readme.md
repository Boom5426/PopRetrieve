# HIR-Bench Results — Experiment 11

## What this directory contains

Seven CSV files produced by `src/experiments/exp11_hir_benchmark.py`.
See `paper/hir_benchmark_protocol.md` for the full protocol specification.

## CSV descriptions

### phase_grid_method_independent.csv
Method-independent difficulty layer.  One row per (grid_cell × seed × welfare_type).
Contains conflict scores, oracle flip risk, utility gap, and theoretical boundary.

Key columns: `grid_id, seed, alpha, conflict_level, information_condition,
topk_disagreement, weighted_kendall_conflict, oracle_flip_risk,
oracle_utility_gap, theoretical_alpha_star, theoretical_boundary_margin`.

### phase_grid_method_performance.csv
Per-method retrieval results.  One row per (grid_cell × seed × method × welfare_type).
The central table for method comparison.

Key columns: `grid_id, seed, method, method_family, welfare_type,
information_condition, selected_top1_drug, oracle_population_optimal_drug,
hit_at_1, hit_at_5, mrr, ndcg, decision_regret`.

### phase_grid_predictability.csv
Predictability summary: AUC for predicting oracle_flip_risk from observable conflict
features, plus feature importances.

### theoretical_boundary.csv
Boundary validation: analytical α* = B/(A+B) vs observed flip for each cell
where a 2-subpopulation conflict exists.

### method_dominance.csv
Which method is best per (welfare_type × information_condition × metric).

### uncertainty_band.csv
Mean, std, and 95% CI for hit@1 per (method × welfare × info_cond).

### sanity_checks.csv
Automated sanity checks with pass/fail.

## Reproduction

```bash
# QUICK (~40s)
python src/experiments/exp11_hir_benchmark.py --quick --n-seeds 3

# FULL (~60 min)
python src/experiments/exp11_hir_benchmark.py --n-seeds 20
```

## Method availability

All 9 methods in the protocol are `available`.  Two predict-then-rank methods
(average_effect_mean, nearest_neighbor_mean) are marked `not_available` because
they require real drug-response data and are evaluated in exp09 instead.
