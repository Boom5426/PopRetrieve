# DART Manuscript — Figure Plan (6 main figures)

Do **not** render figures in this phase — this plan fixes panel content and the exact source
CSV per panel so figure generation is mechanical later. Each figure = one claim + its
boundary. Source-data files listed are on the server under `results/`.

---

## Figure 1 — Distribution-aware retrieval task and unification (Claim 1)

- **A.** Schematic: mean-signature retrieval pipeline (population → mean delta → cosine match).
- **B.** Schematic: DART population-to-population retrieval (full distributions → energy/MMD).
- **C.** Zero-variance collapse schematic: as candidate spread → 0, DART → mean retrieval.
- **D.** Numerical identity bar/annotation: `mean_cosine` = `cmap_cosine` = 0.3885, with
  `cmap_wtcs` = 0.4635 shown as the rank-based (non-identical) sibling; `global_energy` =
  0.837 as the distributional upper reference.
- Source: `results/exp08_signature_baselines/summary.csv`.

## Figure 2 — Observed heterogeneous candidate populations (Claim 2, positive)

- **A.** exp08 benchmark design (controlled SciPlex3 mixtures; observed candidate populations).
- **B.** Hit@1 / nDCG@10 across methods (energy, coverage, pca_dist vs mean/cmap).
- **C.** CMap / PCA / DART comparison; `pca_dist` 0.778 shows effect is not a raw gene-space
  artifact.
- **D.** Ranking-flip examples: queries where DART and mean disagree on the top candidate.
- Source: `exp08_signature_baselines/{summary.csv, summary_by_task.csv, flip_vs_dart.csv}`.

## Figure 3 — Information condition explains predictor failure (Claim 2, boundary + mechanism)

- **A.** predict-then-rank setup (predictor imagines candidate populations; DART ranks them).
- **B.** exp09 performance deltas (DART vs mean nDCG): −0.004 / −0.097 / −0.029 across
  average-effect / nearest-neighbor / cpa-linear.
- **C.** Real vs predicted structure diagnostics: subpop_var_ratio 0.046 vs 0.009; diversity
  0.158 vs 0.057; isotropy 0.959 vs 0.998.
- **D.** Isotropic-collapse schematic tying B to C (no structure → no distributional signal).
- Source: `exp09_predict_then_rank/predictor_ranker_matrix.csv`,
  `exp09_structure_diagnostics/exp09_structure_diagnostics.csv`.

## Figure 4 — HIR-Bench diagnostic framework (Claim 3)

- **A.** Three information-condition modes (observed / predicted_mean / predicted_structure).
- **B.** Latent welfare oracle (u[d,k]=−E‖x−t_k‖²; mean/worst/CVaR aggregation).
- **C.** Analytical flip boundary α*=B/(A+B) vs empirical flips.
- **D.** Sanity checks (all pass) + predictability AUC=0.645 with feature importances
  (topk_disagreement leading).
- Source (FULL, artifacts): `exp11_hir_benchmark/{sanity_checks.csv, method_dominance.csv,
  theoretical_boundary.csv, phase_grid_predictability.csv}`.
- **Provenance flag:** use FULL 13,440-cell values (AUC 0.645), not the QUICK CSVs currently
  on disk (AUC 0.5).

## Figure 5 — Partial-observed retrieval and boundary audit (Claim 4, the signature figure)

- **A.** Protocol: leave-drug-out / leave-MoA-out / partial-library; the recommend /
  mean-sufficient / no-call gate.
- **B.** Energy-proxy gains: DART_coverage_worst regret reduction +0.119, p=4.3e-56, 72%,
  n=621.
- **C.** Non-circular metrics null: MoA-recovery nDCG −0.013; minority-coverage ≈0; exp13
  0/37.
- **D.** Gate limitation: recommended (+0.119) vs non-recommended (+0.122) — advantage not
  concentrated; label "CONDITIONAL-GO". **This panel must explicitly state we ran this
  falsification test ourselves.**
- Source: `exp12_partial_observed_retrieval/{recommendation_vs_outcome.csv, go_nogo_report.md}`,
  `exp13_real_data_projection/{projection.csv, acceptance_report.md}`.

## Figure 6 — Exploratory resistance-associated divergence (Claim 5)

- **A.** Divergent minority-state workflow (per KO: response divergence → 2 subpops → program
  scoring).
- **B.** AXL/mesenchymal enrichment vs divergence (corr +0.134, p=0.003).
- **C.** IFN-response (p=1.9e-6) and antigen-presentation (p=0.04) enrichment.
- **D.** Limitations panel: no timecourse (Part B not evaluable); Part C rescue near-null;
  future longitudinal validation. **Whole figure labeled "Exploratory".**
- Source: `exp15_resistance_precursor_exploration/{enrichment_summary.csv,
  dart_vs_mean_minority_rescue.csv}`.

---

## Supplementary figures (candidates)

- S1. HIR-Bench generator internals + full grid specification.
- S2. Runtime comparison (signature ~8–10 ms, DART ~33 ms, PCA-latent ~640–700 ms/query).
- S3. exp10 PDGrapher drug↔target ranking conversion (inverse-design comparison).
- S4. Full exp09 predictor × retrieval matrix (all metrics, incl. Hit@1 where DART wins on
  2/3 predictors — the honest mixed picture that the nDCG delta summarizes).
