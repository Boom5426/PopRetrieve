<!--
DART Manuscript — CRM draft v1 (writing phase, prose skeleton).
All headline numbers are confirmed against results/ CSVs (see manuscript_evidence_table.md).
Placeholders [INSERT ...] mark values not yet extracted; do not fabricate.
Wording obeys claim_safe_language.md. HIR-Bench numbers are FULL-run (AUC 0.645).
-->

# Information conditions determine when distributional retrieval improves heterogeneous single-cell drug ranking

## Abstract

Inverse drug ranking for heterogeneous single-cell populations — given a target cell
population, which perturbation best reproduces or reverses it — is typically solved by
collapsing each population to a mean differential-expression signature and matching
signatures, as in Connectivity-Map retrieval. Mean collapse discards the subpopulation
structure that motivates single-cell measurement in the first place. We introduce DART
(Distribution-Aware Retrieval for Therapeutic ranking), which ranks candidate drugs by
population-to-population distributional comparison (energy, maximum-mean-discrepancy,
sliced-Wasserstein, and subpopulation-coverage distances). We show that mean-signature
retrieval is the zero-variance special case of this family: under a cosine kernel it is
numerically identical to DART's collapsed objective. On observed heterogeneous candidate
populations DART improves ranking substantially over mean and signature baselines (Hit@1
0.837 vs 0.389). Critically, this advantage is conditional: when candidate responses are
supplied by predictors that collapse populations toward the mean, the distributional signal
vanishes (predict-then-rank nDCG deltas −0.004 to −0.097), and structure diagnostics show
predicted populations carry roughly fivefold less subpopulation variance than real ones. We
formalize these regimes in HIR-Bench, a method-neutral benchmark with an analytical flip
boundary, and build an information-condition gate that triages tasks into recommend /
mean-sufficient / no-call. In a real-data partial-observed audit, DART's gains are
significant under an energy-based welfare proxy (regret reduction +0.119, Wilcoxon
p = 4.3 × 10⁻⁵⁶) but null under oracle-independent metrics, so we report a conditional,
metric-dependent result rather than universal superiority. DART is a reliability-aware
decision framework for deciding *when* distributional information helps, not a universal
drug recommender.

---

## Introduction

Single-cell perturbation screens now profile hundreds of drugs or genetic perturbations
across heterogeneous populations, spanning cell lines, differentiation states, and immune
contexts. These data pose an inverse problem: given a target population — a disease state to
reverse or a phenotype to reproduce — rank candidate perturbations by how well their
response matches. This inverse-retrieval framing underlies connectivity-based drug
repositioning and, increasingly, single-cell-resolved variants of it.

The dominant solution reduces every population to a single mean differential signature and
ranks candidates by signature connectivity, the paradigm established by the Connectivity Map
and its L1000 successor. This reduction is computationally convenient and, for homogeneous
responses, sufficient. But it discards exactly the information single-cell assays are run to
capture: when a perturbation splits a population into distinct response subpopulations, the
mean signature averages them away.

Whether recovering that structure *helps ranking* is not obvious. Distributional scoring can
only add value if the candidate responses actually contain reliable, non-noise
subpopulation structure. If candidate populations are homogeneous, or if they are supplied
by a predictor that collapses them toward a mean, then the distributional signal has nothing
to exploit and mean retrieval is already optimal. The central question of this paper is
therefore not "is distributional retrieval better?" but "under what information conditions
is it better, and can we diagnose those conditions in advance?"

We formulate inverse drug ranking as distribution-aware retrieval (DART), scoring candidates
by population-to-population distance rather than mean-to-mean distance, and we place mean and
signature retrieval inside this family as the zero-variance limit. We then characterize the
regimes in which the distributional generalization helps, the regimes in which it does not,
and a diagnostic that separates them.

Our contributions are: (i) a distributional formulation of inverse drug ranking that unifies
signature retrieval as a collapsed special case; (ii) an information-conditioned advantage,
positive on observed heterogeneous populations and absent on mean-collapsed predicted
populations, with a mechanistic structure diagnosis; (iii) HIR-Bench, a method-neutral
benchmark that defines observed / predicted-mean / predicted-structure regimes and an
analytical flip boundary; (iv) a real-data partial-observed boundary audit that reports
energy-proxy gains and oracle-independent nulls side by side; and (v) an exploratory
analysis linking response divergence to resistance-associated minority states.

