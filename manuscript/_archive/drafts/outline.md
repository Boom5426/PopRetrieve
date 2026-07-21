# Paper outline (stub, transcribed from plan v3 §11)

## Title (recommended)
**DART: Distribution-Aware Retrieval for Therapeutic Ranking**
(subtitle: *Distributional Inverse Drug Retrieval for Heterogeneous Single-Cell Populations*)

Alternatives: On Retrieval Objectives for Single-Cell Inverse Drug Discovery ·
Distribution-Aware Ranking for Single-Cell Inverse Drug Discovery · When Mean-Based
Drug Retrieval Fails in Heterogeneous Cellular Populations · Beyond Mean Signatures.

## Abstract skeleton
Single-cell perturbation models increasingly predict cellular responses at the
population level, yet inverse drug discovery ultimately requires a decision: ranking
candidate drugs for a query cellular population. Existing retrieval objectives often
collapse heterogeneous populations into mean signatures, implicitly assuming the best
drug is the one that best matches the average response. We formulate inverse drug
discovery as a distributional retrieval problem, where both query states and candidate
drug responses are cell-state distributions. Mean-based retrieval fails systematically
when subpopulations exhibit divergent drug-response directions (majority-biased
rankings that miss drugs covering multiple subpopulations). We benchmark
distribution-aware retrieval objectives (energy distance, MMD, sliced-Wasserstein,
subpopulation coverage) across controlled SciPlex3 mixtures, cross-cell-line mixtures,
primary CD34+ cells, and melanoma Perturb-seq, and show the distributional advantage
appears precisely when response divergence exceeds a predictable threshold, reducing to
mean retrieval in homogeneous limits.

## Contributions
1. **Distributional inverse drug retrieval** — d* = argmin_d D(P_d, Q); the objective is
   the ranking/retrieval decision, not a response predictor.
2. **Distribution-aware ranking objectives** — the win comes from *using a distributional
   distance*, not from complex subpopulation modeling (global energy at K=1 already fixes
   most mean-based failure).
3. **Heterogeneity boundary** — divergence-gated (subpop-response cos ≲ 0.9), depth-robust
   (15–60 cells/subpop), metric-agnostic.
4. **Honest real-data boundary** — selectively beneficial, not universally better
   (CD34+ negative; Frangieh natural instance).

## Introduction logic (6 paragraphs)
tech → most ML is forward/generative → practice needs ranking → current ranking
collapses to mean → collapse is conditional (fails when subpops diverge) → we formulate
distributional retrieval + characterize when it is necessary.

## Final claim
We formulate single-cell inverse drug discovery as a distributional drug retrieval
problem; mean-based retrieval is a valid low-variance approximation only when
subpopulation responses are aligned, but produces systematic ranking failures when they
diverge. Distribution-aware objectives strictly generalize mean matching and give robust
ranking precisely in the divergent-response regime.
