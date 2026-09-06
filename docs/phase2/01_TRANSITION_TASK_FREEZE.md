# 01. Transition-to-intervention retrieval: task freeze

Frozen 2026-09-02 against
[`PopRetrieve_PhaseII_Transition_to_Intervention_Retrieval_Frozen_Plan.md`](../PopRetrieve_PhaseII_Transition_to_Intervention_Retrieval_Frozen_Plan.md).
Everything below is fixed before any retrieval number exists. Later phases may change the
predictor and nothing else.

## 1. The task

Given a held-out cellular context `c`:

- `X_source` = the untreated (DMSO_TF) control cells of `c`;
- `X_target` = a desired treated single-cell population in `c`;
- `D` = a fixed candidate drug library;

produce a ranking of `D` by

    d* = argmin_d  Dist( f_theta(X_source, d),  X_target ).

The algorithm never sees the identity of the drug that generated `X_target`. That identity is
held only by the evaluator, and only to compute the rank of the true intervention.

## 2. Frozen inputs, outputs and axes

| Item | Frozen value |
|---|---|
| Input | `X_source` + `X_target` + candidate drug IDs |
| Output | a ranking over the candidate library |
| Generalization axis | unseen cellular context, seen candidate drugs |
| Ground truth | the drug that actually generated `X_target` |
| Primary dataset | Tahoe-100M plate 3, preprocessed release |
| Secondary replication | SciPlex3, identical task definition, split and metrics |

Forbidden substitutions, restated so a later reader can check compliance without the plan in
hand: the query may not become the target response alone; observed candidate responses in the
held-out context may not enter primary retrieval; drug-drug response similarity, MoA labels and
query drug identity may not be inputs; and the main output may not become response prediction,
clustering, classification or similarity estimation. Those are diagnostics only.

## 3. Primary data, as the file actually ships

Source file, hashed at freeze time:

```
plate3_filt_Vevo_Tahoe100M_WServicesFrom_ParseGigalab_preprocessed_cpu.h5ad
5,858,821,682 bytes
sha256 dfca387b6d7e35e49a841ac708be8ad151227317d98302cf91a44dc69daff6bb
4,158,278 cells x 2,304 genes, log1p, single plate `plate3`
```

Two points where the plan's prose and the file disagree, resolved in favour of the file and
recorded here so that neither is silently corrected later:

1. **The library is 92 compounds, not 93.** `obs['drug']` carries 93 categories, one of which is
   the vehicle arm `DMSO_TF`. The vehicle is the source of `X_source` and is not a candidate.
   The plan's "93 compounds" counts the vehicle. Every count in this project uses 92.
2. **One dose per compound, confirmed rather than assumed.** No drug label maps to more than one
   `drugname_drugconc` value, so there is no dose pooling anywhere in this task.

## 4. Frozen pools

- **Contexts**: the 44 cell lines whose vehicle arm has at least 200 cells (section 6).
- **Candidate library**: all 92 non-vehicle compounds of plate 3, for every context, with no
  exception. A compound is never removed from the library, including for a cell-count reason:
  the library is what the ranking is over, so shrinking it would change the task.
- **Query pool**: the 3,992 (context, compound) conditions that pass section 6.

Enumerated in `results/phase2_transition/eligibility/`: `candidate_library.csv`,
`query_eligibility.csv`, `context_summary.csv`, `task_freeze.json`.

## 5. Frozen split

Leave-one-cell-line-out. For target context `c`:

- **training** may use every cell of the other 43 usable contexts, controls and treated alike,
  across all 92 candidates;
- **inference** may use `X_source = X_{0,c}` and the current query's `X_target = X_{q,c}`, both of
  which are task inputs;
- **nothing else from `c` may be used.** In particular no observed treated response
  `X_{d,c}` for any candidate `d` may reach the predictor, any representation fit, or the ranker.
  This is the leakage rule that separates Phase B from Phase A.