---

## Results

### DART formulates drug ranking as population-to-population retrieval

We define the inverse-retrieval task as follows. A query is a target cell population Q
(with a matched control); a candidate is a drug whose response population P (again
control-matched) is available or predicted. A retrieval method scores each candidate and
ranks them; success is measured by how highly the ground-truth perturbation ranks (Hit@k,
MRR, nDCG). DART scores a candidate by a distributional distance between P and Q rather than
between their means, instantiated as energy distance, maximum-mean-discrepancy, sliced-
Wasserstein, or a subpopulation-coverage distance that aggregates per-subpopulation
distances through a temperature continuum from mean to worst-case (Methods).

Mean-signature retrieval is the degenerate limit of this family. As a population's spread
shrinks to zero, every distributional distance reduces to a function of the means, and the
cosine-connectivity score reduces exactly to DART's mean-cosine objective. Empirically this
is not an approximation but an identity: on the controlled SciPlex3 benchmark, mean-cosine
retrieval and CMap cosine retrieval achieve identical Hit@1 (both 0.3885), because they
compute the same operation — the cosine of mean-delta signatures (Figure 1D). The canonical
L1000 WTCS score, a rank-based enrichment of the same mean signature, is a monotone variant
of this quantity (Hit@1 0.4635) but is not algebraically identical to DART. Signature
retrieval is thus one end of a spectrum, not a separate paradigm (Figure 1).

### Distributional retrieval improves ranking when candidate populations preserve heterogeneity

On observed heterogeneous candidate populations — the setting where true response
populations are available — the distributional generalization improves ranking
substantially. The distributional energy score reaches Hit@1 0.837, versus 0.389 for
mean-cosine and the identical CMap cosine, with subpopulation-coverage variants at 0.773
(mean aggregation) and 0.589 (worst-case) (Figure 2B,C). The advantage is not an artifact of
raw gene-space geometry: a PCA-latent distributional score (`pca_dist`) also outperforms its
mean counterpart (0.778 vs 0.518), indicating that the gain comes from using the response
*distribution*, not from any particular coordinate system. Ranking-flip analysis shows
concrete queries where the mean-selected and distribution-selected top candidates disagree,
localized to high-divergence mixtures (Figure 2D). This establishes the upper-bound, oracle
setting: when real candidate populations are observable, distributional information helps.

### Mean-only predicted responses erase DART's advantage

Real workflows rarely observe every candidate's response; instead a predictor imagines it.
We therefore tested predict-then-rank: a perturbation predictor generates each candidate's
response population, and DART ranks the imagined populations. Across three predictor families
— average-effect, nearest-neighbor, and a latent-linear predictor (a CPA-style fallback for
scGen; Methods) — distributional retrieval provides no consistent gain over mean retrieval,
with nDCG deltas of −0.004, −0.097, and −0.029 respectively (Figure 3B). (We note the
picture is metric-dependent even here: on Hit@1 the distributional energy score exceeds mean
retrieval for two of the three predictors; Supplementary Fig. S4. The nDCG delta is the
conservative summary.)

The mechanism is measurable. Structure diagnostics comparing real and predicted candidate
populations show that predicted populations are markedly more collapsed: their
subpopulation-variance ratio is roughly fivefold lower (0.009 vs 0.046), their response
diversity roughly 2.7-fold lower (0.057 vs 0.158), and their covariance closer to isotropic
(isotropy index 0.998 vs 0.959) (Figure 3C). A predictor that returns a near-isotropic blob
around the mean leaves no reliable subpopulation structure for a distributional score to
exploit. The advantage of distributional retrieval is therefore governed by the *information
condition* of the candidate source — not by the retrieval metric alone (Figure 3D).

### HIR-Bench defines and diagnoses heterogeneous retrieval failure regimes

