<!--
DART Manuscript, CRM draft v2 (metric-circularity repositioning).
Positioning: DART is a distributional-retrieval PROBE that exposes evaluation
circularity in heterogeneous inverse drug retrieval, NOT a better recommender.
All headline numbers trace to results/ CSVs (see manuscript_claim_map_v2.md and
manuscript_evidence_table.md). Wording obeys claim_safe_language.md and the
repositioning spec (negative_claims_box.md embedded in Results). HIR-Bench numbers
are FULL-run (AUC 0.640), NOT the on-disk QUICK reproduction (AUC 0.5).
Target: Cell Reports Methods / PLOS Computational Biology / Bioinformatics.
-->

# When is distributional information trustworthy? Auditing evaluation circularity in single-cell drug retrieval

*Working title, see `revised_title_options_metric_circularity.md` for alternatives.*

## Abstract

Distribution-aware drug retrieval for heterogeneous single-cell populations
promises to use the subpopulation structure that mean-signature methods discard,
but its apparent gains can be inflated when the evaluation metric is aligned with
the retrieval objective. We introduce DART (Distributional Auditing of
Retrieval Transfer), a family of population-to-population distributional scores
(energy, maximum-mean-discrepancy, sliced-Wasserstein, and subpopulation-coverage
distances), and use it as a probe to audit how metric choice shapes conclusions in
inverse single-cell drug retrieval. We first show that mean-signature retrieval,
including Connectivity-Map-style cosine retrieval, is the zero-variance collapsed
member of this family: under the implemented cosine kernel it is numerically
identical to DART's collapsed objective (Hit@1 identical to three decimals). On
observed heterogeneous candidate populations, distributional retrieval appears far
stronger than mean retrieval under objective-aligned metrics (energy Hit@1 0.837
versus 0.389; energy-welfare regret reduction +0.119, paired Wilcoxon
p = 4.3 × 10⁻⁵⁶). Critically, these gains do not transfer: under oracle-independent
criteria the advantage collapses (mechanism-of-action recovery nDCG −0.013; 0 of 37
real-data tasks distributionally dominant), and a diagnostic gate built to
concentrate the advantage does not (recommended versus non-recommended proxy gain
+0.119 versus +0.122). Predict-then-rank experiments and structure diagnostics
explain the gap: current perturbation predictors collapse candidate populations
toward the mean (roughly fivefold lower subpopulation-variance ratio than real
data), leaving no reliable structure for distributional scores to exploit. We
formalize these regimes in HIR-Bench, an analytically controlled synthetic stress
test with a specified latent welfare oracle in which retrieval failure is
moderately predictable from observable features (AUC 0.640); its phase boundary is
expected by design, and the real-data gate does not yet isolate oracle-independent
gains. An exploratory analysis links response-divergent minority states to
resistance-associated melanoma programs, a hypothesis-generating observation with
no survival or timecourse validation. DART is best understood as a probe for
evaluating when distributional information is trustworthy, not as a validated
therapeutic recommender.

---

## Introduction

Single-cell technologies have changed what it means to describe a drug's effect: it is not a single number but a distribution. Within a treated population, distinct subpopulations can respond in opposite directions, and the state that governs therapeutic outcome is often a minority one, a persister cell or a resistant clone. This premise drives the current wave of investment in virtual-cell models, single-cell foundation models, and perturbation-response predictors: if responses can be characterized at single-cell resolution, one should be able to rank candidate drugs better than methods that average the population into a mean signature, as the Connectivity Map does.

That premise is rapidly becoming method. Over the past two years, a growing body of work has brought population-to-population distributional distances, optimal transport, maximum-mean-discrepancy, energy distance, and the Wasserstein metric, into single-cell perturbation modeling to capture response structure beyond the mean, and these methods commonly report substantial gains over mean-based approaches. Yet these methods are almost always evaluated by distributional metrics of their own kind. When a distributional model is scored by a distributional yardstick, how much of the reported gain is a genuine improvement in decisions, and how much is simply the method and the yardstick sharing a mathematical target, is a question that has been asked too rarely.

We show why this matters: single-cell perturbation retrieval carries a structural circularity in its evaluation. When a distributional retrieval method is judged by a metric that is itself distributional, an energy-distance regret or a discrepancy-based welfare proxy, the evaluation and the method share the same mathematical objective, and an apparent improvement is close to guaranteed. This is not an oversight of any one study; it is an intrinsic property of aligning an objective with its own measuring stick. The consequence is that "distributional methods are better" can be true under the field's own metrics and false under any criterion an external oracle would actually care about, such as mechanism recovery or measured cell viability.

The distinction we draw throughout is between objective fidelity and independent
utility. Objective-aligned metrics, which we label Class A, are legitimate tests of
whether a method computes its own objective. Task-proximal metrics such as
mechanism-of-action recovery or minority-state coverage (Class B) are more
independent, but they remain derived from the same upstream data. Oracle-independent
utility metrics (Class C), such as dose-response viability, longitudinal survival,
or validated resistance emergence, are what a therapeutic-utility claim ultimately
requires, and they are largely absent from the computational benchmarks on which
these methods are evaluated. An audit across seven representative method families,
spanning signature retrieval, expression prediction, and graph-based inverse design,
finds that objective-aligned evaluation is the default in each. The central question
of this work is therefore not whether distribution-aware retrieval beats mean
retrieval, but where objective fidelity ends and independent utility begins.

