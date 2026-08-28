> ⚠️ **SUPERSEDED IN PART, 2026-07-12.** This document predates an audit that retracted
> several numbers as artifacts of our own code, including the "5.1x structure collapse", the
> hand-entered divergence-gate positions (CD34+ was 0.95; it measures 0.186), the MoA-nDCG
> statistics computed over 165 undefined sentinel values, and the Class A/B contrast that
> compared two different scorers. **Read [CORRECTIONS.md](../../CORRECTIONS.md) before using any
> number below.** Where this file and CORRECTIONS.md disagree, CORRECTIONS.md is right.

# PopRetrieve Project Data Index

A single grounded map of every experiment, its headline numbers, and the four core
contributions they support. Every value below is read directly from the `results/`
CSVs on the compute server; where the on-disk CSV differs from the value cited in
the manuscript, the discrepancy is flagged and reconciled here. This file is the
navigation layer over `manuscript_evidence_table.md` (the locked-numbers authority)
and the per-experiment scripts in `src/experiments/`.

Repository: https://github.com/Boom5426/PopRetrieve  ·  Test suite: 95/95  ·  Phase-1
reproduction: 35/35 within tolerance.

---

## 1. Datasets

| dataset | scale | contexts / conditions | perturbations | role |
|---|---|---|---|---|
| **SciPlex3** (Srivatsan et al. 2020) | 276,325 cells x 2,000 genes | A549, K562, MCF7 | 188 drugs (all present in all 3 contexts) | primary controlled + cross-line benchmark |
| **Frangieh Perturb-CITE-seq** (Frangieh et al. 2021) | 218,023 cells x 2,000 HVGs | Control, IFN-gamma, Co-culture | 239 CRISPR KOs | natural-heterogeneity benchmark |
| **CD34+** (GSE306429) | 33,984 cells x 2,000 genes | myeloid lineages | 36 drugs | honest negative control |
| **LINCS closed-loop / PDGrapher** | 41,070 rows | A549, MCF7, PC3 | 1,369 drugs | inverse-design comparison |
| **HIR-Bench** | synthetic (FULL 13,440-cell grid) | two-subpopulation latent welfare model | tunable conflict | analytic stress test |

---

## 2. Experiment inventory (grounded headline numbers)

### Phase 1: internal retrieval benchmark (exp01-07)

| exp | question | key result (from CSV) | source |
|---|---|---|---|
| exp01 | controlled SciPlex3 retrieval | global_energy Hit@1 up to 1.00 at low alpha; mean_cosine 0.00-0.30 in same cells | `exp01_sciplex3_controlled/metrics_summary.csv` |
| exp02 | divergence gate sweep | metric robustness + dataset positions on gate | `exp02_divergence_gate/` |
| exp03 | cross-line semi-real | retrieval + divergence over A549/K562/MCF7 pairs | `exp03_crossline_semireal/` |
| exp04 | CD34+ honest negative | 35/35 recompute within tolerance (incl. this exp) | `exp04_cd34_negative/` |
| exp05 | Frangieh natural | IFNGR1 max energy advantage +0.60 (mean_cosine 0.20 vs energy 0.80, Control+IFN-gamma); JAK1 +0.05 | `exp05_frangieh_natural/frangieh_retrieval_by_gene.csv` |
| exp06 | theory / degenerate limits | beta-interpolation mean->worst; degenerate limits match | `exp06_theory_limits/` |
| exp07 | ranking flip | controlled top1-flip 0.61-0.65; ours Hit@1 0.76-0.97 vs incumbent 0.11-0.36 | `exp07_ranking_flip/ranking_flip_summary.csv` |

### Phase 2: external baselines + predict-then-rank (exp08-10)

