# hir_bench/, failure predictability

> **SUPERSEDED, 2026-07-12.** The scripts here produced the **retracted** AUC 0.640. The
> live path is now in-tree:
>
>     PYTHONPATH=src python src/experiments/exp11_hir_benchmark.py --skip-method-perf
>
> which writes `results/exp11_hir_benchmark/phase_grid_predictability.csv`. Read
> [CORRECTIONS.md](../../CORRECTIONS.md) R11 before using anything below.

## What was wrong with AUC 0.640

`fig6f_roc_full.py` and `fig6f_roc_lean.py` ran a leave-one-`grid_id`-out logistic regression
on the FULL 13,440-instance grid and reported AUC 0.640, described as "predictable from
observable features". Neither half of that description held.

- **The features were not observable.** All four (`topk_disagreement`,
  `weighted_kendall_conflict`, `standard_kendall_conflict`, `response_cosine`) are functions
  of `cell.utility_matrix`. So is the label, `oracle_flip_risk`. It was one function of the
  oracle predicting another function of the same oracle: the exact circularity this project
  exists to audit. The genuinely observable features
  (`benchmarks.predictability.extract_features`) were implemented and never called.
- **The cross-validation leaked.** `grid_id` also encodes `information_condition`,
  `cells_per_subpop` and `noise_sigma`, none of which change the utility matrix. Holding out
  one `grid_id` left roughly **twelve near-identical copies** of the held-out instance in the
  training set.
- **The sample size was inflated.** The label is a deterministic step function of
  `(alpha, conflict_level)`. There are **28 independent parameter cells**, not 13,440
  instances.

## What the honest run says

Grouping on the label-determining axes, on the FULL grid:

| feature set | AUC |
|---|---:|
| **observable** (variance ratio, isotropy, response diversity of query and candidates) | **0.788** |
| oracle-derived (the four above) | **0.400**, worse than chance |
| majority-class rate | 0.643 |

All of the reported 0.640 was pseudo-replication. The observable-feature result is better than
the number it replaces, but effective n is 28, and because the label is deterministic within a
cell every held-out fold is single-class, so no per-fold AUC distribution exists.

The scripts in this directory are kept for provenance. They also ran outside the repository's
own results tree, which is why `results/` shipped a QUICK run reporting AUC 0.5 while the
manuscript quoted 0.640 and nothing on disk recorded the discrepancy. That is fixed:
`results/exp11_hir_benchmark/PROVENANCE.md` now states which layer came from which grid.