To make that boundary measurable, we introduce DART, a family of population-to-population distributional retrieval scores (energy, maximum-mean-discrepancy, sliced-Wasserstein, and subpopulation-coverage distances). Crucially, we prove that mean-signature retrieval, including Connectivity-Map cosine, is not a competitor but the zero-variance collapsed member of this same family: under the implemented kernel the two are numerically identical, with Hit@1 agreeing to three decimals. This unification makes the comparison exact, mean retrieval is DART's own degenerate limit rather than a straw man, and it lets us use DART as a controlled probe: we turn variance and metric class and watch how the conclusion moves.

Across SciPlex3, Frangieh, and CD34+ data, distributional retrieval appears strong under objective-aligned metrics (energy Hit@1 0.837 versus 0.389), but the advantage does not transfer. Mechanism recovery is flat (mechanism-of-action nDCG −0.013), no real-data task is distributionally dominant (0 of 37), and a gate built to concentrate the advantage fails. We then explain the collapse mechanistically, and this is the affirmative payload of the paper: distributional information is unusable today for two independent reasons. Current perturbation predictors collapse candidate populations toward their means, with roughly fivefold loss of subpopulation variance, and even in real data these subpopulations cannot be reliably identified, as no unsupervised method recovers known bimodal structure (best adjusted Rand index below 0.15). We formalize this as a two-gate criterion: structure must first be preserved, and it must be identifiable, before single-cell resolution can begin to pay off.

Our angle differs from two adjacent lines of work. One line provides distributional prediction methods for single-cell perturbation, using optimal-transport or Schrödinger-bridge formulations to model responses [CellOT, Bunne et al. 2023; Departures 2025]; these study how to predict perturbation outcomes better, not how to retrieve or rank candidate drugs, and they do not test whether the evaluation itself is circular. A second line compares distributional evaluation metrics for generative single-cell models [optimal-metrics 2023; standardized-eval 2026]; these ask which metric better measures whether a generated distribution matches the real one, whereas we ask an orthogonal question: when the retrieval score and the evaluation metric are the same distributional object, how much of the reported gain is self-fulfilling. To our knowledge, neither this circularity nor the identity that mean-signature retrieval is the zero-variance collapse of distributional retrieval has been stated before.

These findings give this fast-growing field three things it currently lacks. A test: a probe, together with a synthetic benchmark (HIR-Bench), for deciding whether a distributional gain is real or circular. A diagnosis: a named failure mode, evaluation circularity, that likely inflates results well beyond drug retrieval. And a roadmap: two concrete, measurable gates that tell a virtual-cell modeler what must be fixed before claiming that single-cell resolution improves decisions. DART is best understood as an instrument for knowing when distributional information can be trusted, not as a validated therapeutic recommender; and as single-cell foundation models proliferate, that question will only become more pressing.

---


## Results

### Result 1: Mean-signature retrieval is a collapsed special case of distributional retrieval

We define the inverse retrieval task at the level of populations. For a target
population $Q$ and a library of candidate perturbation populations $\{P_d\}$, a
retrieval score $s(P_d, Q)$ ranks candidates by similarity of effect. Mean-signature
retrieval replaces each population with its mean differential-expression vector and
scores the cosine (or correlation) between mean signatures, the CMap operation.
DART instead scores the full populations with a distributional distance (energy,
MMD, sliced-Wasserstein, or a subpopulation-coverage aggregate) and ranks by the
negative distance.

These are not two unrelated method classes but two ends of one spectrum. Writing a
population as its mean plus a zero-mean residual, the distributional distance
reduces exactly to the mean-to-mean distance when the residual variance is taken to
zero. Mean-signature retrieval is therefore the **zero-variance collapsed member**
of the distributional family. Under the implemented cosine kernel this is not an
approximation but an identity: on the controlled SciPlex3 benchmark, mean-cosine
retrieval and CMap cosine retrieval achieve identical Hit@1
(**mean_cosine = cmap_cosine = 0.3885**, to six figures 0.388492), because they
compute the same operation, the cosine of mean-delta signatures. The distributional
energy score on the same benchmark reaches Hit@1 **0.837**.

The collapse is one end of a continuous spectrum, not an isolated coincidence. The
subpopulation-coverage aggregate carries a temperature $\beta$ that interpolates
between aggregation regimes: as $\beta \to 0$ it averages per-state discrepancies and
as $\beta \to \infty$ it returns the worst state. On the controlled benchmark the
interpolated distance $D_\beta$ rises monotonically from **0.7125** at $\beta \to 0$,
exactly the mean-aggregated value, to **1.300** at $\beta \to \infty$, exactly the
worst-case value (Figure 2a), so mean pooling and worst-case coverage are the two
endpoints of a single family and the intermediate metrics are graded by how much
subpopulation spread they retain. The global energy distance sits inside this same
family: it equals the single-partition ($K = 1$) coverage aggregate exactly
(Panobinostat, energy = coverage$_{K=1}$ = 0.1099, difference 0; Figure 2b), so
energy, coverage, and mean retrieval are one axis of variance sensitivity rather than
competing method classes. Mean-signature retrieval is the zero-variance endpoint of
that axis (Figure 2c).

