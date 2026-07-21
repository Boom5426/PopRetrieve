> ⚠️ **SUPERSEDED IN PART, 2026-07-12.** This document predates an audit that retracted
> several numbers as artifacts of our own code, including the "5.1x structure collapse", the
> hand-entered divergence-gate positions (CD34+ was 0.95; it measures 0.186), the MoA-nDCG
> statistics computed over 165 undefined sentinel values, and the Class A/B contrast that
> compared two different scorers. **Read [CORRECTIONS.md](../../CORRECTIONS.md) before using any
> number below.** Where this file and CORRECTIONS.md disagree, CORRECTIONS.md is right.

# DART Paper Data Compendium

Everything needed to write the paper in one place: datasets, comparison methods,
experimental results, statistics, and references. Every number is read from the
result CSVs on the compute server and cross-checked against
`manuscript_evidence_table.md` (the locked-numbers authority). Where a value is
proxy-aligned or exploratory, that status is stated next to it. Allowed and
forbidden wording follows the evidence table and is binding.

Server: `ssh:139.180.131.202`, repo `/data/boom/DART`, conda env `Agent`. All
numbers from FULL runs unless marked. This file is a writing aid and is kept local
(gitignored), not committed to the public repository.

---

## 1. Datasets

| dataset | scale | contexts / conditions | perturbations | role in paper |
|---|---|---|---|---|
| **SciPlex3** (Srivatsan et al. 2020) | 276,325 cells x 2,000 genes | A549, K562, MCF7 | 188 drugs (present in all 3 lines) | primary controlled + cross-line benchmark (exp01, exp03, exp08, exp09) |
| **Frangieh Perturb-CITE-seq** (Frangieh et al. 2021) | 218,023 cells x 2,000 HVGs | Control, IFN-gamma, Co-culture | 239 CRISPR KOs | natural-heterogeneity benchmark (exp05, exp15) |
| **CD34+ hematopoietic** (GSE306429) | 33,984 cells x 2,000 genes | myeloid lineages | 36 drugs | honest negative control (exp04) |
| **LINCS closed-loop / PDGrapher** | 41,070 rows | A549, MCF7, PC3 | 1,369 drugs | inverse-design comparison (exp10) |
| **HIR-Bench** | synthetic, FULL 13,440-cell grid | two-subpopulation latent welfare model | tunable conflict | analytic stress test (exp11) |

Data are large and obtained separately (see `DATA.md`); tensors and `.npz` are
gitignored. Preprocessing produces `sciplex3_all.pt` (2.28 GB), `cd34_all.pt`
(297 MB), `frangieh_hvg.npz` (109 MB).

---

## 2. Comparison methods

### 2.1 Field-level audit of seven method families

The paper audits how each representative family of inverse-retrieval / perturbation
method is normally evaluated, and which metric class that evaluation belongs to.
Metric classes: **A** = objective-aligned (evaluation restates the scoring rule);
**B** = task-proximal (more independent but same upstream data); **C** =
oracle-independent utility (dose-response, survival; absent from these benchmarks).

| method family | representative methods | typical metrics | class | key citations |
|---|---|---|---|---|
| CMap / L1000 signature retrieval | Connectivity Map, L1000 WTCS | connectivity score, cosine of mean signatures | A | Lamb 2006; Subramanian 2017 |
| single-cell signature retrieval | sc-resolved connectivity, pseudobulk match | signature correlation, Hit@k, DEG overlap | A (+B) | Peidli 2024 (scPerturb) |
| **DART / distributional retrieval** | energy, MMD, sliced-Wasserstein, coverage | energy/MMD regret (A); MoA-nDCG, coverage (B) | A + B | this work; Far-from-Straightforward 2026; Wei 2026 |
| sc perturbation predictors | scGen, CPA, chemCPA | reconstruction MSE/R2/PCC, DEG recovery | A (+B) | Lotfollahi 2019; Lotfollahi 2023; Hetzel 2022 |
| virtual-cell / foundation models | scGPT, scFoundation, Geneformer | held-out reconstruction, embedding similarity | A + B | Cui 2024; Hao 2024; Theodoris 2023 |
| graph / target-based inverse design | network proximity, GEARS | graph proximity, target overlap | A | Roohani 2024 (GEARS); Guney 2016 |
| PDGrapher-style graph methods | PDGrapher, closed-loop LINCS | target recall/nDCG, graph consistency | A (+B) | Gonzalez 2025 |