To study these regimes systematically we built HIR-Bench, a method-neutral synthetic
benchmark. It generates heterogeneous query populations along a bias continuum and supplies
candidate responses under three information conditions: `observed` (true populations),
`predicted_mean` (mean-collapsed), and `predicted_structure` (structure-preserving). A
latent welfare oracle assigns each candidate a utility per subpopulation
(u[d,k] = −E‖x − t_k‖²) and aggregates it through mean, worst-case, or CVaR welfare, from
which a decision regret and an oracle flip risk follow. For the two-subpopulation core the
benchmark admits an analytical flip boundary α* = B/(A + B), where A and B are the majority
and minority preference margins (Methods).

On the full 13,440-cell grid, HIR-Bench passes its internal sanity checks: the no-conflict
flip rate is 0.0 (below the 0.05 threshold), the median boundary margin is 0.29, and under
the `predicted_mean` condition the DART-minus-mean gap collapses to 0.051 (below 0.10),
recovering the empirical erasure result of the previous section. A predictability layer then
asks whether flip risk can be anticipated from observable (non-oracle) conflict features. Using
leave-one-grid-out logistic regression, oracle flip risk is predicted with AUC 0.645 —
moderate, not accurate — with top-k disagreement the most informative feature (Figure 4D).
HIR-Bench thus provides both the vocabulary (three regimes, an analytical boundary) and a
quantitative, if imperfect, handle on when distributional retrieval will fail.

### Partial-observed retrieval reveals metric-dependent gains and boundary conditions

We next audited DART on real data in the realistic partial-observed setting, holding out
drugs, mechanism-of-action classes, or library fractions on SciPlex3 (6,885 scored
query–candidate rows across 765 diagnostic queries). An information-condition gate — built
from the structure-reliability and preference-conflict diagnostics — triaged queries into
DART_recommended (621), mean_or_no_call (133), and mean_sufficient (11).

Under an energy-based welfare proxy, DART's gains on the recommended subset are large and
highly significant: the worst-case-coverage variant reduces decision regret by a median of
+0.119 (paired Wilcoxon p = 4.3 × 10⁻⁵⁶), improving 72% of the 621 recommended queries. The
gate also behaves correctly at the safe end — on the small mean_sufficient subset DART shows
exactly zero advantage.

We deliberately tested whether this proxy result survives oracle-independent scrutiny, and
report that it does not. On mechanism-of-action recovery (nDCG) the best DART method
*loses* to mean retrieval on the recommended subset (−0.013), and the minority-state
coverage gain is essentially zero (+0.005). Projecting five real datasets onto the HIR-Bench
regime plane, no task (0 of 37) is DART-dominant under the non-circular minority-coverage
criterion, even as the gate correctly flags every predicted-mean task as no-DART (100%).
Finally, the gate does not sharply concentrate even the proxy advantage: median regret
reduction is +0.119 on the recommended subset versus +0.122 on the non-recommended subset.
We therefore report a conditional, metric-dependent result — a conditional-go — rather than
a therapeutic-superiority claim (Figure 5). The energy-welfare proxy is aligned with DART's
own objective, and we treat its gains as suggestive; the oracle-independent nulls bound the
claim.

### Exploratory: response-divergent minority states are enriched for resistance-associated programs

Finally, as an exploratory branch, we asked whether the quantity DART is sensitive to —
response divergence, the splitting of a population into distinct response modes — carries
biological signal. On the Frangieh melanoma Perturb-CITE-seq screen, we measured per-
perturbation response divergence and tested whether the emergent minority subpopulation is
enriched for resistance-associated marker programs. Divergent minority states are enriched
for the AXL/mesenchymal program (correlation +0.134, p = 0.003), the canonical drug-tolerant
melanoma program, and for interferon-response (p = 1.9 × 10⁻⁶) and antigen-presentation
(p = 0.04) programs (Figure 6B,C). We emphasize this is hypothesis-generating: the screen
has no drug timecourse, so the link from pre-treatment divergence to post-treatment survival
cannot be tested, and a direct DART-versus-mean minority-rescue contrast is near-null. We
therefore make no predictive resistance claim (Figure 6D).

---

## Figure captions