This unification is the paper's hardest positive contribution because it holds
independently of any downstream utility metric; it is an algebraic fact about the
scoring rules, not a claim about which method is therapeutically better. Two
scope limits are stated explicitly. First, the exact identity is specific to the
cosine connectivity kernel; the canonical L1000 WTCS score is a rank-based
(GSEA-style) enrichment of the same mean-collapsed signature, monotone in the same
quantity but **not algebraically identical** to DART's cosine
(cmap_wtcs Hit@1 0.4635, which differs). Second, the identity concerns the scoring
operation, not the choice of input population; the value of retaining the full
distribution is exactly what Results 2–4 interrogate.

### Result 2: Objective-aligned evaluation produces large apparent distributional gains

When candidate responses are *observed*, the full candidate populations are
available rather than predicted, distributional retrieval looks decisively
stronger than mean retrieval. On the controlled SciPlex3 benchmark, energy-distance
retrieval reaches Hit@1 **0.837** versus **0.389** for mean-cosine and the
numerically identical CMap cosine; PCA-distance retrieval reaches 0.778 and
PCA-mean 0.518 (Figure 3). Extending from observed populations to a
partial-observed retrieval setting, we score candidates by an energy-based welfare
regret, how much decision regret a ranking incurs against a latent welfare
objective, and find a median regret reduction of **+0.119** for the worst-case
subpopulation-coverage variant over mean retrieval, improving **72%** of
**n = 621** queries (paired Wilcoxon **p = 4.3 × 10⁻⁵⁶**).

By the standard of these metrics, distributional retrieval is far ahead. But the
metric here is objective-aligned: the energy welfare regret and the DART energy
score measure the same distributional object. This result therefore establishes
**objective fidelity**, distributional retrieval computes a discriminative
objective, and observed heterogeneous populations contain real distributional
signal, and we label it as such. It is a *distributional retrieval signal under an
objective-aligned proxy*, not evidence of independent therapeutic utility. Whether
that signal survives a more independent judge is the question Result 3 answers, and
it is the reason we do not report +0.119 without immediately reporting what
follows.

### Result 3: Oracle-independent metrics collapse the apparent gains

This is the central result. On the *same* partial-observed queries where the
energy proxy shows a large advantage, we re-score retrieval with metrics that do
not share DART's objective. Under mechanism-of-action recovery nDCG (does the
ranking recover perturbations with the correct annotated mechanism?), the
distributional advantage over mean retrieval is **−0.013**: DART is, if anything,
marginally worse. Projecting the real datasets onto the retrieval task and applying
the non-circular criterion, **0 of 37** real-data tasks are distributionally
dominant. A near-independent minority-state coverage metric shows no material gain
(discussed below).

Crucially, a diagnostic gate designed to *concentrate* the advantage onto the
queries where distributional information should help does not do so. The median
energy-proxy regret reduction is **+0.119** on the gate-recommended subset versus
**+0.122** on the non-recommended subset, the gate does not separate the cases
where DART helps from where it does not, even on the proxy metric it was tuned
against. A direct audit of the gate (see Methods, *gate diagnosis*) makes the
failure concrete: the gate's structure-reliability axis is **anti-correlated** with
true response divergence (Spearman **ρ = −0.21, p = 3.8 × 10⁻⁹**), it moves
opposite to the quantity it is meant to track; while its preference-conflict axis
is only weakly aligned (ρ = +0.18, p = 3.7 × 10⁻⁷), and the binary recommendation
label does not separate high- from low-divergence queries (Mann–Whitney
p = 0.090). Stratifying directly by true response divergence and bypassing the gate
entirely, the highest-divergence stratum does show a statistically significant
minority-coverage gain, but it is negligible in magnitude (median gap rising
monotonically from **+0.0009** in the lowest divergence quartile to **+0.0018** in
the highest, all Benjamini–Hochberg q ≈ 0), while mechanism-of-action recovery is
null at every stratum (highest-quartile q = 0.57, statistical power 0.06). We
summarize this as verdict **B(−): the effect is statistically real but
negligible**, and the deficit is located in the data and task layer, not only in
the gate.

The conclusion is deliberately strong and deliberately bounded: **apparent
distributional gains are metric-dependent and cannot be interpreted as therapeutic
utility without independent validation.** The same method, on the same data, is
"far ahead" or "no better" depending only on which metric class judges it. That
dependence, not a verdict on any single method, is the finding.