The finding of the audit: objective-aligned (Class A) evaluation is the default in
every family. The circularity risk is field-wide, not specific to DART or to
expression-based methods.

### 2.2 Baselines run head-to-head against DART

These are the methods actually implemented and scored in the experiments (as
retrieval scorers in exp08, as candidate-response predictors in exp09, and as
inverse-design signals in exp10).

| baseline | type | where | role |
|---|---|---|---|
| `mean_cosine` | mean-signature cosine | exp08 | the mean-collapse incumbent; identical to `cmap_cosine` |
| `cmap_cosine` | CMap-style cosine | exp08 | zero-variance limit of DART (identity proof) |
| `cmap_wtcs` | L1000 WTCS (rank-based) | exp08 | GSEA-style sibling, monotone not identical |
| `pca_mean`, `pca_dist` | PCA-latent mean / distance | exp08 | controls that the effect is not a raw gene-space artifact |
| `average_effect` | mean-effect predictor | exp09 | candidate-response source (collapses structure) |
| `nearest_neighbor` | kNN predictor | exp09 | candidate-response source |
| `scgen` (cpa_linear fallback) | latent-linear predictor | exp09 | representative predictor; provenance-stamped, not a scGen benchmark |
| PDGrapher `target_overlap`, `graph_proximity`, `signature_reversal` | graph inverse-design | exp10 | direct inverse-design comparison |
| `field_match` / `random` | reference upper / lower | exp10 | oracle and chance bounds |

---

## 3. Experimental results

### 3.1 exp08 - retrieval scorer comparison (SciPlex3, mean over tasks)

DART's `global_energy` leads; the two CMap/mean scorers are numerically identical.

| method | Hit@1 | Hit@5 | MRR | nDCG@10 | class |
|---|---|---|---|---|---|
| **global_energy** (DART) | **0.8369** | 0.9726 | 0.9018 | 0.9215 | A |
| pca_dist | 0.7782 | 0.9603 | 0.8610 | 0.8919 | A |
| coverage_mean (DART) | 0.7734 | 0.9504 | 0.8565 | 0.8841 | A |
| coverage_worst (DART) | 0.5893 | 0.8770 | 0.7253 | 0.7696 | A |
| pca_mean | 0.5179 | 0.9536 | 0.7233 | 0.7875 | A |
| cmap_wtcs | 0.4635 | 0.9556 | 0.6901 | 0.7629 | A |
| cmap_cosine | **0.3885** | 0.9810 | 0.6686 | 0.7523 | A |
| mean_cosine | **0.3885** | 0.9810 | 0.6686 | 0.7523 | A |

`mean_cosine` = `cmap_cosine` = 0.388492 to six figures: the identity proof (Claim 1).
This is a Class A, objective-aligned comparison; the large energy gain is reported
as an energy-based proxy result, not therapeutic utility.

### 3.2 exp09 - predict-then-rank (does the gain survive predicted candidates?)

Same rankers, but candidates are generated by predictors. DART's distributional
advantage disappears when the candidate source collapses subpopulation structure.

| predictor | dart_energy Hit@1 | dart_coverage Hit@1 | mean_cosine Hit@1 | r2 Hit@1 | n |
|---|---|---|---|---|---|
| average_effect | 0.8972 | 0.7361 | 0.8847 | 0.9014 | 720 |
| nearest_neighbor | 0.8903 | **0.3833** | 0.9875 | 0.8722 | 720 |
| scgen (cpa_linear) | 0.7111 | 0.6014 | 0.6000 | 0.7403 | 720 |

nDCG deltas (DART minus mean, per predictor): average_effect **-0.004**,
nearest_neighbor **-0.097**, scgen **-0.029**. The advantage does not transfer to
predicted candidates.

**Structure diagnostics (why):** predicted candidates collapse toward the mean.

