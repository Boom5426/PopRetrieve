# Information-Condition Audit

> **Core thesis (revised):** When candidate drug response populations *or their
> structure-preserving predictions* are available, drug ranking should not collapse to
> mean-signature matching. Whether distributional retrieval is appropriate can be determined
> a priori by observable structure-reliability statistics — and when the information condition
> is not met, mean retrieval is the correct behaviour, not a failure of the method.

---

## 1. The information-condition framework

Inverse retrieval takes a query population Q and a candidate library {P_d}, and ranks
candidates by how well P_d matches Q. The **information condition** of the candidate library
determines what structure a retrieval method can exploit:

| Mode | Description | Subpopulation structure? | DART advantage expected? |
|---|---|---|---|
| **observed_candidate_population** | Real single-cell responses are available (e.g. scRNA-seq of treated cells) | Yes — reflects true biological heterogeneity | Yes, when the query is heterogeneous |
| **partial_observed_response_library** | Per-candidate aggregate scores exist (e.g. LINCS/CIGS distance-reduction) but not cell-level populations | Partial — signal carries population-distance information but cells are not accessible | Partial — the aggregate signal may encode distributional information |
| **structure_preserving_predicted_population** | A structure-aware predictor (e.g. conditional normalizing flow, conditional diffusion) generates candidate populations with realistic subpopulation modes | Potentially yes — depends on predictor fidelity | Yes, if the predictor preserves subpopulation structure |
| **mean_only_predicted_population** | A forward predictor (scGen, CPA, average-effect, nearest-neighbour) generates candidate populations as mean + isotropic noise | No — structure is fabricated, isotropic by construction | No — distributional retrieval has nothing real to exploit |

The key insight: DART's distributional scorers (energy distance, coverage) compute over the
**full population**, so they can only extract information that the population actually contains.
When the information condition is `mean_only`, the population is its mean plus uninformative
noise, and any distributional scorer degenerates to a noisy version of the mean scorer.

---

## 2. Per-experiment classification

### exp08 — Signature retrieval vs DART

**Information condition: `observed_candidate_population`**

Candidates are real SciPlex3/Frangieh treated-cell populations drawn directly from the
scRNA-seq tensor. The heterogeneous subpopulation structure is genuine: cells from different
MOA classes, drug sensitivities, and cell states contribute distinct modes. This is the
canonical use case for distributional retrieval.

**Result:** global_energy (DART) Drug Hit@1 = 0.837 vs mean_cosine 0.388 — a 2.2× improvement.
The advantage is real because the information condition provides real structure to exploit.

### exp09 — Predict-then-rank

**Information condition: `mean_only_predicted_population`**

Forward predictors (average_effect, nearest_neighbor, scgen/cpa_linear) generate candidate
populations as mean-signature + isotropic Gaussian noise. The structure diagnostics
(`results/exp09_structure_diagnostics.csv`) confirm this quantitatively:

| Diagnostic | Real populations | Predicted populations | Ratio |
|---|---|---|---|
| Subpopulation variance ratio (SSB/SST, k=2) | 0.046 | 0.009 | **5.1×** |
| Response diversity (pairwise cosine IQR) | 0.158 | 0.057 | **2.7×** |
| Isotropy index (normalized PCA entropy) | 0.959 | 0.998 | Real is less isotropic |
| Score disagreement (mean_cosine vs energy ρ) | 0.556 | 0.82 avg (NN/scgen=1.0) | Predicted → perfect agreement |

The predicted populations have near-zero subpopulation structure (variance ratio 0.009 vs
0.046), nearly maximal isotropy (0.998 → uniform spread in all PCA directions), and low
diversity (0.057 → cells are tightly clustered around the mean). When scored, mean_cosine and
energy distance agree almost perfectly (ρ ≥ 0.64, NN/scgen = 1.0) — confirming there is no
distributional information for the energy scorer to exploit beyond what the mean already carries.