> ### What this study does not claim
>
> 1. **We do not claim that DART provides better therapeutic recommendations.** All
>    positive gains are measured under an energy-based, objective-aligned proxy
>    (Class A); no therapeutic-utility metric (Class C) is available in this study.
> 2. **We do not claim oracle-independent therapeutic utility improvement.** Under
>    task-proximal, near-independent metrics (Class B) the advantage is null or
>    negligible (MoA-nDCG −0.013; 0 of 37 real tasks DART-dominant).
> 3. **We do not claim that the current gate reliably transfers to all real
>    retrieval tasks.** The gate is experimental; it flags mean-collapsed predicted
>    responses as no-DART but does not isolate oracle-independent gains in
>    partial-observed real data, and its reliability axis is anti-correlated with
>    true divergence (ρ = −0.21).
> 4. **We do not claim that HIR-Bench is a biological ground truth.** It is a
>    constructive synthetic benchmark whose phase boundary is expected by design.
> 5. **We do not claim that DART predicts resistance.** The resistance analysis is
>    exploratory and hypothesis-generating; there is no timecourse or survival
>    readout, and the minority-rescue contrast is near-null.
> 6. **We do not benchmark live scGen or live PDGrapher.** Perturbation predictors
>    are treated as candidate-response sources, not models under test.
> 7. **We do not claim that all CMap implementations are algebraically identical to
>    DART;** the exact identity is limited to the implemented cosine mean-signature
>    kernel.

### Result 4: The information condition is a two-gate criterion, structure preservation and structure identifiability

Results 2 and 3 together pose a mechanistic question: why is the distributional
signal large on observed populations yet absent under independent metrics? The
answer is a *candidate-response information condition* with two distinct gates.
A distributional score can only exploit subpopulation structure that (i) is
present in the candidate populations supplied to the retriever, and (ii) can
actually be resolved from those populations. We show both gates are closed on
current data, which is why the observed-population result (Result 2) is an upper
bound rather than an operating point.

**Gate 1, structure preservation.** We first test whether generated candidate
populations retain subpopulation structure, using predict-then-rank experiments
in which candidate responses are not observed but produced by a perturbation
predictor, then ranked by DART. Across three predictor families the
distributional advantage over mean retrieval is absent: nDCG deltas are
**-0.004** for an average-effect predictor, **-0.097** for a nearest-neighbor
predictor, and **-0.029** for a CPA-style linear-latent predictor (an in-repo
fallback representative of latent-linear expression models; see Methods).
Structure diagnostics explain why: predicted populations carry roughly
**fivefold** less subpopulation-variance ratio (real 0.046 versus predicted
0.009; Fig 5a), about 2.7-fold less diversity (0.158 versus 0.057), and are more
isotropic (0.959 versus 0.998) than real populations. Current predictors
collapse candidates toward the mean, so the structure a distributional score
exists to exploit is not present in the input.

**Gate 2, structure identifiability.** Preservation is necessary but not
sufficient: even when subpopulation structure is present, a decision layer must
be able to resolve it. We test whether the two-state structure of a query can be
recovered by unsupervised assignment, using a controlled mixture with
ground-truth labels (K562, HDAC-class versus JAK-class cells, alpha = 0.7, 20
seeds), a case where the bimodal structure is known to exist by construction.
Nine unsupervised assignment methods, spanning KMeans (k = 2 to 5), Gaussian
mixtures, PCA-reduced (10 and 50 components) and response-space variants, all
fail to recover it: the best method reaches a median adjusted Rand index of only
**0.10** against ground-truth labels, and none exceeds 0.15, far below the 0.5
threshold that would indicate reliable recovery (Fig 5b). The failure is not a
property of one estimator but of the regime: at the per-query cell counts and
2000-gene dimensionality of single-cell drug screens, subpopulation assignments
are essentially unidentifiable. Consistent with this, across 529 real drugs the
median silhouette of a two-way split is **0.034**, with only 0.4% of drugs
exceeding 0.1.

**Consequence for the coverage layer.** The two gates predict exactly where a
subpopulation-coverage score should and should not carry signal. Stratifying
real-data coverage performance by query identifiability confirms it: coverage
MoA-nDCG rises monotonically with the query silhouette (Spearman rho = **0.26**,
p = 4e-7), from 0.43 in the least-identifiable tertile to 0.58 in the most
(Fig 5c). Coverage works only to the extent that Gate 2 is open, and on current
data it is almost never open: even the most-identifiable tertile has a median
silhouette of 0.038.

The conclusion is a mechanism, not a defect. **A distributional decision layer
cannot exploit subpopulation structure that the candidate source does not
preserve (Gate 1) or that cannot be resolved from the data (Gate 2).** This
delimits when distributional retrieval could help in practice: only where
candidate responses are directly observed, where a generator preserves genuine
subpopulation structure, and where that structure is identifiable at the
available cell depth. It also explains the split seen throughout Results 2 and
3, global distributional scores such as energy distance, which require neither
subpopulation assignment nor structure recovery, retain their apparent
advantage, whereas coverage-type scores, which depend on both gates, collapse to
the mean-retrieval baseline under independent evaluation.

