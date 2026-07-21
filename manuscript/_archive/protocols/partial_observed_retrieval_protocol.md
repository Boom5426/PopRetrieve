# Partial-Observed Retrieval Protocol (exp12)

> **Phase-gate for the Nature Methods route.** This protocol establishes whether
> DART's required information condition — *candidate response populations are
> partially observed, but the optimal drug is hidden* — exists in real
> single-cell drug screens, and whether DART reduces decision regret or improves
> nDCG specifically in the high-conflict / reliable-structure subset.

## 0. Why this is the gate

DART's advantage over mean/signature retrieval has been shown on **fully-observed**
heterogeneous populations (exp08) and shown to vanish on **mean-only predicted**
populations (exp09). The open question that decides the paper's positioning is
whether the *realistic middle ground* — a partially observed response atlas where
the target drug is unknown — supports DART's advantage.

If yes → the method is a practical drug-recommendation tool (Nature Methods).
If no → DART is an evaluation/diagnostic framework only (methods journal).

## 1. Scenario

```text
observed subset of candidate response populations
        +
hidden target drug / hidden MoA / hidden response identity
        ↓
rank candidates using mean / CMap / DART
        ↓
evaluate whether DART better recovers the hidden useful drug
or reduces welfare regret
```

The core is not "all candidate drugs are observed" but: a response atlas / partial
ex-vivo screen / prior screened library already contains *some* candidate response
structure, while the final target to rank or select remains hidden.

## 2. Data priority

1. **First priority (use these):** SciPlex3, Frangieh, CD34+
2. Second priority: CIGS / LINCS2020
3. Third priority: Tahoe-100M (only if the first three cannot answer the question)

All splits in this protocol are runnable on the in-repo SciPlex3 / Frangieh / CD34
tensors. `data/annotation/drug_annotation_master.csv` (189 drugs × {moa_class,
target_genes}) supplies the MoA/target structure for leave-MoA-out and
leave-target-out. No Tahoe download.

## 3. Three partial-observed settings

### Setting A — leave-drug-out within observed response atlas

For each cell_line / condition / state:

1. Hide one drug as the **target**.
2. Remaining drugs form the **observed response library**.
3. The query is the real heterogeneous response induced by the hidden drug, with
   its identity hidden.
4. Rank candidates in the library by each retrieval method.
5. Evaluate the rank of the hidden drug, or recovery of same-MoA / same-target drugs.

Outputs: `drug_rank, MoA_rank, target_rank, Hit@1, Hit@5, MRR, nDCG, decision_regret`.

### Setting B — leave-MoA-out / leave-target-out

1. Hide **all drugs** of one MoA class or target family.
2. Retrieve the nearest surrogate drug from the remaining library.
3. Evaluate whether a same-pathway / same-target / functionally-related candidate
   is recovered.

Harder than leave-drug-out, and closer to real drug repurposing.

### Setting C — partial-library batch selection

Simulates the ex-vivo / response-atlas workflow:

1. 20% / 40% / 60% of drugs already measured.
2. DART / mean / CMap select the next batch of top-k candidates from the measured library.
3. Evaluate the selected batch against the hidden responses in the full data.

Outputs: `batch_coverage, minority_state_coverage, welfare_regret, topk_diversity, MoA_diversity`.

## 4. Leakage rules (mandatory)

Every split declares `split_type ∈ {leave_drug_out, leave_MoA_out, leave_target_out, partial_library}`.

**Forbidden:**
- Building PCA / normalization / candidate statistics from the hidden drug response.
- Using the hidden drug identity or MoA in candidate scoring.
- Estimating preference conflict from the full library.
- Using the held-out context's treated response inside average-effect / NN predictors.

**Allowed:**
- Control populations.
- Candidate responses from the observed library.
- Public MoA / target annotation for **evaluation or stratification only** — never
  fed to DART as a scoring signal.

Every CSV row carries:

```text
split_type, heldout_drug, heldout_MoA, observed_library_fraction,
information_condition_mode, structure_reliability_score, preference_conflict,
method, metric, value, provenance
```

## 5. Information-condition diagnostics (synchronous)

For each partial-observed query, compute (using observed data only):

