# Revised Figure Plan — Metric-Circularity Positioning

Figures are NOT produced in this writing phase (spec §15). This plan specifies the
figure set the repositioned narrative needs, in the new result order. Each figure
serves the evaluation-circularity thesis, not a "DART wins" narrative.

## Figure 1 — The retrieval spectrum and the unification (positive anchor 1)
- **1A** schematic: population-to-population retrieval; mean collapse as the
  zero-variance limit of a distributional family.
- **1B** the metric taxonomy as a diagram (Class A / B / C) with example metrics.
- **1C** bar: exp08 Hit@1 by scorer, highlighting `mean_cosine = cmap_cosine = 0.3885`
  (identical bars) vs `global_energy = 0.837`; annotate WTCS 0.4635 as rank-based sibling.
- *Message:* mean/CMap retrieval is a special case; this is an algebraic fact.

## Figure 2 — Objective-aligned gains (Class A positive; Result 2)
- **2A** exp08 observed Hit@1 across scorers (energy 0.837 vs mean/cmap 0.389,
  pca_dist 0.778, pca_mean 0.518).
- **2B** exp12 per-query energy-welfare regret reduction distribution (+0.119 median,
  72% improved, n=621, p=4.3e-56); label axis "objective-aligned proxy".
- *Message:* under its own objective, distributional retrieval looks strong.

## Figure 3 — The collapse under independent metrics (CENTRAL; Result 3)
- **3A** same queries, Class B metrics: MoA-recovery nDCG delta −0.013; minority
  coverage negligible. Paired with 2B to make the A→B contrast visual.
- **3B** gate does not concentrate the proxy gain: recommended +0.119 vs
  non-recommended +0.122 (side-by-side).
- **3C** gate audit: scatter/curve of structure_reliability vs true divergence
  (ρ=−0.21) and preference_conflict vs true divergence (ρ=+0.18).
- **3D** exp13 real-data projection: 0/37 tasks DART-dominant under the non-circular
  criterion.
- *Message:* the same method is "ahead" or "no better" by metric class alone.

## Figure 4 — Information-condition mechanism (Result 4)
- **4A** exp09 nDCG deltas by predictor (avg −0.004, nn −0.097, cpa_linear −0.029).
- **4B** structure diagnostics real vs predicted: subpop_var_ratio 0.046 vs 0.009,
  diversity 0.158 vs 0.057, isotropy 0.959 vs 0.998.
- *Message:* predictors collapse structure; no structure → no distributional signal.

## Figure 5 — HIR-Bench as controlled stress test (Result 5)
- **5A** three information conditions + analytical boundary α*=B/(A+B).
- **5B** predictability ROC (AUC 0.645, labeled "moderate"); feature importance.
- **5C** transfer: predicted_mean tasks flagged no-DART 100%, but real
  partial-observed gains not isolated.
- *Message:* constructive benchmark; boundary expected by design; gate experimental.

## Figure 6 (optional / supplement) — Exploratory resistance divergence (Result 6)
- **6A** response divergence vs resistance-program scores (AXL/mesenchymal p=0.003,
  IFN p=1.9e-6, antigen-presentation p=0.04). Clearly labeled exploratory.

## Cross-figure rules
- Every panel showing a Class A positive is adjacent to its Class B null.
- No figure titled or captioned as "DART outperforms" / "DART improves treatment".
- Color/legend consistent across 2B and 3A so the collapse reads at a glance.