We tested the two-gate prediction head-on. If identifiable structure is what lets
distributional scores help, the per-query mechanism-recovery advantage of
distributional over mean retrieval should turn positive where structure is present.
Stratifying 600 leave-drug-out queries by response divergence, the advantage does
rise monotonically, and the ordering is real and leakage-free (sliced-Wasserstein
trend Spearman rho = 0.14, permutation p = 2e-4). But it never clears parity: the
most-divergent stratum reaches only +0.02 in nDCG with a bootstrap confidence
interval spanning zero, and it reverses in one of three cell lines. Decisively, when
queries are stratified by the actual Gate 2 variable, query identifiability
(silhouette), the advantage is flat (Spearman rho approximately 0). The divergence
ordering reflects response spread, not resolvable subpopulation structure, and Gate 2
does not open on real data even for the most response-divergent queries. The
conditional advantage that a working information condition would produce is therefore
absent, which is the two-gate criterion confirmed rather than rescued.

*Figure 5. The information condition is a two-gate criterion. (a) Gate 1,
structure preservation: perturbation predictors collapse subpopulation-variance
ratio roughly fivefold relative to real populations (exp09; average across three
predictor families). (b) Gate 2, structure identifiability: on a controlled
mixture whose two-state structure is known by construction, nine unsupervised
assignment methods all fail to recover it (median ARI <= 0.10, none > 0.15;
points are per-seed values, vertical ticks are medians; dashed line marks the
ARI = 0.5 recovery threshold). (c) Consequence: real-data coverage MoA-nDCG
rises with query identifiability (silhouette tertiles; Spearman rho = 0.26,
p = 4e-7), but even the most-identifiable tertile has a median silhouette of
0.038, so Gate 2 is almost never open. n and replication units in Methods.*

### Result 5: HIR-Bench formalizes failure regimes but real-domain transfer remains limited

To study these regimes under controlled conditions, we construct HIR-Bench
(Heterogeneous Inverse Retrieval Benchmark), a synthetic, method-neutral generator
with a specified latent welfare oracle. Each task instantiates one of three
information conditions, **observed**, **predicted_mean** (candidates collapsed to
their means), and **predicted_structure** (candidates with partially preserved
structure), and the generator admits an analytical flip boundary
$\alpha^\* = B/(A+B)$ separating the regime where distributional retrieval can help
from where it cannot. On the FULL 13,440-cell grid the sanity checks hold (no-conflict
flip rate 0.0000; median boundary margin 0.29), and retrieval failure is
**moderately** predictable from observable structure and conflict features
(AUC **0.640**; top feature: top-k disagreement).

Two limitations are essential and stated as such. First, HIR-Bench is intentionally
constructive: because it is built from a specified latent welfare model, its phase
boundary is **expected by design**, and the important question is whether real data
project consistently onto the same regimes, not whether the boundary exists.
Second, the information-condition gate derived from these features is an
**experimental diagnostic**, not a validated decision rule: it correctly identifies
mean-collapsed predicted responses as no-DART (100% in the transfer test), but, as
Result 3 established, it does **not** yet isolate oracle-independent DART gains in
partial-observed real data, and its predictability is moderate rather than strong.
HIR-Bench is thus a controlled evaluation framework for exposing failure modes, not
a final real-world diagnostic.

#### Coda: exploratory resistance-associated divergence

As a direction for future work rather than a load-bearing result, we ask whether the
response divergence DART measures has any biological
correlate, as a direction for future work. In the Frangieh melanoma
Perturb-CITE-seq data, cells whose response direction diverges most between
contexts are enriched for **resistance-associated programs**: an
AXL/mesenchymal program (correlation +0.134, p = 0.003), an interferon-response
program (p = 1.9 × 10⁻⁶), and antigen-presentation genes (p = 0.04).

This analysis is **exploratory and hypothesis-generating throughout**. There is no
longitudinal drug-timecourse, no survival readout, and no post-treatment clone
measurement, so we make **no claim that DART predicts resistance** or identifies
persister cells; a quiescence program's sign was not stable between QUICK and FULL
runs and is not interpreted. Consistent with the rest of the paper, the
distributional-versus-mean minority-rescue contrast is itself near-null. The
observation motivates future experiments with functional readouts, and nothing
more.

---

## Discussion

The main result of this work is not that DART is universally better, but that the
evaluation of distributional inverse retrieval is fragile: proxy objectives can
show large gains that vanish under independent criteria. DART is valuable here as a
**probe**, an instrument that can be scored both by its own objective and by more
independent metrics on the same tasks, rather than as a therapeutic recommender.
The paper's positive anchors survive this reframing intact: the mathematical
unification of mean and distributional retrieval is an algebraic fact, and the
existence of real distributional signal in response-available populations is well
supported. What does not survive is the inference from either of those to
therapeutic utility.

### Why the negative results are central

The exp09 predict-then-rank nulls and the exp12/exp13 oracle-independent nulls are
not failures to be hidden; they are the evidence that supports the paper's core
claim. Had we reported only the objective-aligned positive (Result 2), the paper
would have read as "distributional retrieval improves ranking", a conclusion the
independent metrics do not support. Reporting the positive and the null together,
labeled by metric class, is what makes the contribution honest and, we argue, more
useful: it tells a practitioner exactly which conclusions a given metric licenses.
This is why the nulls sit in the main text next to the proxy positives, and why the
negative-claims box is in Results rather than the supplement.

### Implications for virtual-cell and perturbation-prediction models