**Figure 1. Distribution-aware retrieval and the unification of signature retrieval.**
(A) Mean-signature retrieval collapses each population to a mean differential signature and
matches by cosine connectivity. (B) DART scores candidates by population-to-population
distributional distance. (C) As candidate spread shrinks to zero, every distributional
distance reduces to a function of the means; mean retrieval is the zero-variance limit.
(D) On controlled SciPlex3, mean-cosine and CMap-cosine achieve identical Hit@1 (0.3885),
confirming the identity; the rank-based WTCS variant (0.4635) is a monotone sibling; the
distributional energy score (0.837) is the upper reference.

**Figure 2. Distributional retrieval improves ranking on observed heterogeneous
populations.** (A) exp08 controlled-mixture design. (B) Hit@1 / nDCG across methods.
(C) Distributional scores (energy, coverage, PCA-latent distance) versus mean and CMap
baselines; PCA-latent distance (0.778 vs 0.518) shows the gain is not a raw gene-space
artifact. (D) Ranking-flip examples where mean- and distribution-selected top candidates
disagree, localized to high-divergence mixtures.

**Figure 3. The information condition of the candidate source explains predictor failure.**
(A) Predict-then-rank: a predictor imagines candidate populations that DART ranks. (B) DART
minus mean nDCG deltas across three predictors (-0.004 / -0.097 / -0.029). (C) Real versus
predicted structure diagnostics: subpopulation-variance ratio (0.046 vs 0.009), diversity
(0.158 vs 0.057), isotropy (0.959 vs 0.998). (D) Schematic: predictor collapse toward an
isotropic mean removes the structure distributional retrieval needs.

**Figure 4. HIR-Bench defines and diagnoses retrieval regimes.** (A) Three information
conditions. (B) Latent welfare oracle and mean/worst/CVaR aggregation. (C) Analytical flip
boundary alpha* = B/(A+B) versus empirical flips. (D) Sanity checks (all pass) and moderate
predictability of flip risk (AUC 0.645), with feature importances led by top-k disagreement.
Values from the full 13,440-cell grid.

**Figure 5. Partial-observed boundary audit: metric-dependent gains.** (A) Leave-drug /
leave-MoA / partial-library protocol and the recommend / mean-sufficient / no-call gate.
(B) Energy-proxy gains on the recommended subset (regret reduction +0.119, Wilcoxon
p = 4.3e-56, 72% of 621 queries). (C) Oracle-independent metrics are null (MoA-recovery
nDCG -0.013; minority-coverage ~0; exp13 0/37 real tasks DART-dominant). (D) The gate does
not concentrate the proxy advantage (recommended +0.119 vs non-recommended +0.122);
verdict, conditional-go. This falsification test was performed by the authors.

**Figure 6. Exploratory: response divergence marks resistance-associated minority states.**
(A) Per-perturbation workflow: response divergence, two-subpopulation split, marker-program
scoring in the minority versus majority state. (B) AXL/mesenchymal enrichment versus
divergence (corr +0.134, p = 0.003). (C) Interferon-response (p = 1.9e-6) and
antigen-presentation (p = 0.04) enrichment. (D) Limitations: no drug timecourse (survival
not evaluable), near-null minority rescue; longitudinal validation is future work. Entire
figure is exploratory.

---

## Discussion

Distribution-aware retrieval is best understood not as a better drug recommender but as a
reliability-aware decision framework. Its central lesson is negative in form and useful in
consequence: the distributional generalization of signature retrieval helps only when the
candidate responses carry reliable subpopulation structure, and current perturbation
predictors do not supply it. By making signature retrieval the zero-variance limit of a
single family, DART turns "mean versus distributional" from a dichotomy into a diagnosable
continuum.

The honest boundary is the contribution. A predict-then-rank negative (exp09) and a
non-circular null on real data (exp12/exp13) would be liabilities for a method paper that
claimed universal superiority; here they are the evidence base for the framework's actual
deliverable — knowing *when not to* use distributional retrieval. The information-condition
gate operationalizes this as a triage: recommend DART where reliable structure and high
preference conflict coincide, defer to mean retrieval where they do not, and decline to call
where the candidate source is mean-collapsed. In the transfer test this gate correctly
flags every predicted-mean task as no-DART, which is precisely the regime a practitioner
most needs warning about.

