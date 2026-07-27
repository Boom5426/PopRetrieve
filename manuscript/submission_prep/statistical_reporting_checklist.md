# EvalShift Manuscript — Statistical Reporting Checklist

Per result: sample size, unit of analysis, test, effect size, CI, p-value, multiple-testing
correction, and **metric class** (circular-risk / proxy / independent). The metric-class
column is load-bearing for Claim 4's honesty.

Metric-class legend:
- **circular-risk** — outcome aligned with EvalShift's own objective (energy/distributional).
  Gains are suggestive, not conclusive.
- **proxy** — synthetic/oracle-based welfare; internally valid, externally unvalidated.
- **independent** — outcome EvalShift does not directly optimize (MoA recovery, minority
  coverage, marker enrichment). Closest to an unbiased test.

---

## exp08 — observed-population retrieval

| field | value |
|---|---|
| unit of analysis | per query (controlled SciPlex3 mixture) |
| sample size | full-run queries per task; Hit@1 averaged over tasks |
| test | descriptive (Hit@1 / nDCG@10 point estimates) |
| effect size | energy 0.837 vs mean/CMap 0.389 (Hit@1) |
| CI / p | not a hypothesis test — report as benchmark point estimates |
| metric class | **circular-risk** (energy vs mean on observed populations; upper-bound / oracle setting — state this) |

## exp08 Claim-1 identity

| field | value |
|---|---|
| statement | `mean_cosine` = `cmap_cosine` = 0.388492 (exact) |
| basis | algebraic identity of the cosine kernel, confirmed in source; **not** a statistical test |
| metric class | n/a (identity) |

## exp09 — predict-then-rank (information-condition boundary)

| field | value |
|---|---|
| unit of analysis | per query, per (predictor × retrieval); n = 720 per cell |
| effect size | EvalShift−mean nDCG delta: −0.004 / −0.097 / −0.029 |
| test | paired comparison within predictor (delta of matched queries) |
| metric class | **independent-ish** — nDCG on real-drug candidates; EvalShift does not optimize it |
| caveat | Hit@1 shows EvalShift winning on 2/3 predictors — report the nDCG delta *and* the mixed Hit@1 (Supp. S4); do not summarize as "all negative" |

## exp09 structure diagnostics

| field | value |
|---|---|
| unit | per (source × predictor × drug × seed) population |
| effect size | subpop_var_ratio 0.046 vs 0.009; diversity 0.158 vs 0.057; isotropy 0.959 vs 0.998 |
| test | group means (real vs predicted); report distributions, not just means |
| metric class | **independent** (structural properties, no EvalShift objective involved) |

## HIR-Bench (FULL 13,440 cells)

| field | value |
|---|---|
| unit | benchmark cell (grid_id × seed) |
| sanity | no_conflict_flip_rate 0.0 (thr 0.05); boundary margin 0.2917 (thr 1.0); predicted_mean gap 0.0507 (thr 0.10) — all pass |
| predictability | AUC = 0.640 (n_pos 8640, n_neg 4800); leave-one-grid-out CV |
| metric class | **proxy** (synthetic welfare oracle) |
| caveat | AUC is *moderate*; use FULL values, not on-disk QUICK CSVs (AUC 0.5) |

## exp12 — partial-observed retrieval (the boundary audit)

| field | value |
|---|---|
| unit | per query; n = 621 (DART_recommended), 133 (mean_or_no_call), 11 (mean_sufficient) |
| energy-proxy effect | DART_coverage_worst regret reduction: mean +0.264, **median +0.113**, 72% improved |
| test | **paired Wilcoxon** signed-rank vs mean_cosine; p = 4.26e-56 |
| multiple testing | 5 EvalShift methods × 3 modes compared; report best-per-mode, note the family |
| metric class (regret) | **circular-risk** — energy-based welfare proxy aligned with EvalShift's objective |
| non-circular effects | MoA-recovery nDCG gain −0.013; minority-coverage gain +0.005 (≈0) |
| metric class (nDCG/coverage) | **independent** — near-null, reported alongside the positive |
| gate discrimination | recommended +0.119 vs non-recommended +0.122 median (does not separate) |

## exp13 — real-data projection

| field | value |
|---|---|
| unit | real task (dataset × held-out × seed); n = 37 (QUICK-scale projection) |
| primary result | 70.3% projection agreement; predicted_mean→no-DART 100% |
| independent criterion | **0 / 37 tasks EvalShift-dominant** under minority-coverage outcome |
| metric class | **independent** (minority coverage, not EvalShift's objective) |
| test | agreement fraction; per-dataset PASS at ≥0.6 |

## exp15 — exploratory resistance divergence

| field | value |
|---|---|
| unit | per (context × KO); 450 rows FULL (IFNγ + Co-culture) |
| effect size | AXL/mesenchymal corr +0.134; IFN corr +0.042; antigen +0.037 |
| test | **Mann–Whitney U** (high- vs low-divergence split) + Pearson correlation |
| p-values | AXL 0.003; IFN 1.9e-6; antigen 0.044; quiescence 7.7e-7 (sign-flips, not claimed) |
| multiple testing | 5 programs tested — apply/report Benjamini–Hochberg; AXL/IFN survive, antigen marginal |
| metric class | **exploratory / independent** — marker enrichment; no EvalShift objective |
| hard limitation | no drug timecourse → Part B (survival) not evaluable; Part C rescue near-null |

---

## Global reporting rules

1. State the **unit of analysis** for every p-value (per query, per cell, per task).
2. For exp12, **never report +0.119 without the −0.013** in the same sentence or caption.
3. Label every headline metric with its class (circular-risk / proxy / independent).
4. exp15 p-values get **BH correction** and the "exploratory" qualifier.
5. Report the energy-welfare regret as **median** with Wilcoxon (skewed distribution), not
   mean alone.