Result 4 has a direct implication for the fast-growing class of perturbation
predictors and virtual-cell foundation models. In this framework such models are
**candidate-response sources**, and whether a distributional decision layer can add
anything on top of them depends entirely on whether they preserve reliable
subpopulation structure. Our measurements on the predictors tested show mean
collapse severe enough to erase the distributional signal, but we do **not** claim
to benchmark all published models; the point is methodological, structure
preservation, not mean-level accuracy, is the property that determines whether
distributional retrieval is even applicable, and it should be measured and reported
as such. This is consistent with independent benchmarking: Ahlmann-Eltze et al.
(2025) compared five foundation models and two other deep-learning predictors
against deliberately simple baselines for single- and double-perturbation
prediction and found that none outperformed the baselines, and zero-shot
evaluations reach the same conclusion for single-cell foundation models
(Kedzierska et al. 2025), external evidence that objective-aligned reconstruction
accuracy need not translate into an advantage over mean or linear baselines.

### What independent validation would require

Turning DART from an evaluation probe into a therapeutic method would require
Class C, oracle-independent readouts that this study does not contain: dose-response
viability, longitudinal treatment survival, functional perturbation validation,
post-treatment clone expansion, and combination-response validation. Until such
readouts are available, the defensible claim is that distributional information is
*present* in response-available populations but *not yet sufficient* to establish
therapeutic utility. The exploratory resistance signal (Result 6) is precisely the
kind of observation that would need such validation to become a claim.

### Field-level evaluation implications

The broader lesson is that the central distinction is not DART versus mean
retrieval, but **objective fidelity versus independent utility**. Our field-level
audit shows that objective-aligned evaluation is the default across signature
retrieval, expression prediction, and graph-based inverse design: the headline
metric is usually a restatement of the method's own objective. This is legitimate
for testing objective fidelity, and we do not claim any prior method is wrong. But
it means that strong benchmark numbers, on their own, answer a narrower question
than they are often read to answer. This reading is corroborated by recent
metric-focused work: the same distributional metrics DART uses have documented
failure modes, the Wasserstein distance degrades in high-dimensional expression
space under variance scaling and the energy distance can overlook disruptions in
gene–gene dependencies (*Evaluating Single-Cell Perturbation Response Models Is Far
from Straightforward*, 2026), and the choice of evaluation metric alone can flip
model rankings (*The Metric Picks the Winner*, 2026). We cite the first of these
against ourselves: it bounds the interpretation of DART's own Class A scores. DART's
contribution is to make that distinction
explicit and measurable on a single task set, a template other inverse-retrieval
methods could adopt to separate what their metrics establish from what they do not.

---

## Methods

### Data sources and preprocessing

We use four single-cell and perturbation datasets. **SciPlex3** (Srivatsan et al.,
2020): 276,325 cells × 2,000 genes across three contexts (A549, K562, MCF7) and 188
drugs, all present in all three contexts. **Frangieh melanoma Perturb-CITE-seq**
(Frangieh et al., 2021): 218,023 cells × 2,000 highly variable genes across Control,
IFNγ, and Co-culture conditions with 239 CRISPR knockouts. **CD34+** (GSE306429):
33,984 cells × 2,000 genes, 36 drugs (used as an honest negative). **LINCS
closed-loop / PDGrapher benchmark**: 41,070 rows across A549, MCF7, PC3 with 1,369
drugs. Expression is processed to log-normalized differential profiles against
matched controls; per-context control means and treated-population rows are exposed
through a common dataset interface.

### DART retrieval task and distributional metrics

Given a target population $Q$ and candidate populations $\{P_d\}$, DART ranks by a
population-to-population distance. Implemented scores: **energy distance**
(`score_energy`, subsampled to a fixed maximum cell count with a fixed seed), an
**RBF maximum-mean-discrepancy** (`score_mmd_rbf`), a **sliced-Wasserstein** distance
(`score_sliced_wasserstein`, 128 projections), and a **subpopulation-coverage**
aggregate (`score_coverage`) with a temperature parameter $\beta$ interpolating from
mean aggregation ($\beta \to 0$) to worst-case ($\beta \to \infty$). Mean-signature
retrieval (`score_mean_cosine`, `score_mean_l2`) is the zero-variance limit of the
same family.

### Signature and PCA baselines

CMap-style signature retrieval is implemented in `cmap_signature.py`: with
`scoring='cosine'` it computes the cosine of mean-delta signatures, identical to
`score_mean_cosine`, which is the source of the exact Hit@1 identity, and with
`scoring='wtcs'` a rank-based (GSEA-style) weighted connectivity score, a monotone
sibling that is not algebraically identical. PCA-latent retrieval
(`pca_latent_retrieval.py`) fits PCA per query and scores in latent space by mean
or distributional distance.

### Predict-then-rank baselines

Candidate responses are generated by an **average-effect** predictor
(per-drug mean deltas), a **nearest-neighbor** predictor (nearest training context
by control-state similarity, with a strict leave-one-context-out guarantee), and a
**CPA-style linear-latent** predictor used as an in-repo fallback for scGen
(Lotfollahi et al. 2019) when the
isolated scGen environment could not be made numerically stable; the active backend
is provenance-stamped in every output. These predictors stand in for the broader
class of published perturbation predictors and virtual-cell foundation models:
scGen (Lotfollahi et al. 2019), CPA (Lotfollahi et al. 2023), chemCPA (Hetzel et al.
2022), GEARS (Roohani et al. 2024), scGPT (Cui et al. 2024), scFoundation (Hao et
al. 2024), and Geneformer (Theodoris et al. 2023), and are used here as
candidate-response *sources*, not models under benchmark.

