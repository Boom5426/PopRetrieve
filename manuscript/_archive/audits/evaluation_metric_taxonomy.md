# Evaluation Metric Taxonomy for Heterogeneous Inverse Retrieval

**Purpose.** This document defines the metric classes used throughout the DART
manuscript and its field-level circularity audit. The distinction it draws —
*objective fidelity* versus *independent utility* — is the conceptual backbone of
the repositioned paper. Every metric a method is scored by falls into one of three
classes, and the class determines what a good score is allowed to mean.

The central principle:

> Objective-aligned metrics are legitimate tests of objective fidelity, but they
> should not be interpreted as independent therapeutic or biological utility.

This is not a criticism of any method or metric. It is a statement about *what
question a metric answers*. A metric structurally aligned with a method's scoring
objective answers a narrower question ("does the method do what it mathematically
claims?") than an oracle-independent metric ("does the method's output have
external functional value?").

---

## Class A — Objective-aligned proxy metrics

**Definition.** Metrics that measure the same mathematical object the method
optimizes or scores. Success on a Class A metric confirms the method computes its
own objective correctly and that the objective is discriminative on the data — but
it cannot, on its own, be read as evidence of downstream utility, because the
evaluation and the method share the same mathematical target.

**Examples across the field.**

| method family | Class A metric | why it is objective-aligned |
|---|---|---|
| energy / MMD distributional retrieval (DART) | energy-distance regret, MMD-based welfare proxy | the evaluation distance *is* the scoring distance |
| CMap / L1000 signature retrieval | connectivity / cosine score of mean signatures | the metric is the scoring rule restated |
| single-cell expression predictors (scGen, CPA, chemCPA) | gene-expression reconstruction (MSE, R², PCC of predicted vs. true delta) | the training loss and the metric optimize the same reconstruction |
| graph / target inverse design (PDGrapher-style) | graph proximity / target-set overlap to the intended target | the scoring graph and the evaluation graph coincide |

**What a good Class A score licenses.** "The method faithfully computes its
objective, and that objective separates candidates on this benchmark." Nothing
stronger.

**DART's own Class A metrics.** `score_energy`, `score_mmd_rbf`,
`score_sliced_wasserstein`, and the energy-based welfare-regret proxy used in the
partial-observed audit (exp12). The +0.119 median regret reduction on the
gate-recommended subset (Wilcoxon p = 4.3 × 10⁻⁵⁶) is a Class A result and is
labeled as such in the manuscript.

---

## Class B — Task-proximal but not fully independent metrics

**Definition.** Metrics that move biologically closer to the intended task than the
method's raw objective, but still fall short of external functional validation.
They typically use annotation or structure that the method did not directly
optimize, yet remain correlated with the objective or with shared upstream data.

**Examples across the field.**

```text
mechanism-of-action (MoA) recovery
drug-target-family recovery
differential-expression (DEG) overlap
pathway-enrichment recovery
minority-state coverage
```

**What a good Class B score licenses.** "The method's output aligns with a
biologically meaningful annotation it was not scored on." This is more independent
than Class A, but MoA labels, DEG sets, and pathway annotations are themselves
derived from expression data and curation pipelines that overlap with the inputs,
so Class B is not a clean external oracle.

**DART's own Class B metrics.** MoA-recovery nDCG and minority-state coverage,
used as the *near-independent* judges in the boundary audit. In the manuscript
these carry the central negative result: MoA-recovery nDCG gain −0.013 on the
recommended subset, minority-coverage gain effectively negligible even where it is
statistically significant (median +0.0009 → +0.0018 across true-divergence
strata). Note that minority-state coverage is a *mean-based* cosine proxy: if
anything it disadvantages DART, which optimizes distributional, not
mean-to-minority-mean, distance — this makes its near-null result conservative.

---

## Class C — Oracle-independent utility metrics

**Definition.** Metrics with external biological or functional grounding, produced
by an experiment or readout that does not share the method's objective or its
input-derived annotations. These are the metrics required to support a therapeutic
or biological *utility* claim.

**Examples across the field.**

```text
dose-response viability
longitudinal treatment survival
post-treatment clone / persister expansion
experimentally validated resistance emergence
functional protein- or cell-state readouts
experimental combination-response efficacy
```

**What a good Class C score licenses.** "The method's output has external
functional consequence" — i.e., an actual therapeutic-utility claim.

**DART's own Class C metrics.** *None are available in this study.* The datasets
used (SciPlex3, Frangieh Perturb-CITE-seq, CD34+, LINCS closed-loop) contain no
drug timecourse, survival, or post-treatment readout. This absence is exactly why
the manuscript makes **no** therapeutic-utility claim and frames the exploratory
resistance analysis (exp15) as hypothesis-generating: it identifies an enrichment
(AXL/mesenchymal, interferon programs in divergent minority states) that *would*
require Class C validation — longitudinal drug-timecourse data this study does not
contain — to become a utility claim.

---

## How the classes structure the DART argument

The repositioned manuscript is organized around the gap between Class A and
Class B/C:

1. **Unification (Result 1)** is class-independent — the identity
   `mean_cosine = cmap_cosine = 0.3885` is an algebraic fact, not a metric score.
2. **Apparent gains (Result 2)** are a Class A result — large and real *as a
   retrieval signal* (energy Hit@1 0.837 vs 0.389; regret reduction +0.119).
3. **Collapse (Result 3, central)** is the Class A → Class B transition — the
   Class A gain does not transfer to the Class B judges (MoA-nDCG −0.013; 0 of 37
   real tasks DART-dominant), and the diagnostic gate does not even concentrate
   the Class A advantage (recommended +0.119 vs non-recommended +0.122).
4. **Utility (not claimed)** would need Class C metrics, which are absent — so the
   paper stops at "signal exists, independent utility not established."

The taxonomy is what lets the paper hold a real positive and a real null at the
same time without contradiction: they are answers to different questions, asked by
different metric classes.

---

## One-line summary

> A method can be strong on Class A (objective fidelity) while being null on
> Class B (task-proximal) and untested on Class C (independent utility). DART
> makes this stratification explicit rather than reporting a single headline
> number that silently conflates the three.
