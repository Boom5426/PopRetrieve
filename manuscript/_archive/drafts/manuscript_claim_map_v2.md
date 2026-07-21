# Manuscript Claim Map v2 (metric-circularity positioning)

Each claim → its metric class → headline evidence → source → allowed / forbidden
wording. Supersedes the Claim 4 row of the v1 evidence table with the refined
exp16/17 audit numbers. **No claim may exceed its evidence.** All numbers are FULL
runs (server `ssh:139.180.131.202`, `/data/boom/DART`, env `Agent`).

---

## Claim 1 — Method unification (strongest, class-independent)

- **Statement.** Under the implemented cosine kernel, CMap-style mean-signature
  retrieval is numerically identical to DART's collapsed mean-cosine objective;
  signature retrieval is the zero-variance end of a distributional spectrum.
- **Metric class.** Independent of metric class (an algebraic identity, not a score).
- **Evidence.** `mean_cosine` Hit@1 = `cmap_cosine` Hit@1 = **0.3885** (0.388492);
  `cmap_wtcs` = 0.4635 (rank-based, differs); `global_energy` = 0.8369.
- **Source.** `results/exp08_signature_baselines/summary.csv`;
  `src/baselines/cmap_signature.py` (cosine of mean-delta = `score_mean_cosine`).
- **Allowed.** "CMap-style cosine retrieval is a collapsed mean-signature special
  case of the DART family." / "Mean-signature retrieval is the zero-variance limit."
- **Forbidden.** "All CMap methods are identical to DART." / "WTCS is mathematically
  identical to DART." (WTCS = monotone rank-based sibling, not an identity.)

## Claim 2 — Objective-aligned evaluation inflates apparent gains (Class A positive)

- **Statement.** Distributional retrieval shows large gains under metrics aligned
  with its own objective.
- **Metric class.** A (objective-aligned proxy).
- **Evidence.** exp08 observed Hit@1: `global_energy` 0.837 vs mean/CMap 0.389,
  `pca_dist` 0.778, `pca_mean` 0.518. exp12 energy-welfare regret: DART_coverage_worst
  median reduction **+0.119**, paired Wilcoxon **p = 4.3 × 10⁻⁵⁶**, **72%** of
  **n = 621** recommended queries improved.
- **Source.** `results/exp08_signature_baselines/summary.csv`;
  `results/exp12_partial_observed_retrieval/` (go_nogo_report.md).
- **Allowed.** "Under an energy-based proxy DART reduces decision regret." Always
  label as objective-aligned proxy / distributional retrieval signal.
- **Forbidden.** Reporting +0.119 without the −0.013 (Claim 3). Any reading of the
  Class A gain as therapeutic utility.

## Claim 3 — Oracle-independent metrics collapse the gains (CENTRAL falsification)

- **Statement.** Under more independent criteria, DART shows no universal advantage,
  and the diagnostic gate does not concentrate even the proxy advantage.
- **Metric class.** A → B transition (the pivot of the paper).
- **Evidence.**
  - MoA-recovery nDCG gain on recommended subset **−0.013** (DART slightly loses).
  - minority-state coverage: statistically significant but negligible — median gap
    Q1 **+0.0009** → Q4 **+0.0018** across true-divergence strata (all BH q ≈ 0),
    i.e. real and divergence-monotone but far below any practical effect floor.
  - exp13: **0 of 37** real tasks DART-dominant under the non-circular criterion.
  - gate does not separate: recommended vs non-recommended median regret
    **+0.119 vs +0.122**.
  - **gate reliability axis anti-correlated with true divergence:** Spearman
    **ρ = −0.21, p = 3.8 × 10⁻⁹**; preference-conflict axis weakly aligned
    ρ = +0.18, p = 3.7 × 10⁻⁷; binary recommendation label does not separate
    high/low divergence (Mann–Whitney **p = 0.090**).
  - **MoA-nDCG null at every stratum** (Q4 BH q = 0.57, power 0.06 — severely
    underpowered; ~27,800 queries needed for 80% power).
