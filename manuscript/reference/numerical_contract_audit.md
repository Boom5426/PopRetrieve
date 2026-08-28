# Numerical-contract audit, R3 to R5

**Status:** complete, and updated 2026-07-29 after the author decisions were applied. **R3, R4 and R5
prose are all unblocked**; drafts are in `manuscript/rewrite/`. C-1, C-2, C-3 and D-2 are applied.
U-1 is blocked to Methods only (its value does not enter R4). U-2 resolved to a **FAIL** that is
handled by withholding the number, and it leaves one repair outstanding in the existing `.tex`.

**Date:** 2026-07-29
**Scope:** every main-text numerical claim in the approved R3, R4 and R5 sections, plus the recovery of
the manuscript's MoA-defined query set reported as `n = 600`.
**Audit code:** `analysis/audit/numerical_contract_stage1.py` (recovery and recomputation) and
`analysis/audit/numerical_contract_stage2.py` (paired tests), both committed and re-runnable from any
working directory. Outputs land in `results/audit/`. See Appendix B.

**Statistical-software caveat, stated up front.** `scipy` is not installed in any interpreter on this
machine. The Wilcoxon signed-rank normal approximation used below is implemented in
`numerical_contract_stage2.py` with average-rank tie handling, the standard tie-corrected variance
`n(n+1)(2n+1)/24 - sum(t^3-t)/48`, zeros dropped (`zero_method='wilcox'`), and no continuity
correction. It was validated against two p-values the project's own scipy-based pipeline had already
written into the manuscript:

| Quantity | Project pipeline (scipy) | This audit (hand-rolled) | Agreement |
|---|---|---|---|
| Class A, coverage-worst vs mean cosine, n = 765 | `1.6e-66` | `1.5680e-66` | exact to 2 s.f. |
| Class B, coverage-worst vs mean cosine, n = 600 | `2.4e-4` | `2.4614e-4` | exact to 2 s.f. |

Both match, so the implementation is treated as sound for every other test in this document.

---

## 1. Provenance findings

### 1.1 The `n = 600` set is recovered exactly

**Code path.** `src/experiments/exp16_common.py`, lines 26 to 57. The rule is documented there and
nowhere else in the repository:

> `exp12` encodes "this metric is undefined for this split type" as the literal value `-1`, not as
> `NaN` (`exp12_partial_observed_retrieval.py`, the `leave_MoA_out` and `partial_library` branches).
> Mechanism-of-action recovery is undefined for `leave_MoA_out`, because the whole MoA class is
> removed from the library, and for `partial_library`. [...] On the shipped `per_query_scores.csv`
> that is 165 of 765 queries (21.6%): 120 `leave_MoA_out` + 45 `partial_library`.

`mask_undefined()` sets `moa_ndcg <= -1 + 1e-9` to `NaN` for the metric list
`SENTINEL_METRICS = ("moa_hit@1", "moa_hit@5", "moa_mrr", "moa_ndcg", "moa_rank", "target_hit@5", "target_mrr")`.

**Applying it gives exactly 600.** Verified by execution:

```
n_total 765 | moa_defined 600 | rejected-rule (n_gt_moa > 0) 579
splits   {'leave_MoA_out': 120, 'leave_drug_out': 600, 'partial_library': 45}
sentinel {'leave_MoA_out': 120, 'partial_library': 45}
```

The MoA-defined set is **identically the `split_type == 'leave_drug_out'` stratum**. The sentinel is a
property of the split type, not of an individual query, so the two definitions coincide exactly and
neither is an approximation of the other.

**The `n_gt_moa > 0` rule is rejected.** It yields 579 and is not the original rule. It was my working
hypothesis in the previous session and it is wrong: 21 of the 600 `leave_drug_out` queries have
`n_gt_moa == 0` yet a defined (non-sentinel) `moa_ndcg`, so filtering on `n_gt_moa` silently drops
them. Every value I reported from the 579 set in the previous session is superseded by this document.

### 1.2 Query-set identifiers

**Query key:** `(split_type, cell_line, heldout_drug, observed_library_fraction, information_condition_mode, seed)`.
This key is unique across the 6,885 rows at 9 methods per query, giving 765 distinct queries.

| Set | n | SHA-256 of the sorted, pipe-joined, newline-separated identifiers |
|---|---:|---|
| All partial-observed | 765 | `11e6c902577e06dde041a94a75502266d748b8426175426d34d7c7a65dd9baa1` |
| **MoA-defined (`n = 600`)** | 600 | `1dda00b16e71fedba7e12bc1a6f66d51cf4762714cc359b4c2141ceb0ab6650b` |

The full 600-row identifier list is written to `results/audit/moa_defined_query_set.csv`. Recomputing
the hash is the cheapest way for any future pass to prove it is using the same set.

### 1.3 Inclusion and exclusion

- **Inclusion criterion:** `moa_ndcg` is not at the `-1` sentinel for the query, equivalently
  `split_type == 'leave_drug_out'`.
- **Exclusion count:** 165 of 765 (21.6%).
- **Exclusion reasons:** 120 `leave_MoA_out` (the entire MoA class is removed from the candidate
  library, so MoA recovery is undefined by construction) and 45 `partial_library` (same reason,
  applied to a partially observed library).

### 1.4 Identical-query-set confirmation

All ten variant series that feed the two published ranges (5 Class-A + 5 Class-B) were checked for
set identity after `dropna()`. Result: **`True`, all ten on the same 600 queries.** No variant loses a
query to a missing value in either metric class. The two ranges are therefore directly comparable
once C-1 below is applied.

### 1.5 Two independent provenance defects found outside the `n = 600` question

- **`figures/fig3/fig3a.py`, line 5** states "energy 0.837 vs mean/CMap cosine **0.389**". The
  reproduced value is `0.388492`, which the manuscript correctly prints as 0.388. The figure
  docstring is wrong. Code comment only, no rendered number affected.
