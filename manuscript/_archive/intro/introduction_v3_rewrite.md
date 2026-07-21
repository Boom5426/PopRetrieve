## Introduction

Choosing which perturbation will drive a cell population toward a desired state is a
central problem in therapeutic discovery, from reversing a disease transcriptome to
steering differentiation. Single-cell measurement has reframed this problem, because
a perturbation acts not on an average cell but on a structured mixture of
subpopulations that can respond in different, even opposing, directions. The
computational task that formalizes the choice is inverse retrieval: given a target
population, rank candidate perturbations by how closely their effect reproduces it.
The dominant approach collapses each population to a mean differential-expression
signature and matches signatures, as in Connectivity-Map retrieval (Lamb et al.
2006; Subramanian et al. 2017). Mean collapse is computationally convenient, yet it
discards the very subpopulation heterogeneity that motivates single-cell
measurement; two perturbations with identical mean effects can act on entirely
different subpopulations.

This limitation motivates distribution-aware retrieval, which compares the full
candidate and target populations rather than their means, using population-level
statistics such as energy distance, maximum mean discrepancy, and optimal-transport
costs. The intuition is compelling, the machinery is well developed, and under
natural distributional metrics the improvement over mean retrieval can be large. The
same population-level distances have become standard tools for quantifying
perturbation effects across single-cell biology (Peidli et al. 2024). It would seem
to follow that distribution-aware retrieval is simply the better method.

A recurring lesson from recent benchmarking cautions against that inference. Across
single-cell perturbation modeling, methods of rising sophistication have struggled
to improve consistently over deliberately simple baselines: deep-learning
perturbation predictors do not yet outperform linear or mean-based baselines
(Ahlmann-Eltze et al. 2025), and single-cell foundation models show similar limits
under zero-shot evaluation (Kedzierska et al. 2025). A second, subtler finding
sharpens the concern: the verdict often depends on the metric itself, so that the
choice of evaluation criterion can flip method rankings (Wei et al. 2026), and the
distributional distances now in common use have failure modes that are only
beginning to be characterized. This is the hazard at the center of the present work.
When a distributional retrieval method is scored by a metric that is itself
distributional, an energy-distance regret or a discrepancy-based welfare proxy, the
evaluation and the method share the same mathematical target. A high score then
confirms that the method computes its objective faithfully and that the objective is
discriminative on the data, but it does not, on its own, establish that the output
has independent biological or therapeutic value. We call this objective-aligned
evaluation, and we show that it is a field-wide default rather than an artifact of
any single method.

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

We approach that question by using DART (Distribution-Aware Retrieval for Therapeutic
ranking), a family of population-to-population distributional scores, not as a method
to be defended but as an instrument that makes the gap measurable. DART can be scored
both ways on the same tasks, so it exposes the evaluation sensitivity of
distributional inverse retrieval rather than serving as a therapeutic recommender. On
this instrument we establish five results. First, mean-signature retrieval, including
Connectivity-Map cosine retrieval, is the zero-variance collapsed member of the
distributional family, a positive theoretical anchor that holds independently of any
utility metric and is numerically exact on our benchmark (Hit@1 identical to three
decimals). Second, under objective-aligned metrics distribution-aware retrieval
appears strongly superior, with energy Hit@1 of 0.837 against 0.389 for mean and
Connectivity-Map retrieval and an energy-welfare regret reduction of +0.119 (paired
Wilcoxon p = 4.3 x 10^-56); we report these as proxy results, not as therapeutic
utility. Third, and centrally, these gains do not transfer: under oracle-independent
criteria the advantage collapses to a null (mechanism-of-action recovery nDCG of
-0.013, and 0 of 37 real-data tasks distributionally dominant), and a diagnostic gate
built to concentrate the advantage does not isolate it. Fourth, structure diagnostics
explain the gap, because distributional scores can only exploit the subpopulation
structure that a candidate source actually contains, and current predictors collapse
that structure toward the mean (roughly a fivefold lower subpopulation-variance ratio
than real data). Fifth, we formalize these regimes in HIR-Bench, an analytically
controlled stress test with a specified latent welfare oracle in which retrieval
failure is moderately predictable from observable features (AUC 0.645) and the phase
boundary is expected by construction. An exploratory analysis linking
response-divergent minority states to resistance-associated melanoma programs is
offered as a hypothesis for future work, with no survival or timecourse validation.

Taken together, these results reframe the negative findings not as failures to be
minimized but as the core evidence of the paper. Distribution-aware inverse retrieval
is evaluation-sensitive, and separating the classes of metric is what allows a
genuine signal and a genuine null to be reported honestly side by side. DART is best
understood as a probe for deciding when distributional information is trustworthy,
and the framework it makes concrete is a template other inverse-retrieval methods can
adopt to state precisely what their benchmarks establish and what they do not.