- **Source.** `results/exp12_partial_observed_retrieval/`;
  `results/exp16_gate_diagnosis/gate_vs_true_divergence.csv`,
  `gate_variants_sweep.csv`;
  `results/exp17_true_divergence_subset/divergence_stratified.csv`,
  `power_analysis.csv`; `results/exp16_17_verdict.md`.
- **Verdict.** **B(−): statistically real but negligible** (refined from v1's
  "conditional-go"). Lesion is in the data/task layer, not only the gate.
- **Allowed.** "Apparent distributional gains are metric-dependent and cannot be
  interpreted as therapeutic utility without independent validation."
- **Forbidden.** "DART provides better therapeutic recommendations." / "improves
  oracle-independent utility."

## Claim 4 — Information condition explains predictor failure (mechanism)

- **Statement.** DART's advantage depends on whether candidate populations carry
  reliable subpopulation structure; predictor-collapsed candidates erase it.
- **Metric class.** Mechanistic (structure diagnostics + Class A/B retrieval deltas).
- **Evidence.** exp09 nDCG deltas: average_effect **−0.004**, nearest_neighbor
  **−0.097**, scgen/cpa_linear **−0.029**. Structure diagnostics real vs predicted:
  subpop_var_ratio **0.046 vs 0.009** (~5×), diversity **0.158 vs 0.057** (~2.7×),
  isotropy **0.959 vs 0.998**.
- **Source.** `results/exp09_predict_then_rank/`,
  `results/exp09_structure_diagnostics/`.
- **Allowed.** "DART's advantage depends on the candidate-response information
  condition." / "Predictor-collapsed populations erase the distributional advantage."
- **Forbidden.** "DART improves any perturbation predictor." (scGen = CPA-linear
  fallback, representative of latent-linear predictors, not a scGen benchmark.)

## Claim 5 — HIR-Bench: controlled stress test, not oracle (framework + limitation)

- **Statement.** HIR-Bench defines observed / predicted_mean / predicted_structure
  regimes with an analytical flip boundary and a latent welfare oracle.
- **Metric class.** Constructive synthetic (not biological ground truth).
- **Evidence (FULL 13,440-cell run, artifact).** no_conflict_flip_rate 0.0000;
  median_boundary_margin 0.29; predicted_mean DART−mean gap 0.051; predictability
  AUC **0.645** (n_pos 8640, n_neg 4800); top feature `topk_disagreement`;
  boundary α* = B/(A+B).
- **Source.** `results/exp11_hir_benchmark/` (FULL artifact — NOT the on-disk QUICK
  reproduction, AUC 0.5); `src/benchmarks/theory_boundary.py`.
- **Allowed.** "Failure risk is moderately predictable from observable structure and
  conflict features." / "analytically controlled stress test."
- **Forbidden.** "Failure risk is accurately predicted." / "HIR-Bench proves DART is
  always better." (Use *moderate* for AUC 0.645, never *accurate*.)

## Claim 6 — Exploratory resistance-associated divergence (clearly exploratory)

- **Statement.** Response-divergent minority states are enriched for melanoma
  resistance-associated programs; no survival/longitudinal validation.
- **Metric class.** Class B enrichment; Class C (utility) absent.
- **Evidence (exp15 FULL).** AXL/mesenchymal corr **+0.134, p = 0.003**;
  IFN-response **p = 1.9 × 10⁻⁶**; antigen-presentation **p = 0.04**; quiescence
  sign-flips QUICK↔FULL (not claimed); Part C DART minority rescue +0.0008 (near-null).
- **Source.** `results/exp15_resistance_precursor_exploration/`.
- **Allowed.** "Exploratory analysis suggests response divergence may mark
  resistance-associated minority states."
- **Forbidden.** "DART predicts resistance." / "identifies persister cells." /
  "response divergence predicts treatment survival."

---

## Cross-cutting rules (binding)

1. exp09 is a boundary result presented as mechanism, never hidden.
2. exp12 non-circular nulls sit in the main text next to the energy-proxy positives.
3. exp15 is exploratory throughout, always with the no-timecourse limitation.
4. No therapeutic-superiority language anywhere; DART is a probe, not a recommender.
5. HIR-Bench headline numbers cite the FULL artifact (AUC 0.645), not the on-disk
   QUICK reproduction (AUC 0.5).
