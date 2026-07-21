# PDGrapher-Aligned Comparison — Plan & Protocol

DART ranks candidate **drugs** for a heterogeneous cell population by population-to-population
retrieval. PDGrapher (Gonzalez et al., *direct inverse design*) ranks candidate **intervention
targets** (genes/network nodes) by how well perturbing them steers a diseased state toward a
desired one, using network/graph proximity. These live in different output spaces, so a fair
head-to-head needs a common currency in **both** directions. This document specifies how exp10
does that, what is and isn't trained, the exact metrics, and the honest limitations.

---

## 1. Why not train PDGrapher from scratch?

Two reasons, one practical and one methodological:

1. **The ranked outputs already exist.** The repository ships a precomputed closed-loop
   benchmark, `data/benchmarks/pdgrapher_closed_loop_benchmark.parquet` (41,070 rows = 6 queries
   × 1369 candidate drugs × 5 baseline rankers), plus two CIGS signal parquets
   (`signature_reversal_scores_CIGS.parquet`, `response_rescue_labels_CIGS.parquet`, 64,356 rows
   each). Every PDGrapher-family signal we need — `graph_proximity`, `target_overlap` — is
   materialized per candidate, alongside a `field_match` relevance column that defines ground
   truth. `torch_geometric` and `pdgrapher` do import in the `Agent` env, so retraining is
   *possible*, but it would reproduce signals we already hold.
2. **Isolating the comparison.** Retraining introduces a second source of variance (checkpoint,
   graph, optimizer) that confounds the thing we actually want to measure: how a
   network-proximity target ranking behaves as a drug ranker, and vice-versa. Consuming the
   fixed ranked outputs keeps the comparison about the *ranking signal*, not a training run.

If a reviewer requires an end-to-end PDGrapher rerun, the hook is a drop-in: replace
`pdgrapher_adapter.ranking_for(...)` with a live PDGrapher inference call returning the same
`drug_name → score` frame; nothing downstream changes.

---

## 2. The benchmark, precisely

- **Queries (6):** {A549, MCF7, PC3} × {sample-0, sample-1}, each `field_source = observed_target`.
  Each query has a single observed target field (e.g. A549|sample-0 → **EGFR**).
- **Candidates (1369 drugs / query / baseline):** identified by both `drug_name` and
  `candidate_id` (canonical SMILES).
- **Ground truth:** `field_match >= 1.0` marks target-relevant drugs (97 for the A549|s0 query).
  These are the drugs whose annotated targets match the query's observed target field.
- **Signals per candidate:** `graph_proximity`, `signature_reversal`, `target_overlap`,
  `rescue_score`, `final_score`, and (from `response_rescue_labels_CIGS`) the
  `relative_source_to_target_distance_reduction`.

---

## 3. Drug ↔ target conversion protocol

The bridge is a bidirectional aggregation over a drug→target map. We use the CIGS graph's own
`drug_target_prior.parquet` (columns include `candidate_id` [SMILES], `drug_name`, `target_gene`,
`target_weight`, `node_index`), which matches the benchmark **exactly** on both keys
(1369/1369). DrugCentral (`drugcentral_target_annotations.parquet`) is a case-insensitive
fallback with ~842/1369 coverage.