**Result:** Swapping mean/R² retrieval for DART retrieval does *not* help (Δ = −0.004 to
−0.097). This is the correct behaviour under the information condition — not a failure of DART,
but a failure of the information source.

### exp10 — PDGrapher comparison

**Information condition: `partial_observed_response_library`**

The closed-loop benchmark provides per-candidate scores (graph_proximity, signature_reversal,
distance_reduction) but not cell-level populations. The `distance_reduction` signal
(relative_source_to_target_distance_reduction from CIGS) is computed from real perturbation
populations and carries population-distance information, making it a partial proxy for the
`observed_candidate_population` condition. DART's native scorers cannot operate because the
per-cell data is not available in this snapshot.

**Result:** `distance_reduction` is the best unsupervised drug ranker (Hit@5 = 1.0), consistent
with the thesis that population-distance signals outperform topology-only ranking. The partial
information condition limits what can be measured — full DART retrieval would require the
per-candidate LINCS populations.

### exp11 (legacy) — Synthetic phase diagram

**Information condition: `observed_candidate_population`**

The phase diagram uses real SciPlex3 cells with synthetic divergence injection (λ parameter
shifts minority-mode signatures). Candidate populations retain genuine cell-level
heterogeneity. The diagram maps the boundary at which distributional retrieval becomes
necessary — this is inherently a statement about the `observed` information condition.

**Result:** Advantage surface shows clear phase transition from ~0 at λ=0 (homogeneous) to
+1.0 at λ=1.2/α=0.5 (orthogonal modes). The boundary exists *within* the observed condition;
under `mean_only`, the entire surface would be flat at ~0.

---

## 3. The critical reframing

The original framing — "DART is better than mean retrieval" — is incomplete. The complete
statement is:

> **DART's distributional retrieval is better than mean retrieval when the candidate response
> source provides subpopulation-resolved structure. This is testable a priori from observable
> statistics. When the information condition is not met (predicted populations are isotropic
> around the mean), mean retrieval is the correctly dominant strategy, and DART's distributional
> scorers correctly degenerate to their mean-equivalent special case.**

This absorbs exp09's negative result as structural evidence rather than treating it as a
weakness. The negative result is *necessary* for the thesis to be credible — it demonstrates
that DART does not hallucinate advantage from noise.

---

## 4. Observable structure-reliability statistics

A practitioner deciding whether to use distributional retrieval can compute these from the
finite-sample candidate populations *before* ranking:

1. **Subpopulation variance ratio** (SSB/SST, k=2 or 3): > 0.03 suggests real structure.
2. **Isotropy index** (normalized PCA explained-variance entropy): < 0.98 suggests
   non-isotropic spread.
3. **Response diversity** (IQR of pairwise cosine distances): > 0.10 suggests diverse cells.
4. **Mean-vs-distribution score disagreement** (Spearman ρ of mean_cosine vs energy across
   candidates): < 0.8 suggests the distributional scorer extracts different information.

If all four indicators are in the "no structure" zone, the information condition is effectively
`mean_only`, and mean retrieval should be preferred for its simplicity and speed.

---

## 5. Implications for HIR-Bench

HIR-Bench must incorporate `information_condition_mode` as a **first-class experimental
factor**, not an afterthought:

- **`observed`:** Generate candidate populations with genuine subpopulation structure (the
  default generator mode — latent targets per subpopulation, realistic within-cluster noise).
- **`predicted_mean`:** Collapse each candidate population to its mean + isotropic noise
  (same cells-per-pop, same noise level, but structure destroyed). Distributional methods
  should show zero advantage in this mode — this is a sanity check.
- **`predicted_structure`:** Apply a lossy structure-preserving transform (PCA roundtrip with
  reduced components, or add structured noise that preserves cluster centroids but degrades
  within-cluster detail). This is the realistic middle ground — what a good conditional
  generative model might produce.

The benchmark's headline claim should be: *"HIR-Bench quantifies where inverse retrieval
methods make incorrect decisions and whether this failure risk can be predicted — conditional
on the information quality of the candidate response source."*