## 6. Frozen eligibility thresholds

| Constant | Value | Where it comes from |
|---|---:|---|
| `MIN_TREATED_CELLS` | 100 | plan section 3, verbatim |
| `MIN_CONTROL_CELLS` | 200 | fixed here; see below |
| `N_SOURCE` | 200 | plan section 5 |
| `N_TARGET` | 200 | plan section 5 |
| seeds | 13, 29, 47, 71, 101 | plan section 5 |

The plan requires "enough DMSO control cells" without a number. It is set to 200, equal to the
source draw, for one reason: at that floor every context contributes a source population of the
same size, drawn without replacement, so source size cannot act as a confounder in any
cross-context comparison. A floor of 100 would admit 48 contexts and 4,139 queries but would let
source size vary from 102 to 3,386 cells. The 100-cell variant is pre-registered here as a
sensitivity analysis, to be run with everything else identical if a primary result is borderline;
it is not an alternative to be chosen after seeing which one is favourable.

## 7. Frozen query construction

For each eligible `(c, q)` and each of the five seeds:

- `X_source`: up to 200 cells drawn without replacement from the vehicle arm of `c`.
- `X_target`: up to 200 cells drawn without replacement from the query half of `X_{q,c}`
  (section 8).
- Mean-based and population-based methods receive **the same drawn cells**, never separate draws.

## 8. Frozen oracle split (Phase A only)

Phase A replaces the predicted candidate response with the observed one in the held-out context.
It is an information ceiling, not a deployable result, and every table that reports it must say so.

The query half and the oracle-bank half of the generating drug's cells must be disjoint. The plan
prefers a batch-disjoint split where a replicate label exists. Plate 3 carries two candidate
labels and they are not interchangeable:

- `sample` (96 values) is **nested inside the drug axis**: every sample contains exactly one drug
  and up to all 50 cell lines. Splitting on it cannot separate two halves of one condition, so it
  is not a replicate label for this purpose.
- `sublibrary` (105 values) is a library-preparation pool. Every condition is spread across a
  median of 105 of them, at a median of 7 cells per (condition, sublibrary), and all 3,992
  eligible queries have at least two.

Frozen choice: **split the 105 sublibraries into two halves with a seeded permutation, and assign
each cell to the half its sublibrary is in.** This is cell-disjoint and additionally shares no
library preparation between the two halves, which a random cell split does not achieve. The split
is drawn per seed and applied identically to every condition.

## 9. Frozen response definition

    mu_source   = mean(X_source)
    P_target    = { x_i^target - mu_source }
    P_hat_d     = { x_hat_{i,d} - mu_source }

Both the mean route and the population route therefore describe the same transition, and differ
only in how much of the population they keep. No new normalization is introduced.

## 10. Frozen metrics

- **Primary**: MRR of the true generating drug over the 92-candidate library.
- **Secondary exact**: Hit@1, Hit@5, Hit@10.
- **Secondary biological**: MoA-nDCG@10, computed only on queries that have at least one
  same-MoA candidate in the library.
- Absolute performance is always reported for both routes. Reporting only the difference is
  forbidden, because a positive difference between two failing rankers is not a result.

## 11. Frozen stopping rule

- Oracle population shows no material gain: stop developing predictors; the bottleneck is
  decision relevance.
- Oracle gains but prediction does not: the bottleneck is the forward model; a stronger
  non-additive predictor branch opens, with the task unchanged.
- Both gain: proceed to the mechanism analysis of which contexts and drugs satisfy the three-gate
  regime.

## 12. Open item carried into Phase A

`MoA-nDCG@10` needs a compound-to-MoA table for the 92 compounds. Plate 3's `obs` carries no MoA
or target annotation, so this metric is blocked until an external annotation is supplied and its
provenance recorded. It is a secondary metric; the primary and secondary exact metrics are
unaffected. This is listed as an open item rather than quietly dropped.