**Target ranking → drug ranking** (score PDGrapher's target ranking as a drug ranking):

```
score(drug) = agg_{t ∈ targets(drug)} target_score(t)          agg ∈ {max, mean}
```

A drug is as good as its best (max) intervention target. Drugs with no annotated target that
appears in the target ranking receive −∞ (ranked last, honestly).

**Drug ranking → target ranking** (score DART's drug ranking as a target ranking):

```
score(target) = agg_{d ∈ drugs(target)} drug_score(d)          agg ∈ {max, mean}
```

A target inherits the score of the best drug that hits it. Both directions are deliberately
simple, monotone aggregations: the comparison should reflect the ranking signal, not a tuned
mapping. `max` is the default (reported); `mean` is available as a robustness variant.

**Ground-truth targets** for target-side metrics are the union of the annotated targets of the
query's ground-truth drugs (for A549|s0 this collapses to {EGFR}, matching `field_source`).

**Round-trip consistency check.** `conversion_consistency.csv` takes PDGrapher's `graph_proximity`
drug scores → converts to a target ranking → converts back to a drug ranking, and re-scores.
This exposes information lost in the target bottleneck (round-trip Hit@1 = 0, MRR ≈ 0.017 for
graph_proximity — its network-central targets don't re-resolve to the EGFR-specific GT drugs),
which is itself an informative property of network-proximity ranking.

---

## 4. DART's representation on this task

DART's native scorers operate on single-cell **populations**, but the closed-loop benchmark is a
precomputed per-candidate score table with no per-candidate population attached
(`drug_deg_vectors.npy` in this snapshot is empty). The faithful DART analogue available here is
`relative_source_to_target_distance_reduction` from `response_rescue_labels_CIGS`: how much a
candidate **reduces the source→target population distance** — i.e. how far it moves the diseased
population toward the target state. This is the population-distance flavour of DART's
distributional retrieval, and exp10 reports it as `distance_reduction`.

This is a *proxy*, stated as such. A fully native DART rerun would require the per-candidate
LINCS populations (or their cell-level embeddings); when those are provided, `distance_reduction`
is replaced by `score_energy` / `score_coverage` over the real populations with no other change.

---

## 5. Metrics (exp10 outputs)

| Output CSV | Contents |
|---|---|
| `drug_ranking_comparison.csv` | per (query, signal): Hit@1/5/10/20, MRR, nDCG@10, best/median rank |
| `drug_ranking_summary.csv` | the above averaged over queries, per signal |
| `target_ranking_comparison.csv` | per (query, signal): target nDCG@10, target recall@{1,5,10,20} |
| `target_ranking_summary.csv` | target metrics averaged over queries |
| `flip_vs_pdgrapher.csv` | each signal vs `graph_proximity`: top-k overlap, top-1 flip, Δrank |
| `conversion_consistency.csv` | PDGrapher drug→target→drug round-trip recovery |
| `runtime.csv` | per-signal ranking wall-clock |
| `provenance.csv` | benchmark path, drug→target source, GT definition, "no training" note |

Multi-relevant queries (a query has many GT drugs) use a tie-broken rank: candidates are sorted
by score, each candidate's rank is its unique position, Hit@k = 1 if any GT is in the top-k, MRR
from the best GT rank, nDCG@10 with binary relevance normalized so the ratio stays in [0, 1].
(An earlier version double-counted tied GT candidates and produced nDCG > 1; fixed before
finalizing — see `_multi_gt_metrics` in `exp10_pdgrapher_comparison.py`.)

---

## 6. Findings

1. **Pure network proximity is a weak drug ranker.** `graph_proximity` scores Drug Hit@1 = 0 and
   target nDCG = 0 — it ranks promiscuous, network-central drugs (Lenalidomide, Thalidomide)
   above the query-specific EGFR inhibitors. Direct inverse design in *target* space does not
   transfer to good *drug* ranking without target specificity.
2. **The population distance-reduction signal is the best unsupervised ranker.**
   `distance_reduction` reaches Drug Hit@5 = 1.0 and target recall@5 = 1.0 (nDCG@10 = 0.43),
   outscoring every other unsupervised signal on both sides. This supports the thesis that a
   distributional / population-distance signal beats topology-only ranking.
3. **The bridge works both ways.** target→drug conversion recovers 97/97 GT drugs when the target
   ranking is informative; the round-trip check quantifies where the target bottleneck loses
   drug-level specificity.
4. **Reference signals behave as expected.** `field_match` (the GT relevance itself) is a perfect
   upper reference; `target_overlap` is near-perfect on the drug side by collinearity with it;
   `random` is the floor.

---

## 7. Limitations & the honest asterisks

- **Predictor availability.** scGen could not be built on this stack; exp09's published-predictor
  slot runs the `cpa_linear` fallback (provenance-stamped). This does not affect exp10.
- **DART proxy.** `distance_reduction` is the population-distance analogue of DART's retrieval on a
  benchmark that ships scores, not populations. It is labelled a proxy everywhere it appears.
- **Small query count.** The closed-loop benchmark has 6 queries; results are consistent across
  all 6 but the sample is small. Metrics are reported per query in `*_comparison.csv` so the
  spread is inspectable, not just the mean.
- **Single observed target per query.** Ground-truth targets collapse to the observed field
  (often one gene), which makes target recall coarse; target nDCG is the more discriminating
  target-side metric here.