| diagnostic | real data | predicted | ratio |
|---|---|---|---|
| subpopulation-variance ratio | **0.046** | **0.009** | ~5x lower |
| response diversity | 0.158 | 0.057 | ~2.7x lower |
| isotropy index | 0.959 | 0.998 | more isotropic |

### 3.3 exp10 - inverse-design comparison (LINCS closed-loop, PDGrapher)

Among unsupervised signals, DART's distance-reduction is the best (behind only the
oracle `field_match` and the supervised `target_overlap`).

| signal | family | drug Hit@5 | drug nDCG@10 | target recall@5 | target nDCG@10 |
|---|---|---|---|---|---|
| field_match | reference upper | 1.0 | 1.00 | 1.0 | 1.000 |
| target_overlap | pdgrapher (supervised) | 1.0 | 1.00 | 0.0 | 0.000 |
| **distance_reduction** | **DART distributional** | **1.0** | 0.11 | **1.0** | **0.431** |
| graph_proximity | pdgrapher | 0.0 | 0.00 | 0.0 | 0.000 |
| signature_reversal | signature retrieval | 0.0 | 0.00 | 0.0 | 0.000 |
| random | reference lower | 0.0 | 0.00 | 0.0 | 0.000 |

DART is the best unsupervised ranker on both the drug side (Hit@5 = 1.0) and the
target side (recall@5 = 1.0, nDCG@10 = 0.431). This remains a Class A comparison.

### 3.4 The A-vs-B contrast (the paper's spine)

The same method, same recommended queries, two metric classes:

| metric class | metric | value | verdict |
|---|---|---|---|
| **A - objective-aligned** | energy Hit@1 (exp08) | **0.837** vs 0.389 mean/CMap | large gain |
| **A - objective-aligned** | energy-welfare regret reduction (exp12, coverage_worst median) | **+0.119**, p=4.26e-56, 72% of 621 | large, highly significant |
| **B - task-proximal** | MoA-recovery nDCG (exp12) | **-0.013** | no transfer |
| **B - task-proximal** | minority-state coverage gain (exp12/17) | ~0 (+0.005) | no material transfer |
| **B - task-proximal** | real-data dominance (exp13) | **0 of 37 tasks** | no transfer |
| **gate** | recommended vs non-recommended regret (exp12) | +0.119 vs +0.122 | gate does not separate |

### 3.5 HIR-Bench (exp11, FULL 13,440-cell)

| item | value |
|---|---|
| grid size | 13,440 cells |
| flip-risk predictability AUC | **0.640** (n_pos 8640, n_neg 4800), moderate |
| top predictive feature | topk_disagreement |
| sanity: no_conflict_flip_rate | 0.0000 (pass) |
| sanity: predicted_mean DART-mean gap | 0.0507 (pass) |
| analytical boundary | alpha* = B/(A+B) |

On-disk `phase_grid_predictability.csv` is a QUICK 144-cell repro (AUC 0.5) that
overwrote FULL; cite the FULL artifact value 0.640.

### 3.6 exp15 - exploratory biology (Frangieh, clearly marked exploratory)

| program | corr with divergence | p | status |
|---|---|---|---|
| AXL / mesenchymal | +0.134 | 0.003 | exploratory |
| IFN-response | +0.042 | 1.9e-6 | exploratory |
| antigen-presentation | +0.037 | 0.044 | exploratory |
| quiescence | -0.127 | 7.7e-7 | sign-flips QUICK<->FULL, NOT claimed |

No drug timecourse in Frangieh, so divergence -> survival is not evaluable and is
reported as a limitation. No resistance-prediction claim.

---

## 4. Statistics and reproducibility

- **Phase-1 reproduction:** 35/35 recomputed values within tolerance
  (`all_existing_results_recomputed.csv`).
- **Test suite:** 95/95 passing.
- **exp12 significance:** paired Wilcoxon, p = 4.26e-56, n = 621, 72% of queries
  improved (Go-1 metric = DART_coverage_worst median regret reduction +0.119).
- **exp17 power:** minority-coverage effect real but negligible (achieved power
  1.00, n for 80% power = 45); MoA-nDCG null genuinely underpowered (power 0.06,
  n for 80% power = 27,794) - reported as "no detectable effect," not "proven zero."