| exp | question | key result (from CSV) | source |
|---|---|---|---|
| exp08 | signature/PCA baselines | **Hit@1 (mean over tasks): global_energy 0.837, pca_dist 0.778, coverage_mean 0.773, coverage_worst 0.589, pca_mean 0.518, cmap_wtcs 0.464, cmap_cosine = mean_cosine = 0.3885** | `exp08_signature_baselines/summary.csv` |
| exp09 | predict-then-rank | predictor x ranker Hit@1: predictors reach 0.87-0.99 under mean_cosine/r2 but DART_coverage collapses (nn 0.383, avg 0.736); PopRetrieve advantage does not appear on predicted candidates | `exp09_predict_then_rank/predictor_ranker_matrix.csv` |
| exp09-struct | structure diagnostics | **subpopulation-variance ratio: real 0.0463 vs predictors 0.008-0.009 (~5x lower)**: predictors collapse structure | `exp09_structure_diagnostics/..._summary.csv` |
| exp10 | PDGrapher comparison | unsupervised distance_reduction: drug Hit@5 = 1.0, target recall@5 = 1.0, target nDCG@10 = 0.431 (best unsupervised, still Class A) | `exp10_pdgrapher_comparison/{drug,target}_ranking_summary.csv` |

### Phase 3: evaluation audit + gate diagnosis (exp11-17)

| exp | question | key result (from CSV / FULL artifact) | source |
|---|---|---|---|
| exp11 | HIR-Bench stress test | **flip-risk predictability AUC 0.640 (FULL 13,440-cell; n_pos 8640 / n_neg 4800)**. On-disk CSV is a QUICK 144-cell repro (AUC 0.5) that overwrote FULL; cite FULL. | `phase_grid_predictability.csv` (FULL = artifact) |
| exp12 | partial-observed retrieval | **Go-1: DART_coverage_worst median regret reduction +0.1190 (Wilcoxon p=4.26e-56, 72% improved, n=621)**; gate does NOT separate (recommended +0.1190 vs non-recommended +0.1219) | `exp12_partial_observed_retrieval/{recommendation_vs_outcome,go_nogo_report}` |
| exp13 | real-data projection | **0 of 37 tasks distributionally dominant** under the non-circular criterion | `exp13_real_data_projection/projection.csv` (37 rows) |
| exp15 | resistance exploration | AXL_mesenchymal corr with divergence +0.134 (p=0.0032); IFN_response +0.042; exploratory, no survival/timecourse | `exp15_resistance_precursor_exploration/enrichment_summary.csv` |
| exp16/17 | gate diagnosis + true-divergence audit | structure_reliability anti-correlated with true divergence (Spearman rho=-0.211, p<1e-8); preference_conflict weakly aligned (rho=+0.183); minority-coverage gap monotone but negligible (Q1 median +0.0009 -> Q4 +0.0018, all q<0.001); MoA-nDCG null at every stratum | `exp16_gate_diagnosis/gate_vs_true_divergence.csv`, `exp17_true_divergence_subset/{divergence_stratified,power_analysis}.csv` |

---

## 3. The A-vs-B contrast (the paper's spine)

The same method, on the same recommended queries, judged by two metric classes:

| metric class | metric | value | verdict |
|---|---|---|---|
| **A: objective-aligned** | energy Hit@1 (exp08) | **0.837** vs 0.389 mean/CMap | large gain |
| **A: objective-aligned** | energy-welfare regret reduction (exp12, coverage_worst median) | **+0.1190** (p=4.26e-56, 72%/621) | large, highly significant gain |
| **B: task-proximal** | MoA-recovery nDCG (exp12) | **-0.0134** (PopRetrieve slightly loses) | no transfer |
| **B: task-proximal** | minority-state coverage gap (exp17 Q4 median) | **+0.0018** (significant, negligible) | no material transfer |
| **B: task-proximal** | real-data dominance (exp13) | **0 of 37 tasks** | no transfer |
| **gate** | recommended vs non-recommended regret (exp12) | +0.1190 vs +0.1219 | gate does not separate |

**Power context (exp17 Q4):** the minority-coverage effect is real but negligible
(achieved power 1.00, n for 80% power = 45); the MoA-nDCG null is genuinely
underpowered (achieved power 0.06, n for 80% power = 27,794), so it is reported as
"no detectable effect," not "proven zero."

---

## 4. Core contributions (what the data supports)