These results also clarify the relationship to prior work. Connectivity-based retrieval
(CMap, L1000) is not a competitor but the mean-collapsed limit of the same family.
Perturbation predictors and virtual-cell models (scGen, CPA, PDGrapher) are not competitors
either; they are candidate-population *sources* whose information condition determines
whether a distributional decision layer on top of them can add value. The framework thus
sits downstream of prediction and upstream of decision, and its message to both is the same:
the value of population structure is conditional and measurable.

The strongest limitation is the one that also defines the next step. Our positive result
rests on an energy-based welfare proxy aligned with DART's own objective; the metrics we
trust more — mechanism-of-action recovery, minority-state coverage — are null. Upgrading the
claim from "conditional, proxy-supported" to "practically useful" requires an
oracle-independent utility with real consequences, most naturally a longitudinal
treatment-survival or resistance readout. The exploratory finding that response-divergent
minority states are enriched for drug-tolerant programs (AXL/mesenchymal, interferon) points
at exactly such a readout, and connects the retrieval framework to a concrete biological
question — but establishing it needs drug-timecourse data this study does not contain.

---

## Methods (outline — to be expanded to full prose)

1. **Data sources and preprocessing.** SciPlex3 (276,325 cells, 2000 HVGs, A549/K562/MCF7,
   188 drugs); Frangieh melanoma Perturb-CITE-seq (218,023 cells, Control/IFNg/Co-culture,
   239 CRISPR-KOs); CD34+ (33,984 cells, 36 drugs); precomputed LINCS/PDGrapher closed-loop
   benchmark (41,070 rows, A549/MCF7/PC3, 1,369 drugs). Normalization, HVG selection, control
   matching per dataset.
2. **DART retrieval task.** Query/candidate/control definitions; ground-truth assignment;
   Hit@k, MRR, nDCG.
3. **Distributional metrics.** Energy distance; MMD-RBF (median-bandwidth); sliced-
   Wasserstein-1 (random projections); subpopulation-coverage distance with the
   log-sum-exp temperature continuum from mean (beta->0) to worst-case (beta->inf), K=1
   reducing to the global distance. Subsampling (max_cells) and small-population penalties.
4. **Signature and PCA baselines.** CMap cosine and WTCS-lite (rank enrichment); PCA-latent
   mean and distance scores.
5. **Predict-then-rank baselines.** Average-effect and nearest-neighbor predictors;
   scGen — because the published scGen stack is unbuildable on the current toolchain, an
   isolated environment falls back to an in-repo CPA-style latent-linear predictor, with the
   backend stamped in all outputs; results are representative of latent-linear predictors,
   not a scGen benchmark.
6. **Information-condition diagnostics.** Structure-reliability (bootstrap stability,
   energy-disagreement, subpopulation-variance ratio, diversity) and preference-conflict
   (per-state Kendall) features; the recommend / mean-sufficient / no-call gate.
7. **HIR-Bench generator and oracle welfare.** Bias-continuum generation; latent utility
   u[d,k] = -E‖x - t_k‖^2; mean/worst/CVaR welfare; oracle flip risk with tie tolerance;
   analytical boundary alpha* = B/(A+B). QUICK and FULL grid specifications.
8. **Partial-observed retrieval protocol.** Leave-drug-out, leave-MoA-out, partial-library
   splits; welfare-regret proxy; recommendation-mode assignment.
9. **Real-data projection.** Percentile transfer of the HIR-Bench conflict boundary to real
   conflict distributions; minority-coverage outcome as the non-circular criterion.
10. **Resistance-associated exploratory analysis.** Response divergence (between-subpopulation
    variance ratio of the control-subtracted response); marker-program scoring against a
    common z-reference; Mann–Whitney high- versus low-divergence enrichment.
11. **Statistical analysis.** Paired Wilcoxon signed-rank (regret); Mann–Whitney U and
    Pearson correlation (enrichment); leave-one-grid-out CV (predictability AUC);
    Benjamini–Hochberg correction for exp15; explicit circular/proxy/independent metric
    labeling throughout (see `statistical_reporting_checklist.md`).
12. **Code and data availability.** Code at github.com/Boom5426/DART; data obtained from the
    original sources per DATA.md; large regenerable dumps excluded from the repository.

---

<!-- END draft v1. Next phase (not this one): final figures, README, cover letter. -->