### Information-condition diagnostics and gate diagnosis

The information condition is tested as two gates. Gate 1 (structure preservation)
uses the predict-then-rank experiments (exp09): candidate responses are generated
by each predictor family, ranked by DART, and compared to mean retrieval, with
structure diagnostics (subpopulation-variance ratio, diversity, isotropy) computed
on generated versus real populations. Gate 2 (structure identifiability) tests
whether a query's subpopulation structure can be recovered by unsupervised
assignment on a controlled mixture with known two-state composition (K562,
HDAC-class versus JAK-class cells, mixing fraction alpha = 0.7, 20 seeds, 400
cells per query). Nine assignment methods are evaluated: KMeans with k = 2 through
5, Gaussian mixtures with 2 components, all on raw expression and on PCA-reduced
representations (10 and 50 components), plus a response-space KMeans variant. Each
method's assignment is scored against the ground-truth class labels by adjusted
Rand index (ARI); ground-truth labels are used only to evaluate ARI, never as
input to any clustering. Query identifiability on real drugs is the silhouette of
a two-way KMeans split computed per drug on the query cells alone. The
consequence analysis stratifies real-data coverage MoA-nDCG by query-silhouette
tertile (leave-drug-out, A549), reporting the Spearman correlation between query
silhouette and coverage performance.

The gate is additionally audited directly (exp16/exp17) by re-running the
partial-observed retrieval with an additively computed **true response
divergence** column (leave-out-free, from the observed candidate populations),
then correlating each gate axis with true divergence and stratifying retrieval
gaps by divergence quartile with Benjamini-Hochberg control and power analysis.
This audit is the basis for the Result 3 findings that the structure-reliability
axis is anti-correlated with true divergence and that the minority-coverage
effect, while significant, is negligible.

### HIR-Bench generator and synthetic welfare oracle

HIR-Bench generates heterogeneous retrieval tasks from a specified two-subpopulation
latent welfare model with tunable conflict, yielding an analytical flip boundary
$\alpha^\* = B/(A+B)$. Each task is instantiated under the observed, predicted_mean,
and predicted_structure information conditions. A predictability model is trained to
predict retrieval flips from observable structure and conflict features; reported
numbers are from the FULL 13,440-cell grid (n_positive 8,640, n_negative 4,800, AUC
0.640), not from smaller QUICK reproductions.

### Partial-observed retrieval protocol and real-data projection

The partial-observed protocol (exp12) scores candidates by an energy-based welfare
regret against the latent objective and records both the objective-aligned regret
and oracle-independent metrics (MoA-recovery nDCG, minority-state coverage) per
query. Real-data projection (exp13) maps the four datasets onto the HIR-Bench regime
plane and applies the non-circular dominance criterion, yielding the 0-of-37 result.

### Evaluation metric taxonomy and circularity audit

We classify every evaluation metric into three classes (defined fully in
`evaluation_metric_taxonomy.md`). **Class A: objective-aligned proxy metrics**
measure the same mathematical object the method optimizes or scores (e.g.
energy-distance regret for energy-based retrieval, connectivity score for signature
retrieval, reconstruction error for expression predictors, graph proximity for
graph inverse design); they test objective fidelity, not independent utility.
**Class B: task-proximal metrics** are biologically closer but still derived from
the same upstream data (MoA recovery, target-family recovery, DEG overlap, pathway
enrichment, minority-state coverage). **Class C: oracle-independent utility
metrics** have external functional grounding (dose-response viability, longitudinal
survival, post-treatment clone expansion, validated resistance emergence, functional
readouts, combination efficacy) and are required for therapeutic-utility claims. A
field-level audit across seven method families
(`related_work_metric_audit_table.csv`), spanning signature retrieval (Lamb et al.
2006; Subramanian et al. 2017; Peidli et al. 2024), expression predictors and
foundation models (Lotfollahi et al. 2019, 2023; Hetzel et al. 2022; Cui et al.
2024; Hao et al. 2024; Theodoris et al. 2023), and graph/target inverse design
(Guney et al. 2016; Roohani et al. 2024; Gonzalez et al. 2025), shows
objective-aligned evaluation is a
field-wide default; population-level distributional metrics are themselves standard
in recent perturbation-prediction benchmarks (Wei et al. 2026). The manuscript
reports DART under both Class A and Class B and
notes that no Class C metric is available in the datasets used. Verified citations
with DOIs for every family are compiled in `related_work_metric_audit_references.md`.

### Resistance-associated exploratory analysis

Response divergence per cell (exp15) is correlated with curated
resistance-associated program scores (AXL/mesenchymal, interferon-response,
antigen-presentation) in the Frangieh data. This analysis is exploratory; no
survival, timecourse, or functional readout is available, and no
resistance-prediction claim is made.

