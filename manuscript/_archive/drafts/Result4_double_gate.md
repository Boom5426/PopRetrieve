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
0.009; Fig 4a), about 2.7-fold less diversity (0.158 versus 0.057), and are more
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
threshold that would indicate reliable recovery (Fig 4b). The failure is not a
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
(Fig 4c). Coverage works only to the extent that Gate 2 is open, and on current
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

*Figure 4. The information condition is a two-gate criterion. (a) Gate 1,
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