1. **A unified retrieval spectrum (positive, theoretical).** Mean-signature retrieval,
   including CMap-style cosine, is the zero-variance collapsed member of the
   distributional family. Grounded by the exact Hit@1 identity: mean_cosine =
   cmap_cosine = 0.3885 (exp08), independent of any utility metric.

2. **Objective-aligned evaluation can inflate apparent distributional gains.** Under
   metrics aligned with its own objective, distributional retrieval shows large,
   highly significant gains (energy Hit@1 0.837; regret reduction +0.1190,
   p=4.26e-56): reported as an energy-based proxy result, not therapeutic utility.

3. **Oracle-independent metrics collapse the apparent gains (central finding).** Under
   more independent criteria the advantage is null (MoA-nDCG -0.0134; 0 of 37 tasks
   dominant), and the diagnostic gate does not isolate a transferable advantage
   (+0.1190 vs +0.1219; structure_reliability axis anti-correlated with true
   divergence, rho=-0.211).

4. **Information condition explains the gap.** Distributional scores can only exploit
   subpopulation structure the candidate source actually contains; current predictors
   collapse it (subpop-variance ratio ~5x lower than real: 0.009 vs 0.046, exp09),
   erasing the distributional signal. HIR-Bench formalizes these regimes analytically
   (flip predictability AUC 0.640), and an exploratory link between response-divergent
   minority states and resistance-associated melanoma programs (AXL corr +0.134) is a
   hypothesis for future work, not a claim.

**One-line thesis.** PopRetrieve is best understood as a probe for evaluating when
distributional information is trustworthy in heterogeneous inverse drug retrieval,
not as a validated therapeutic recommender.

---

## 5. Provenance and reconciliation notes

- **exp11 AUC:** cite the FULL 13,440-cell run (AUC 0.640). The original FULL output was
  overwritten by a later QUICK 144-cell reproduction (AUC 0.5) and no FULL artifact
  survived; the value was regenerated 2026-07-12 via `results/_audit/fig6f_roc_lean.py`
  (mirrored at `upgrade/fig6f_roc_lean_runner.py`), which rebuilds the identical grid and
  calls the shipped `predictability_auc`. Reproduced AUC 0.640 (was cited as 0.645 before
  the FULL run was lost). Documented in `manuscript_evidence_table.md`.
- **exp12 regret:** the manuscript's +0.119 is the Go-1 **median** regret reduction
  for `DART_coverage_worst` (`go_nogo_report.md`), not the DART_energy **mean**
  (0.1716) in `recommendation_vs_outcome.csv`. Current exp12 CSVs are byte-identical
  to the pre-exp16/17 backup (the re-run only added `true_divergence` columns).
- **exp15 quiescence:** sign flips between QUICK (IFN-gamma only) and FULL (both
  contexts): context-dependent, explicitly not claimed as robust.
- **Related-work citations:** 17 DOI-verified references in
  `related_work_metric_audit_references.md` (Crossref / arXiv checked).

---

## 6. Document map (paper/)

- **Manuscript:** `manuscript_CRM_draft_v2_metric_circularity.md` (v2, probe framing);
  `manuscript_CRM_abstract_intro_zh.md` (formal Chinese abstract + intro).
- **Locked numbers:** `manuscript_evidence_table.md` (authority);
  `manuscript_claim_map_v2.md` (claim -> evidence -> allowed wording).
- **Audit:** `evaluation_circularity_audit.md`, `evaluation_metric_taxonomy.md`,
  `related_work_metric_audit_table.csv` (+ references).
- **Guardrails:** `negative_claims_box.md`, `claim_safe_language.md`,
  `reviewer_risk_register.md`, `response_to_expected_reviewers.md`.
- **Protocols:** `hir_benchmark_protocol.md`, `partial_observed_retrieval_protocol.md`,
  `information_condition_audit.md`, `statistical_reporting_checklist.md`.
- **Figures (planned):** `revised_figure_plan_metric_circularity.md`,
  `figure_plan_CRM.md`, `figure_captions.md`.
- **Review:** `code_review_report.md`.