### Statistical analysis

Paired comparisons use the Wilcoxon signed-rank test; group comparisons use
Mann–Whitney U; monotone associations use Spearman correlation. Multiple comparisons
across strata use Benjamini–Hochberg false-discovery-rate control, and we report
statistical power and the sample size required for 80% power where effects are small.
Effect sizes are reported alongside p-values throughout, and statistically
significant but negligible effects are labeled as such.

### Code and data availability

All code, experiment scripts, and the evaluation-metric taxonomy are available at
`https://github.com/Boom5426/PopRetrieve`. The test suite (`python tests/run_tests.py`)
passes 95/95, and the Phase-1 headline numbers reproduce to within tolerance
(35/35). Large single-cell tensors are obtained separately as described in the
repository `DATA.md`.

---

*Figures are not produced in this writing phase (see `figure_plan_CRM.md` and
`revised_figure_plan_metric_circularity.md` for the planned figure set). All
numbers herein trace to `results/` CSVs via `manuscript_claim_map_v2.md`.*


---

## References

Method-family and evaluation-critique citations were verified against Crossref
(peer-reviewed) or arXiv (conference/preprint); full annotations are in
`related_work_metric_audit_references.md`. Preprints are labeled.

1. Lamb J, et al. (2006). The Connectivity Map: using gene-expression signatures to connect small molecules, genes, and disease. *Science* 313:1929–1935. https://doi.org/10.1126/science.1132939
2. Subramanian A, et al. (2017). A Next Generation Connectivity Map: L1000 platform and the first 1,000,000 profiles. *Cell* 171:1437–1452. https://doi.org/10.1016/j.cell.2017.10.049
3. Peidli S, et al. (2024). scPerturb: harmonized single-cell perturbation data. *Nature Methods* 21:531–540. https://doi.org/10.1038/s41592-023-02144-y
4. Lotfollahi M, Wolf FA, Theis FJ (2019). scGen predicts single-cell perturbation responses. *Nature Methods* 16:715–721. https://doi.org/10.1038/s41592-019-0494-8
5. Lotfollahi M, et al. (2023). Predicting cellular responses to complex perturbations in high-throughput screens (CPA). *Molecular Systems Biology* 19:e11517. https://doi.org/10.15252/msb.202211517
6. Hetzel L, et al. (2022). Predicting cellular responses to novel drug perturbations at a single-cell resolution (chemCPA). *NeurIPS 35.* arXiv:2204.13545 (preprint/conference). https://arxiv.org/abs/2204.13545
7. Cui H, et al. (2024). scGPT: toward building a foundation model for single-cell multi-omics using generative AI. *Nature Methods* 21:1470–1480. https://doi.org/10.1038/s41592-024-02201-0
8. Hao M, et al. (2024). Large-scale foundation model on single-cell transcriptomics (scFoundation). *Nature Methods* 21:1481–1491. https://doi.org/10.1038/s41592-024-02305-7
9. Theodoris CV, et al. (2023). Transfer learning enables predictions in network biology (Geneformer). *Nature* 618:616–624. https://doi.org/10.1038/s41586-023-06139-9
10. Roohani Y, Huang K, Leskovec J (2024). Predicting transcriptional outcomes of novel multigene perturbations with GEARS. *Nature Biotechnology* 42:927–935. https://doi.org/10.1038/s41587-023-01905-6
11. Guney E, et al. (2016). Network-based in silico drug efficacy screening. *Nature Communications* 7:10331. https://doi.org/10.1038/ncomms10331
12. Gonzalez G, et al. (2025). Combinatorial prediction of therapeutic perturbations using causally inspired neural networks (PDGrapher). *Nature Biomedical Engineering.* https://doi.org/10.1038/s41551-025-01481-x
13. Ahlmann-Eltze C, Huber W, Anders S (2025). Deep-learning-based gene perturbation effect prediction does not yet outperform simple linear baselines. *Nature Methods* 22:1657–1661. https://doi.org/10.1038/s41592-025-02772-6
14. Kedzierska KZ, et al. (2025). Zero-shot evaluation reveals limitations of single-cell foundation models. *Genome Biology* 26. https://doi.org/10.1186/s13059-025-03574-x
15. Wei X, et al. (2026). Benchmarking algorithms for generalizable single-cell perturbation response prediction (scPerturBench). *Nature Methods.* https://doi.org/10.1038/s41592-025-02980-0
16. Evaluating Single-Cell Perturbation Response Models Is Far from Straightforward (2026). *bioRxiv* (preprint). https://doi.org/10.64898/2026.02.14.705879
17. The Metric Picks the Winner: Evaluation Choice Flips Model Rankings for Drug-Response Prediction in Unseen Chemistry (2026). arXiv:2606.12639 (preprint). https://arxiv.org/abs/2606.12639

**Datasets.** Srivatsan SR, et al. (2020). *Science* 367:45–51 (SciPlex3). Frangieh CJ, et al. (2021). *Nature Genetics* 53:332–341 (Perturb-CITE-seq). GSE306429 (CD34+). LINCS closed-loop / PDGrapher benchmark (ref. 12).