- **A value collision in R4.** The uncorrected-oracle energy correlation (`+0.0967`) and the
  magnitude-partialled energy correlation (`+0.0969`) both print as **`+0.097`**, and the manuscript
  quotes them 21 lines apart at [:469](../latex/PopRetrieve_manuscript.tex#L469) and
  [:490](../latex/PopRetrieve_manuscript.tex#L490) as if they were the same kind of quantity. They are
  two unrelated statistics. Both values are individually correct. See D-2.

---

## 2. Exact denominator tree

Every R3 and R4 partial-observed number lives on this tree. One `per_query_scores.csv`, one query key,
765 leaves.

```
765   all partial-observed queries          per_query_scores.csv, 6,885 rows / 9 methods
 │                                          sha256 11e6c902...
 │
 ├── by evaluator definability (the R4 axis)
 │    ├── 600  MoA-defined      split_type == 'leave_drug_out'      sha256 1dda00b1...
 │    └── 165  MoA-undefined    120 leave_MoA_out + 45 partial_library
 │
 └── by gate label (the R4-P4 axis, recommendation_mode)
      ├── 621  DART_recommended
      ├── 133  mean_or_no_call        (the manuscript's "non-recommended")
      └──  11  mean_sufficient
```

The two partitions are **independent cuts of the same 765 queries**. They are not nested, and a value
computed on one cut cannot be quoted alongside a value computed on the other. That is precisely the
defect C-1 records.

Class-A regret (`decision_regret`) is defined on all 765. Class-B recovery (`moa_ndcg`) is defined on
600. R3 therefore reports on 765 and R4 reports on 600, and the manuscript's decision to hold both
metric classes on the same 600 for the A-to-B comparison is correct and should be kept.

---

## 3. Numerical-contract tables

Common conventions:

- **Class A comparison direction:** `mean_cosine - variant` on `decision_regret`. Positive means the
  distributional variant incurs less decision regret, i.e. is better.
- **Class B comparison direction:** `variant - mean_cosine` on `moa_ndcg`. Positive means the
  distributional variant recovers mechanism better.
- **Baseline** is `mean_cosine` throughout. `cmap_match` is numerically identical to it on Hit@1
  (see R3-01) but is a distinct column and was not used as the baseline.
- **Aggregation** is stated per row. Hit@1 rows are unweighted macro-means over the seven
  (task x setting) cells unless marked otherwise.

### 3.1 R3, objective-aligned gain

| # | Claim (manuscript) | Query set | n | Source file | Source columns | Aggregation | Direction | Reproduced | Manuscript | Verdict |
|---|---|---|---:|---|---|---|---|---|---|---|
| R3-01 | mean cosine and CMap cosine are numerically identical | 7 cells | 7 | `results/exp08_signature_baselines/summary.csv` | `hit@1`, `method` | unweighted macro-mean | identity | `0.388492` both | `0.3885` / `0.388492` | **PASS** |
| R3-02 | energy Hit@1 | 7 cells | 7 | same | `hit@1` | unweighted macro-mean | absolute | `0.836905` | `0.837` | **PASS** |
| R3-03 | PCA-distance vs PCA-mean Hit@1 | 7 cells | 7 | same | `hit@1` | unweighted macro-mean | absolute | `0.778175` / `0.517857` | `0.778` / `0.518` | **PASS** |
| R3-04 | query-weighted macro-mean (sensitivity) | 7 cells | 7 | same | `hit@1`, `n_queries` | weighted macro-mean | absolute | `0.886508` / `0.421429` | `0.887` / `0.421` | **PASS** |
| R3-05 | Frangieh counterexample, mean beats energy | Frangieh cell | 90 | same | `hit@1` | single cell | absolute | `0.600000` / `0.577778` | `0.600` / `0.578` | **PASS** |
| R3-06 | WTCS is a rank-based sibling, not identical | 7 cells | 7 | same | `hit@1` | unweighted macro-mean | absolute | `0.463492` | `0.4635` | **PASS** |
| R3-07 | median regret reduction, coverage-worst | all765 | 765 | `results/exp12_partial_observed_retrieval/per_query_scores.csv` | `decision_regret` | median of paired diff | `mean_cosine - variant` | `+0.11826` | `+0.118` | **PASS** |
| R3-08 | mean regret reduction | all765 | 765 | same | `decision_regret` | mean of paired diff | same | `+0.25790` | `+0.258` | **PASS** |
| R3-09 | fraction of queries improved | all765 | 765 | same | `decision_regret` | fraction `> 0` | same | `0.7203` | `72%` | **PASS** |
| R3-10 | paired Wilcoxon | all765 | 765 | same | `decision_regret` | two-sided, zeros dropped (710 used, 55 tied) | same | `T = 32002`, `z = -17.230`, `p = 1.568e-66` | `p = 1.6e-66` | **PASS** |
| R3-11 | gate-recommended subset is indistinguishable | recommended621 | 621 | same | `decision_regret`, `recommendation_mode` | median of paired diff | same | `+0.11900` | `+0.119` | **PASS** |
| R3-12 | all five variants show positive Class-A gain | all765 | 765 | same | `decision_regret` | median of paired diff | same | `+0.0495` to `+0.1183`, all `> 0` | "all five positive" | **PASS** |
| R3-13 | beta interpolation spans mean to worst-case | controlled | 10 beta values | `results/exp06_theory_limits/beta_interpolation.csv` | `D_beta`, `mean`, `max` | endpoints | absolute | `0.712500` to `1.300000`, endpoints exact | `0.7125` to `1.300` | **PASS** |
| R3-14 | global energy equals K=1 coverage exactly | Panobinostat | 1 | `results/exp06_theory_limits/degenerate_limit_real.csv` | `global_energy`, `coverage_K1` | identity | difference | both `0.10994338989257812`, diff `0` | `0.1099`, difference 0 | **PASS** |
| R3-15 | dataset positions on the divergence axis | 3 datasets | 3 | `results/exp02_divergence_gate/dataset_positions_on_gate.csv` | `typical_cross_cos` | median per dataset | absolute | `0.03236` / `0.70860` / `0.18574` | `0.032` / `0.709` / `0.186` | **PASS** |

**R3 verdict: 15 of 15 PASS.** R3 prose is unblocked.

### 3.2 R4, the independent evaluator ladder

All partial-observed rows use `results/exp12_partial_observed_retrieval/per_query_scores.csv`.

| # | Claim (manuscript) | Query set | n | Source columns | Aggregation | Direction | Reproduced | Manuscript | Verdict |
|---|---|---:|---:|---|---|---|---|---|---|
| R4-01 | both metric classes defined on 600 queries | moa600 | 600 | `moa_ndcg` sentinel mask | count | n/a | `600` | `600` | **PASS** |
| R4-02 | 165 excluded, MoA undefined | complement | 165 | `split_type` | count | n/a | `120 + 45 = 165` | `165` | **PASS** |
| R4-03 | Class-A median, coverage-worst | moa600 | 600 | `decision_regret` | median | `mean - variant` | `+0.12883` | `+0.129` | **PASS** |
| R4-04 | Class-A mean, coverage-worst | moa600 | 600 | `decision_regret` | mean | `mean - variant` | `+0.27515` | `+0.275` | **PASS** |
| R4-05 | Class-B median vanishes exactly | moa600 | 600 | `moa_ndcg` | median | `variant - mean` | `+0.00000` | `0.000` | **PASS** |
| R4-06 | Class-B mean turns negative | moa600 | 600 | `moa_ndcg` | mean | `variant - mean` | `-0.03707` | `-0.037` | **PASS** |
| R4-07 | fraction worsened | moa600 | 600 | `moa_ndcg` | fraction `< 0` | `variant - mean` | `0.4133` | `41.3%` | **PASS** |
| R4-08 | fraction improved | moa600 | 600 | `moa_ndcg` | fraction `> 0` | `variant - mean` | `0.3417` | `34.2%` | **PASS** |
| R4-09 | Class-B paired Wilcoxon | moa600 | 600 | `moa_ndcg` | two-sided, zeros dropped (453 used, 147 tied) | `variant - mean` | `T = 41194.5`, `z = -3.666`, `p = 2.461e-4` | `p = 2.4e-4` | **PASS** |
| **R4-10** | **five-variant Class-A range** | **moa600** | **600** | `decision_regret` | median per variant | `mean - variant` | **`+0.053` to `+0.129`** | **`+0.056` to `+0.129`** | **FAIL, see C-1** |
| R4-11 | five-variant Class-B range | moa600 | 600 | `moa_ndcg` | mean per variant | `variant - mean` | `-0.0111` to `-0.0371` | `-0.011` to `-0.037` | **PASS** |
| **R4-12** | **per-class best-scorer selection would report `+0.119` against `-0.013`** | mixed | 621 / 600 | `decision_regret`, `moa_ndcg` | best variant per class | mixed | `+0.119` on 621; the least-negative Class-B variant is **mmd at `-0.0111`**, not `-0.013` | `+0.119` / `-0.013` | **FAIL, see C-2** |
| R4-13 | gate does not concentrate the gain | recommended621 / nonrec133 | 621 / 133 | `decision_regret`, `recommendation_mode` | median | `mean - variant` | `+0.11900` / `+0.12194` | `+0.119` / `+0.122` | **PASS** |
| R4-14 | 11 queries labelled mean-sufficient | meansufficient11 | 11 | `recommendation_mode` | count | n/a | `11` | `11` | **PASS** |
| R4-15 | real-data coverage advantage, all tasks | exp13 | 239 | `results/exp13_real_data_projection/projection.csv`, `observed_dart_minority_cov`, `observed_mean_minority_cov` | mean | `dart - mean` | `+0.001806` | `+0.0018` | **PASS** |
| **R4-16** | **Wilcoxon on the tasks with a nonzero difference** | exp13 | 137 | same | Wilcoxon | `dart - mean` | **two-sided `2.620e-7`**; `1.3e-7` is the **one-sided** half | `p = 1.3e-7` | **FAIL, see C-3** |
| R4-17 | tasks with an exactly zero difference | exp13 | 239 | same | count `== 0` | `dart - mean` | `102` | `102` | **PASS** |
| R4-18 | metric operating range | exp13 | 239 | same | min / max over both arms | absolute | `[0.5999, 0.9969]` | `[0.60, 1.00]` | **PASS** |
| R4-19 | per-dataset breakdown | exp13 | 90/90/23/12/24 | same, `dataset` | mean per dataset | `dart - mean` | `+0.004264` / `+0.000382` / `+0.000420` / `+0.000269` / `+0.000030` | `+0.0043` / `+0.0004` / `+0.0004` / `+0.0003` / `+0.00003` | **PASS** |
| R4-20 | Class C, energy vs correctly specified mean incumbent | class-C | 103 | `results/upgrade/class_c_functional_oracle.json` | median Spearman | absolute | `0.276089` / `0.082553` | `+0.276` / `+0.083` | **PASS** |
| R4-21 | magnitude-matching scalar | class-C | 103 | same | median Spearman | absolute | `0.231780` | `+0.232` | **PASS** |
| R4-22 | energy after partialling magnitude out | class-C | 103 | same | median partial Spearman | absolute | `0.096925` | `+0.097` | **PASS** |
| R4-23 | per-line residual | class-C | 34/34/35 | same, `per_line` | per-line partial Spearman | absolute | `0.1307` / `0.0533` / `0.1624` | `+0.131` / `+0.053` / `+0.162` | **PASS** |
| R4-24 | energy beats the scalar on 62 of 103, not significantly | class-C | 103 | `results/upgrade/class_c_functional_oracle.csv`, `energy_rho`, `magnitude_match_rho` | count `> 0`; two-sided Wilcoxon | `energy - magmatch` | `62 of 103`; `T = 2132.5`, `z = -1.795`, `p = 0.07271` | `62 of 103`, `p = 0.073` | **PASS** |
| R4-25 | query-independent magnitude ordering | class-C | 103 | `class_c_functional_oracle.json` | median Spearman | absolute | `-0.330214`, so the reversed ordering gives `+0.330` | `-0.330` / `+0.330` | **PASS** |
| R4-26 | potency matching | class-C | 103 | same | median Spearman | absolute | `0.398730` | `+0.399` | **PASS** |
| R4-27 | mean baseline scored without control subtraction | class-C | 103 | same | median Spearman | absolute | `0.241253` | `+0.241` | **PASS** |
| R4-28 | uncorrected oracle reverses the ordering | class-C | 103 | `class_c_functional_oracle.csv`, `*_uncentered` | median Spearman | absolute | energy `0.096715`, mean incumbent `0.138035`, magnitude scalar `0.216912` | `+0.097` / `+0.138` / `+0.217` | **PASS**, but see D-2 |
| R4-29 | confounder audit, mismatched potency oracle | class-C | 103 | `results/upgrade/class_c_magnitude_control_v2.json` | median Spearman | absolute | energy `-0.520244`, magnitude-only `+0.691845`, energy-vs-candidate-magnitude `+0.790985` | `-0.520` / `+0.692` / `+0.791` | **PASS** |
| R4-30 | oracle scale parameters | class-C | 103 | `class_c_functional_oracle.json` | n/a | n/a | `n_queries = 103`, oracle string records 966 held-out lines and centering on all 286 GDSC2 compounds | `103` / `966` / `286` | **PASS** |
| R4-31 | `\CENTERUNCEN`, "85% of drug pairs positive, median +0.178, versus 52% and +0.015 once corrected" | GDSC2 similarity matrix | n/a | printed by `analysis/class_c/class_c_functional_oracle.py` line 149 to stdout; persistence added 2026-07-29, re-run blocked | n/a | n/a | **not reproducible from any saved artifact** | as quoted | **BLOCKED, see U-1 update. Methods only, absent from R4 prose** |
| R4-32 | the five variants order themselves oppositely under the two criteria | MoA-defined | 600 (5 variants) | `decision_regret` and `moa_ndcg` | Spearman of the two variant rankings | rank-vs-rank | Class A ranks `1,2,3,4,5`, Class B ranks `4,5,3,2,1`, $\sum d^2 = 38$, $\rho = -0.90$ | **new, not in the current manuscript** | **PASS**, reported without a p-value ($n = 5$) |

**R4 verdict: 29 PASS, 3 FAIL corrected, 1 BLOCKED to Methods.** C-1, C-2 and C-3 are applied in
`manuscript/rewrite/R4_evaluator_ladder.md`; U-1's value does not appear in R4 under the approved
architecture, so **R4 prose is unblocked**. R4-32 is a new row: a free observation from data already
under contract, added because it is the variant-level form of the section's argument.

### 3.3 R5, oracle statistical form

Source: `results/upgrade/oracle_shape_test.json`.

| # | Claim (manuscript) | Query set | n | Source columns | Aggregation | Direction | Reproduced | Manuscript | Verdict |
|---|---|---|---:|---|---|---|---|---|---|
| R5-01 | mean beats energy under the mean-shaped oracle | Frangieh, all conditions | 659 | `mean_vs_oracleMEAN`, `energy_vs_oracleMEAN` | Spearman | absolute | `0.242099` / `0.146191` | `+0.242` / `+0.146` | **PASS** |
| R5-02 | energy beats mean under the distribution-shaped oracle | same | 659 | `energy_vs_oracleDIST`, `mean_vs_oracleDIST` | Spearman | absolute | `0.529107` / `0.333988` | `+0.529` / `+0.334` | **PASS** |
| R5-03 | the reversal holds in each of the three immune conditions | per condition | 213 / 227 / 219 | `per_condition` | Spearman per condition | absolute | Control `flips: true`, IFNg `flips: true`, Co-culture `flips: true`; all three have mean leading under MEAN and energy leading under DIST | "holds independently in each" | **PASS** |
| R5-04 | per-condition query counts | per condition | 213 / 227 / 219 | `per_condition.n` | count | n/a | Control 213, IFNg 227, Co-culture 219 | `213`, `227`, `219` | **PASS** |
| R5-05 | the magnitude scalar climbs as the oracle turns distributional | same | 659 | `magmatch_vs_oracleMEAN`, `magmatch_vs_oracleDIST` | Spearman | absolute | `0.124653` / `0.352353` | `+0.125` / `+0.352` | **PASS** |
| R5-06 | energy still leads the scalar under the distributional oracle | same | 659 | `magnitude_confound` | difference of Spearmans | `energy - magmatch` | `0.176754` under DIST, `0.021538` under MEAN | `+0.177` / `+0.022` | **PASS** |
| R5-07 | "20 surface proteins in the same 218,331 cells" | Frangieh | see U-2 | `class_c_protein_oracle.py:16,85`; `figures/source_data/ed1_dataset_scale.csv:3` | n/a | n/a | protein file **218,331**, RNA file and ED1a **218,023**, analysis unit is the barcode intersection of the two and is not persisted; panel is **24** measured, **4** isotype controls dropped, **20** used | `20` / `218,331` | **FAIL, see U-2 update** |

**R5 verdict: 6 PASS, 1 FAIL.** The failure is a dataset-scale descriptor, not a result, and it is
handled by withholding the cell count from the drafted prose. **R5 prose is unblocked.** The existing
`.tex` at [:549](../latex/PopRetrieve_manuscript.tex#L549) still carries the contradiction with Extended
Data Fig. 1 and must be repaired before submission.

**Note for R5 prose.** The total `n = 659` is in the artifact but is never stated in the manuscript,
which quotes only the three per-condition counts. `213 + 227 + 219 = 659`, so nothing is missing, but
stating the total once would let a reader add them up without doing arithmetic.

---

## 4. Unresolved failures

### C-1. The five-variant Class-A range is a cross-subset composite. REQUIRED CORRECTION.

**Location:** [`PopRetrieve_manuscript.tex:349`](../latex/PopRetrieve_manuscript.tex#L349),
"Class-A gain `+0.056` to `+0.129`".

**Finding.** The published lower bound and upper bound come from **two different query sets**.

| Query set | n | Class-A five-variant median range |
|---|---:|---|
| all partial-observed | 765 | `+0.0495` to `+0.1183` |
| gate-recommended | 621 | **`+0.0557`** to `+0.1190` |
| **MoA-defined (the set the paragraph is about)** | **600** | `+0.0533` to **`+0.1288`** |

`+0.056` is reproducible only on the 621-query gate-recommended subset. `+0.129` is reproducible only
on the 600-query MoA-defined subset. **No single denominator produces the published pair.** Per-variant
medians on the correct 600 set:

| Variant | Class-A median (600) | Class-B mean (600) |
|---|---:|---:|
| `DART_energy` | `+0.05332` | `-0.01290` |
| `DART_mmd` | `+0.06159` | `-0.01112` |
| `DART_sliced_wasserstein` | `+0.06329` | `-0.01597` |
| `DART_coverage_mean` | `+0.09328` | `-0.02475` |
| `DART_coverage_worst` | `+0.12883` | `-0.03707` |

The Class-B range `-0.011` to `-0.037` is correct as published and needs no change.

**Why this matters beyond arithmetic.** The sentence exists to establish that the A-to-B collapse does
not depend on which distributional variant is chosen. That argument requires both ranges to be on the
same queries. As published, they are not, so the sentence does not currently support its own claim.
After the correction it does, and the collapse is slightly larger than published, not smaller.

**Correction:** `+0.056 to +0.129` becomes **`+0.053 to +0.129`**. This is a change of one printed
digit and it strengthens the paragraph. It cannot be deferred, because R4-10 is a headline value.

### C-2. The best-scorer-selection figure `-0.013` cannot be reproduced under the stated rule. REQUIRED DISCLOSURE.

**Location:** [`PopRetrieve_manuscript.tex:337`](../latex/PopRetrieve_manuscript.tex#L337), "it would
report `+0.119` against `-0.013`".

**Finding.** `+0.119` reproduces exactly as the best Class-A variant (`coverage_worst`) on the
621-query gate-recommended subset. `-0.013` does **not** reproduce as "the best Class-B variant". On
the 600-query set the least-negative Class-B variant is **`DART_mmd` at `-0.0111`**, not `-0.013`.
`-0.0129` is the value for **`DART_energy`**, which is the third-least-negative of the five.

Three readings are possible and the artifact cannot distinguish them:

1. "Best" for Class B meant `DART_energy` under some selection rule not stated in the text.
2. The pair was computed on a variant set that excluded `mmd` and `sliced_wasserstein`.
3. `-0.013` was computed on a subset other than the 600.

**Status.** The sentence's *argument* survives under every reading: the cherry-picked pairing yields a
smaller collapse (`0.119` to `-0.013`, a drop of `0.132`) than the honest pairing (`0.129` to `-0.037`,
a drop of `0.166`), which is exactly the point being made. Only the second number is unattributable.

**Recommendation.** This sentence is already scheduled to move to Methods under the approved
architecture. Move it, and either (a) restate it with the reproducible pair `+0.119 against -0.011`,
which preserves the argument and strengthens it slightly, or (b) drop the numerals and state the
comparison qualitatively. Do not carry `-0.013` forward unattributed.

### C-3. One p-value is one-sided while its neighbours are two-sided. REQUIRED DISCLOSURE.

**Location:** [`PopRetrieve_manuscript.tex:355`](../latex/PopRetrieve_manuscript.tex#L355), "Wilcoxon
`p = 1.3e-7` on the 137 tasks with a nonzero difference".

**Finding.** The two-sided Wilcoxon on those 137 tasks gives `p = 2.620e-7`. Exactly half of that is
`1.310e-7`, which is what the manuscript prints. The value is therefore **one-sided**, and the
sidedness is not stated. Every other paired test in the manuscript that I could reproduce
(`1.6e-66` at R3-10, `2.4e-4` at R4-09, `0.073` at R4-24) is two-sided.

**Recommendation.** Report `p = 2.6e-7` two-sided, for consistency with the rest of the paper. The
conclusion is unchanged; the effect is described in the same sentence as "practically negligible", so
nothing rests on the factor of two. If a one-sided test was intended, it must be declared as
pre-specified, which would be hard to defend for a claim the paper elsewhere presents as a null.

### U-1. `\CENTERUNCEN` has no saved artifact.

**Location:** `PopRetrieve_manuscript.tex:109-110`, quoted at
[:464](../latex/PopRetrieve_manuscript.tex#L464): "85% of drug pairs positive, median `+0.178`, versus
52% and `+0.015` once corrected".

**Finding.** `analysis/class_c/class_c_functional_oracle.py` line 149 prints the centered-oracle
similarity summary to stdout. Neither the centered nor the uncentered off-diagonal similarity
distribution is written to any file under `results/`. The four numbers cannot be checked against a
saved artifact.

**Recommendation.** Add two lines to that script writing the off-diagonal similarity summaries to
`results/upgrade/class_c_oracle_similarity_summary.json`, re-run it, and re-derive the macro. This is
a five-minute fix and it is the only R4 number in the manuscript with no persisted provenance. Under
the standing rule that results without complete provenance must be regenerated or removed, and given
that this number justifies the centering choice on which the entire affirmative Class-C result
depends, **regeneration is the right call, not removal.**

### U-2. The Frangieh cell count is not checked in this audit.

**Location:** [`PopRetrieve_manuscript.tex:549`](../latex/PopRetrieve_manuscript.tex#L549), "20 surface
proteins in the same 218,331 cells".

**Finding.** `oracle_shape_test.json` records `n_queries = 659` and the three per-condition counts but
not the cell count. The figure is a dataset-scale descriptor rather than a result, and was not traced
in this pass.

**Recommendation.** Verify once against the loaded AnnData object at write-up time, or cite it to the
Frangieh source publication rather than to our own preprocessing.

### U-1 UPDATE, 2026-07-29. Persistence added, re-run BLOCKED in this environment.

**Code change made.** `analysis/class_c/class_c_functional_oracle.py` now writes
`results/upgrade/class_c_oracle_similarity_summary.json` from inside `build_functional_oracle()`,
carrying every field the author decision requires: `n_drug_pairs`, `frac_positive`,
`median_similarity` plus `q25`/`q75`/`min`/`max`, for **both** the `centered` and the `uncentered`
off-diagonal distributions; a `source_matrix` block with `n_drugs`, `n_cell_lines_after_holdout`,
`n_drugs_in_full_gdsc_matrix`, `min_shared_lines` and `median_shared_lines`; a prose
`centering_rule`; and `source_input`, a SHA-256 plus byte size of the GDSC2 workbook via the new
`_gdsc_provenance()` helper. Syntax checked; not executed.

**Re-run blocked.** Three prerequisites are absent from this machine:

| Prerequisite | State |
|---|---|
| `results/upgrade/GDSC2_fitted_dose_response.xlsx` | absent. Not redistributable (`DATA.md:51-59`); the verified release is 8.5, `GDSC2_fitted_dose_response_27Oct23.xlsx` |
| `scipy` | not installed in any interpreter |
| `data/processed` SciPlex3 tensor via `data.load_sciplex3` | not verified, and unreachable without the above |

**Consequence for R4: none.** Under the approved architecture the oracle-construction derivation and
the centering protocol both live in **Methods**, not in R4 (content-placement ledger, "Move to
Methods"). `\CENTERUNCEN` is quoted at [:464](../latex/PopRetrieve_manuscript.tex#L464), which is inside
the material being relocated. **R4 prose is therefore not blocked by U-1**, and the drafted R4 in
`manuscript/rewrite/R4_evaluator_ladder.md` contains no value from this artifact. U-1 blocks the
**Methods** paragraph only, and the block clears the moment the workbook and `scipy` are available.

### U-2 UPDATE, 2026-07-29. Resolved, and the finding is worse than the audit predicted.

Tracing "20 surface proteins in the same 218,331 cells" produced a defect rather than a confirmation.

| Fact | Source | Value |
|---|---|---|
| Rows in the protein h5ad | `analysis/class_c/class_c_protein_oracle.py:85` | **218,331** |
| Rows in the cached RNA tensor | same line | **218,023** |
| Frangieh cell count in the paper's own Extended Data Fig. 1a | `figures/source_data/ed1_dataset_scale.csv:3` | **218,023** |
| Cells actually analysed | `oracle_shape_test.py:103-106`, barcode intersection | `len(shared)`, printed to stdout, **never persisted** |
| Protein markers measured | `oracle_shape_test.py:67`, `class_c_protein_oracle.py:16` | **24** |
| Isotype controls dropped | same | **4** (`Rat_IgG2a`, `Mouse_IgG1`, `Mouse_IgG2a`, `Mouse_IgG2b`) |
| Protein markers used | derived | **20** |

Three findings:

1. **The main text contradicts Extended Data Fig. 1.** The main text says 218,331 and ED1a says
   218,023. Both are in the submitted package. A reviewer can find this in under a minute.
2. **Neither number is the analysis unit.** Both scripts inner-join RNA to protein on barcode and
   analyse only the intersection, which is at most 218,023 and in general smaller.
3. **The published sentence mixes filtering stages.** It pairs the **post-filter** protein count (20 of
   24) with a **pre-join** cell count. One of the two numbers has been filtered and the other has not.

**Code change made.** `analysis/class_c/oracle_shape_test.py` now writes
`results/upgrade/oracle_shape_join_provenance.json` with `n_cells_protein_file`, `n_cells_rna_file`,
`n_cells_joined_by_barcode`, `n_markers_measured`, `n_isotype_controls_dropped`, `n_markers_used`, the
marker list, the join rule, the ADT normalization, and a SHA-256 per source h5ad via `_h5ad_provenance()`.
The two pre-subset row counts are captured before `p` and `r` are overwritten by the barcode subset.
Syntax checked; not executed, because `data/raw/frangieh2021/` does not exist here and `anndata`,
`scanpy` and `scipy` are not installed.

**Consequence for R5: handled, not blocked.** The drafted R5 prints **no cell count**. It states the
join qualitatively ("in the same cells whose RNA the retrieval scores read"), which is exactly what a
barcode join licenses and all the section's argument requires, and it uses `\PROTMARKERS` = 20 with
the 24-minus-4 derivation given in Methods. `\SHAPECELLS` is deliberately left undefined and the macro
block carries a `TODO(U-2)` recording why. The total oracle-shape query count is stated once as
`\SHAPEN` = 659 with per-condition counts 213, 227 and 219, per the author decision.

**Outstanding and required before submission.** The main-text-versus-ED1 contradiction must be
resolved whichever way the re-run lands. Withholding the number from R5 removes it from the drafted
prose but does not repair the existing `.tex` at [:549](../latex/PopRetrieve_manuscript.tex#L549).

### D-1 to D-2. Two defects that are not failures.

- **D-1.** `figures/fig3/fig3a.py:5` says `0.389` where the reproduced value is `0.388492`. Code
  comment only. Fix in passing.
- **D-2.** `+0.097` denotes two unrelated quantities in R4, twenty-one lines apart: the uncorrected
  oracle's energy correlation ([:469](../latex/PopRetrieve_manuscript.tex#L469), reproduced `0.096715`)
  and the magnitude-partialled energy correlation ([:490](../latex/PopRetrieve_manuscript.tex#L490),
  reproduced `0.096925`). Both are correct. Under the approved architecture these land in R4-P7 and
  R4-P8, adjacent paragraphs, which makes the collision worse rather than better. **Print the
  uncorrected-oracle value to three decimals as `+0.0967` and the partial as `+0.097`, or vice versa,
  so a reader cannot mistake one for the other.** This is a presentation decision requiring author
  sign-off.

---

## 5. Proposed final numbers

Everything R4 prose needs, in the form it should be written. All values are on the 600-query
MoA-defined set (`sha256 1dda00b1...`) unless the row says otherwise.

### 5.1 R4 headline contract, locked

| Quantity | Final value | Set | n |
|---|---|---|---:|
| Class-A median, coverage-worst | `+0.129` | MoA-defined | 600 |
| Class-A mean, coverage-worst | `+0.275` | MoA-defined | 600 |
| Class-B median, coverage-worst | `0.000` | MoA-defined | 600 |
| Class-B mean, coverage-worst | `-0.037` | MoA-defined | 600 |
| Fraction worsened | `41.3%` | MoA-defined | 600 |
| Fraction improved | `34.2%` | MoA-defined | 600 |
| Fraction tied | `24.5%` (new, optional) | MoA-defined | 600 |
| Paired Wilcoxon, two-sided | `p = 2.4e-4` | MoA-defined | 600 |
| **Class-A five-variant range** | **`+0.053 to +0.129`** (was `+0.056 to +0.129`) | MoA-defined | 600 |
| Class-B five-variant range | `-0.011 to -0.037` | MoA-defined | 600 |
| Excluded queries | `165` (120 `leave_MoA_out`, 45 `partial_library`) | complement | 165 |

### 5.2 R3 headline contract, locked

| Quantity | Final value | Set | n |
|---|---|---|---:|
| Energy Hit@1, unweighted macro-mean | `0.837` | 7 cells | 7 |
| Mean / CMap cosine Hit@1 | `0.388` (`0.388492`, identical to six figures) | 7 cells | 7 |
| Query-weighted sensitivity | `0.887` / `0.421` | 7 cells | 7 |
| Frangieh counterexample | mean `0.600` beats energy `0.578` | Frangieh | 90 |
| Median regret reduction | `+0.118` | all partial-observed | 765 |
| Mean regret reduction | `+0.258` | all partial-observed | 765 |
| Fraction improved | `72%` | all partial-observed | 765 |
| Paired Wilcoxon, two-sided | `p = 1.6e-66` | all partial-observed | 765 |

### 5.3 Values whose printing must change

| Location | Current | Proposed | Reason |
|---|---|---|---|
| [:349](../latex/PopRetrieve_manuscript.tex#L349) | `+0.056 to +0.129` | `+0.053 to +0.129` | C-1, cross-subset composite |
| [:337](../latex/PopRetrieve_manuscript.tex#L337) | `+0.119 against -0.013` | `+0.119 against -0.011`, moved to Methods | C-2, `-0.013` unattributable |
| [:355](../latex/PopRetrieve_manuscript.tex#L355) | `p = 1.3e-7` | `p = 2.6e-7` (two-sided) | C-3, sidedness inconsistent with the rest of the paper |
| [:469](../latex/PopRetrieve_manuscript.tex#L469) | `+0.097` | `+0.0967` | D-2, collides with the partial at [:490](../latex/PopRetrieve_manuscript.tex#L490) |
| `figures/fig3/fig3a.py:5` | `0.389` | `0.388` | D-1, code comment |

### 5.4 Single-source macros to add

Under the existing macro discipline (134 macros at `PopRetrieve_manuscript.tex:46-110`), the four
partial-observed denominators should each become a macro so no future edit can reintroduce C-1:

```latex
\newcommand{\NALL}{765}        % all partial-observed queries
\newcommand{\NMOA}{600}        % MoA-defined (split_type == leave_drug_out)
\newcommand{\NREC}{621}        % gate-recommended
\newcommand{\NNONREC}{133}     % non-recommended (mean_or_no_call)
\newcommand{\CLASSARANGE}{+0.053 to +0.129}
\newcommand{\CLASSBRANGE}{-0.011 to -0.037}
```

---

## 结论

1. **`n = 600` 已精确复原**，规则是 `src/experiments/exp16_common.py` 记录的 `-1` 哨兵掩码，等价于
   `split_type == 'leave_drug_out'`。上一轮我用的 `n_gt_moa > 0` 规则（得 579）是错的，本文档取代
   上一轮所有基于 579 的数值。
2. **R3 全部 15 项通过，R5 六项通过一项待核（仅为数据规模描述符）。这两节可以立即动笔。**
3. **R4 三项不通过：** C-1（五变体 Class-A 区间是跨子集拼接，须改为 `+0.053 to +0.129`）、
   C-2（`-0.013` 在任何声明规则下都复现不出）、C-3（一个 p 值是单侧，而全文其余为双侧）。
   另有 U-1（`\CENTERUNCEN` 无落盘产物）与 D-2（两个不同量都印成 `+0.097`）。
4. **关键判断：C-1 修正后论证变强而非变弱。** A 到 B 的塌缩比已发表版本略大，且两个区间此后共享同一
   600 条查询，那句"结论不取决于变体选择"才第一次真正成立。

## 建议

- 立即执行 C-1、C-3 与 D-1（各改一处，零风险）。
- C-2 的句子按已批准架构移入 Methods，同时改用可复现的 `-0.011`。
- U-1 补两行落盘代码后重跑 `analysis/class_c/class_c_functional_oracle.py`。这是全文唯一一个无落盘
  证据、却支撑着 Class-C 校正选择的数字，按"无完整 provenance 者须重生成或删除"的规则，应当重生成。
- D-2 的印刷位数需要你拍板。
- 上述五项完成后，R4 散文解锁。R3 与 R5 不必等待。

## 风险

- **本审计的统计实现风险已被压到最低但不为零。** 本机无 scipy，Wilcoxon 由本文档自带实现，已用项目
  自身 scipy 管线产出的两个 p 值（`1.6e-66` 与 `2.4e-4`）双向验证，均精确吻合。若日后在装有 scipy
  的环境复核，应优先重跑 `audit_stage2.py` 的对照两行。
- **U-1 若选择删除而非重生成，则 Class-C 校正的辩护性会显著下降**，因为 `\CENTERUNCEN` 正是"未校正
  的 oracle 让几乎所有药对看起来相似"这一论证的唯一定量支撑。
- **本审计只覆盖 R3 到 R5。** R6 与 R7 的门统计量、Tahoe 宏、患者肿瘤数值尚未过合同，动笔前需要同等
  强度的一轮。

---

## Appendix A. Approved architecture revisions, recorded

Applied to the architecture approved in the previous turn. No prose written.

| # | Revision | Status |
|---|---|---|
| A-1 | R6 carries only 2 to 3 main-text sentences on HIR-Bench; construction, analytic boundary, AUC values, pseudo-replication analysis and transfer failure move to Supplementary Information | recorded, supersedes the 175-word R6-P8 paragraph |
| A-2 | The Gate-2 gap is never called "solvable". Wording: "The gap localizes the current limitation to recoverability rather than absence of information, identifying an algorithmic target for future methods." | recorded, applies to R7-P2 and Discussion D3 and D7 |
| A-3 | The rhetorical Tahoe sentence ("A condition that is usually met and sometimes not is a condition...") is deleted and replaced by a direct empirical statement | recorded, applies to R7-P5 |
| A-4 | R5 does not interpret the distribution-shaped protein oracle as establishing external utility. The controlled swap demonstrates evaluator-form dependence: the same protein measurements contain both mean-level and distribution-level structure, and the analysis does not determine which representation is more useful for an external decision | recorded, applies to R5-P4 |
| A-5 | The six Discussion controls consolidate into four groups: task alignment; baseline adequacy; prospective population specification; evaluator robustness | recorded, applies to Discussion D5 |
| A-6 | Six versus seven main figures is not finalized. Recorded only: the oracle-form reversal requires prominent visual treatment | recorded |

Author decisions carried forward: Frangieh retained in R3 main text; unweighted macro-mean primary and
query-weighted a sensitivity analysis; `rho = 0.835` is the main disjoint Gate-3 premise statistic with
`rho = 0.878` moved to Methods or SI; the two surviving HDAC drugs are SI-only; Gate 3 is a required
candidate-preference-change condition and not a demonstrated binding condition; the uncorrected mean
baseline (`+0.241`) is retained in the Discussion baseline-adequacy recommendation; Abstract targets
170 to 175 words; HIR-Bench or predictor results without complete provenance must be regenerated or
removed even in SI.

Revised word budget, unchanged from the approved architecture except that R6 loses roughly 120 words
to A-1: Abstract 172, Introduction 1,100, R1 400, R2 575, R3 525, R4 1,350, R5 575, R6 1,230,
R7 1,150, Discussion 1,700. Main text total **8,605**, inside the 8,000 to 9,000 ideal band and
1,395 words below the 10,000 hard ceiling.

## Appendix B. Reproduction recipe

Both scripts are committed to the repository and take no arguments. Paths resolve from `__file__`, so
they run from any working directory.

```bash
python3 analysis/audit/numerical_contract_stage1.py   # recovery, denominator tree, recomputations
python3 analysis/audit/numerical_contract_stage2.py   # paired tests on the dumped difference vectors
```

Stage 1 imports the project's own `mask_undefined` from `src/experiments/exp16_common.py` rather than
reimplementing the sentinel rule, so the recovery of `n = 600` is by construction the same code path
the original analysis used. Outputs are written to `results/audit/`:

| File | Contents |
|---|---|
| `moa_defined_query_set.csv` | the 600 query identifiers, one row each |
| `audit_stage1.json` | denominator tree, every Class-A and Class-B block on all five subsets, the oracle JSONs, the uncentered medians |
| `paired_diffs.npz` | the eleven paired-difference vectors stage 2 tests |
| `audit_stage2.json` | medians, means, sd, improved/worsened/tied fractions, Wilcoxon under both zero methods |

To confirm a future pass is on the same query set:

```python
import hashlib, pandas as pd
KEY = ["split_type", "cell_line", "heldout_drug", "observed_library_fraction",
       "information_condition_mode", "seed"]
q = pd.read_csv("results/audit/moa_defined_query_set.csv")[KEY]
lines = ["|".join(str(x) for x in t) for t in sorted(map(tuple, q.values))]
assert hashlib.sha256("\n".join(lines).encode()).hexdigest().startswith("1dda00b1")
```