```text
structure_reliability_score      composite of the diagnostics below
subpopulation_variance_ratio     between/total variance (k-means k=2 on query)
response_diversity               mean pairwise cosine distance among query cells
isotropy_index                   λ_min/λ_max of query covariance
mean_energy_disagreement         Kendall distance between mean-cosine and energy rankings
bootstrap_rank_stability         top-1 stability over bootstrap resamples of the query
preference_conflict_topk         top-k disagreement across query subpopulations
recommendation_mode              four-state decision (below)
```

`structure_reliability_score` = mean of {subpop_variance_ratio (higher=better),
1−isotropy_index (higher=more anisotropic=more structure), response_diversity,
bootstrap_rank_stability}, clipped to [0,1].

**Recommendation logic:**

```text
if structure_reliability low:                         recommendation_mode = mean_or_no_call
elif preference_conflict low:                         recommendation_mode = mean_sufficient
elif preference_conflict high and structure high:     recommendation_mode = DART_recommended
else:                                                 recommendation_mode = uncertain
```

Outputs:
- `results/exp12_partial_observed_retrieval/information_condition_summary.csv`
- `results/exp12_partial_observed_retrieval/recommendation_vs_outcome.csv`

**Core test:** *Is DART stably better than mean only on the real-task subset where
recommendation_mode = DART_recommended?*

## 6. Metrics — priority order

Hit@1 is **not** the sole primary metric.

**Primary:** `decision_regret, nDCG, MRR, minority_state_coverage, welfare_utility_gap`

**Secondary:** `Hit@1, Hit@5, top-k overlap, rank_delta, MoA recovery, target recovery`

Reason: real partial-observed libraries have many candidate drugs (Hit@1 can be
low), and reviewers care about reducing wrong decisions and covering minority
subpopulations more than single top-1 hits.

### Real-data regret proxy (no synthetic oracle)

Real data has no synthetic utility matrix. We define a **coverage-based welfare
proxy**: cluster the query into K states (k-means on query cells), and for each
candidate compute per-state utility as the negative energy distance between the
candidate population and that query state. Welfare functions (mean / worst) then
aggregate across states exactly as in HIR-Bench. `decision_regret =
U_welfare[oracle-in-library] − U_welfare[method-selected]`, where the "oracle in
library" is the observed-library drug maximizing the welfare proxy. This keeps the
regret definition consistent with HIR-Bench while using only observed data.

## 7. Go / No-Go criteria

### Nature Methods **Go** — satisfy ≥ 3 of:

1. In real partial-observed retrieval, DART significantly lowers decision regret on
   the DART_recommended subset.
2. DART's nDCG or MRR beats mean/CMap on the high-conflict + reliable-structure subset.
3. CD34+ / low-conflict tasks are correctly judged mean_sufficient (DART does not win spuriously).
4. exp09 mean-only predictors are correctly judged no-DART / no-call.
5. At least one real case where DART changes the top-k drug ranking and covers a
   minority state that mean retrieval missed.

### Nature Methods **No-Go** — any one of:

1. DART is not better than mean on the high-conflict reliable-structure subset.
2. The information-condition gate cannot separate DART-effective from DART-ineffective regions.
3. Real-data projection systematically disagrees with HIR-Bench predictions.
4. DART's advantage exists only in the fully-oracle observed-full-library setting and
   disappears under partial-observed.

If No-Go: stop positioning DART as a practical drug-recommendation method; convert to
an NCS / Cell Reports Methods / Bioinformatics evaluation-science paper titled
*a benchmark and information-condition analysis of distributional retrieval objectives*.

## 8. Output files

```text
results/exp12_partial_observed_retrieval/
  summary.csv                        per (split × method × metric) aggregate
  per_query_scores.csv               per-query raw scores (kept on server; large)
  information_condition_summary.csv  per-query diagnostics + recommendation_mode
  recommendation_vs_outcome.csv      DART−mean advantage stratified by recommendation_mode
  go_nogo_report.md                  auto-generated verdict against §7
```

## 9. QUICK vs FULL

- **QUICK:** few held-out drugs, few seeds, SciPlex3 controlled only — smoke path.
- **FULL:** leave-one-out over all annotated drugs across SciPlex3 controlled +
  cross-line + Frangieh + CD34, all three settings, full seeds.