- **exp16 gate diagnosis:** structure_reliability axis anti-correlated with true
  divergence (Spearman rho = -0.211, p < 1e-8); preference_conflict weakly aligned
  (rho = +0.183).
- **Seeds:** FULL run seed counts CTRL=20, XLINE=10, DRUGS=15, CD34=8, FRAN=20,
  GATE=20 (`scripts/run_all_core.sh`).
- **Provenance flags:** exp11 cite FULL artifact (not on-disk QUICK); exp12 +0.119
  is coverage_worst *median* (go_nogo_report), not energy *mean* (0.172); scGen is a
  CPA-linear fallback, not a scGen benchmark; exp15 quiescence not claimed.

---

## 5. Claim -> wording map (binding)

| claim | supported statement | forbidden |
|---|---|---|
| 1 Method unification | "CMap cosine retrieval is the zero-variance limit of distribution-aware retrieval" | "all CMap methods identical to DART"; "WTCS mathematically identical" |
| 2 Information-conditioned advantage | "DART's advantage depends on the information condition of the candidate source" | "DART improves any perturbation predictor" |
| 3 HIR-Bench | "failure risk is moderately predictable from observable features" | "failure risk is accurately predicted" |
| 4 Boundary audit | "under an energy proxy DART reduces regret; under oracle-independent metrics the advantage is not yet demonstrated" | "DART provides better therapeutic recommendations" |
| 5 Exploratory biology | "response divergence may mark resistance-associated minority states" | "DART predicts resistance"; "identifies persister cells" |

Global rule: DART is a reliability-aware evaluation probe, not a therapeutic
recommender. Report the +0.119 (Class A) and the -0.013 (Class B) together, never
separately.

---

## 6. References (17 verified, DOI-checked via Crossref / arXiv)

**Anchor methods and datasets**
1. Lamb et al. 2006, Science, Connectivity Map. 10.1126/science.1132939
2. Subramanian et al. 2017, Cell, L1000/CMap. 10.1016/j.cell.2017.10.049
3. Peidli et al. 2024, Nat Methods, scPerturb + E-distance. 10.1038/s41592-023-02144-y
4. Lotfollahi et al. 2019, Nat Methods, scGen. 10.1038/s41592-019-0494-8
5. Lotfollahi et al. 2023, Mol Syst Biol, CPA. 10.15252/msb.202211517
6. Hetzel et al. 2022, NeurIPS, chemCPA. arXiv:2204.13545
7. Cui et al. 2024, Nat Methods, scGPT. 10.1038/s41592-024-02201-0
8. Hao et al. 2024, Nat Methods, scFoundation. 10.1038/s41592-024-02305-7
9. Theodoris et al. 2023, Nature, Geneformer. 10.1038/s41586-023-06139-9
10. Roohani et al. 2024, Nat Biotechnol, GEARS. 10.1038/s41587-023-01905-6
11. Guney et al. 2016, Nat Commun, network proximity. 10.1038/ncomms10331
12. Gonzalez et al. 2025, Nat Biomed Eng, PDGrapher. 10.1038/s41551-025-01481-x
13. Srivatsan et al. 2020, Science, SciPlex3. 10.1126/science.aax6234
14. Frangieh et al. 2021, Nat Genet, Perturb-CITE-seq. 10.1038/s41588-021-00779-1

**Evaluation-critique tier (bounds DART's own scores)**
15. Ahlmann-Eltze et al. 2025, Nat Methods, DL predictors vs simple baselines. 10.1038/s41592-025-02772-6
16. Kedzierska et al. 2025, Genome Biol, zero-shot foundation-model limits. 10.1186/s13059-025-03574-x
17. Wei et al. 2026, Nat Methods, scPerturBench. 10.1038/s41592-025-02980-0

Preprints (labeled as such in text): Far-from-Straightforward (bioRxiv 2026,
10.64898/2026.02.14.705879); The Metric Picks the Winner (arXiv:2606.12639).

Full annotated bibliography with per-reference notes:
`related_work_metric_audit_references.md`.
