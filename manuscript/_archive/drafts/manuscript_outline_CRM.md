# DART Manuscript — Outline (Cell Reports Methods target)

Working title: **Information conditions determine when distributional retrieval improves
heterogeneous single-cell drug ranking**

Target: Cell Reports Methods / PLOS Computational Biology / Bioinformatics.
Every value below is confirmed in `manuscript_evidence_table.md`. Wording obeys
`claim_safe_language.md`.

---

## Abstract (180–220 words)

Single sentence beats: (1) inverse drug ranking for heterogeneous single-cell populations
usually collapses responses to mean signatures; (2) DART ranks candidate drugs by
population-to-population distributional comparison; (3) mean-signature retrieval is the
zero-variance special case (exp08 identity); (4) DART improves ranking on *observed*
heterogeneous candidate populations (energy 0.837 vs mean 0.389); (5) the advantage
disappears when predictors generate mean-only / isotropic populations (exp09); (6)
HIR-Bench and an information-condition gate diagnose the regime; (7) under oracle-independent
metrics the advantage is not yet demonstrated (exp12/exp13), so we report a conditional,
metric-dependent result; (8) conclusion — DART is a reliability-aware decision framework,
not a universal recommender.

---

## Introduction (5 paragraphs)

1. Single-cell perturbation screens (SciPlex3, Perturb-CITE-seq) expose population
   heterogeneity and create an inverse problem: given a target population, rank drugs.
2. Existing retrieval (CMap / L1000 connectivity, signature reversal) collapses each
   population to a mean differential signature.
3. Mean collapse discards subpopulation structure. Distributional scoring *should* help —
   but only if reliable structure exists in the candidate responses. This conditionality is
   the paper's organizing question.
4. DART formulates inverse drug ranking as distribution-aware retrieval (energy / MMD /
   sliced-Wasserstein / subpopulation coverage), with mean retrieval as the zero-variance
   limit.
5. Contributions: (i) distributional formulation + unification of signature retrieval;
   (ii) information-conditioned advantage with a mechanistic structure diagnosis; (iii)
   HIR-Bench method-neutral diagnostic framework; (iv) real-data partial-observed boundary
   audit with honest non-circular nulls; (v) exploratory resistance-associated minority-state
   analysis.

---

## Results (6 subsections)

### Result 1 — DART formulates drug ranking as population-to-population retrieval
- Task definition; distributional objective; mean retrieval as collapsed special case.
- **CMap cosine identity**: mean_cosine = cmap_cosine = 0.3885 (Claim 1).
- → Figure 1.

### Result 2 — Distributional retrieval improves ranking only when candidate populations preserve heterogeneity
- exp08 positive: energy 0.837 vs mean/CMap 0.389; `pca_dist` 0.778 (latent distributional)
  shows the effect is not a raw gene-space artifact; coverage 0.773/0.589.
- Ranking-flip examples between mean and DART.
- → Figure 2.

### Result 3 — Mean-only predicted responses erase DART's advantage
- exp09 predict-then-rank negatives: nDCG deltas −0.004 / −0.097 / −0.029.
- Structure diagnostics: real vs predicted subpop_var_ratio 0.046 vs 0.009; diversity 0.158
  vs 0.057; isotropy 0.998 (predicted) vs 0.959 (real).
- Conclusion: the information condition of the candidate source governs the advantage.
- → Figure 3.

### Result 4 — HIR-Bench defines and diagnoses heterogeneous retrieval failure regimes
- observed / predicted_mean / predicted_structure modes; latent welfare oracle
  (u[d,k]=−E‖x−t_k‖²); analytical boundary α*=B/(A+B).
- FULL sanity checks pass (no_conflict_flip_rate 0.0; boundary margin 0.29; predicted_mean
  gap 0.051); predictability AUC = 0.645 (moderate).
- → Figure 4.

### Result 5 — Partial-observed retrieval reveals metric-dependent gains and boundary conditions
- exp12: energy-proxy positive (DART_coverage_worst regret reduction +0.119, Wilcoxon
  p=4.3e-56, 72%, n=621); non-circular metrics null (MoA-recovery nDCG −0.013;
  minority-coverage ≈0); gate does not separate recommended (+0.119) from non-recommended
  (+0.122).
- exp13: 0/37 real tasks DART-dominant under non-circular criterion; predicted_mean→no-DART
  100% (transfer of the gate).
- Conclusion: CONDITIONAL-GO, metric-dependent.
- → Figure 5.

### Result 6 — Exploratory response-divergent minority states are enriched for resistance-associated programs
- exp15: AXL/mesenchymal corr +0.134 (p=0.003); IFN p=1.9e-6; antigen-presentation p=0.04.
- Limitations: no timecourse (Part B not evaluable); Part C rescue near-null; quiescence
  sign-flip not claimed.
- → Figure 6.

---

## Discussion

- DART is **not** a universal drug recommender; it is a reliability-aware decision framework.
- Use DART only when candidate responses contain reliable population structure; the gate
  triages recommend / mean-sufficient / no-call.
- Why the honest boundary matters: it converts a negative (exp09) and a null (exp12/exp13)
  into the paper's central, defensible contribution — knowing *when not to* use distributional
  retrieval.
- Relationship to prior work: signature retrieval (CMap/L1000) is the mean-collapsed limit;
  virtual-cell / perturbation predictors (scGen, CPA, PDGrapher) supply candidate populations
  whose information condition determines DART's usefulness — shoulders, not competitors.
- Strongest future direction: link response divergence to longitudinal treatment
  survival / resistance (the oracle-independent utility that would upgrade the claim).

---

## Methods (subsections)

1. Data sources and preprocessing (SciPlex3, Frangieh Perturb-CITE-seq, CD34+, precomputed
   LINCS/PDGrapher benchmark; 2000-HVG panels).
2. DART retrieval task and query construction.
3. Distributional metrics (energy, MMD-RBF, sliced-Wasserstein, subpopulation coverage;
   the coverage temperature continuum mean↔worst).
4. Signature and PCA baselines (cmap cosine / wtcs; PCA-latent mean/dist).
5. Predict-then-rank baselines (average-effect, nearest-neighbor, scGen→CPA-linear fallback
   with stamped provenance).
6. Information-condition diagnostics (structure reliability, preference conflict).
7. HIR-Bench generator and oracle welfare functions (mean/worst/CVaR; flip risk; α*).
8. Partial-observed retrieval protocol (leave-drug-out / leave-MoA-out / partial-library).
9. Real-data projection (percentile transfer of the HIR boundary; minority-coverage outcome).
10. Resistance-associated exploratory analysis (divergence, marker-program enrichment).
11. Statistical analysis (paired Wilcoxon, Mann–Whitney; circular vs proxy vs independent
    metric labeling — see `statistical_reporting_checklist.md`).
12. Code and data availability (github.com/Boom5426/DART).
