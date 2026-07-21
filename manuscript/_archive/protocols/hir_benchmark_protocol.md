# HIR-Bench Protocol

## Overview

HIR-Bench (Heterogeneous Inverse Retrieval Benchmark) quantifies where
inverse retrieval methods make incorrect decisions and whether this failure
risk can be predicted — conditional on the information quality of the
candidate response source.

The benchmark is **method-neutral**: DART distributional scorers are entries
under the same evaluation protocol as mean-signature, CMap, and coverage
methods.  The oracle welfare and conflict scores are defined independently
of any retrieval method.

## Benchmark cells

Each benchmark cell consists of:

- A query population Q with K subpopulations (latent targets t_k, mixture weights w_k)
- A candidate drug library of D drugs, each with a per-subpopulation response population
- A utility matrix u[d,k] = -E||x - t_k||² (mean squared distance to the latent target)

The generator (`src/benchmarks/heterogeneous_retrieval_benchmark.py`) uses a
bias-continuum design where each drug has a bias parameter b ∈ [-1, +1].  At
conflict_level=0, all drugs are symmetric across subpopulations; at
conflict_level=1, specialists for one subpopulation are strongly differentiated.

## Oracle welfare functions

Three welfare functions aggregate per-subpopulation utility to a scalar:

1. **Mean welfare**: U_mean[d] = Σ_k w_k · u[d,k]
2. **Worst-subpopulation welfare**: U_worst[d] = min_k u[d,k]
3. **CVaR welfare** (q=0.5): average of the bottom q-fraction of {u[d,k]}

**Oracle flip risk** = 1 when the mean-optimal drug ≠ the population-optimal
drug under a given welfare function.  Implemented with a tie-tolerance to
avoid fragile argmax noise on symmetric cells.

## Theoretical boundary (2-subpopulation core)

For 2 subpopulations with majority fraction α, the analytical flip boundary is:

    α* = B / (A + B)

where A = u[d_M, 0] - u[d_C, 0] (majority's margin for the majority specialist)
and B = u[d_C, 1] - u[d_M, 1] (minority's margin for the coverage drug).

When α > α*, mean-welfare picks the majority specialist; worst-welfare picks the
coverage drug.  The boundary is analytical, not estimated.

## Preference-conflict scores

Method-independent scores quantify how much subpopulations disagree:

1. **topk_disagreement**: 1 - |TopK₁ ∩ TopK₂| / K (primary)
2. **standard_kendall_conflict**: pairwise Kendall tau distance
3. **weighted_kendall_conflict**: top-weighted Kendall variant
4. **response_cosine**: pairwise cosine of utility vectors (lower = more conflict)

## Information-condition modes

A first-class experimental factor:

1. **observed**: candidate populations retain full subpopulation structure
2. **predicted_mean**: each candidate collapsed to mean + isotropic noise
   (structure destroyed; DART should show zero advantage)
3. **predicted_structure**: PCA roundtrip with reduced components + small noise
   (structure partially preserved; realistic middle ground)

## Method entries

Nine methods evaluated under the protocol:

| Method                     | Family              | Status      |
|----------------------------|---------------------|-------------|
| mean_cosine                | mean_signature      | available   |
| mean_l2                    | mean_signature      | available   |
| cmap_signature_match       | cmap_signature      | available   |
| cmap_signature_reverse     | cmap_signature      | available   |
| DART_energy                | DART_distributional | available   |
| DART_mmd                   | DART_distributional | available   |
| DART_sliced_wasserstein    | DART_distributional | available   |
| DART_coverage_mean         | DART_coverage       | available   |
| DART_coverage_worst        | DART_coverage       | available   |
| average_effect_mean        | predict_then_rank   | not_available |
| nearest_neighbor_mean      | predict_then_rank   | not_available |

Predict-then-rank methods are not evaluated in HIR-Bench synthetic cells because
they require real drug-response data for training; their evaluation is in exp09.

## Output CSVs (7 files)

All outputs under `results/exp11_hir_benchmark/`:

| File                               | Description                                |
|------------------------------------|--------------------------------------------|
| phase_grid_method_independent.csv  | Method-independent difficulty layer         |
| phase_grid_method_performance.csv  | Per-method hit@k/mrr/ndcg/regret           |
| phase_grid_predictability.csv      | AUC for predicting flip risk from features  |
| theoretical_boundary.csv           | α* boundary validation                      |
| method_dominance.csv               | Best method per (welfare, info_cond, metric) |
| uncertainty_band.csv               | Mean/std/CI per method                      |
| sanity_checks.csv                  | Automated pass/fail checks                  |

## Sanity checks

Three automated sanity checks:

1. **no_conflict_flip_rate ≤ 0.05**: at conflict=0, flip risk should be negligible
2. **median_boundary_margin ≤ 1.0**: analytical α* should be within the tested range
3. **predicted_mean Δ(DART−mean) ≤ 0.10**: under predicted_mean, DART should not
   outperform mean retrieval (validates the information-condition thesis)

## Grid specification

- **QUICK**: 2α × 3conflict × 2cells × 1noise × 2library × 2info × 3 seeds = 144 cells
- **FULL**: 4α × 7conflict × 2cells × 2noise × 2library × 3info × 20 seeds = 13,440 cells

Fixed: n_subpops=2, dim=50 (robustness sweeps over n_subpops/dim are planned extensions).

## Predictability layer

Extracts observable (non-oracle) features and predicts flip risk via leave-one-grid-out
logistic regression:

- Features: topk_disagreement, weighted/standard_kendall_conflict, response_cosine
- Population features (future): mean_subpop_variance_ratio, isotropy_index, response_diversity
- Metric: AUC on oracle_flip_risk
