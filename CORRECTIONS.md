# Corrections and retractions, 2026-07-12

An audit of this repository found that several published numbers were artifacts of our own
code rather than properties of the data or of the methods being studied. This file records
every correction, what the number was, what it is, and why it changed. It exists because the
paper's thesis is that objective-aligned evaluation inflates results, and a paper making
that argument cannot itself ship numbers it has not checked.

**None of them overturns the paper's central claim.** The distributional gain is
still large under objective-aligned metrics and still fails to transfer to oracle-independent
ones. Several corrections make the negative result *sharper*. Two retract a mechanism we had
asserted, and one converts an apparent confirmation into a refutation.

**R14 is the one that adds a result rather than removing one, and it is the most serious
process failure recorded here.** The manuscript asserted, in three places, that no Class C
(oracle-independent) metric was available in this study. The repository has contained one the
whole time: 155 SciPlex3 drugs matched to GDSC dose-response viability, plus the experiment and
the control that decides it. A paper arguing that the field avoids oracle-independent evaluation
cannot claim no such readout exists while shipping one in its own code. The result, once the
controls are applied, is the strongest evidence in the paper *for* the paper's thesis: the
apparent Class C win is a response-magnitude confound, beaten by a scalar that never looks at
the query.

**R13 is the one that changes a headline claim, and it took three attempts.** The paper's
"0 of 37 real-data tasks are distributionally dominant" quotes a QUICK sanity run. Our first
correction ("11 of 215 are dominant") was also wrong: it swapped the denominator and, worse,
reported a count of threshold crossings as a finding, which is the error this paper exists to
criticize. What we report now is the distribution: the real-data advantage is statistically
real (Wilcoxon p = 1.3e-7) and practically negligible (mean +0.0018), and it is confined to
the cell-line mixtures we constructed. The thesis is untouched; an absolute became a
distribution.

---

## R1. RETRACTED: "predictors collapse subpopulation structure ~5x"

**Was:** predicted candidate populations carry roughly fivefold less subpopulation-variance
ratio than real data (real 0.046 versus predicted 0.009). Reported in the abstract, the
introduction, Result 4, Fig 4c, and ED Fig 3c.

**Is:** false, on both sides of the comparison.

- The *predicted* side (0.009) was the **null value of the statistic**, not a measurement.
  Every predictor synthesized its population as `control_mean + delta + iid N(0, sigma)`,
  which is unimodal by construction (isotropy index 0.998). A k-means k=2 between-total
  variance ratio on an isotropic cloud returns ~0.009 no matter what the predictor learned.
  We were measuring our own synthesizer.
- The *real* side (0.046) was a **single-context** treated population, not the alpha-blended
  candidate population that a scorer actually ranks.

**Corrected measurement** (`results/exp09_structure_diagnostics/`, n=96 per row). Populations
are now synthesized by applying the predicted effect to the query context's real control
cells, one cell at a time, which is what latent-arithmetic models actually do:

| candidate population | subpop-variance ratio | induced response cosine |
|---|---:|---:|
| **real** (alpha-blended, what the scorer ranks) | **0.138** | **0.014** |
| predicted, average-effect | 0.142 | 0.186 |
| predicted, latent (scGen-family) | 0.462 | 0.239 |
| predicted, nearest-neighbour | 0.142 | 0.366 |

**The corrected mechanism is stronger than the retracted one.** Predictors do not collapse
structure; they preserve it. What they fail to produce is *differential response*. Real
subpopulations respond near-orthogonally (cosine 0.014); predicted ones respond in largely
aligned directions. This is analytic, not empirical: average-effect, nearest-neighbour, scGen
and CPA are all **additive** models that add one delta vector to every cell, so the two
subpopulations' response deltas are identical and the induced divergence is exactly zero. A
distributional score has nothing differential to exploit however much structure survives.

Code: `src/baselines/population_synthesis.py` (new, documents both synthesizers);
`src/baselines/scgen_predictor.py:179` no longer averages scGen's per-cell output away.
Pinned by `tests/test_predictors_smoke.py::test_additive_predictors_induce_zero_response_divergence`.

---

## R2. CORRECTED: MoA-nDCG statistics were computed over 165 undefined values

**Was:** MoA-nDCG median gap = 0.000 in every divergence stratum, n=765, Q4 needs n≈27,794
for 80% power.

**Is:** MoA recovery is **undefined** for the `leave_MoA_out` and `partial_library` splits,
where the whole mechanism class is removed from the library. `exp12` wrote those 165 of 765
queries (21.6%) as the literal value **-1**, and `exp16`/`exp17` differenced them like
measurements: `(-1) - (-1) = 0`. Those 165 structural zeros were entering n, pinning the
median at exactly 0.000 in every stratum, shrinking the standard deviation, and feeding the
power calculation.

**Corrected** (`exp16_common.mask_undefined`; sentinel written as NaN at source):

| stratum | n (was 191) | median gap (was 0.000) | BH q |
|---|---:|---:|---:|
| Q1 (lowest divergence) | 166 | **−0.030** | 5.8e-5 |
| Q2 | 150 | 0.000 | 0.073 |
| Q3 | 141 | 0.000 | 0.566 |
| Q4 (highest) | 143 | 0.000 | 0.566 |

Total n for MoA-nDCG: **600**, not 765. Q4 n for 80% power: **20,844**, not 27,794.

**This sharpens the negative result.** At the lowest divergence level PopRetrieve does not merely
fail to help, it **significantly hurts** annotation recovery. `minority_state_coverage` is
unaffected (it never used the sentinel): Q1 +0.0009, Q4 +0.0018 stand as published.

---

## R3. RETRACTED: the CD34+ negative control confirmed the divergence gate

**Was:** a table in `exp02_divergence_gate.py` placed the three datasets on the divergence
axis: CD34+ at cosine **0.95** ("below gate, no advantage"), Frangieh 0.65, cross-line 0.14.
The comment above it read "from probes". **No probe ran.** The three values were typed in.
The table is the source data for Fig 1e and Fig 2e.

**Is** (now computed, `results/exp02_divergence_gate/dataset_positions_on_gate.csv`):

| dataset | measured cosine | clears the ≲0.9 gate? | who actually wins |
|---|---:|:---:|---|
| cross-line (SciPlex3) | 0.032 | yes | **PopRetrieve** |
| **CD34+ lineages** | **0.186** | **yes** | **mean-cosine** |
| Frangieh immune | 0.709 | yes | mean-cosine (0.600 vs 0.578) |

The hand-entered 0.95 placed CD34+ *outside* the gate, which made our negative control look
like a **confirmation** of the criterion. The measured value on the same cells is 0.186:
strongly divergent, comfortably inside the gate. The gate therefore predicts PopRetrieve should win
on CD34+, and it does not. Two of three datasets clear the gate and still favour the mean.

**The divergence criterion is refuted by our own negative control.** This agrees with the
direct gate audit already in the paper (the gate's reliability axis is *anti*-correlated with
true divergence, rho = −0.21, p = 3.8e-9), so it strengthens a conclusion we had already
drawn, but by a route we had been getting backwards.

---

## R4. CORRECTED: the Class A / Class B contrast compared two different methods

**Was:** "The same method, on the same data, is far ahead or no better depending only on
which metric class judges it", citing Class A **+0.119** against Class B **−0.013**.

**Is:** those two numbers come from **different scorers on different query sets**. +0.119 is
`coverage_worst` on 621 queries; −0.013 is `energy` on 480. Each side had been selected as
the best of five for the metric class that flattered it, which is exactly the analytic degree
of freedom this paper exists to criticize.

**Corrected:** one scorer, one query set. On the 480 queries where both metric classes are
defined, `coverage_worst` gives Class A **+0.129** and Class B **−0.037**. The collapse is
*larger* under the disciplined comparison. All five variants behave the same way (Class A
+0.056 to +0.129; Class B −0.011 to −0.037). Fig 3a had been plotting the honest pair all
along; the prose was the outlier.

---

## R5. FALSIFIED PANEL: "No predictor gives a positive gain"

`figures/fig4/fig4b.py` reindexed on `'scgen_cpa_linear'` while
`results/exp09_predict_then_rank/summary.csv` keys that predictor as `'scgen'`. The reindex
produced NaN, the predictor was silently dropped, and it rendered as a blank row labelled
`+nan`. It is the **one predictor with a positive gain** (+0.027 nDCG@10, recorded in the
deck's own `source_data/fig4b_predictor_gaps.csv`).

The panel title is now "Gain is small and sign-inconsistent" and the three values are
reported: −0.071 (nearest-neighbour), −0.016 (average-effect), **+0.027** (latent-linear).
The panel raises rather than plotting NaN if a predictor goes missing again. Our own
`statistical_reporting_checklist.md:43` had warned "do not summarize as all negative".

---

## R6. CORRECTED: "leave-one-dataset-out cross-validation"

The held-out unit in `exp16` is a **cell line** (A549, K562, MCF7), and all three come from
**SciPlex3**. This is leave-one-cell-line-out within a single experiment, not
leave-one-dataset-out: the lines share batch, protocol, HVG set and normalization. The column
`cross_dataset_pos_fraction` is renamed `cross_cellline_pos_fraction`, and the
cross-dataset generalization claim is withdrawn.

---

## R7. CORRECTED: exp13's acceptance test was declared PASS on a degenerate label

On the shipped run the observed label was **constant** (`mean_sufficient` in 37 of 37 tasks),
so it carried zero information. A constant predictor scores 100%; the reported 70.3% is 30
points **worse** than saying nothing, and it was nonetheless declared **PASS** against a ≥0.6
threshold. The test now reports the majority-class baseline and refuses to issue a verdict on
a degenerate ground truth.

**That shipped run was a QUICK sanity run**, and the label is not constant on the full task
set. See R13, which supersedes the reading of this experiment. On the FULL set the test is no
longer degenerate, it is simply **failed**: the majority-class baseline is 95.4% and the
projection scores 61.1%. **Both numbers were reissued on 2026-09-03** under the unbiased
estimator and a boundary re-fitted on the full 4,480-cell grid: the baseline is 95.8% and the
projection scores 39.7%. The correction's finding is unchanged and larger.

The related "predicted_mean → `no_DART`: 100%" is a **tautology**: `predict_regime` returns
`no_DART` unconditionally for that information condition. It is now labelled as such and no
longer offered as evidence.

---

## R8. CORRECTED: the aggregate table disagreed with the per-query data

`exp12`'s `recommendation_vs_outcome.csv` reported a median regret reduction of 0.1133 where
`per_query_scores.csv` gives 0.1190, and **the figures were built from the aggregate**. Cause:
the paired lookup keyed on `(split_type, cell_line, heldout_drug, seed)`, which is not unique
because the partial-library queries exist at three `observed_library_fraction` values; the
subsequent `.iloc[0]` paired a PopRetrieve row at fraction 0.4 against a baseline row at fraction
0.2. The key now includes all six fields and raises on a non-unique index. Regenerated:
+0.1190 (recommended, n=621) versus +0.1219 (non-recommended, n=133), matching the text.

---

## R9. CORRECTED: the identifiability phase diagram said clustering gets harder with more cells

At fixed separation, the published phase diagram showed ARI **falling** with cell budget
(median 1.000 at 25 cells/source down to 0.289 at 400, at separation 2.0). Clustering does
not get harder as you collect more cells. Cause: the separation manipulation computed source
centroids on the **sampled** cells and then shifted **those same cells**, so at small n it
amplified whatever separation each draw happened to contain. The centroids are now computed
once on the full source populations, making the manipulation sample-independent.

---

## R10. CORRECTED: "9 unsupervised clustering methods"

The nine columns comprise **6-7 distinct algorithms**. `response_kmeans_k2` is bit-identical
to `raw_kmeans_k2` on all 20 seeds (k-means is translation-invariant, so subtracting a
constant control mean changes nothing), and `bestk3/4/5` are one best-k method under three
names. All are centroid- or Gaussian-based; no density (DBSCAN, HDBSCAN) or graph (Leiden,
Louvain) method was tested, which is the natural next objection and is now stated as open.
The headline "best median ARI 0.106" is a median over the **4 of 20 seeds** in which k=4 won;
the dense columns sit at 0.037-0.078 and the global maximum is 0.149.

---

## R11. RETRACTED: "failure is predictable from observable features (AUC 0.640)"

**Was:** on the FULL 13,440-cell HIR-Bench grid, a leave-one-grid-out logistic regression
predicts retrieval failure at AUC 0.640 from observable structure and conflict features.

**Is:** wrong on the features, wrong on the cross-validation, and wrong on the sample size.

- **The features were not observable.** All four (`topk_disagreement`,
  `weighted_kendall_conflict`, `standard_kendall_conflict`, `response_cosine`) are functions
  of `cell.utility_matrix`. So is the label, `oracle_flip_risk`. It was one function of the
  oracle predicting another function of the same oracle: **the exact circularity this project
  exists to audit, committed inside the project.** The module docstring asserted it "must NOT
  import oracle_utility"; it did not import it, but it received the oracle's quantities as
  columns, so the firewall was nominal. The genuinely observable features
  (`predictability.extract_features`) were implemented and **never called**.
- **The cross-validation leaked.** `grid_id` also encodes `information_condition`,
  `cells_per_subpop` and `noise_sigma`, none of which change the utility matrix. Holding out
  one `grid_id` therefore left roughly **twelve near-identical copies** of the held-out
  instance in the training set.
- **The sample size was inflated 480-fold.** The label is a deterministic step function of
  `(alpha, conflict_level)`. Grouping on those axes leaves **28 independent parameter cells**,
  not 13,440 instances. Any confidence interval computed on n = 13,440 is meaningless.

**Corrected** (`results/exp11_hir_benchmark/phase_grid_predictability.csv`, FULL grid,
leave-one-parameter-cell-out):

The full 2x2 (feature set x cross-validation grouping), which is what actually separates the
two failure modes. Majority-class rate is 0.643 throughout.

| feature set | 28 label-determining cells | 672 instances (leaky) | inflation |
|---|---:|---:|---:|
| **observable at query time** | **0.788** | 0.836 | +0.048 |
| oracle-derived (the old four) | **0.400** | 0.640 | **+0.240** |

**The attribution, stated precisely.** An earlier version of this file said "all of the
reported 0.640 was pseudo-replication". That is an over-simplification and it is now
corrected. Both mechanisms are real and the 2x2 separates them:

- **Feature circularity** costs 0.388 of AUC (0.400 vs 0.788 under honest grouping). The
  oracle-derived features carry no generalizing signal at all.
- **Pseudo-replication** inflates the oracle-derived features by **+0.240** but the honest
  features by only **+0.048**, a factor of five.

The interaction is the interesting part: **an instance-level holdout preferentially rescues a
circular feature set**, because memorizing near-duplicates is the only thing such a feature set
can do; features carrying real signal barely benefit. A benchmark whose cross-validation unit
is finer than its label-determining axes will manufacture apparent predictability exactly where
there is none.

**Also corrected: "worse than chance".** We wrote that AUC 0.400 is "worse than chance" in the
manuscript abstract, Results and a figure caption. With n_eff = 28 and no per-fold distribution,
a 0.1 deviation in AUC is **not distinguishable from 0.5**, and reading it as a directional
finding repeats, at n_eff = 28, exactly the error this correction is about. The defensible
statement is **"no better than chance"**. Likewise "the dominant feature is the query's response
diversity" is downgraded to "the highest-weighted feature": feature-importance ranking on 28
effective units was never tested for stability.

Two caveats travel with the 0.788 and must not be dropped: the effective sample size is 28
parameter cells, and because the label is deterministic within a cell, every held-out fold is
single-class, so no per-fold AUC distribution exists and the pooled out-of-fold AUC is the
only statistic available. "Moderately predictable" is as strong as this supports.

`exp11_hir_benchmark.py --skip-method-perf` makes the FULL grid runnable in-tree, and
`exp11_write_provenance.py` stamps which layer in `results/exp11_hir_benchmark/` came from
which grid, because the method-performance layer is still a QUICK 144-instance sanity pass and
a reader must not have to guess.

---

## R14. RETRACTED: "no Class C metric is available in this study"

**Was:** the manuscript stated, in the negative-claims box, in the Discussion, and in the
Methods metric taxonomy, that no oracle-independent (Class C) utility metric was available in
the datasets used, and that reaching Class C would require future wet-lab work.

**Is:** false. The repository has contained a Class C experiment the whole time:

- `results/upgrade/drug_match_table.csv`, 155 SciPlex3 drug x cell-line pairs matched to
  **GDSC dose-response** records (AUC, LN_IC50) in the same three cell lines.
- `analysis/class_c/class_c_experiment.py`, leave-one-drug-out retrieval scored against that
  potency oracle, 152 queries.
- `analysis/class_c/class_c_magnitude_control.py`, the control that decides it.

Dose-response viability is the **first metric named in our own Class C definition**. A paper
whose thesis is that the field avoids oracle-independent evaluation cannot claim no such
readout was available while shipping one in its own repository.

### R14a. The v1 Class C scripts had a sign error that INVERTED the result. Do not use their numbers.

`retrieval.metrics.score_energy` returns **minus** the energy distance, i.e. a **similarity**
(higher = more similar). Both v1 scripts ranked it **ascending**:

```python
# class_c_experiment.py:121,133
dart_ranks   = stats.rankdata(dart_scores)      # rank 1 = most NEGATIVE score
dart_top1_idx = np.argmin(dart_scores)          # "lowest energy = top pick"  <-- WRONG
# class_c_magnitude_control.py:91
er = stats.rankdata(e_scores)                   # "energy: low = similar"     <-- WRONG
```

The variable holds a negated distance, so `argmin` selects the candidate **farthest** from the
query. The mean-cosine baseline in the same scripts was ranked **correctly** (`argmax`). PopRetrieve
was therefore ranked backwards and its incumbent was not.

This is not cosmetic. Large-response candidates sit far from everything (rank corr between
energy **distance** and candidate magnitude = **+0.79**), and large response predicts potency.
Ranking "farthest first" therefore selects potent drugs. That, and nothing else, produced v1's
apparent **+0.52** PopRetrieve-versus-potency correlation. It is the true value with the sign flipped.

Two further faults in v1, both fixed: it pooled **all four doses** (10 nM to 10 uM) while every
other retrieval experiment in the paper runs at 10 uM, and it pooled **GDSC1 and GDSC2** AUCs,
which are different platforms and not on a common scale.

### R14b. The corrected result

`analysis/class_c/class_c_magnitude_control_v2.py`, 10 uM only, GDSC2 only, 34-35 drugs per
line, 103 leave-one-drug-out queries. Median Spearman rho with true potency:

| ranking of candidates | A549 | K562 | MCF7 | all |
|---|---:|---:|---:|---:|
| energy (distributional retrieval) | -0.538 | -0.625 | -0.486 | **-0.520** |
| mean cosine, control-subtracted (correct incumbent) | +0.049 | +0.438 | +0.091 | +0.105 |
| mean cosine, as commonly run (no control subtraction) | -0.573 | -0.647 | -0.482 | -0.533 |
| **candidate response magnitude alone** (*no retrieval*) | +0.692 | +0.708 | +0.583 | **+0.692** |

**Distributional retrieval is ANTI-correlated with potency (-0.520), with the same sign in all
three cell lines.** The candidates it ranks first, the ones most similar to the query, are the
**less potent** ones. A query-independent scalar that never looks at the query outranks it on
**103 of 103 queries**.

The mechanism is arithmetic: response magnitude predicts potency (rho = -0.69 / -0.71 / -0.58
by line), and energy **distance** tracks candidate magnitude (+0.79), so ranking nearest-first
returns the smallest-response, weakest drugs. Retrieval fidelity and therapeutic utility are
anti-aligned on this data.

**Do not restate this as a fraction.** An earlier internal note said the correlation was "83%
explained by response magnitude (rho = -0.83)". A Spearman rho is not a fraction of variance
explained; that is the error R12 already records.

**Do not quote a p-value across the 103 queries.** They share a candidate pool within a cell
line and the magnitude-only ranking is query-independent, so a paired test is anticonservative.
Report the per-line medians and the unanimity of the sign.

**Scope.** The oracle is *semi-real*: potency is a separate bulk assay, joined by compound name,
at a different dose regime. It is strong enough to **withdraw any claim of therapeutic utility**
and not strong enough to **prove that no distributional method could help**.

Code: `analysis/class_c/class_c_magnitude_control_v2.py` (v1 retained, marked superseded).
Data: `results/upgrade/class_c_magnitude_control_v2.{csv,json}`, `results/upgrade/drug_match_table.csv`.

---

## R12. Smaller corrections

- **README Hit@1 table** was labelled "controlled SciPlex3 benchmark". It is an unweighted
  **macro-mean over 7 (task × setting) cells of three tasks**. Query-weighted, the numbers are
  0.887 / 0.421 rather than 0.837 / 0.389. Both are now reported, and the Frangieh
  counterexample (mean-cosine 0.600 **beats** energy 0.578 on the only natural real dataset)
  is stated in the README, the manuscript, and the Fig 2 caption.
- **"energy CV at n=120 is 6.3%"** cited the wrong file. The probe reports **3.8%**; 6.3% is
  the CV of a different quantity (the same-drug self-distance) in a different CSV.
- **"83% of it is explained by response magnitude alone (rho = -0.83)"**: a Spearman rho is
  not a fraction of variance explained, and no such decomposition exists in the repository.
  The defensible statement is that a magnitude-only scalar scores +0.756 where energy scores
  +0.520, and the control-subtracted distributional signal is +0.088.
- **HIR-Bench "13,440 cells"** are benchmark **instances** (672 configurations × 20 seeds),
  not biological cells. Renamed throughout; in a single-cell paper the old wording misleads.
- **The project's acronym expansion** in README.md and CITATION.cff was still the
  pre-repositioning "Distribution-Aware Retrieval for Therapeutic Ranking", which advertised a
  drug-ranking method. It was corrected to the audit-flavoured "Distributional Auditing of
  Retrieval Transfer", and the acronym has since been dropped entirely (see R43 and
  manuscript/reference/naming.md).
- **"35/35 reproduce end-to-end"** is a **consistency re-check** of cached CSVs against
  hard-coded constants; `recompute_all.py` runs no experiment. Relabelled.

---

## Reproducibility repairs

- `figures/figstyle.py` now defines `apply_style(sizes=...)`, the entry point every
  `figN_assemble.py` calls. It previously existed only in an external authoring tool, so
  **none of the six main composites could be rebuilt from a checkout**.
- `figures/edfigs/ed_panels.py` was dead code: thirteen draw functions referencing fifteen
  module-level names that were never assigned, with no loader, no assemble step, no savefig
  and no `__main__`. **All four Extended Data figures now rebuild from committed code.**
- Figure panels that read a top-level `upgrade/` directory now read `results/upgrade/`, which
  is where the analysis scripts actually write. The duplicate directory is gone.
- `exp11_hir_benchmark.py --skip-method-perf` makes the FULL-grid predictability layer
  runnable in-tree. It previously required an out-of-tree "lean runner", which is why the
  artifact committed under `results/` was a 144-instance QUICK run reporting AUC 0.5 while
  the manuscript quoted 0.640.

## Housekeeping: the duplicate top-level `upgrade/` directory is gone

The repository used to carry a hand-curated top-level `upgrade/` alongside `results/upgrade/`,
which is where every script in `analysis/` actually writes. The two were out of sync, and the
duplication was a standing provenance hazard: some figure panels read one copy, the analysis
scripts wrote the other.

The top-level copy has been removed. `results/upgrade/` is now the single location, it holds
the full set of audit artifacts, and **every figure panel reads it**. Two files were not
carried over because they are superseded rather than lost: `conditional_advantage_per_query.csv`
and `conditional_advantage_summary.csv`. Figure 4g now reads
`results/exp17_true_divergence_subset/divergence_stratified.csv`, which is the same quantity
computed on the corrected, sentinel-masked data and is the source the verdict document quotes.

## Known remaining gap

The repository is **not under version control**. Until `git init` and a tagged commit, no
result in `results/` has provenance, the corrections above cannot be diffed against what they
replaced, and an accidental deletion like the one recorded above is unrecoverable rather than
a `git checkout` away. This is the single highest-value remaining fix.

---

## R13. RETRACTED: "0 of 37 real-data tasks are distributionally dominant"

**This one took three attempts to get right, and the two failed attempts are instructive
enough to record.**

**Was:** "No real-data task is distributionally dominant (**0 of 37**)." A headline negative
claim, in the abstract, the introduction, Result 3, the Methods, the Fig 3 caption, the
negative-claims box, and the whole of panel Fig 3g.

**Problem 1: 37 is the QUICK sanity task count.** Calling exp13's task builders directly:

| configuration | tasks | what it is |
|---|---:|---|
| QUICK | **37** | 1 cell line, 4 drugs, 1 cross-line pair, 2 seeds. A **sanity run**. |
| FULL | **239** | 3 cell lines, 10 drugs, 3 cross-line pairs, 3 seeds. |

The 37 in the paper and the 37 that QUICK builds are the same number. A sanity run had been
shipped in `results/` and quoted as the real-data result, and nothing on disk said so. This
is the third instance of that failure mode in this repository (see R11 for HIR-Bench, and
`results/exp11_hir_benchmark/PROVENANCE.md`). And the mechanism is worse than a mislabel:
QUICK never samples the A549→MCF7 cross-line pair at all, which is precisely where the only
robust effect lives. **"0 of 37" was not a measurement. It was a consequence of not looking.**

**Problem 2 (our first correction was also wrong).** We first replaced it with "11 of 215
observed-condition tasks (5.1%) are distributionally dominant". That is wrong twice over. The
like-for-like denominator is **239**, not 215: swapping to the observed-only subset quietly
improves the rate. And, more seriously, it reports a **count of threshold crossings as a
finding**, which is the same error the paper exists to criticize, merely in the opposite
direction.

**Why a dominance count cannot be reported on this data.**

- The **threshold is not calibrated**. The 0.01 margin sits at **0.77 standard deviations**
  of the nonzero-difference distribution (sd = 0.0130), i.e. **inside its noise band**. It is
  also **one-sided**: on the FULL run 11 tasks clear it for PopRetrieve and **2 clear it for the
  mean**, and only the first number would ever be reported.
- **The seed is not a replicate.** In exp13 it re-draws which drugs are held out
  (`rng.choice(common, n_drugs)`, exp13:234) and it **redefines the minority subpopulation**
  by re-clustering (`_query_states(qX, k=2, seed=seed)`, exp13:242). A task recorded as
  dominant at one seed carries no information about robustness.
- **The count is a count of noise excursions.** Holding the drug fixed and resampling the
  seed 10 times (harness validated first: it reproduces 30 of 30 recorded deltas to 0.00e+00):

| cross-line task recorded as dominant | recorded | mean ± sd over 10 seeds | dominant in |
|---|---:|---:|:---:|
| **A549→MCF7 Abexinostat** | +0.0867 | **+0.0896 ± 0.0130** | **10/10** |
| **A549→MCF7 Belinostat** | +0.0583 | **+0.0812 ± 0.0266** | **10/10** |
| K562→A549 Sirtinol | +0.0327 | +0.0124 ± 0.0139 | 5/10 |
| K562→A549 Costunolide | +0.0304 | +0.0111 ± 0.0110 | 5/10 |
| K562→A549 UNC0379 | +0.0260 | +0.0116 ± 0.0133 | 4/10 |
| K562→A549 SRT2104 | +0.0154 | +0.0094 ± 0.0130 | 3/10 |
| K562→A549 AG-490 | +0.0239 | +0.0077 ± 0.0105 | 3/10 |
| K562→A549 Alvespimycin | +0.0260 | +0.0088 ± 0.0115 | 3/10 |
| K562→A549 Droxinostat | +0.0344 | +0.0068 ± 0.0130 | 2/10 |
| K562→A549 IOX2 | +0.0339 | +0.0064 ± 0.0109 | 2/10 |

  And the control that settles it: drugs that are dominant at **no** recorded seed clear the
  same threshold in **1 to 4 of 10** resamples (median 3; Amisulpride 4/10, WP1066 4/10,
  GSK J1 3/10, Disulfiram 2/10, Abexinostat K562->MCF7 1/10). The threshold is inside the noise.

  **The control set itself had to be corrected.** It was originally selected by `task_id`,
  which carries a `:sN` seed suffix, so a drug that crossed the threshold at one seed and
  missed at another could land in **both** the dominant group and the control group. Sirtinol
  did exactly that. A control must be a drug that is above threshold at no seed, so the
  selection now deduplicates to `(pair, drug)` and subtracts the dominant set. This changed the
  reported control range from "2 to 4 of 10" to **1 to 4 of 10**. Comparing a dominant set
  against a control set that partly contains it is not a control.

**Is (what we now report): the distribution, not a count.** Across all 239 real-data tasks
the PopRetrieve-minus-mean minority-state coverage is **statistically real and practically
negligible**:

| | |
|---|---:|
| mean over 239 tasks | **+0.0018** |
| exactly zero (both families pick the same drug) | 102 / 239 |
| nonzero (n=137): mean, sd | +0.0032, 0.0130 |
| Wilcoxon, one-sided (H1: PopRetrieve > mean) | **p = 1.3e-07** |
| metric operating range | [0.60, 1.00] |

And it is **confined to the mixtures we constructed**:

| regime | n | mean coverage gain |
|---|---:|---:|
| **SciPlex3 cross-line (constructed)** | 90 | **+0.0043** |
| SciPlex3 within-line | 90 | +0.0004 |
| Frangieh (natural) | 23 | +0.0004 |
| CD34+ (natural) | 12 | +0.0003 |
| predicted candidates | 24 | +0.00003 |

**This converges with exp17.** The divergence audit independently reports a coverage gain
that is "statistically real but negligible", median **+0.0018**. exp13's distribution mean is
**+0.0018**. Two experiments sharing no code path land on the same number, and the retracted
"0 of 37" had been hiding it.

**What survives resampling: exactly two tasks, and they are a hypothesis.**
A549→MCF7 **Abexinostat** (+0.090 ± 0.013, 10/10 seeds) and **Belinostat** (+0.081 ± 0.027,
10/10), both **HDAC inhibitors**, both ~7 sd above the noise band. With n=2, one cell-line
pair and one drug class, this is suggestive and nothing more. A pre-registered test of HDAC
inhibitors against the rest of the panel would be needed before claiming mechanism
specificity. We record it because it is the only place in the study where distributional
retrieval buys something on real data that survives being checked.

**Side effect on R7.** With a non-constant label the acceptance test is no longer vacuous, it
is simply **failed**: majority-class baseline 95.4%, projection accuracy 61.1%, i.e. 34
points worse than a constant predictor. The HIR-Bench boundary does not transfer, and that
holds whatever one makes of the threshold.

**The thesis is untouched.** The natural datasets stay at zero, the predicted-candidate
conditions stay at zero, the projection still fails, and the real-data advantage is still
negligible. What changed is that an absolute ("zero") became a distribution, and the
distribution is both more honest and more informative.

---

## R15. The Class-C oracle was semantically mismatched to the retrieval task

**Severity: fatal to the conclusion drawn, not to the data.**

R14 fixed a sign error and established that energy retrieval correlates at rho = -0.520 with
**absolute GDSC potency**, and that a query-independent magnitude scalar reaches +0.692. We wrote
that up as "retrieval fidelity and therapeutic utility point in opposite directions".

**That conclusion does not follow, and the fault is in the oracle, not the method.** A similarity
retriever is asked which candidate *resembles* the query. Absolute potency asks which candidate
kills hardest. Handed a weak query, a correctly working retriever *should* return other weak
drugs, and this scoring counts that as failure. Worse, the comparison is not neutral: potency is
largely driven by response magnitude, and a scalar that sorts by magnitude is therefore
near-guaranteed to win. Both the negative correlation and the scalar's "103/103 sweep" were
close to preordained by the choice of oracle.

**The corrected oracle** (`analysis/class_c/class_c_functional_oracle.py`) is drug-drug
**functional similarity**: the rank correlation between two compounds' GDSC2 dose-response AUC
profiles across the 966 cell lines that remain once the three SciPlex3 lines are excluded, so it
is measured out of context. It is query-dependent (a query-independent scalar cannot game it) and
mean-centered per compound (a drug's overall potency *level* cannot drive it).

Cell lines differ enormously in general drug sensitivity, which inflates every drug-drug
correlation: uncorrected, 85% of drug pairs look positively similar (median +0.178). Each cell
line's mean AUC, estimated over all 286 GDSC2 compounds, is therefore subtracted first; the
corrected oracle is symmetric about zero (52% positive, median +0.015). **This correction was
specified on that reasoning before the retrieval results were inspected**, and both oracles are
reported: they change every scorer's absolute value but not the ordering that carries the
conclusion.

| ranking (103 queries) | median rho | performs retrieval? |
|---|---|---|
| potency match (needs the query's own AUC; diagnostic only) | **+0.399** | no |
| inverse-magnitude fixed ordering (query-independent) | +0.330 | no |
| **energy (distributional)** | **+0.276** | yes |
| mean cosine, no control subtraction | +0.241 | yes |
| **response-magnitude match (query-dependent scalar)** | **+0.232** | no |
| mean cosine, control-subtracted (correct incumbent) | **+0.083** | yes |

energy partialled on magnitude-match: **+0.097**. energy beats magnitude-match on **62/103**
queries (Wilcoxon p = 0.073, itself anticonservative).

**The result is layered, and it is stronger than either the buggy +0.52 or the corrected -0.52.**
Distributional retrieval *does* beat the correctly specified mean incumbent on an independent,
out-of-context functional oracle, by a factor of three. But almost all of that margin is a
**response-magnitude channel** that a scalar reproduces without comparing any distributions, and
the residual attributable to the distribution is about +0.10. Objective fidelity does not make the
gain imaginary; it makes it look an order of magnitude larger than it is.

The absolute-potency analysis is retained as a **confounder audit** (Extended Data Fig. 5). It
establishes the mechanism that makes the magnitude control mandatory: the energy *distance* tracks
the candidate's own magnitude at rho = +0.791.

---

## R16. Gate 2 was supported only by centroid clustering, with no upper bound

**Severity: the claim was unsupported; the corrected evidence happens to support it more strongly.**

The manuscript claimed "no unsupervised method recovers known bimodal structure" and that "real
subpopulations cannot reliably be told apart". The evidence was k-means and Gaussian mixtures
only. Two gaps made that claim unsupportable:

1. **No graph- or density-based method.** Leiden and HDBSCAN are the field's actual defaults and
   were never run. "Centroid clustering failed" is not "the structure is not there".
2. **No supervised upper bound.** Without one, clustering failure cannot distinguish
   (a) *the information is absent from the representation* from
   (b) *the information is present and unsupervised methods cannot reach it*.
   These have opposite implications, and asserting (a) from clustering failure alone is the same
   species of error this paper criticizes in others.

`analysis/identifiability/gate2_supervised_upper_bound.py` measures both. Every method is scored
in one unit, best-permutation accuracy, with the label matching given to each clusterer for free.

| method | accuracy (real separation) |
|---|---|
| k-means (true k given) | 0.632 |
| Gaussian mixture (true k given) | 0.661 |
| **Leiden (graph)** | **0.674** |
| HDBSCAN (density) | 0.500 (finds no density structure at all) |
| supervised logistic | 0.685 |
| supervised random forest | 0.669 |
| supervised kNN | 0.605 |
| **supervised ceiling (best of 3)** | **0.692** (AUC 0.752) |

**Gap between the ceiling and the best unsupervised method: +0.018.** Unsupervised clustering is
already extracting essentially everything the representation contains. A nonlinear learner does
not beat a linear one, so the boundary is not a hidden nonlinear one our probe was too weak to
find. **Gate 2 stands, but as an INFORMATION limit, not an algorithmic one**, which is a stronger
and more useful statement than the one we could previously support.

Two design points, both of which flip the answer if got wrong:
- **The unsupervised methods get the easier (transductive) PCA; the supervised probe re-fits PCA
  inside each training fold.** The comparison is deliberately biased *against* the conclusion drawn.
- **ARI and AUC are not comparable.** Reporting "probe AUC 0.75 vs GMM ARI 0.10" would have made
  the gap look enormous and produced the *opposite* (wrong) conclusion. The common unit is what
  makes the result readable. Our first run of this experiment made exactly that error.

**Positive control:** raise the separation artificially and the probe *does* pull away from
clustering (ceiling 0.828 vs 0.714 at 1.5x; 0.924 vs 0.762 at 2x). Its failure to pull away on
real data is therefore a measurement, not an insensitive probe.

**Consequence for the framework.** Gate 2 cannot be read as "a distributional score must cluster":
energy, MMD and sliced-Wasserstein are cluster-free and never form a partition. What it implies is
subtler and closes the loop with R15: if the subpopulation signal sits at an information ceiling
this low, it cannot be what dominates a distributional distance, so something else must, and we
have measured what: the candidate's own response magnitude (rho = +0.791). That is why the
distributional score behaves like a magnitude scalar on the functional oracle.

---

## R17. The "scGen/CPA" predictor is neither scGen nor CPA

**Severity: fatal to a field-level claim; the algebraic claim is untouched.**

`results/exp09_predict_then_rank/provenance.csv` records `scgen,cpa_linear`. The predictor labelled
"scGen" throughout is `_CPALinearLatent`: a PCA encoder, a per-perturbation additive latent delta,
and a linear decoder. **It is additive by construction.** The published scGen variational
autoencoder was never run (scvi-tools is not installed); CPA was never run.

The manuscript nevertheless stated that "current perturbation predictors are additive and
therefore cannot produce differential response", listing "average-effect, nearest-neighbour, scGen
and CPA". **We built an additive model, labelled it scGen, and then concluded that the field's
models are additive.** That is the self-fulfilling structure this paper indicts in others.

**What is withdrawn:** any claim about deployed perturbation predictors as a class.

**What survives, and it is what actually carries the argument:** the *algebra*. A predictor that
adds a single delta vector to every cell has, by definition, two subpopulations with identical
responses; their induced cosine is exactly 1 and the exploitable divergence is exactly zero. This
is a property of a model class, not of any implementation, and no amount of training removes it.
Additivity is therefore *sufficient* to shut Gate 1. The three predictors we implement all sit at
or near that ceiling, which demonstrates the algebra rather than surveying the field.

The manuscript now says so explicitly, names the untested falsification (a non-additive,
cell-state-conditional predictor: optimal transport, flow, Schrodinger bridge, or a perturbation
foundation model), and states that if such a predictor restored the distributional advantage, the
two-gate framework would be confirmed, and if it did not, the framework would be wrong.

---

## R18. Gate 2 was not an information limit. It was a limit of our own constructed benchmark.

**Severity: we asserted a property of biology from a property of a benchmark we built. Retracted.**

R16 concluded, from the HDAC-versus-JAK mixture in SciPlex3, that Gate 2 is an *information*
limit: the supervised ceiling was 0.692 accuracy and the best unsupervised method reached 0.674,
so clustering was already extracting essentially everything present, and we wrote that real
subpopulations sit at an information ceiling no method can exceed.

**That mixture is not biology. We constructed it.** Testing the same protocol on ZhaoSims2021,
acute-slice culture and biopsy from 10 glioblastoma patients, where malignant glioma cells,
tumour-associated myeloid cells and oligodendrocytes co-exist inside a single patient's tumour
and nobody mixed anything:

| | constructed mixture (HDAC vs JAK) | **natural tumour (malignant vs myeloid)** |
|---|---|---|
| supervised ceiling | 0.692 | **0.964** |
| best unsupervised (Leiden) | 0.674 | **0.949** |
| ceiling minus unsupervised | +0.018 | +0.015 |

**In a real patient tumour the subpopulation structure is highly separable and off-the-shelf
clustering finds it.** The "information limit" was a property of the benchmark, not of biology.
The reviewer who predicted exactly this was right, and the claim is withdrawn.

What survives, and is now stated with the correct scope: the *gap* between the supervised ceiling
and unsupervised clustering is small in BOTH regimes (+0.018 and +0.015). The unsupervised
assignment step is not the bottleneck anywhere. What differs enormously between the constructed
and the natural setting is how much structure there is to assign.

## R19. The constructed benchmark also OVERSTATED differential response, by an order of magnitude

The same comparison cuts the other way on Gate 1, and we did not see this coming either.

| | induced response cosine, cos(d_maj, d_min) |
|---|---|
| constructed SciPlex3 mixtures (A549+K562 etc.) | **0.014 to 0.044** (near-orthogonal) |
| natural tumour (malignant vs myeloid, 17 patient-drug pairs) | **median 0.566** (range 0.08 to 0.76) |

Mixing two unrelated cell lines makes one drug push them in nearly orthogonal directions. Inside
one patient's tumour, malignant cells and tumour-associated macrophages share most of their
response direction. **Our constructed benchmark therefore inflated the divergence a distributional
score has to exploit by roughly an order of magnitude**, at the same time as it deflated the
identifiability. Both distortions flatter the premise of the paper, and both are now reported.

## R20. The two-gate criterion is necessary but NOT sufficient, and the motivating premise is only weakly supported

Both gates are OPEN on natural tumour data: the compartments are identifiable (0.964) and they do
respond in different directions (cos 0.566 < 1). The two-gate account therefore predicts that
distributional information should be usable there. **It is barely usable.**

The paper's motivating scenario, Fig. 1a, is that two drugs can share a mean signature and do
opposite things to a subpopulation. Tested for the first time on a real tumour (18 within-patient
drug pairs), mean-signature similarity predicts malignant-compartment response similarity at

    Spearman rho = +0.878   (p = 1.6e-6)

**The mean is largely, though not entirely, sufficient in real tumour tissue.** Of the 5 drug
pairs most similar on the mean, 2 have a malignant-compartment response meaningfully less similar
than their mean suggests. The residual is real and it is small.

An earlier version of the analysis script declared "PREMISE HOLDS" on a threshold of rho < 0.9,
which the observed 0.878 cleared by 0.02. **That threshold was ours, it was applied after seeing
the number, and clearing it by 0.02 licenses nothing.** Moving a threshold after seeing the result
is precisely the analytic freedom this paper exists to criticize. The pass/fail verdict has been
deleted from the script; the correlation is reported and interpreted in the text.

**Consequence for the framework.** Opening both gates does not deliver a distributional advantage,
because even when subpopulations are identifiable and do respond differently, that differential
response is largely collinear with the mean. The two gates are necessary conditions, not
sufficient ones, and the paper now says so.

**This converges with the Class-C result (R15) rather than contradicting it.** There, energy
retrieval beat the mean incumbent on an independent functional oracle (+0.276 vs +0.083) but a
scalar magnitude control reproduced nearly the whole margin, leaving a distributional residual of
+0.097. Here, in real tissue, the mean explains rho = 0.88 of the compartment-specific structure.
Both say the same thing: **the distributional signal is real, positive, and about an order of
magnitude smaller than objective-aligned evaluation makes it look.**

---

## R21. The natural Gate-2 test measured the wrong partition, so the withdrawal in R18 was made on bad evidence (and the claim is still withdrawn, for a different reason)

**What was wrong.** `analysis/natural/zhao_two_gates.py::gate2_natural` separated **malignant from
myeloid CONTROL cells** (`control=True`). That is a **cell-type** identification task: a glioma cell
against a macrophage, two lineages differing in thousands of genes. The constructed benchmark
separates **HDAC-treated from JAK-treated K562 cells**: a **drug-response** task, one lineage, cells
differing only in which drug they saw. The script's own docstring claimed "Identical protocol ...
directly comparable to the 0.692 ceiling". It is not. Gate 2 is *defined* on the partition a
retrieval score must resolve inside a candidate population, which is a drug-response partition.
Separating two lineages says nothing about it. **The 0.964 is withdrawn.**

**What the correct experiment says** (`analysis/natural/gate2_drug_response.py`, one drug against
one drug in both settings, matched representation, median paired gap):

| arm | best unsupervised | supervised ceiling | gap |
|---|---|---|---|
| constructed, drug CLASS pooled (what the paper reported) | 0.687 | 0.700 | +0.013 |
| constructed, one drug vs one drug (like-for-like) | 0.837 | 0.879 | +0.007 |
| **natural tumour, one drug vs one drug (within compartment)** | **0.777** | **0.923** | **+0.117** |

Two corrections, and the second reverses us again:

1. **The 0.692 "information limit" was substantially an artefact of POOLING drugs within a class.**
   Split the same K562 cells one drug against one drug and the ceiling is 0.879. What we read as an
   information limit was the within-class heterogeneity of several compounds we had merged.
2. **In real tissue the information IS present and unsupervised clustering CANNOT reach it.**
   Ceiling 0.923, best unsupervised 0.777, gap +0.117 against +0.007 constructed. Centroid methods
   collapse (k-means 0.638) where the graph method partly survives (Leiden 0.780): the signature of
   a dominant variance direction that is not the drug-response axis.

**So Gate 2 in real tissue is an ALGORITHMIC bottleneck, not an informational one.** This
contradicts the original claim (R18's target) *and* the reading that replaced it ("real
subpopulations are simply easy to resolve"). It is the one constructive finding in the study: the
partition is there, off-the-shelf clustering misses it, and a better method could close the gap.

**Bounds.** 30 of the 36 splits come from one patient (PW030); 39.9% of cells are dropped by the
compartment-assignment margin, and the discarded cells are by construction the hardest to place, so
both numbers are optimistic; the drug panels differ between arms.

## R22. The Gate-2 bias direction was stated backwards, in the code, the Methods and the figure

We wrote that giving the clusterers the easier transductive PCA while re-fitting the probe's PCA
in-fold "biases the comparison AGAINST the conclusion we draw". **It biases it FOR.** The conclusion
is that the *gap* is small; inflating the unsupervised arm and deflating the supervised arm makes
the gap *smaller*. The +0.018 was therefore an underestimate presented as a conservative bound. The
ceiling is now also reported under the **matched** representation (the same transductive PCA the
clusterers get, which leaks no labels because PCA never sees them), and that is the number used.

## R23. "Both oracles give the same verdict" was false: the Class-C result depends on the centering

| ranking rule | corrected oracle | uncorrected oracle |
|---|---|---|
| energy (distributional) | **+0.276** | +0.097 |
| mean cosine, control-subtracted (the incumbent) | +0.083 | **+0.138** |
| magnitude scalar | +0.232 | **+0.217** |

Under the uncorrected oracle energy does not merely lose to the scalar; **it loses to the mean
incumbent**, reversing the single affirmative Class-C finding. The paper claimed the two oracles
"give the same verdict" and quoted only energy and the scalar at the point of use, omitting the
incumbent, which is the comparison the headline rests on. Full table now in Supplementary Table 4.
The centering is defensible and was specified in advance, but the affirmative result is conditional
on it. **Only the negative survives both constructions:** under neither oracle does the
distributional score significantly beat a scalar that compares no distributions.

## R24. The premise result is close to a single-patient measurement

rho = +0.878 over "18 within-patient drug pairs" has **15 of those 18 pairs from one patient**
(PW030, the only one given more than two compounds), reusing the same six drugs; the other three
patients contribute one pair each. `p = 1.6e-6` treated them as 18 independent observations. **This
is the pseudo-replication the paper devotes a section to criticising.** The p-value is deleted from
the text and from the figure; the correlation is reported with its dependency structure stated.

## R25. "An order of magnitude" was not supported by any pair of comparable numbers

The divergence overstatement was computed as a **ratio of cosines** (0.566 / 0.014 = 40x), which is
meaningless when one cosine is near zero. On any sensible divergence scale it is 1.2x to 2.3x
(1-cos: 0.99 vs 0.43 = 2.3x; angle: 89.2 deg vs 55.5 deg = 1.6x). Separately, the Class-A gain (a
Hit@1 or regret improvement) and the Class-C residual (a Spearman rho) are different quantities on
different scales and were being divided by one another. Both claims are restated with the actual
ratio and its units, or dropped.

## R26. The oracle's SHAPE picks the winner (new result, not a correction)

Same 218,331 cells, same 20 surface proteins, same two RNA rankings. The protein oracle is built
twice, changing **only** its statistical form:

| RNA ranking | oracle = MEAN protein | oracle = protein DISTRIBUTION |
|---|---|---|
| energy (distributional) | +0.146 | **+0.529** |
| mean cosine (incumbent) | **+0.242** | +0.334 |
| magnitude scalar (control) | +0.125 | +0.352 |

**The winner swaps, independently in each of the three immune conditions.** No scorer sees protein
data, so this is not Class-A circularity (a method grading its own objective). It is objective
alignment operating **between two external, independent, blind criteria**: the judge's own
statistical form selects the victor. This explains why the GDSC oracle favoured energy and the
protein oracle favoured the mean; they were not in conflict, they were differently shaped.

**The magnitude control survives it.** Both distributional objects are energy distances, and an
energy distance tracks response magnitude (rho = +0.791), so a magnitude-to-magnitude channel could
have produced the swap with no distribution compared. It does not, quite: the scalar climbs from
+0.125 to +0.352 as the oracle turns distributional (the confound behaving exactly as predicted),
but energy still leads it by +0.177 there against +0.022 under the mean-shaped oracle. A genuine
distributional signal exists in these cells, and **it is visible only to a criterion that is itself
distributional.**

## R27. Data provenance: what we could verify and what we could not

**Verified.** scPerturb Zenodo record 13350497 (DOI 10.5281/zenodo.13350497, release 1.4) is real
and contains all four h5ad files we use; `ZhaoSims2021.h5ad` on disk is 586,888,140 bytes, matching
the Zenodo listing exactly. SciPlex3 was obtained through **scPerturb, not GEO**: the manuscript's
`\TODO{GSE accession}` was asking us to fill in a path the code never took. The underlying primary
accession GSE139944 (Srivatsan/Trapnell, sci-Plex) is confirmed and is now cited as the primary
source, with the scPerturb file named as the artefact actually analysed.

**Not verified, and stated as such in Data Availability.** The GDSC2 workbook was saved without its
release suffix and has not been retained on either machine, so **we cannot certify which GDSC
release the Class-C numbers were computed from, and we do not assert one.** The derived join table
(`results/upgrade/drug_match_table.csv`, with DRUG_ID / cell line / AUC) is released, which is
enough to identify the release by comparison against any candidate download; the loader now raises
with instructions to do exactly that. Re-deriving the Class-C result from a named, current GDSC2
release is a correction owed before publication.

## R28. The Gate-1 measurement was cross-context, so it never tested the additivity theorem

**What the theorem says.** A predictor that adds a single delta vector to every cell **of the query
context** gives its two subpopulations identical response deltas, so `cos(d_0, d_1) = 1` exactly.

**What we measured.** `analysis/predictors/exp_nonadditive_gate1.py` measured that cosine on an
**alpha-blended candidate population whose two subpopulations are two different cell lines**
(A549 + K562). An additive predictor emits a **different delta per context**, so the quantity
measured was `cos(delta_A549, delta_K562)`: the similarity of two contexts' deltas. It has no reason
to equal 1 and **is not a test of additivity at all.**

**How it was caught.** The script asserts that its additive-by-construction controls must return
1.000, because the algebra fixes that value. They returned **0.267 and 0.353**, and the script
printed *"SELF-CHECK FAILED: the measurement is wrong, not the model"* and refused to report. The
guard did its job. **This is the practice worth generalising: when theory pins a control to an exact
value, assert it, do not merely print it.**

**Consequence for the manuscript.** The published explanation of the measured 0.19-0.37 values, that
they fall short of 1 because a scorer must estimate the partition and does so imperfectly (Gate-2
assignment error), **is wrong**. The real cause is the cross-context structure. That paragraph is
rewritten.

**The corrected experiment** (`analysis/predictors/gate1_within_context.py`): both subpopulations are
drawn from **one** cell line's own control cells (PCA + k-means on cell state), and the predictor is
run **separately on each subpopulation's control cells**, so the partition is true by construction
and no assignment step enters. Population synthesis draws a permutation, which preserves a mean
exactly, so an additive predictor gives `d_0 = d_1 = delta` and `cos = 1.000` to floating point. The
self-check is now exact and is asserted.

**Still outstanding.** In the last full run CPA did not fit and the OT map was scored VOID by the
`learned_check` (cos(predicted mean delta, true mean delta) = 0.183). **No Gate-1 number from that
run is reportable**, and the question the framework names as its own falsification test, whether a
genuinely non-additive predictor opens Gate 1, remains open.

## R29. Two sample sizes were reported in the wrong unit, one of them inflating n by 43x

- **"54,180 real queries"** (metric-correlation matrix, ED Fig. 1c). The retrieval experiments run
  **1,260 queries**, each against a 43-candidate library: 1,260 x 43 = 54,180. The unit is the
  **query-candidate scored pair**, not the query. Calling them queries overstates the independent
  sample size by a factor of 43.
- **"529 real drugs"** (silhouette analysis). The study's SciPlex3 panel is **188 drugs**. 529 is the
  number of **(cell line, drug) pairs** with enough cells to cluster. The unit is the pair.

Both are now stated in their correct unit. Neither changes a conclusion, but a reader recomputing a
confidence interval from either number would have been badly misled.

## R30. An additive latent model induces zero TRUE divergence and large APPARENT divergence, and the difference is its reconstruction error

**Setup.** With the Gate-1 construct fixed to be within-context (R28), the calibration check finally
runs. `average_effect`, which adds a delta in gene space, returns **cos = 1.000000000 exactly**, so
the instrument is now provably correct. `linear_latent` does **not**: it returns 0.61, -0.03, -0.13.

**The paper claims linear_latent is "additive by construction". Under one baseline that is true and
under the other it is false, and both baselines are defensible.** A latent model does not add a
delta to a cell. It *reconstructs* the cell and adds a delta to the reconstruction:

    predicted(C) = P(C) + W.dz          P = the autoencoder's reconstruction

so the response of subpopulation k depends on what it is referred to:

| baseline | d_k | cos(d_0, d_1) |
|---|---|---|
| the model's OWN decoded control, P(C_k) | `W.dz` | **1.000000, EXACT (all 9 tested)** |
| the REAL control cells, C_k | `[mean(P(C_k)) - mean(C_k)] + W.dz` | 0.61, -0.03, -0.13, ... |

The bracket is the **PCA reconstruction bias of subpopulation k**. It is cell-state dependent, so it
differs between subpopulations and does not cancel. The two subpopulations' reconstruction biases
are themselves near-orthogonal (cos = -0.05 to -0.18 by context), and they swamp `W.dz`.

**Consequences.**

1. **The theorem is intact.** An additive latent model induces *exactly zero* true response
   divergence. Verified to floating point.
2. **But a retrieval scorer forms its response against real control cells**, so it sees the second
   row, and measures substantial apparent divergence. **None of that divergence is drug response.**
   It is the generator's reconstruction error. A distributional score run on such a candidate
   population is confidently scoring an autoencoder's artefacts.
3. **This condemns a class of diagnostics, including ours.** Any structure-preservation or
   divergence measurement evaluated on a latent generative model's output *against real controls*
   is at risk of measuring the autoencoder rather than the perturbation. The
   subpopulation-variance-ratio and induced-cosine diagnostics reported in this paper are computed
   that way and inherit the risk.
4. **The docstring in `src/baselines/scgen_predictor.py` asserting that this model "induces no
   response divergence between subpopulations" was false as written** (it is true only against the
   model's own baseline) and has been corrected in place.

`analysis/predictors/gate1_within_context.py` now reports **both** baselines side by side, declares
per predictor which kind it has (`BASELINE_KIND`: a reconstructing model has its own baseline, a
non-reconstructing one such as `average_effect` or the OT map does not), and asserts the 1.000000
value on the correct column.

**This is the paper's own thesis reached a third way: what you measure against decides what you
find.** First the metric class (Class A vs B vs C), then the oracle's shape (mean vs distribution),
now the baseline (real controls vs the model's own reconstruction).

## R31. The +0.117 gap now has an uncertainty estimate, and it survives three attacks

The claim that Gate 2 in real tissue is an *algorithmic* bottleneck (R21) rests entirely on the gap
between the supervised ceiling (0.923) and the best unsupervised method (0.777). It was reported as
a bare median with **no uncertainty of any kind**, and it had entered the abstract, the introduction,
Fig. 5d and the discussion in that state. Three things were wrong with it and all three were tested
(`analysis/natural/gate2_uncertainty.py`).

**1. The winner's curse.** The gap is `max(3 supervised probes) - max(4 unsupervised clusterers)`.
Both terms are maxima, both are upward-biased, and the biases do not cancel. Recomputing every
**fixed (probe, clusterer) pair**, with no selection anywhere:

|  | reported (both maximised) | no selection (9 fixed pairs) |
|---|---|---|
| natural tumour | +0.117 | **+0.122** |
| constructed, like-for-like | +0.007 | **-0.002** |

The maximisation moves the natural number by **-0.005**. The conclusion is unchanged. (Pairs
involving HDBSCAN are excluded from that summary and reported separately: it assigns every cell to
noise and scores exactly 0.500, so a large "gap" against it means the clusterer did nothing, not
that the information is unreachable. Including it would have inflated the fixed-pair median to
+0.193 for a trivial reason.)

**2. No confidence interval, and the obvious bootstrap would have been wrong.** 30 of the 36 natural
splits come from one patient (PW030) and reuse the same six drugs. **A split-level bootstrap would
treat them as 36 independent observations and return an interval several times too narrow** -- the
same pseudo-replication this paper devotes a section to criticising. The bootstrap is therefore a
**cluster bootstrap over patients**:

- natural gap **+0.117, 95% CI [+0.115, +0.135]**
- constructed gap +0.007, 95% CI [-0.008, +0.065]
- natural minus constructed **+0.109, 95% CI [+0.052, +0.129]**, 0 of 5,000 draws at or below zero

**Caveat stated in the paper:** a cluster bootstrap with only **four** clusters is known to
under-cover. The interval is reported as a floor on the uncertainty, not a faithful estimate.

**3. Drop the dominant patient.** Removing PW030 leaves 6 splits in 3 patients, and the gap there is
**+0.123 [+0.098, +0.138]**, and the fixed-pair gap +0.200. Slightly **larger**, not smaller.

**Verdict: the claim holds, and the reported number is conservative on every axis tested.** This is
the first time in this project that a robustness check has confirmed rather than overturned one of
our own numbers, and it is worth recording that it was run with the same intent as the ones that
overturned things.

## R32. The within-context Gate 1 finally runs. One deployed model is measured; the falsification test is NOT

The corrected within-context measurement (R28) passes its calibration check: **both additive
predictors return cos = 1.000000 exactly against their own baseline**, as the algebra requires. The
instrument is sound, so its numbers mean what they say.

Every predictor is first required to pass a **learning check**: cos(predicted mean delta, TRUE mean
delta). A model that has not learned the drug effect cannot be said to open or shut any gate, and
its "divergence" is noise structure. This is enforced, not assumed.

| predictor | learning check | TRUE induced divergence (vs its own baseline) | fraction of real divergence reproduced |
|---|---|---|---|
| **REAL treated cells** | -- | **+0.205** | (the target) |
| average_effect (gene-space additive) | 0.502 PASS | **1.000000** | 0% |
| linear_latent (additive latent) | 0.343 PASS | **1.000000** | 0% |
| **scgen_real (PUBLISHED scGen VAE)** | 0.420 PASS | **0.972** | **~3%** |
| ot_map (entropic OT, non-additive) | **0.057 VOID** | (0.767) | **NOT REPORTABLE** |
| cpa_real (published CPA) | did not converge | -- | -- |

**What this earns.** The paper previously refused to say anything about deployed models. It can now
say one thing: **the published scGen VAE is near-additive in practice** (0.972 against the additive
ceiling of 1.000, where real cells sit at 0.205). Its nonlinear decoder buys a small departure from
strict additivity and reproduces roughly 3% of the divergence real subpopulations show. Gate 1 is
essentially shut for it. That is a fact about scGen, not about the field.

**What it does NOT earn, and this is the important part.** The optimal-transport map, the one
genuinely non-additive predictor, **failed its learning check**: cos = 0.057 +- 0.119 between its
predicted and the true mean delta, against **0.502 for a plain average-effect predictor on the
identical transfer task**. The task is therefore learnable and **our OT implementation is what
failed**. Its measured divergence of 0.767 is noise structure. **It is discarded, not reported**,
even though reporting it would have produced the headline "a non-additive predictor opens Gate 1",
which is exactly the result we wanted.

**Consequence: the central prediction of the two-gate account -- that opening Gate 1 restores a
distributional advantage -- remains UNTESTED.** The paper names this as the experiment that would
falsify it, and now also records that we did not manage to run it. Fixing the OT map (or running a
flow / Schrodinger-bridge predictor) is the highest-value experiment left.

## R33. The OT map is fixed (latent space), and it DOES open Gate 1, a crack. Part B still untested

R32 recorded that the OT map failed its learning check (cos 0.057) and so could not test whether a
non-additive predictor opens Gate 1. That failure was diagnosed and fixed.

**Two bugs, both the same class the paper is about.** (1) *Curse of dimensionality:* in 2000 gene
dimensions all pairwise costs are near-equal after normalization, so the Sinkhorn plan is nearly
uniform and carries no signal. Every deployed neural-OT perturbation model (CellOT and kin) runs OT
in a latent space for exactly this reason; we use a PCA-30 latent. (2) *Cross-context confound* (the
same error as R28): pooling control and treated cells across non-query contexts in raw space makes
the transport learn the context shift, not the drug response. Each fit context is now centred on its
own control mean before pooling.

**The configuration (PCA-30, reg 0.05) was chosen by the LEARNING check, not by the divergence it is
used to measure.** With the fix, learning check rises 0.057 -> **0.352** (bar 0.30), so the map now
learns the drug effect and its divergence is interpretable.

| predictor | learned | TRUE induced divergence | interpretation |
|---|---|---|---|
| REAL cells | -- | **0.205** | the biological target |
| additive (average-effect, linear-latent) | pass | **1.000000** | Gate 1 shut, exactly |
| scgen VAE (published) | 0.42 | 0.972 | Gate 1 essentially shut |
| **OT map (latent, non-additive)** | **0.352** | **0.903 +- 0.101** | **Gate 1 opens, a crack** |

**Result:** a genuinely non-additive predictor DOES give different subpopulations different responses
(0.903 is ~5 SE below the additive ceiling of 1.000 over n=30). But it closes only about an eighth of
the distance from the ceiling (1.000) to real divergence (0.205), and its learning is weak, so part
even of that crack is prediction noise.

**Still untested: Part B.** Whether opening Gate 1 this far buys any *retrieval* gain is the central
prediction of the two-gate account, and it requires re-running predict-then-rank with this map. Not
done. The manuscript now states this as the single highest-value experiment left and names it as the
falsification test.

## R34 (update). Part B was run. It is inconclusive, for an instructive reason

R33 left Part B (does opening Gate 1 buy retrieval gain?) untested. It has now been run
(`analysis/predictors/part_b_ot_retrieval.py`, cross-line predict-then-rank, additive baseline vs
the fixed OT map, n=8 seeds, 720 queries).

**Result: inconclusive, because the OT map is too weak a predictor in this setting.**

| candidate source | Hit@1 mean-cosine | Hit@1 energy | Hit@1 coverage |
|---|---|---|---|
| average_effect (additive) | 0.879 | 0.899 | 0.886 |
| **ot_map (Gate-1-opening)** | **0.053** | **0.007** | **0.008** |

On OT candidates **every retrieval rule collapses to near chance, mean-cosine included** -- not just
PopRetrieve. So the PopRetrieve-minus-mean contrast on OT candidates (all negative) measures nothing about Gate 1;
it measures that the predictor is unusable. The cross-line task is leave-two-contexts-out, harder
than the within-context divergence measurement, and the same weak learning that lets the OT map only
crack Gate 1 open (learning check 0.35) leaves it near chance as a predictor here.

**The honest conclusion: we lack a predictor that BOTH predicts accurately AND opens Gate 1.** The
additive predictors predict well (Hit@1 ~0.88) but cannot open Gate 1 by construction; the OT map
opens Gate 1 but predicts near chance. A clean Part-B test needs one predictor with both properties,
most plausibly a well-trained flow or Schrodinger-bridge model. This is consistent with the paper's
thesis (the accurate part of a predictor is its mean; the non-additive part is noise) but is a
**limitation, not a positive falsification**, and the manuscript presents it as such.

**Leakage guard added along the way:** exp09 passed `exclude_context` only to the nearest-neighbour
predictor, gated on `loco`. The OT map transports toward the query drug's treated cells, so without
excluding the query's own contexts it transports toward the answer. The guard is now mandatory for
the OT map and excludes both contexts of a cross-line query.

## R27 (resolved). GDSC release recovered and verified: release 8.5

R27 recorded that we could not certify which GDSC release the Class-C numbers came from. It is now
recovered. The server reaches the Sanger mirror; downloading GDSC2 release 8.5
(`GDSC2_fitted_dose_response_27Oct23.xlsx`, 21.3 MB) and checking it against the retained
`drug_match_table.csv` gives an exact match: JQ1 (DRUG_ID 2172) AUC 0.734237 / 0.892312 / 0.679716
in A549 / K-562 / MCF7, plus A-366 and ABT-737, all **6/6 at 1e-5**. The full Class-C oracle was
re-run from this file and reproduces the setup exactly (966 lines after holding out the 3 SciPlex
lines, 286 drugs, 591 usable pairs, median 909 shared lines, centered oracle median +0.015). The
Data Availability statement now names release 8.5 instead of admitting the gap, and the loader error
message names it too.

## R21 (robustness added). The natural Gate-2/Gate-1 numbers survive the assignment thresholds

M21 flagged that 0.923/0.777/0.566 rest on two hand-picked 0.25 constants plus a 39.9% cell drop,
where the dropped cells are the hardest to classify. Sweep (analysis/natural/zhao_threshold_sensitivity.py),
floor=margin in {0.10, 0.25, 0.40, 0.50}, all passing validation:

| floor=margin | dropped | Gate2 ceiling | unsup | gap | Gate1 cos |
|---|---|---|---|---|---|
| 0.10 | 28.8% | 0.923 | 0.773 | 0.125 | 0.594 |
| 0.25 (paper) | 39.9% | 0.923 | 0.780 | 0.122 | 0.566 |
| 0.40 | 51.6% | 0.915 | 0.780 | 0.108 | 0.562 |
| 0.50 | 58.2% | 0.923 | 0.797 | 0.120 | 0.538 |

Ceiling flat at ~0.92, unsup ~0.78, gap ~0.12, Gate-1 cosine drifts mildly 0.59->0.54. **The
threshold choice does not drive the result**, and 0.25 is mid-range, not cherry-picked. (The premise
rho re-derived inline here is ~0.80 and likewise stable across thresholds; the production value 0.878
uses a slightly different pairing, and stability is what the sweep tests.)

## R27 (further confirmed). Class-C reproduces exactly from the recovered release 8.5

Re-running the functional oracle from GDSC2 release 8.5 gives energy +0.2761, mean-cosine-ctrl
+0.0826, magnitude-match +0.2318, energy-partial +0.0969, energy>magmatch 62/103 (p=7.3e-2), and the
per-line values, all matching the manuscript to the reported precision. The Class-C result is fully
reproducible from a named, verified release.

## R32 (update 2). CPA runs but does not learn per-drug effects; both non-additive predictors fail as Part-B instruments

The CPA prediction path is fixed (two bugs: the query AnnData was never registered against the
trained model's vocabulary, so predict raised `KeyError('perts not found')`; and its zero-effect
baseline used the `_NULL_DRUG` sentinel, which is absent from CPA's registry -- CPA's real baseline
is predicting the "control" perturbation). With both fixed, CPA runs, and the honest result is:

| predictor | learning check | reconstruction | true induced divergence | verdict |
|---|---|---|---|---|
| ot_map (latent) | 0.352 | -- | 0.900 | opens Gate 1, but too weak to retrieve (Part B) |
| **cpa_real (published, 60 cells/group, 20 ep)** | **0.076** | R2 0.39 | 1.000 | **VOID** |

CPA trains all 20 epochs and reconstructs cells acceptably (r2_mean 0.39, stable from epoch 5), but
`acc_pert` stays ~0.007 throughout: with 189 drugs at ~60 cells each, its per-drug perturbation
embeddings never learn the drug-specific effect. So CPA reconstructs *cells* but not *responses*,
and its delta learning check is 0.076 (below 0.30) -- VOID, divergence not reportable. The lever is
cells-per-drug, not epochs, so a 300-cell/group run is under way to see whether more per-drug signal
lets CPA learn.

**300-cell confirmation.** Raising CPA's per-drug data 5x (60 -> 300 cells/group; fit time scaled
5.3x, 387s -> 2038s, confirming the data actually grew) leaves the learning check at 0.076,
UNCHANGED. acc_pert rose only 0.007 -> 0.009 (chance ~0.005). So the failure is not merely data
volume: with 189 drugs the adversarial objective holds per-drug signal near chance, and more cells
do not rescue it.

**Net: neither non-additive predictor we could run serves as a clean Part-B instrument.** The OT map
learns and opens Gate 1 but is too weak to retrieve with; CPA reconstructs cells (r2 0.39) but not
responses (learning 0.076 at both 60 and 300 cells/group). The clean falsification (a predictor that
both predicts accurately and opens Gate 1) remains out of reach with the predictors and compute
available, and the manuscript states this as a limitation. This is the honest endpoint of a genuine
attempt: two real predictor bugs were fixed (OT latent-space + context-centering; CPA prediction
registration + baseline), and both predictors were run to a conclusive, well-diagnosed negative.

## R40 (extension). A modern flow-matching model (CellFlow + ECFP4) tried as the Part-B predictor: same wall, now with a mechanism

The Discussion named "a well-trained flow or Schroedinger-bridge model" as the highest-value test
that would falsify the framework. We trained exactly that: CellFlow (Klein et al. 2025, bioRxiv
10.1101/2025.04.11.648220; theislab/cellflow), an optimal-transport flow-matching predictor, in the
SciPlex3 HVG gene space, conditioned on 2048-bit Morgan/ECFP4 fingerprints built from a verified
drug->SMILES map (188/188 drugs, sourced verbatim from trapnell_drugs_smiles.csv; 5 truncated names
resolved by mechanism cross-check against the sci-Plex target/pathway; ECFP4 independently
RDKit-recomputed bit-for-bit).

Result. Trained on all three cell lines CellFlow learns (mean-delta cosine 0.244 over 20 drugs at
40k iters, up to 0.81 for AR-42, 0.67 for JQ1; the 20-drug average is below the 0.30 bar) and opens
Gate 1 (induced divergence 0.85). But in the leakage-safe leave-one-context-out setting the clean
Part-B requires, learning collapses to 0.029 at the IDENTICAL 40k budget and 20-drug set (matched
control cellflow_gate1_transductive.json vs cellflow_gate1_loco.json), an 8.4x drop; per-drug it is
paired (AR-42 0.81->0.27, JQ1 0.67->0.06). The collapse is mechanistic, not incidental: per-drug
leave-one-context-out learning tracks the drug's cross-context response similarity (Pearson r=0.85,
Spearman rho=0.73; crosscos_vs_loco.csv). On SciPlex3 that similarity is low (median cross_cos 0.04)
and near zero for exactly the response-divergent drugs the retrieval task selects, so a predictor
conditioned on chemistry alone cannot supply the accurate cross-context responses the clean test
needs. Step 2 (retrieval falsification) was therefore NOT run: by the framework's own learn-then-test
logic, retrieval numbers from a predictor that fails the leakage-safe learning gate are
uninterpretable.

Truthfulness audit (5 adversarial verifiers over the actual code and result files). No fabrication:
all 188 SMILES verbatim from source, ECFP4 bit-for-bit reproducible, every reported number reproduces
exactly from the CSV/JSON, and the leave-one-out is genuine (query context's control AND treated cells
dropped before training; scored drugs present in the other two contexts with 386-480 treated cells
each). Two things the audit corrected, applied here: (i) the wrapper's additive self-check is a
tautology (pure arithmetic, never calls predict), so it does NOT validate the CellFlow pipeline; the
pipeline is instead validated independently by the transductive per-drug signal (AR-42 0.81 while most
drugs ~0, impossible if predict returned near-control). (ii) Wording was overclaimed and is now
scoped: "memorization" -> in-distribution reconstruction vs out-of-distribution prediction;
"principled/no drug-conditioned model/inherently" -> bounded, for the predictors we evaluated, by the
cross_cos ceiling; an earlier note's "first N by cell count" was wrong (drug_pool is alphabetical).

Manuscript edits (Results Part-B paragraph, Discussion "well-trained flow" paragraph, Limitations item)
weave in the CellFlow result with the audited wording; references.bib gains the real CellFlow entry.
Scripts: /data/boom/DART/analysis/predictors/cellflow/{export_sciplex3_ecfp4,cellflow_gate1_verify,
crosscos_regression}.py (remote 4090). Results:
results/exp14_nonadditive_predictors/cellflow_gate1{,_loco,_transductive}.{csv,json},
crosscos_vs_loco.csv. Net: the clean Part-B falsification remains out of reach, now demonstrated with
a modern flow-matching model and explained by a cross_cos transfer ceiling, strengthening the paper's
stated limitation rather than resolving it. The CPA-with-ECFP control (use_rdkit_embeddings, a
2048-bit Morgan fingerprint) was built and its plumbing verified but not run to completion, blocked
by GPU contention on the shared 4090; it remains open.

## R41 (closes R40's two open threads). CPA-ECFP completed, and the CellFlow collapse re-scored with distribution/DE metrics

Both deferred jobs ran once the shared GPU freed. Neither changes a conclusion; both strengthen one.

CPA with ECFP conditioning (the R40 open control). Re-run with the perturbation embedding FIXED to
the 2048-bit Morgan/ECFP fingerprint (cpa-tools use_rdkit_embeddings) instead of a freely learned
vector, transductive, 20 drugs, 100 epochs, 300 cells/group: overall delta learning 0.034 (A549
-0.146, K562 0.239, MCF7 0.008), still VOID, and gate1-vs-own-baseline 0.9995 (near-additive). The
free-embedding CPA was 0.076-0.08; chemistry conditioning does NOT rescue it. This refutes the
hypothesis that CPA's VOID was a representation artefact and locates the failure in the adversarial
objective. (cpa_ecfp4_gate.py; results/exp14_nonadditive_predictors/cpa_ecfp4_gate.json.)

CellFlow collapse re-scored beyond the mean (motivated by cell-eval, ArcInstitute/cell-eval, and the
principle that a mean-delta cosine can mislead). For every saved (setting, context, drug) triplet we
recomputed, alongside the mean cosine, a distributional energy ratio energy(pred,true)/energy(ctrl,true)
and gene-resolved DE metrics (direction match, recall@50, LFC Spearman). Transductive -> leave-one-
context-out: cos_delta 0.243->0.029, energy_ratio 0.984->2.121, DE-direction 0.696->0.517 (~chance),
DE-recall 0.282->0.066, LFC-Spearman 0.126->-0.003. The collapse holds on EVERY axis; the
distributional metric is even more damning than the mean, since leave-one-context-out predictions are
FARTHER from the true treated population than the unperturbed control is (energy ratio > 1). So the
collapse is a genuine loss of the response, not an artefact of a first-moment score. Honest caveat:
cell-eval's turnkey MetricsEvaluator could not run because it requires non-negative (log1p/count)
input and PopRetrieve's HVG matrix is centred/scaled (min -2.05); we therefore computed the same metric
FAMILIES directly (transparent, delta-based), and note this in the text rather than claiming the
cell-eval pipeline itself was run. (cellflow_save_preds.py + celleval_metrics.py;
results/exp14_nonadditive_predictors/cellflow_celleval.{csv,json}.)

Manuscript: the Results Part-B paragraph now states the collapse holds under distributional and DE
metrics and that ECFP does not rescue CPA; the Limitations item carries the same two clauses. No
conclusion is revised; the mean-based claim is upgraded from provisional to multi-metric-confirmed.

---

## R42. The premise correlation shared 43% of its cells between the two quantities it correlated

**Was:** "Across 18 within-patient drug pairs, the similarity of two drugs' *mean* signatures ranks
the similarity of their *malignant-compartment* responses at Spearman rho = +0.878" (Results, the
natural-heterogeneity section; Fig 4f caption; Methods).

**Is:** rho = +0.878 for that statistic, and **rho = +0.835** for the disjoint form, which is now
the load-bearing figure. On PW030 alone, +0.821 and +0.804.

**Why it changed.** The mean signature is taken over all called cells, and malignant glioma is
41,314 of the 96,225 called cells (Supplementary Table 3). The mean signature therefore *contains*
43% of the very cells whose response it is being asked to rank, so part of the correlation is
arithmetic rather than biology. This is the same structural error the project has already recorded
twice in another guise (R28, R30: a subpopulation's response must be referred to its own matched
baseline, or the baseline difference survives into the response). Here it is not a baseline error
but an overlap error, and it is the same family.

The corrected statistic asks the question the premise actually poses, which is whether what the
bulk of the tumour does already tells you what the compartment of interest does. It ranks the
malignant-compartment response by the **myeloid**-compartment response. The two compartments share
no cells, and each response is referred to its own compartment-matched control, so neither the
cells nor the baselines are shared.

**Nothing is retracted.** The finding survives at a slightly lower value, and the direction, the
interpretation and the severe single-patient caveat (15 of 18 pairs from PW030, no p-value quoted)
are unchanged. What changes is that the number reported is now one the paper's own argument
permits: a study whose thesis is that a scoring rule and its evaluator must not share their object
cannot quote a premise statistic whose two sides share half their cells.

**How it was found.** While recomputing the same statistic on Tahoe-100M plate 3, where the
analogous overlap is 26% (G2M cells inside a mean taken over all cells) and is worth +0.064 of
rho (0.905 overlapping, 0.841 disjoint). The tissue overlap is larger, 43%, but the effect on rho
is smaller, -0.043.

(analysis/natural/zhao_premise_disjoint.py; results/zhao_gbm/premise_disjoint.csv. The per-pair
table results/zhao_gbm/premise_mean_vs_compartment.csv already carried the myeloid column, so the
correction required no new computation on the tumour data and cannot have drifted from the
published figure.)

---

## R43. The DART-to-JUDGE rename (2026-07-26) broke one experiment and falsified thirteen comments

**What was wrong.** The pass that renamed the project from DART to JUDGE replaced the string
`DART` globally in prose, but three classes of occurrence were not prose:

1. **`exp13_real_data_projection.py` stopped running.** Five sites became
   `x.startswith("JUDGE")` and `piv["JUDGE"]`, where the value being tested is a **method key** from
   `results/exp11_hir_benchmark/phase_grid_method_performance.csv`. Those keys are
   `DART_energy`, `DART_mmd`, `DART_sliced_wasserstein`, `DART_coverage_mean`,
   `DART_coverage_worst`. After the rename `startswith("JUDGE")` matched nothing, every method was
   labelled `mean`, the pivot came back with a single column, and `fit_hir_boundary()` died with
   `KeyError: 'JUDGE'` before producing a number. `_observed_best_family()` had the same fault and
   would have raised on `np.max([])`. Restoring the literal recovers 72 grid cells and a mean
   distributional advantage of `+0.867585`, which is what the published boundary was fit on.
2. **The regime label `no_DART` was renamed in the text that reports it, but not in the code that
   emits it.** `predict_regime()` returns the literal `"no_DART"`, and `exp12_go_nogo.py` tests
   `HIR_predicted_regime.isin(["no_DART", "mean_sufficient"])`, but the report strings in both
   files had been changed to say `no-JUDGE`. The printed verdict then named a label that appears
   nowhere in the data it summarises.
3. **Twelve source comments recording a historical fact were falsified.** Each read "replaces
   hardcoded /data/boom/DART", which is what the pre-release code actually contained; the rename
   changed them to `/data/boom/JUDGE`, a path that never existed.

**Why it happened.** The rename pass protected identifiers that *look* like identifiers
(`DART_energy` as a whole token) but not the bare prefix `"DART"` used inside `startswith`, and it
could not distinguish a comment that *uses* the project name from one that *quotes* an old value.
Neither error is visible to the checks that were run: `py_compile` passes on all three classes,
and the LaTeX build and the figure typography gate never touch `src/experiments/`.

**Fixed** in the same pass that renamed JUDGE to PopRetrieve: all five `exp13` sites restored to the
frozen `DART_` prefix with a comment saying why, all three `no-JUDGE` strings restored to the
literal `no_DART`, and all twelve path comments restored to `/data/boom/DART`. The exp13 fix was
verified by re-running the boundary fit on the committed HIR-Bench CSVs, not by re-reading the
code.

**No published number changes.** `results/exp13_real_data_projection/` was written before the
rename and is unaffected; the regression was that the script could no longer regenerate it.

**Naming, for the record.** DART (through 2026-07-26) to JUDGE (one day) to **PopRetrieve**. Both
earlier names were acronyms; PopRetrieve is not, which removes the expansion string that had already
gone stale once (see the entry above). The full rationale, including why JUDGE was abandoned after
a day, is in `manuscript/reference/naming.md`.

---

## R44. A multi-agent audit of the whole repository. 86 defects confirmed, 60 fixed here

**What this was.** After the PopRetrieve rename (R43), the repository was swept by eight independent
auditors, one per dimension (rename integrity in executable code, manuscript numbers, manuscript
structure, documents-versus-reality, the figure build, consistency against this file, claim hygiene,
and data provenance). Every finding was then handed to an adversarial verifier instructed to refute
it and to default to refuted when it could not independently reproduce the defect. 100 findings were
raised, 86 survived refutation. What follows is what they found, grouped by kind. Nothing here
changes a published number except where stated.

**The paper asserted a measurement it did not make, in the abstract.** Six sites, including the
abstract's own closing sentence, said that in patient glioblastoma both gates open "and no advantage
appears". The Results say, in bold, "We did not run retrieval here, so we report no retrieval
result", and the Methods repeat it. A reader of the abstract alone, and every paper citing it, would
have reported that this study measured distributional retrieval on patient tumours with both gates
open and found no gain. No such measurement exists. This is the exact class of overclaim the paper
exists to criticise, in its most-read sentence. All six now say what the Results say: the mechanism
an advantage would run through is largely absent, and no retrieval was run. The abstract is still
exactly 150 words.

**The one affirmative result was stated unconditionally in four places and conditionally in four
others.** The Class-C positive holds under the cell-line-centred oracle and reverses under the
uncorrected one (R23, Supplementary Table 4), which the Limitations and Results both say. The
abstract, both Introduction statements and the Discussion said it flatly, and the Discussion used
"establishes", the strongest verb in the paper. All four now carry the condition. The paper's own
rule, "a paper arguing that the choice of criterion decides the winner cannot exempt its own
criterion", now applies to itself.

**"No stratum is positive" was false of the bars it described.** The Fig. 5g caption declares its
bars to be means; the Q4 mean is $+0.003$. The SI states it correctly, with the significance
qualifier ($q = 0.57$); the main text and caption had dropped it. Both now carry it.

**Gate 3's proposed status was silently lifted at the highest-n site.** The paper says of Gate 3
"we mark that difference wherever it appears", and the Tahoe-100M section did not: it said
"re-measured all three conditions", "Gate 3 replicates", and titled ED Fig. 7 "The three conditions
re-measured". What Tahoe recomputes is the premise statistic Gate 3 rests on, not decision
relevance: no candidate ranking and no decision outcome enter that dataset. Corrected in the
Results, the Methods and the ED Fig. 7 caption.

**Every shipped Extended Data PDF was a stale render, and three printed retracted numbers that
contradicted their own captions on the same page.** `edfig2.pdf` showed the pre-sentinel-fix power
analysis (n = 191, 27,794 queries for 80% power) while its caption already gave the corrected 143
and 20,844 (R2). `edfig3.pdf` printed "collapse structure 5.1x" and "9 clustering methods", both
retracted (R1, R10), while its caption said the opposite. `edfig1.pdf` titled a panel "Metric
correlation (54,180 queries)", the unit overstatement R29 corrects two sentences later in the same
paper. `edfig6.pdf` could not be regenerated at all: `ed6.py` imported four panel functions from
`fig5/`, which had since been re-cut into the two-gate figure, so it drew four panels unrelated to
its own caption; the real panels were parked in `figures/fig4/_stale/`, one directory deeper than
their own path resolution allowed. All seven now rebuild from source through `figures/build_ed.py`,
and the compiled SI contains none of those strings.

**The released per-panel source data had drifted from the figures it was supposed to let a reader
check.** `figures/source_data/` was maintained by hand with no record of what each file mirrored.
Four had drifted, two of them onto retracted values: the ED2 pair carried R2's superseded sample
sizes, and `fig3g_exp13_projection.csv` held the 37-row QUICK subset behind the retracted "0 of 37"
(R13) rather than the 239-row real run. In every case the panel was right, because panels read
`results/` directly, and the file offered to check the panel was wrong. `figures/sync_source_data.py`
now regenerates the mirrors, distinguishes them from hand-built derived views and from primary
inputs, and fails on drift.

**A "report only" dry run mutated the repository, before the gate that guards it.** `build()` in
four of the six assemble modules called `fig.savefig()`, so `python figures/build_all.py` without
`--write`, documented as a dry run, overwrote four tracked composites, and did so BEFORE
`assert_min_fontsize` ran, so a figure that then failed the gate had already been written. Exports
now go only through `figstyle.save()`, which applies the floor first.

**The typography gate is blind in two directions, and two documents claimed otherwise.** It reads
nominal point sizes, so it cannot see (a) the scale factor LaTeX applies to a figure authored wider
than the text block, or (b) mathtext sub/superscripts, which matplotlib renders at 0.7x. Sixteen
sub/superscripts across four main figures print between 3.9 and 4.9 pt while the gate reports CLEAN.
`figstyle.mathtext_offenders()` now measures the second and `build_all.py` reports it per figure;
it is reported rather than enforced, because compliance means raising nominal sizes to about 7.2 pt,
which re-authors the panel. README.md and the manuscript build guide no longer claim the gate knows
the column width.

**Two shell entry points could not do what they said.** `scripts/run_all_figures.sh`, described as
"one-click reproducible", drove the superseded v1 plotting pipeline: it reads
`results/exp01_sciplex3_controlled/`, which does not exist, so it dies with FileNotFoundError on any
clone, and would have written a different deck into a gitignored directory. It now drives
`build_all.py`, `build_ed.py` and `sync_source_data.py`. `scripts/run_hir_benchmark.sh` in QUICK
mode overwrote the tracked FULL tables in place, reproducing verbatim the incident this repository's
own PROVENANCE.md records as having already happened once; it now refuses without an explicit
`ALLOW_QUICK_OVERWRITE=1`.

**Four retracted numbers were living in documents that bind drafting.** The submission-prep
statistics checklist listed the retracted AUC 0.640 and the retracted 0.046-vs-0.009 collapse as
current results; the reviewer risk register offered R1's retracted "~5x structure collapse" as the
paper's prepared answer to a reviewer; the claim-safe language guide instructed authors to call the
retracted AUC "moderate"; and the negative-claims box still asserted "no therapeutic-utility metric
(Class C) is available in this study", the exact claim R14 calls "the most serious process failure
recorded here". Each is corrected in place with a pointer to its entry, and every live working
document under `manuscript/`, `analysis/` and `figures/` now carries a supersede banner naming
CORRECTIONS.md as the authority. The build guide `manuscript/latex/README.md` was rewritten from
scratch: it had presented the retracted AUC as the authoritative headline, described the Makefile
and the bibliography as "TODO, not yet built", and carried a title the manuscript had not used for
months.

**Smaller corrections.**
- `exp16_17_verdict.py` read its template from `paper/`, a gitignored author-local directory that
  does not exist and never entered git history, so the last step of `scripts/run_exp16_17.sh` ended
  in a traceback for everyone. Anchored to the repository; the verdict now regenerates, and does so
  byte-identically apart from the deliberate rename. Its committed output had also been hand-edited
  after generation; that edit is now in the template, so code and output agree.
- `exp13_real_data_projection.py` could not run from a fresh clone: one `.gitignore` glob excluded
  both a 3.8 MB table and the 60 KB grid layer the script reads unguarded. The small one is now
  tracked.
- `analysis/class_c/class_c_functional_oracle.py` looked for the GDSC2 workbook in
  `results/_audit/`, which does not exist, while `match_drugs_v2.py` read the same workbook from
  `results/upgrade/`. Unified.
- `audit_minority_coverage.py` overrode its own declared output directory and wrote into the source
  tree, leaving its consumer reading a stale copy under `results/upgrade/`.
- The README headline table's query-weighted Hit@1 column was wrong in four of six rows, and two
  macro values were misrounded. Recomputed from `results/exp08_signature_baselines/summary.csv`.
- The ED3a y axis printed the raw dataframe column names `ari_gmm2_raw` and `ari_gmm2_pca50`,
  because the display-name map keyed those two methods differently from the data. The silent
  `.get(key, key)` fallback that allowed it now raises.
- The Fig. 3c caption said "every bar $\leq 0.006$"; the Q3 bar is 0.006195.
- The ED3b silhouette caption gave the unit as "drugs" (R29: the unit is the (cell line, drug) pair)
  and attributed a SciPlex3-only median of 0.034 to both datasets; the pooled median is 0.040 and
  Frangieh's is 0.084.
- Both documents said there were three Supplementary Notes; there are four, and the fourth is the
  one that states the scope of every claim in the paper. The Additional Information statement
  announced Extended Data Figs. 1 to 6 of the seven that exist.
- Supplementary Table 1's footnote pointed the predictability analysis at "Fig. 5b"; it is
  main-text Fig. 4b.
- The title page understated the Methods by 40% (4,897 words against about 6,900) and the main text
  by about 1,300. Recounted with figure captions excluded.
- The Frangieh cell count appears as both 218,331 and 218,023 with no statement that these are
  different cell sets; they are, and the Data sources entry now says so.
- `requirements.txt` omitted anndata, scanpy and hdbscan, so one of README's own reproduce commands
  died at import; DATA.md omitted ZhaoSims2021, the GDSC2 workbook and the Frangieh protein
  modality entirely.
- `manuscript/latex/figures/fig7.pdf` was tracked in the directory documented as "the PDFs the
  documents include", was referenced by no `.tex`, and plotted the 0.964 cell-type ceiling that the
  ED3 caption explicitly withdraws. Removed. Its source, `figures/fig7/fig7_natural.py`, is live and
  stays: it draws Fig. 4e and 4f.
- `analysis/predictors/README.md` documented a `--nonadditive` flag that
  `exp09_predict_then_rank.py` does not parse.
- `CONTRIBUTING.md` told contributors that `results/**/per_query_scores.csv` is git-ignored; one
  such file is deliberately un-ignored and tracked, because Fig. 2c is an ECDF over its rows.
- `CITATION.cff` and `README.md` carried the pre-pluralisation title.

**Not fixed, and why.** Reported rather than changed, so that nothing here is a number this pass
invented:
- The five-variant Class-A range is quoted as "$+0.056$ to $+0.129$". Recomputing per variant on
  the 600-query MoA-defined set reproduces the Class-B range exactly ($-0.011$ to $-0.037$) but
  gives Class-A $+0.0495$ to $+0.1183$, so the denominator behind $+0.056$ and $+0.129$ could not
  be identified. Left alone; it needs the author to pin which subset the sentence means.
- `results/exp11_hir_benchmark/phase_grid_predictability_2x2.csv`, which backs main-text Fig. 4b,
  has no producer in the repository, and the regeneration command in that directory's PROVENANCE.md
  destroys the layer exp13 needs. Both are provenance gaps that cannot be closed by editing text.
- The CellFlow and CPA-ECFP artifacts behind one Results paragraph (R40, R41) were never committed.
- ED1 to ED4 print at roughly 2.8 to 3.5 pt because they are authored far wider than the text block;
  Fig. 5 overflows its page and Supplementary Table 1 runs into the right margin. These are layout
  defects the author has deferred to a dedicated re-layout pass, and rebuilding at unchanged
  authored geometry cannot fix them.

---

## R45. Figure 2e's control axis was described as the wrong quantity, in the caption and in the Results

**Was:** the manuscript said, in two places, that Fig. 2e sweeps the *similarity* of the two
constructed subpopulations. The Results read "progressively merging the two constructed
subpopulations did not produce a consistent monotonic loss of the energy-distance advantage", and
the caption read "Increasing the similarity of the two constructed subpopulations does not
consistently eliminate the energy-distance advantage". The panel itself labelled its x axis
"subpopulation mixing $\alpha$ (higher = more merged)".

**Is:** alpha is a mixing PROPORTION at fixed orthogonality, not a similarity knob.
`ControlledMixtureTask.build` (`src/retrieval/tasks.py:108`) computes

```python
n_maj = int(round(alpha * self.n_total))   # cells drawn from the HDAC response pool
n_min = self.n_total - n_maj               # cells drawn from the JAK response pool
```

so the query's 400 cells are drawn from two fixed real response pools and alpha sets their ratio:
200:200 at alpha = 0.5 through 360:40 at alpha = 0.9. The two states are two orthogonal
mechanism-of-action responses throughout, and nothing about them merges. What the sweep actually
does is starve the minority state, from half the query population down to a tenth of it. Since the
`covers-both` ground truth is built at the same alpha while `majority-only` is not, the
discriminating evidence shrinks with the minority state, which is why the task gets harder.

**Why the wrong description was plausible.** A merging sweep does exist in this repository, and it
is in the same module: `build_divergence_query(task, lam, alpha, ...)`, documented as "lam=0 ->
identical subpops, lam>=1 -> orthogonal". It is the control axis of exp02 (divergence gate) and
exp11 (synthetic phase diagram). Figure 2e plots exp01, which does not use it. Two different
control axes from two different experiments were described as one.

**What survives.** The finding is unchanged and its wording is now tied to what was run: reducing
the minority state from 50% to 10% of the query collapses the energy advantage in K562 (+1.00 to
+0.05) and does not in A549 (+0.40 to +0.65) or MCF7 (+0.35 to +0.45). The claim was always that
the collapse is not universal, and it still is.

**What changed.** The Results sentence, the Fig. 2 caption entry for **e**, and the panel, which
now plots the advantage directly (energy Hit@1 minus mean-cosine Hit@1, one curve per line instead
of six), labels its x axis "alpha, fraction of query cells in the HDAC state", and carries a strip
showing the query composition at each alpha. `figures/fig2/fig2e.py` asserts the alpha grid and the
cell-line set against the defaults `exp01_sciplex3_controlled.run` declares, so a re-run with a
different sweep breaks the build instead of relabelling itself.

**How it was found.** Two agents redrawing and then auditing the panel each rejected the brief's
description of alpha independently, after reading `ControlledMixtureTask.build`. Neither drew the
merged geometry the brief asked for, because the code does not produce it.

## R46. Figure 2g's matrix cannot be regenerated from the released code (reported, not fixed)

`figures/source_data/ed1_metric_correlation.csv` is the 6x6 Spearman matrix behind Fig. 2g and
behind the manuscript's "identical scores at every query-candidate pair (Spearman $\rho=1.000$ over
54,180 scores)". No file under `results/` holds those 54,180 query-candidate scores,
`exp08_signature_baselines.py` exports none, and `sync_source_data.py` does not know the file;
`figures/source_data/README.md` classifies it PRIMARY, i.e. nothing regenerates it.

This was tolerable while the panel was Extended Data Fig. 1c. It is a main-text reproducibility gap
now: a reader cannot check the panel or the sentence it supports. The fix is a generator that
re-scores the 1,260 queries against their 43 candidates under the six scorers and writes the pairs,
not an edit to any text. Recorded here and in `figures/source_data/README.md` so it is not
mistaken for a checked number. R29 corrected the *unit* of the 54,180 figure; this concerns its
*provenance*.

---

## R47. Figure 3f's null was manufactured by pooling two opposite verdicts

**Was:** panel 3f compared the 621 queries the information-condition gate recommended against the
144 it did not, on measured response divergence, and reported medians 1.66 against 1.68 with
Mann-Whitney p = 0.090. Drawn as two boxplots under the title "Recommendation cannot sort by
divergence", it read as an absence of any relationship.

**Is:** the gate issues THREE pre-specified verdicts, not two, and the two decline verdicts point
in opposite directions. Splitting on the gate's own categories:

| verdict | n | median true divergence |
|---|---|---|
| `DART_recommended` | 621 | 1.660 |
| `mean_or_no_call` | 133 | 1.689 |
| `mean_sufficient` | 11 | 0.509 |

The 133 queries declined as `mean_or_no_call` are significantly MORE divergent than the 621
recommended (Mann-Whitney p = 0.0011; a recommended query is the more divergent of a random pair
only 41.0% of the time, 95% bootstrap CI 0.362 to 0.458, entirely below the 0.5 the gate's premise
requires). The 11 declined as `mean_sufficient` sit below the fifth percentile of BOTH other
groups, so on those eleven the gate is correct.

Pooling the two decline verdicts into one group of 144 returns p = 0.090. That is not an absence:
it is a 133-query effect above the recommended group and an 11-query effect far below it,
cancelling. A Kolmogorov-Smirnov test on the same pooled comparison rejects equal distributions
(D = 0.154, p = 0.0069), so the pooled null was never a statement that the two groups were alike.

**Why this matters beyond one panel.** Manufacturing a null by pooling a mixture is the error this
paper exists to criticise, and the paper had made it about its own diagnostic. The corrected
reading is also STRONGER for the paper's argument: the gate does not merely fail to sort queries by
divergence, it sorts them backwards on the arm where it is actually used.

**What changed.** `figures/fig3/fig3f.py` draws both decline arms, the 133 as a distribution and
the 11 as individual ticks, computes and asserts the pooled statistic so the caption cannot drift
from it, and asserts that pooling still changes the answer. The Fig. 3 caption states both
readings. `figures/fig3/README.md` is updated. No manuscript Results sentence quoted the pooled p,
so no prose changed.

**How it was found.** The agent redrawing the panel refused to draw the two decline verdicts as one
group after reading their medians.

## R48. Figure 3c's "negligible" depended on which denominator was chosen

**Was:** panel 3c drew four quartile means as bars on an axis truncated at 0.012 under the title
"Minority-coverage gain is negligible", and the Fig. 3 caption read "All four differences are
statistically significant but at most 0.0062 on a metric whose values run from 0.89 to 0.99".

**Is:** two problems, one of framing and one of fact.

*Framing.* "Negligible" is a ratio, and the available denominators disagree by two orders of
magnitude. The largest quartile mean, +0.00619, is 0.6% of the nominal [0, 1] metric range, 2.6%
of the metric's observed range, 5.1% of its central 98%, 28.6% of its standard deviation across
queries, and **53.5% of its own interquartile range**; the paired Cohen's d of the per-query gain
is 0.331. Reporting the flattering denominator as though it were the natural one is precisely the
move this paper argues against, so the panel now reports none of them and instead gives the metric's
own median (0.985) and interquartile range (0.012) as the scale, and lets the reader size the gain.

*Fact.* "A metric whose values run from 0.89 to 0.99" is the central 98% of the observed values,
not their range, which is 0.756 to 0.996.

**What the data support without a choice of denominator:** the gain is positive in every divergence
stratum (each Wilcoxon p < 1e-6) and does not grow with divergence. Spearman(true_divergence, gain)
= +0.0502, p = 0.165 over all 765 queries, Q4 sits below Q3, and all four quartile intervals
overlap. The bar chart's apparent rise from Q1 to Q3 was noise on a truncated axis.

**What changed.** The panel plots four point estimates with 95% bootstrap intervals rather than
bars, states the Spearman result, and claims the absence of a trend rather than an effect size.
That also moves it into the same family as panels d, e and f: it is the gate's premise failing.
The Fig. 3 caption is rewritten accordingly. The manuscript's Results sentence, "Stratifying
queries by their measured response divergence did not reveal a hidden regime of large benefit",
was already the defensible claim and is unchanged.

---

## R49. Figure 3a and 3b were drawn on the subset the diagnostic itself selected

**Was:** panels 3a and 3b read `figures/source_data/fig3a_classA_vs_classB.csv`, a 480-row table,
and the panel stated `n = 480 paired queries`. The Results text reports the same analysis on 600:
"Among the 600 partial-observation queries for which both response-matching and mechanism
annotations were available".

**Is:** those 480 are `split_type == "leave_drug_out"` **intersected with the gate's
`DART_recommended` verdict**. The full leave-one-drug-out set is 600 queries, of which the gate
recommends 480, declines 109 as `mean_or_no_call`, and declines 11 as `mean_sufficient`. So the
figure's opening panel, the one carrying the paper's central reversal, was drawn on a
**gate-selected subset**, while the text reported the full set precisely so that the headline would
not rest on one.

The manuscript's numbers reproduce exactly on the 600 and not on the 480:

| | manuscript | 600 (correct) | 480 (was drawn) |
|---|---|---|---|
| mechanism recovery decreased | 41.3% | **41.3%** | 40.6% |
| increased | 34.2% | **34.2%** | 35.0% |
| unchanged | 24.5% | **24.5%** | 24.4% |
| paired Wilcoxon | 2.4e-4 | **2.46e-4** | 1.13e-3 |
| Class A median | +0.129 | +0.1288 | +0.1292 |
| Class B mean | -0.037 | -0.0371 | -0.0369 |

**This is the second occurrence of one bug.** Fig. 2c had exactly the same defect and was fixed on
2026-08-30: it plotted the 621-query gate-recommended subset while its caption and the Results text
both reported all 765. The mechanism is the same in both cases, a hand-built file under
`figures/source_data/` with no generator, silently holding a narrower query set than the panel's
own caption claims. `figures/fig2/fig2c.py` records the first occurrence.

**What changed.** Both panels now read
`results/exp12_partial_observed_retrieval/per_query_scores.csv` directly, filter on `split_type`
alone, never on `recommendation_mode`, and assert `n == 600`, so a subset cannot silently return.
The corrected set is also a balanced design, 200 queries per cell line, where the gate-selected one
was 157 / 146 / 177. The Fig. 3 caption is updated: 34% rather than 35% favour population, 24.5%
rather than 24% are exact ties, the Wilcoxon p strengthens from $1.1\times10^{-3}$ to
$2.5\times10^{-4}$, the Class A mean moves from +0.288 to +0.275, and the truncated tail is 4%
rather than 5% of the row. No conclusion changes; every one of them is slightly better supported.

`figures/source_data/fig3a_classA_vs_classB.csv` is no longer read by any panel. It is kept as
released data and reclassified, with its 480-row scope stated, so nobody mistakes it for the
analysis set again.

**How it was found.** The author of the figure noticed that the panel said 480 while the Results
said 600, and asked which was right before any redrawing began.

## R50. Every mathtext glyph in the deck was set in a different typeface from the text around it

`figstyle.apply_style` set `font.sans-serif` to Arial and left `mathtext.fontset` at matplotlib's
`dejavusans` default, so all 55 mathtext strings across the five main figures, every Spearman
$\rho$, every $\alpha$, every italic $P$ and every `$-$`, were rendered in DejaVu Sans beside Arial
digits and labels. All five figure PDFs embedded both families.

The minus sign was the worst of it. In the resolved Arial face a mathtext `$-$` measures 6.48 pt at
7.2 pt nominal, against 4.32 pt for a real U+2212 and 7.20 pt for that face's em dash: the minus in
a label like "population - mean advantage" was printing at 90 per cent of the width of an em dash,
in a project whose house rule is that em dashes never appear.

Fixed in `figstyle.apply_style` with `mathtext.fontset = "custom"` pointing at the sans family. All
five figures now embed Arial alone (regular, bold and italic), with no missing-glyph warnings, and
both build gates still pass: `build_all.py` reports 5 of 5 CLEAN with 0 typography violations and
`check_overlaps.py` reports 0 collisions. Found by the agent auditing Fig. 3a, which measured the
glyph widths rather than judging them by eye.

---

## R51. The power analysis moved from Figure 3 to Supplementary Note 2

Not a correction: a scope decision, recorded because it moves evidence out of a main figure and a
reader deserves to know where it went.

Main-text Fig. 3 carried two panels showing that the mechanism-recovery null is not a power
artefact, measured in the highest response-divergence quartile: achieved power 1.00 for
minority-state coverage ($n=191$) against 0.06 for MoA-nDCG ($n=143$), and 45 queries needed for
80% power against 20,844. On 2026-08-31 they were removed from the page and their numbers moved
into Supplementary Note 2 in full, together with the reading they support. The Results sentence that
cited "Fig. 3j,k and Supplementary Note 2" now cites the Note alone, and the surviving panels `l`
and `m` were relabelled `j` and `k`.

**Why.** The two panels are third-tier diagnostics on a page whose argument is its first four rows,
and they cost a whole row of a thirteen-panel figure. Removing them shortened the canvas from 9.20
to 7.96 in, a 13.5 per cent shorter page, and lifted panel a from 15.6 to 17.5 per cent of panel
area without resizing any other panel.

**The risk this takes, stated plainly.** A power analysis is the direct answer to the single most
likely objection to a paper whose central result is a negative, and moving it to the Supplementary
Information makes that answer one click further away. The mitigation is that the Note now carries
more than the panels did: both effect sizes, both standard deviations, both sample sizes, both
achieved powers, both required sample sizes, and the asymmetric reading the numbers actually
support, which the panels could not state in the space they had. That reading is worth repeating
here, because it is easy to overstate in the paper's favour:

- The minority-state comparison is well powered and returns a small effect. That is evidence of a
  small effect.
- The mechanism-recovery comparison is **not** adequately powered at $n=143$. Its null is an
  absence of evidence, not evidence of absence, and the main text's mechanism-recovery conclusion
  therefore rests on the full 600-query set and on the shape of the whole distribution
  (Fig. 3a,b), not on this stratum.

The difference between the two is not effect size, which differs by less than a factor of two, but
variance: the MoA-nDCG gap has twelve times the standard deviation.

`figures/edfigs/ed_panels.draw_ed2a` and `draw_ed2b` remain in the repository. They are now the only
code that reads `results/exp17_true_divergence_subset/power_analysis.csv`, so they are how that
table is regenerated and checked, and they should not be deleted.

---

## R52. Figure 4 moved to the deck's 6.5 pt floor, and lost four panels to Supplementary Note 4

Figure 4 was the last main figure still running on the deck defaults: a 5 pt production floor and a
(8, 7, 6) type ladder, while Figures 1 to 3 had moved to 6.5 pt and (8.5, 7.2, 6.8). It carried
**336 text artists below 6.5 pt, 21 of them at exactly 5.0 pt**, which is what Nature Portfolio
rejects rather than what a reader can take in at 183 mm. A reader turning from Figure 3 to Figure 4
watched the type shrink.

Two structural problems went with it. The seven third-tier panels occupied **47.8 per cent** of the
figure, and there was no hero: the largest panel, d at 13.7 per cent, is not the headline. Worse,
**panel b was the 11th largest of thirteen at 6.2 per cent**, and panel b is the one place in this
paper where circularity is measured rather than asserted.

**What changed.** Panels j to m, the four marker-floor robustness sweeps, left the page.
Supplementary Note 4 already carried every one of their numbers in prose (the 0.25 thresholds, the
39.9 per cent unassigned fraction varying 29 to 58 per cent, the supervised ceiling 0.915 to 0.923,
the best unsupervised 0.77 to 0.80, the paired gap 0.11 to 0.13, and the median cosine 0.54 to
0.59), so nothing was lost and the Results citation now points at the Note alone. The freed row went
back into the nine remaining panels rather than off the page: every axes grows from 1.46 or 1.56 in
to 1.75 in, and the canvas goes from 8.09 to 7.97 in.

`figures/fig4/fig4_style.py` now exists, and `fig4_assemble` gained `_assert_floor` at 6.5 pt and
`_assert_no_titles` capping panel text at 7.2 pt. Three legends that sat inside their axes (c, d, h)
became direct labels, which is both house style and where the space for larger type came from. What
those legends said is now in the caption, which grew from 579 to 723 words while losing four panel
entries.

**One clearance is thin and nothing guards it.** Panel c's y-axis label clears panel b's colour-bar
label by 1.78 pt and its own tick labels by 1.51 pt, measured on the rendered page. Any growth in
panel b's colour-bar label collides, and no build gate watches horizontal clearance between
neighbouring panels.

## R53. Figure 4e draws a band from four hard-coded numbers, and one of them cannot be sourced

`figures/fig7/fig7_natural.py:55` defines

```python
CONSTRUCTED = {"ceiling": 0.692, "unsup": 0.674, "cos_lo": 0.014, "cos_hi": 0.044}
```

as four literals, and main-text Fig. 4e imports it to draw the shaded band that its own label calls
the constructed-mixture range. `fig7/` is a retired figure directory.

`cos_lo = 0.014` reproduces: it is the mean induced-response cosine of the `real / real_blend` arm,
0.014288, over 96 rows of
`results/exp09_structure_diagnostics/gate1_response_divergence.csv`.

**`cos_hi = 0.044` reproduces from nothing.** On that same 96-row sample the candidate summaries are
median 0.011, q75 0.038, q90 0.079, q95 0.104, max 0.132, mean plus one standard error 0.019, and
per-pair mean maximum 0.026. The two closest coincidences are the 78th percentile (0.0422) and the
mean plus 0.64 standard deviations (0.0449), and neither is a statistic anyone chooses. A search of
`results/` for a matching value returns only unrelated columns.

So a band on a main-text figure is drawn from an unsourced literal, and the panel's own module
docstring points at `fig7_natural` as the fix site rather than at a results file. This is the same
class of defect as R46 (Fig. 2g's correlation matrix has no generator) and R49 (Fig. 3a plotted a
hand-copied subset): a number reaching a main figure through a file with no derivation.

### FIXED 2026-09-01

The band was worse than a provenance problem, and measuring it said so. The Figure 4 caption
described it as "the range spanned by our own constructed mixtures". **The drawn band contained 24
of the 96 values, 25 per cent.** Its lower edge was the MEAN, so it hid the entire lower half of a
distribution that is centred near zero and runs negative: the real summaries are min $-0.0938$,
q25 $-0.0156$, median $+0.0110$, q75 $+0.0380$, max $+0.1317$.

It also concealed an overlap. The constructed values reach $+0.132$ and one of the 17 natural
patient--drug pairs sits at $+0.081$, inside the constructed range. With the old band no natural
point came near it, so the panel showed a clean separation that the data do not have.

**What changed.** `fig7_natural.CONSTRUCTED` is no longer four literals; it is a `constructed()`
function that reads every value from its own source. `ceiling` and `unsup` come from
`results/upgrade/gate2_supervised_upper_bound.csv` at `separation_scale == 1.0` as medians over
seeds, which is the same aggregation `fig5e` uses, so the two panels cannot disagree; they
reproduce the old literals at 0.692 and 0.674. The divergence summaries come from the 96
`real / real_blend` rows of `gate1_response_divergence.csv`.

The band is now the observed range, min to max, with the median drawn inside it, so the caption's
"range" is literally true and the overlap is visible. The caption states the range, the median, the
n, and the overlapping pair.

**The label prints no number at all.** It reads "constructed mixtures" and nothing else. The
endpoints were previously typed twice, once in the dict and once in a hard-coded string
`"constructed mixtures\n0.014 - 0.044 (near-orthogonal)"`, with a guard in `fig4_nat` comparing
the two; both copies were wrong together, so the guard passed. A label that prints no number cannot
drift from the band it names, and the guard is deleted rather than re-pointed.

**One related literal, fixed at the same time.** `ed7_tahoe.draw_a`, which is main-text Fig. 5h,
anchored its "constructed mixtures" reference line at a typed `0.014`. That number did reproduce,
being the same arm's mean, but it is now computed from the same file, and as the MEDIAN so that the
two figures describe the constructed mixtures by the same statistic. The anchor moves from 0.014288
to 0.011017, 0.3 per cent of that axis, and the Figure 5 caption's "fewer than 0.11% of conditions
as divergent as the constructed mixtures" is 3 of 3630 under either value.

---

## R54. Figure 5k reported the square of Spearman's rho as "R^2", beside a least-squares line whose R^2 is 0.61

`ed7_tahoe.draw_d`, which is main-text Fig. 5k, computed

```python
r, _ = spearmanr(j.g1, j.spearman_rho)
...  f"$\\rho$ = {r:+.2f}\n$R^2$ = {r ** 2:.2f}\nn = {len(j)} lines"
```

and the caption repeated it as `$R^2=0.38$`. Two things were wrong with it.

It carried no information. `r ** 2` is the square of the rho printed on the line above, so the
second line was the first line restated.

More seriously, the panel also draws a least-squares line through the raw values, and **the
R-squared of that line is Pearson's, 0.6057, not 0.3846**. A reader takes "R^2" beside a fitted
line to be the variance that line explains, and the printed value understated it by 0.22. Over
44 cell lines: Spearman rho +0.6202 (p = 7.1e-6), Pearson r +0.7783 (p = 5.0e-10).

**Fixed.** The panel now prints rho and n only. Rho is the right statistic for the claim the panel
makes, which is that differential response and state-ordering agreement are related but not
equivalent; the dashed line stays as a visual trend guide, and the panel no longer implies it is
the model rho describes. The caption drops `$R^2=0.38$`. The macro `\TAHOECOUPLINGRSQ`, defined as
`0.385` in both the manuscript and the SI and never used by either, is deleted rather than left for
someone to wire into prose.

Removing it also resolved a type conflict: `$R^2$` is mathtext with a superscript, which matplotlib
renders at 0.7x nominal, so meeting the 6.5 pt floor would have needed 9.3 pt nominal, above
Figure 5's 7.2 pt cap on panel text, and would have set the base R half again as large as the text
beside it.

---

## R55. Main text cited Fig. 5h-j, three clustering panels, for a claim about predictor algebra

The Results sentence

> This is an algebraic property of the model class rather than a consequence of insufficient
> training (Fig.~\ref{fig:5}h--j and Supplementary Note~3).

pointed at three panels that measured unsupervised recovery of the constructed two-state mixture:
median ARI across nine clustering configurations, per-population silhouette under a raw k=2
partition, and a seed-averaged ARI grid over separation by cell budget. None of them shows anything
about whether an additive predictor can generate state-specific differential response. The caption
said so on its own face: "**h-j**, Recoverability measured three further ways on the constructed
mixture of **e**."

**Fixed.** The three panels moved to Supplementary Note 2 (see R56) and the citation is now
`(Supplementary Note~3)`, which derives the additive-predictor algebra and carries the claim
alone.

A second, smaller citation defect was fixed at the same time: **panels c, d and f were cited
nowhere in the Results**, only described in the caption. Each is now cited where its evidence
belongs, c and d in the differential-response paragraph and f in the recoverability paragraph.

---

## R56. Figure 5 could not meet the deck's 6.5 pt floor at fourteen panels, and three of them had no Supplementary home

Figure 5 was the last figure to get the typography pass, and it was the worst page in the deck:
**239 of its 263 text artists sat below 6.5 pt, 33 of them at exactly 5.0 pt**, and every one of
its fourteen panels failed the floor.

The cause was geometric rather than careless. Seven panels arrived on 2026-08-30 when the Extended
Data deck was retired, as a three-across row and a four-across row at 1.06 to 1.50 in wide.
Measured at 6.5 pt against the slot each packing affords:

| packing | slot | a b d f | c | e | g | Tahoe |
|---|---|---|---|---|---|---|
| four-across | 1.66 in | fit | +0.099 | +0.130 | +0.587 | +0.31, +0.16 on two |
| three-across | 2.22 in | fit | +0.099 | +0.006 | +0.252 | fit but for +0.020 |
| two-across | 3.33 in | fit | +0.099 | fit | fit | fit |

So the floor could not be raised while fourteen panels were on the page. Panel c's overflow is the
one that does not move with width: it is a second y axis and needs a right margin.

**Fixed, at eleven panels.** h, i and j left. Unlike the panels cut from Figures 3 and 4, **no
Supplementary Note carried their numbers**: there was no ARI 0.106, no SciPlex3 or Frangieh
silhouette, no separation-by-budget grid anywhere in the SI. Supplementary Note 2 therefore gained
"Unsupervised recovery of constructed two-state structure" *before* the panels were removed,
carrying all three measurements. The four Tahoe panels stayed, renumbered h to k.

The page went from 234 mm, the deck maximum and 0.02 in inside the float budget, to 206 mm. The
type ladder went from twelve sizes spanning 5.0 to 8.0 pt to four: 6.5, 6.8, 7.2 and the 9.5 pt
panel letters.

Two further defects were found and fixed while re-laying the panels.

**Purple carried two meanings at once.** It was patient tissue in the Tahoe differential-response
and recoverability panels, and the "cell state" partition in the state-ordering panel, where the
same purple also drew the tissue reference line at 0.835. The cell-cycle median is 0.841, so that
panel put a purple line through a *blue* series and labelled it in the other series' colour. The
two partitions are separated by x position and by their own tick labels and never needed a colour
contrast; they are now one colour, and purple means tissue.

**Orange carried two meanings at once.** It was the mean signature and the additive limit in
panels b, c and g, and "the constructed mixtures" as a reference mark in the two Tahoe panels. The
two met on one axis: the Tahoe differential-response panel drew the constructed-mixture anchor in
orange and the additive ceiling at cosine 1 in near-black, while panel c drew that same ceiling,
the same quantity on the same axis, in orange. Orange is the deck's mean-signature colour and
cannot move, so the constructed mixtures moved to slate and the additive ceiling is orange in both.

**One hierarchy inversion was corrected.** On the first cut of the new ledger the largest panel was
e at 17.8 per cent of panel area, and e is the panel whose general reading this paper withdraws
(R18, R21), while a, the schematic the figure is organised around, was 8.9. Row heights were
rebalanced; e is now 16.1 against g's 15.7. e remains the single largest because it scores seven
methods in one unit and seven two-line categorical labels need 3.39 in, which is a content
constraint rather than a claim.

---

## R57. Figure 1 stated six of its conclusions twice, and painted evidence classes in colours that already meant something else

Figure 1 was the last figure to get the panel-phrase pass. It already met the 6.5 pt floor, so the
problems here were not typographic.

**Six conclusion sentences were drawn on the panels.** `fig1_style` ended in a `title()` helper,
documented as "the single phrase a panel states over itself", and seven of the eight panels called
it at 8.5 pt, the largest non-letter type in the figure:

| panel | phrase | the caption already said |
|---|---|---|
| a | same library, different ranking | "the two ranked stacks ... disagree at rank 1" |
| d | Means tie, distributions separate | "A mean score cannot separate them; a population score prefers A" |
| e | Better representation, better decision? | "Why an evaluation can mislead" |
| f | Evidence ladder | "**f**, The evidence ladder." |
| g | Mean retrieval = zero-variance limit | "**g**, Mean retrieval is the zero-variance limit of population retrieval." |
| h | Population scoring is a continuum | "**h**, Population scoring is itself a continuum." |

`fig1_assemble` recorded the duplication in a comment of its own: the phrases "are the caption's
own opening clauses". So the figure asserted its conclusions in two places, one of which cannot
qualify, scope or attribute them.

**Fixed.** All six removed, `fig1_style.title()` deleted rather than deprecated, and
`fig1_assemble._assert_no_titles` added, capping panel text at 7.2 pt so no panel can reimplement
the helper with a bare `ax.text`. Text that is entirely mathtext is exempt, because panel a
composes its subscripted distances by hand (base at PT_EQ, subscript at PT_SMALL, reproducing
mathtext's 1.43 ratio) and panel h sets its y axis to $D_\beta$ the same way; a symbol is not a
claim, and a conclusion sentence is never wrapped in dollar signs.

One phrase survived. Panel b's **same mean** names the dashed rule it sits on, the way an axis
label names an axis, and without it the reader meets an unexplained orange line. It is now set at
PT_ANNOT like every other direct label on the figure.

**Panel f gave two established colours a second meaning.** Its three evidence-class platforms were
washed and outlined in POP blue (Response matching), SHARED grey (Mechanism recovery) and EXT green
(External function). `fig1_style` teaches four colours across panels a to e, where blue means
"population-level / distributional" and grey means "everything both routes have in common". An
evidence class is neither, so a reader who had learned the vocabulary reached the last panel of the
figure and found two of its colours attached to something else. The module's own rule covers the
case: "if a panel needs to separate two things and has run out, it separates them by shape, fill,
or position, not by inventing a hue." This panel had not run out; it had three hues it did not
need, because the ordinal axis is already carried twice, by the staircase offset and by the
labelled arrow beside it.

**Fixed.** All three platforms are one neutral and the ordering is position alone. Panel e's fills
were checked at the same time and are correct, so they stay: its circles are labelled "population
distance", its ranking cards are shared machinery, and its judge card is an external evaluator, all
three the vocabulary's own meanings.

**The README described a figure that was not being drawn.** Four of its claims were false of the
code, and all four are corrected:

- "Colour appears only in a-d ... Panels e and f ... are ink and grey." Both panels have used
  fills and hue throughout.
- "GREEN and PURPLE are not used in this figure." Green is used in e, and was used in f.
- "the caption has six entries and the figure now has eight. g and h still need their entries
  written." The caption has carried all eight since 2026-08-31, with g's and h's endpoint numbers
  and their source.
- "g and h ... have no `fig1g.py` or `fig1h.py`, because `fig1_assemble.py` imports
  `ed_panels.draw_ed1d` and `ed_panels.draw_ed1e` directly." Both files exist and `fig1_assemble`
  imports `draw_1g` and `draw_1h` from them. The README also pointed twice at a `TITLES` dict in
  `fig1_assemble.py` as the authority for g's and h's claims; no such dict exists.

The page came down from 234 mm, the deck maximum, to 219 mm. The saving is entirely furniture,
`LETTER_BLOCK` 0.24 to 0.17 and `ROW_GAP` 0.30 to 0.22, both of which were sized to separate the
bold phrases that are now gone. The rows themselves gave back less than 0.03 in each, because these
are schematics whose type is absolute while their layout is fractional.

A measurement note worth keeping, because it nearly caused a wrong edit:
`PathCollection.get_window_extent` does not report the extent of the drawn points, so a first pass
read panel c as having 0.40 in of dead space above its content and 0.02 in below. Measured from the
collection offsets instead, the real figures are 0.06 and 0.02, and panel c needed no change at all.

---

## R58. Figure 2 panel a spent 40 per cent of its axes on an annotation column, and two other panels had furniture hung on axes fractions

The author's report was that panel a was too wide. It was, and the cause was measurable: its axes
was 5.88 x 1.20 in, a **4.9:1 strip** whose longest bar was 3.00 in of 6.9 pt ink, **44:1**, and
`xlim` ran to 1.656 so that **2.33 in of the axes, 40 per cent of it, sat beyond the data range**,
holding the eight value labels, the `+0.448` headline block and the provenance key.

That width was spent rather than wasted, which is why the obvious repair does not work: folding the
annotation column back in only lengthens the track, and at full width the alternative to dead space
is longer, thinner bars. The panel could not be fixed inside its own box.

**That forces the layout.** A full-width panel at even the shortest row height in this figure is
5.76 in^2 of axes against the narrowed hero's 5.72, so once panel a stops being full width, nothing
else may be full width either, and seven panels cannot tile two per row. A panel had to go.

**The panel that went is the old d, and it was a duplicate.** Figure 3 panel d is the same
measurement, and Figure 3's caption said so in those words: "The same measurement as
Fig.~\ref{fig:2}d". The gate null was a main-text panel twice over, and Figure 3 is where the
diagnostic's failure is argued (its d--f are "three independent ways the diagnostic fails"). Its two
load-bearing caveats moved into Figure 3's caption entry with it: that queries within a cell line
share a candidate library, which makes the test anticonservative and therefore strengthens a null;
and that pooling the 11 mean-sufficient queries gives the same verdict. The old e, f and g moved up
one letter to d, e and f, and the two source-data mirrors named after them were renamed with them.

Panel a is now 2.95 x 1.94 in, **1.52:1**, with a row pitch of 15.8 pt against the old 9.8 and bars
0.101 in thick against 0.068. What it costs, stated plainly: the longest bar is 1.47 in rather than
3.00, and the horizontal distance between the population floor (coverage-worst, 0.589) and the mean
ceiling (PCA-mean, 0.518) is 0.124 in rather than 0.253. The ratio the panel argues from is
unchanged; the absolute separation is 3.2 mm rather than 6.4 mm.

The value column stays OUTSIDE the track. Folding it inside the wash's Hit@1 = 1 ceiling would buy a
2.10 in track instead of 1.75, i.e. 0.6 mm more separation, but `figstyle`'s presentation layer
states that value labels sit right-aligned past the end of the track and every other value column in
the deck does. 0.6 mm is not worth being the one panel that reads differently.

### Two more panels had the defect fig2a lost on 2026-08-31

Freeing 1.01 in of page and spending it on the two lower rows exposed the same class of bug twice,
and it is invisible until a box height moves:

- **`fig2b`** dropped its group separator to `-0.40` and its n line to `-0.275` on the xaxis
  transform, which is a fraction of the axes HEIGHT. When the panel went from a 1.08 in axes to
  2.04 in, the separator fell 0.816 in against a 0.50 in pad and hung **0.316 in into the row
  below**.
- **`fig2c`** set its two x-label lines at `-0.19` and `-0.30`. At 1.55 in the second line fell
  0.465 in and its descenders left the panel.

Both now measure in inches and convert at draw time, preserving the printed drops they had at their
old heights. **No gate could have caught either**: `_assert_floor` and `_assert_no_titles` read font
sizes, not positions, and `check_overlaps.py` reads text against text, not text against its box.
They were found by a per-panel harness that measures ink against the panel's own rect, which is the
check this deck does not have as a build gate.

Spending the freed inch also fixed the original complaint one panel over: **d's curve was
3.23 x 0.66 in, 4.9:1**, the very proportion panel a was rebuilt to escape. It is now 2.86:1.

The figure went from 176 x 197 mm with seven panels to 176 x 193 mm with six.

### One thing found on the way that is not a layout matter

Panel a groups eight scorers into two families and washes them, on the strength of the weakest
population scorer (0.589) sitting above the strongest mean one (0.518). **That is a property of the
macro-mean and holds in only 3 of the 7 individual task settings**; in the other four,
coverage-worst is beaten by PCA-mean or CMap WTCS, and on Frangieh mean cosine is the best of all
eight. Nothing on the page over-claims: the x axis label says "macro-average across 7 task
settings", the caption quotes the two macro-means it is comparing, and panel b carries the Frangieh
reversal explicitly. But `fig2a.py`'s docstring called the separation "the whole design" without
recording that it is a mean-level property, and it now does. The practical consequence is recorded
in the panel README: do not add per-cell dispersion to this panel, because the dots would visibly
break the grouping in four of seven columns.

---

## R59. The Results quoted a Wilcoxon p that rounded the wrong way, and the figure caption quoted the right one

Fig. 3a's mechanism-recovery arm carried **two hand-typed copies of one statistic that disagreed**:
the Results said `p = 2.4e-4` and the Fig. 3a caption entry said `p = 2.5e-4`. Recomputed under the
documented convention (two-sided Wilcoxon, zeros dropped, the scipy default) on the 600 paired
queries `fig3a.class_a_b()` returns, **p = 2.46141e-4**, so the caption was right and the Results
had truncated rather than rounded.

A third copy existed and was worse. `\CLASSBP` was defined in the preamble, annotated with the
correct convention, held the wrong value `2.4e-4`, and **was referenced nowhere in the document**.
Both call sites now use `\CLASSBP` and it holds `2.5e-4`, so the statistic has one source.

Nothing else in that paragraph moved: median +0.1288, mean -0.0371, and 41.3 / 34.2 / 24.5 per cent
all reproduce exactly.

## R60. Three Results citations pointed at panels that do not carry the claim, and two panels were never cited at all

Found by cross-checking, for all 45 panels in the deck, what each assemble script actually draws
against what the caption letters and what the `\ref{fig:N}` panel runs in the Results say. Caption
coverage was already 45 of 45. Four defects were on the Results side.

- **Fig. 3c was cited for a mechanism-of-action result it does not draw.** The sentence read "the
  minority-state advantage remained small ... and mechanism-of-action recovery showed no significant
  positive gain in that stratum (Fig. 3c)". `fig3c.py` draws minority-coverage gain by divergence
  quartile; the MoA-by-quartile result (mean +0.003, q = 0.57) is **Fig. 5g**, which states it
  verbatim. The sentence is now split and each half points at its own panel.
- **Fig. 3c was also cited for panel g's numbers.** "239 real-data tasks, mean +0.0018, 102 tasks
  selecting the same candidate" are all three panel g's; c is the n = 765 quartile panel and carries
  none of them. The citation is now `g` alone.
- **Fig. 3j,k were cited in support of a claim they qualify.** They sat after "This provides an
  affirmative result: population-level transcriptional similarity contains functional information
  that is not captured as strongly by the mean signature". Panel j is the absolute-potency endpoint
  audit, whose own caption says "an endpoint diagnostic, not evidence that retrieval fails", and k
  is the response-magnitude channel behind it, median rho = +0.791. Both are the evidence for the
  **next** paragraph's caveat, and they are cited there now. Provenance: the citation read
  `(Extended Data Fig. 5 ...)` before `e773b29`, and ED Fig. 5 is exactly what became 3j and 3k, so
  the repoint was faithful and the misdirection predates it.
- **Fig. 3e and Fig. 3f were the only two panels in the deck with no Results citation.** Both carry
  substantive statistics, the caption groups them with d as "three independent ways the diagnostic
  fails", and the Results discussed only d. Both are now cited where d is, with the statistics
  recomputed from `_merged_query_divergence.csv`: e, rho = -0.2110, p = 3.79e-9, n = 765; f, medians
  1.6888 against 1.6595, the 133 declined queries being more divergent than the 621 recommended.

Re-running the audit after the edits: drawn = captioned = cited for all 45 panels, 0 misalignments.

## R61. A Results paragraph attached four numbers to Fig. 5c, and none of them is on Fig. 5c

The worst of the set, because a reader who follows the citation sees the opposite of what the
sentence says. The paragraph reports the within-context differential-response experiment: real cells
0.205 over 30 cell-line and drug combinations, the average-effect and linear-latent predictors
"returned a cosine of 1.000 by construction", scGen 0.972, an optimal-transport map 0.900. It cited
`Fig. 5c and Supplementary Note 3`.

Those numbers are Supplementary Note 3's, from
`results/exp14_nonadditive_predictors/gate1_within_context.{csv,json}`, n = 30 contexts. **Fig. 5c
is a different experiment**: `fig5c.py` reads `exp09_structure_diagnostics/`, 96 constructed
cross-line mixtures, and plots real 0.014 against average-effect 0.186, linear-latent 0.239 and
nearest-neighbour 0.366. scGen and the OT map are not on the panel at all.

So the sentence said two named predictors return 1.000 while the cited panel plots those same two
predictors at 0.186 and 0.239, **next to a rule the panel labels "additive limit, cos = 1"**.

The two are reconcilable and the reconciliation was only in the SI, in a subordinate clause: the
additive limit is exact "when the perturbation response is referenced to the model-consistent
baseline". `gate1_within_context.json` records this per predictor as `baseline_kind`, and the same
file shows the size of the difference directly, e.g. scGen is 0.9724 against its reconstruction
baseline and 0.4044 against the real control cells.

Fixed as the author chose, minimally: the `Fig. 5c` pointer is removed from that sentence, which now
cites Supplementary Note 3 alone. Fig. 5c would then have been uncited, i.e. the R60 defect again,
so it is cited for the 96-mixture measurement it does draw, and its caption entry now states the
panel's own numbers on both axes and says which baseline convention the Results values use.

## R62. Two more reference anchors in Fig. 5h were unsourced literals, one line below the R53 fix

R53 replaced Fig. 5h's constructed-mixture anchor with a value computed from its source file. The
same `for` loop carried two more anchors as literals, `0.205` and `0.566`, and they were not looked
at when R53 was fixed. Both now come from their own source of record:

- real cells, state split: `exp14_nonadditive_predictors/gate1_within_context.csv`, `real_cells`
  mean of `cos_within`, **0.20543**, the statistic Supplementary Note 3 quotes it by.
- patient tissue: `zhao_gbm/gate1_natural.csv`, median `induced_response_cosine`, **0.56562**, the
  statistic the Fig. 4e caption quotes it by.

The two use different statistics deliberately: an anchor points at a result stated elsewhere, so it
has to reproduce the number that result is quoted by. Both literals reproduced to three decimals, so
nothing on the page moved; what was wrong was that neither could fail if its data changed.

## R63. The Additional Information section said all 21 Extended Data panels were in the main figures, and nine had left

`e773b29` folded 21 Extended Data panels into Figs. 1 to 5 and the section has said so since. Four
later commits moved panels back out, and the sentence was not revisited. Against `e773b29`'s own
allocation table:

| | ED panels | now |
|---|---|---|
| Fig. 1 g,h; Fig. 2 g; Fig. 3 l,m; Fig. 4 g-i; Fig. 5 k-n | 12 | in Figs. 1-5 |
| Fig. 3 j,k (`9e41f7c`); Fig. 4 j-m (`5c5ad32`); Fig. 5 h-j (`10f7311`) | 9 | Supplementary Notes 2 and 4 |

The sentence now gives 12 and nine, and keeps the five that were removed as duplicates.

## R64. Smaller items from the same pass

- **Fig. 5b's caption listed its three values in an order matching neither the panel nor any naming**
  (`-0.071, -0.016 and +0.027`, unnamed), while the panel plots avg-effect, linear-latent,
  nearest-neighbour top to bottom. The caption now names each value and says "in the order plotted".
- **A preamble comment still called the Tahoe panels `Fig. 5k-n`**; they have been h to k since
  `10f7311`.
- **The SI's two references into the main figures were hard-coded**, which it has to be, since
  `\ref{fig:N}` cannot resolve across documents. They now go through `\MAINRECOVER` and
  `\MAINCLASSAB`, so a renumber of the main deck has one place to edit rather than two to find. The
  comment above them also said the file holds Supplementary Notes 5 to 8; it holds 1 to 4.

## R65. NOT FIXED: the optimal-transport dispersion in Supplementary Note 3 has no source in the results

Recorded rather than changed, because changing a reported statistic is the author's call.

Supplementary Note 3 and the Results both give the optimal-transport predictor's induced-response
cosine as **0.900 +- 0.107**. The 0.900 reproduces: it is `ot_map.cos_vs_model_baseline` in
`gate1_within_context.json`. **The 0.107 does not appear in either file.** The only dispersion
available for that predictor is in `gate1_within_context.csv`, where the ot_map rows give s.d.
0.0968, but that CSV is from an earlier run (14 Jul) than the JSON (15 Jul) and disagrees with it on
this predictor's whole convention: `baseline_kind` is `identity` there and `reconstruction` in the
JSON, and the mean is 0.767 rather than 0.900. The real_cells and scGen values agree across the two
files; only ot_map does not.

Both texts hedge with "approximately", so nothing is overstated. But the number cannot currently be
regenerated from the repository, which is the standard the rest of this file holds. Re-running
`exp14_nonadditive_predictors` under the JSON's convention and writing the per-condition rows would
settle it.

---

## R66. Three stale geometry records surfaced while measuring the deck's whitespace

The author's report was that the panels sit too far apart. Measuring it, rather than adjusting the
ledgers by eye, meant walking every panel's real ink against its own allocated box, which turned up
three records that were simply wrong.

- **`fig4_assemble.BANNER_Y` was dead and stale.** Three row-banner positions, referenced from
  nowhere in the repository, left behind when the row headings moved into the caption. Its first
  entry was the figure's canvas height, `7.97`, from two revisions earlier; anyone checking the
  geometry against it would have been reading a stale number that no longer described anything.
  Deleted, with a note saying what it was.
- **The two-float comment in the manuscript preamble gave both of its ranges wrong.** It said the
  five graphics "are now 7.19 to 9.26 in tall" and their captions "277 to 648 words". Measured, the
  graphics were 7.57 to 8.60 in and the captions 548 to 769 words. The conclusion it draws is
  unaffected and still holds after this pass (the shortest possible pairing is now 7.09 + about
  5.4 in against a 9.46 in text block), but the numbers supporting it described an older deck.
- **Three panel READMEs quoted canvas sizes that the whitespace pass then changed**, and are
  updated with it: fig2 7.57 -> 7.35 in, fig3 7.96 -> 7.67, fig5 8.11 -> 7.34.

The retune itself is in the commit, not here, since loose spacing is not an error. What the
measurement found is worth recording: the corridor between two rows is ROW_GAP plus the upper row's
UNUSED bottom pad plus LETTER_BLOCK less the letter's own height, so it has three independent terms
and inspecting any one of them tells you nothing. Figure 5 ran 0.47 to 0.56 in and Figure 4 ran 0.48
to 0.53 while Figure 3 ran 0.21 to 0.32 and Figure 1 ran 0.04, and every one of those ledgers said
`ROW_GAP = 0.22`. Figure 5's left pads were the clearest case: all eleven panels had exactly 0.22 in
between the box edge and the first ink, which is the letter reserve arriving completely unused,
because `_letter()` draws at the box edge rather than inside the pad.

**No axes changed size in any figure except to grow.** Every row height was cut by the same amount
as its panels' bottom pads, and every left-pad cut went into axes width, so what left the page is
white. Heights: fig1 219 mm (unchanged, it had no reclaimable white and its rows already measure
0.04 in apart), fig2 193 -> 187, fig3 203 -> 195, fig4 203 -> 181, fig5 207 -> 187.

## R67. Figure 4f drew the overlapping premise statistic under a caption that described the disjoint one

`figures/fig7/fig7_natural.draw_c`, imported unchanged into Figure 4 as panel f, plotted
`cos_mean_signature` against `cos_malignant_response` and printed `Spearman rho = +0.878`, with an
x axis reading `cos(mean signature A, B)`. The Figure 4 caption and the Results sentence that cites
the panel both describe the DISJOINT comparison, myeloid-response similarity against
malignant-response similarity at `rho = +0.835`. A reader comparing panel to caption saw two
different statistics, two different x quantities and two different numbers.

**Was:** panel = mean-signature form (`+0.878`); caption and Results = disjoint form (`+0.835`).
**Is:** all three are the disjoint form. `\PREMISEOVERLAP` was defined in the preamble and used
nowhere; the overlapping value is now quoted in the Results, where it belongs as the quantity the
disjoint repeat was run against, together with the share that makes the repeat necessary.

The fix required no new computation on the tumour data. The per-pair table
`results/zhao_gbm/premise_mean_vs_compartment.csv` has carried `cos_myeloid_response` since it was
written, and the panel computes its own rho from the column it plots, so changing the column
changed the printed value to `+0.835` without a digit being retyped. The existing axis limits
`(-0.2, 0.95)` already contain the myeloid range (`-0.106` to `0.810`), so the diagonal, the equal
aspect and the limits are untouched. `figures/fig7` is no longer built as a figure of its own
(`build_all.STEMS` covers 1 to 5), so the edit reaches only Figure 4f.

Both the panel docstring and the geometry wrapper now name the constraint, because the failure mode
is a one-word edit away in either file.

## R68. The Source Data file shipped for Figure 5c,d contained a run the panel itself retracts

`figures/source_data/fig5cd_structure_diagnostics.csv` held `real 0.046` against predictors near
`0.009`, which is the "predictors collapse subpopulation variance, 5.1x collapse" claim that
`figures/fig5/fig5c.py`'s own docstring retracts, plus a predictor named `scgen_cpa_linear` that
appears in no file under `results/`. The panels had moved to the faithful `cells` synthesizer
(`0.138 / 0.142 / 0.462`); the shipped table had not. Nature sends Source Data to reviewers, so a
reviewer downloading this table would have received numbers reproducing neither panel nor text.

**Root cause, and what changed.** The file sat in `sync_source_data.DERIVED`, a category whose
check is `if not (REPO / rel).exists()`: it verifies the parent is on disk and never looks at the
view's contents, so content drift in a derived view could not fail the gate. A third category,
`GENERATED`, now holds views that have a builder; they are rebuilt from their parents on every sync
and drift-checked like a MIRROR. `fig5cd_structure_diagnostics.csv` moved there with a builder that
selects the rows the two panels plot and joins the induced-response cosine, so the table now
reproduces both panels and both of the Results sentences that quote them. Run against the old file,
the new gate fails with `DRIFTED`, which is the behaviour that was missing.

`DERIVED` still exists for hand-built views with no generator; the rule is now to prefer
`GENERATED` whenever a builder can be written.

## R69. The Discussion attached a by-construction claim to a model that was never run

Discussion: "a model that applies the same perturbation effect\cite{ref4,ref5} to every cell can
preserve heterogeneity in the starting population yet, by construction, cannot generate
state-specific differential responses." `ref5` is CPA, and
`results/exp14_nonadditive_predictors/gate1_within_context.json` records `"cpa_real": {"status":
"did not run"}`; CPA is not measured, described or limited anywhere in the submission. `ref4` is
scGen, of which Methods states the opposite: "Because the decoder is nonlinear ... the
induced-response cosine is not pinned to 1 by construction as it is for the linear-latent control",
and Results measures it at 0.972 rather than 1.000.

**Is:** the citations are dropped from the by-construction sentence, which now applies to the
strictly additive predictors actually measured, followed by a sentence naming what was measured for
the deployed latent-arithmetic model. `ref5` remains cited in the Introduction, where it is a
forward-prediction reference and accurate.

## R70. Two attributions that contradicted their own source

- **honest and leaky cross-validation units were swapped.** Methods, "Reading the HIR-Bench
  verification panels": "Under the leaky cross-validation unit, the latent-utility feature set
  reaches a pooled out-of-fold AUC of 0.400."
  `results/exp11_hir_benchmark/phase_grid_predictability_2x2.csv` assigns `0.400` to
  `label_determining_cells` (28, the honest unit) and `0.640` to `instance_grid_id_LEAKY` (672).
  The sentence then explains the number by "the benchmark has 28 label-determining parameter
  cells", i.e. it explains the honest unit while naming the leaky one, and `figures/fig4/fig4f.py`
  draws the matrix the right way round. Now reads "Under the honest, 28-cell cross-validation
  unit ... 0.400 (0.640 under the leaky, 672-instance unit)".
- **Tahoe recoverability is scored on drug identity, not on state labels.** Methods says so
  plainly: "Tahoe recoverability was evaluated using drug identity rather than the state labels
  used above." The Figure 5 caption nevertheless opened panels h to k with "All three requirements
  measured on Tahoe-100M", and panel i's entry with a bare "Recoverability", while the requirement
  is defined on state structure and Fig. 5e measures it that way. Both the caption and the Results
  sentence now name the construct. This paper's argument is that an evaluator must not be
  mismatched to what it evaluates; using one word for two different recoverabilities on the figure
  carrying that argument is the version of the error a reviewer would quote back.

## R71. A Supplementary heading asserted the opposite of its own paragraph

Supplementary Note 2 carried `\paragraph{The mechanism-recovery null is not a power artefact.}`
over a body that concludes "the mechanism-recovery comparison is not adequately powered, so its
null is an absence of evidence rather than evidence of absence", with an achieved power of 0.06
against 1.00 for the minority-state comparison in the same stratum. The heading described the
minority-state half and denied the mechanism-recovery half. A reader skimming headings would take
away the reverse of what the paragraph establishes. Retitled to name what the paragraph does,
"Power of the two task-proximal comparisons in the highest-divergence stratum". No number, no
verdict and no hedge changed; the asymmetric reading the paragraph already states is the correct
one and stands.

## R72. Figure 2 marked a cosine baseline built in this study as a published one

`fig2_style.SCORERS["cmap_cosine"]` carried `label="CMap cosine", published=True`, and panel a
prints `dagger published baseline` under the glyph that flag draws. The canonical L1000
connectivity score is WTCS, which is the row above and is genuinely published; this row is a cosine
applied to the same mean signatures, and the main text has always been careful about it ("the
implemented CMap-style cosine", three times). The figure was less careful than the text it
illustrates, and the equivalence result the figure supports is exactly the claim a reviewer would
check the provenance of.

**Is:** `label="CMap-style cos.", published=False`, so the dagger marks only WTCS, and the caption
key now says which score is the published one and what the other is. Typography and overlap gates
pass unchanged.

## R73. A retracted decision-level table was sitting unmarked beside the live results

`results/upgrade/class_c_viability.csv` carries the schema a decision-level external-utility
analysis would have (`dart_top1_drug`, `dart_top1_auc`, `mean_top1_drug`, `mean_top1_auc`,
`most_potent_drug`), which is exactly why it is dangerous: it looks finished. It is the output of
`analysis/class_c/class_c_experiment.py`, retracted by R14a, which ranks `score_energy` ascending
although that function returns a similarity, so the population scorer's rank-1 candidate in the
file is the population farthest from the query. The signature is visible in the data:
`dart_top1_drug` is effectively query-independent, naming Panobinostat in 142 of 152 rows against
27 to 32 distinct picks for `mean_top1_drug`.

The retraction lived only on the producing script and in this ledger. Nothing named the CSV, and
nothing next to the CSV warned a reader who opened it directly. Moved to
`results/upgrade/_retracted/` with a README stating the sign error, the dose and platform pooling,
and what to use instead; the producing script now writes there too, so a re-run cannot replant it
among the current tables.

## R74. NOT FIXED, carried forward from this pass

- **The macro layer is mostly dead.** The preamble declares that every number is a macro with a
  provenance comment, and 88 of the main text's 104 macros are never used while the same values are
  hand-typed in prose: `\HITENERGY` (0.837), `\REGRETALLP` (1.6e-66), `\CLASSBMED`, the whole
  `TAHOE*` block. The hand-typed values are currently correct, so this is a drift risk rather than
  an error, but it is the seam R67 came through: a number that lives in two places will eventually
  disagree, and the mechanism built to prevent that is not connected.
- **The Fig. 2 headline task is described as plain source identification.** Methods,
  "Observed-population retrieval", says the library contains "the perturbation that generated the
  query response together with competing perturbations". In all three exp08 tasks the query is a
  constructed two-mode alpha-mixture and the ground truth is `covers-both`, a held-out re-mixture at
  the same alpha; `majority-only` and `minority-only` are also candidates and are scored as misses.
  For the controlled task those two are single-class HDAC and JAK populations, and for the
  crossline and Frangieh tasks they are the same perturbation observed in one context. No sentence
  in either .tex discloses the construction. This needs a Methods rewrite, not a one-line edit, and
  it runs in the direction that flatters the headline gap, so it is recorded here rather than
  patched quietly.
- **No cluster-level resampling on the n=765 and n=600 paired tests.** A patient-level cluster
  bootstrap exists (`analysis/natural/gate2_uncertainty.cluster_bootstrap`), as do leave-one-cell-
  line-out CV in exp16, `(alpha, conflict)`-grouped CV for HIR-Bench and exp13 seed stability, but
  none is computed on these two statistics, whose p-values are formed as if queries were
  independent. The estimator is reusable with the cluster key changed to `heldout_drug` (144 and
  130 clusters).

---

## R75. R42's own overlap figure was wrong, and understated the overlap it was conceding

**Was:** R42 above, and with it `\PREMISESHARE` in the manuscript preamble, the Results sentence it
fed, `analysis/natural/zhao_premise_disjoint.py`, `figures/fig7/fig7_natural.py`,
`docs/phase2/FINAL_FIGURE_NUMBER_LEDGER.md` and `analysis/tahoe_pilot/README.md`: "the mean
signature contains 43% of the malignant cells it is being asked to rank", sourced as 41,314 of
96,225 called cells.

**Is:** the malignant compartment contributes exactly **half** of that mean signature, by
construction. `analysis/natural/zhao_two_gates.py:127-128` builds it as
`mean_a = 0.5 * (a[malignant] + a[myeloid])`, an equal-weight average of two compartment deltas.
It is not a cell-weighted mean over called cells at all.

**Why 43% was wrong twice over.** The denominator 96,225 pools **three** compartments and includes
23,233 oligodendrocytes, which never enter this signature. And no cell-count reading gives 43%
either: malignant/(malignant+myeloid) is 56.6% of all called cells, 55.0% of the drug-treated cells
across all ten patients, and 60.2% of the drug-treated cells of the four patients
(PW030/PW032/PW034/PW036) this analysis actually uses.

**Direction of the error.** R42 existed to concede how much of the +0.878 was arithmetic. Every
correct reading of the overlap (50% by construction, 55-60% by cell count) is **larger** than 43%,
so the concession was understated. The load-bearing number is unaffected: the manuscript's argument
rests on the disjoint +0.835, which shares no cells and is what Fig. 4f draws.

**Also wrong:** `zhao_premise_disjoint.py` attributed the 43% to Supplementary Table 3. That table
is the GDSC2 functional-similarity sensitivity analysis and carries no compartment counts; the
count source is `results/zhao_gbm/compartment_validation.csv`.

**What changed.** `\PREMISESHARE` is retired from the manuscript preamble with a note forbidding
its reinstatement at 43%; `\PREMISEOVERLAP` (+0.878) moved from Results into the Methods paragraph
that already explains why the disjoint comparison is the reported one, now with the correct
half-weight reason; the Results paragraph goes straight to the disjoint statistic. The two Python
files and the Tahoe README carry the corrected wording. R42's text above is left as written, since
this file is a record of what was believed when.

**Not revisited here:** the Tahoe comparison quoted inside R42 (26% overlap, +0.064 of rho) was not
re-derived in this pass and may carry the same class of error.

---

## R76. A preflight audit, and the seven things it changed

An eight-dimension preflight audit (front-half alignment, figure/legend sync, Methods and SI
anchoring, terminology, statistical reporting, claim-source support, data availability, and a
reviewer-side rejection pass), each finding adversarially re-checked against the files before it
was accepted. 75 findings proposed, 34 survived, 7 fixed here. Claim-source support returned
nothing: the three-stage citation audit of 2026-09-06 holds.

**Figure 3's legend declared the wrong estimator for two panels.** The figure-wide preamble said
"Points, medians" and flagged its one known exception (panel c, "diamonds, dataset means").
Panels d and e were unflagged exceptions: `fig3c.py:234` and `fig3d.py:166` both compute the
drawn point with `stat=np.mean`. Recomputed from the modules' own loaders, panel e's four
quartile medians are -0.0062, 0.0000, 0.0000 and 0.0000 against the drawn means -0.0497, -0.0391,
-0.0158 and +0.0142, because 17 to 32% of queries in each quartile score identically under
mechanism-of-action recovery. The paper reports the same quantity as a MEDIAN everywhere else
(`\CLASSBMED` = 0.000, Fig. 3a,b), so a reader comparing panel e's -0.050 against panel a's 0.000
was comparing a mean to a median without being told. The preamble now names both exceptions and
the d and e entries carry both summaries.

**Two of the three population scores declared for the Tahoe task were reported; the third was
not, and it has the opposite sign.** Methods specify "MMD and sliced Wasserstein as secondary
variants". Both were computed and shipped in `results/phase2_transition/phase_a/`. MMD reproduces
energy (MRR 0.975, +0.0101 over the magnitude-aware mean); **sliced Wasserstein reaches 0.922 and
sits below both mean baselines**, -0.0230 against direction-only (CI -0.0301 to -0.0166) and
-0.0431 against the magnitude-aware mean (-0.0509 to -0.0359). Neither interval covers zero. The
Results sentence asserts a property of the population RUNG ("the three scoring rules of Fig. 1a
again form a ladder"), so reporting only the two variants that clear the baseline made that
assertion broader than the evidence. Both are now reported.

**The n=18 premise correlation is 15/18 one patient, and only the neighbouring result said so.**
`results/zhao_gbm/premise_mean_vs_compartment.csv`: PW030 contributes 15 pairs, three other
patients one each. rho = +0.835 overall and +0.804 within PW030 alone. Neither .tex contained the
string "PW030". The SI discloses the same dependency for the recoverability gap at line 416 ("30
of the 36 splits contributed by a single patient") and even reports a leave-that-patient-out
check, so the disclosure was present for one natural-tissue result and absent for the other, and
the absent one carries the stronger conclusion. Both reporting sites now state it.

**Two Methods sentences contradicted each other on control referencing.** Preprocessing said the construction "makes the comparison ... differ in the response
structure retained rather than in the underlying perturbation or control definition"; the
baselines paragraph forty lines later said "the population distances are computed on normalized
expression rather than on control-referenced responses, whereas the mean-signature scores subtract
the matched control mean". `rankers.py:76-78` passes `control_P`/`control_Q` to both mean scores
and neither to `score_energy`.

  The first repair of this was itself wrong, in both directions, and an adversarial pass over the
  edit caught it. **The energy distance and the mean L2 are exactly invariant to subtracting a
  control that a query and its candidates share** (verified: both scores identical to 8 decimal
  places under a shared shift; only the cosine changes). So wherever the control IS shared there is
  no asymmetry to concede at all, and the first repair surrendered the controlled-comparison claim
  across the whole paper. It was also stated as a global property while being false for the Tahoe
  arm, where `phase_a_oracle.py:173,181` subtracts the source mean from BOTH the candidate bank and
  the target before every score. The sentence now states the invariance and scopes the exception to
  the two-context mixture task, which is the one place the candidate classes carry different
  matched controls (`tasks.py:253-256`) and therefore the one place the asymmetry has a numerical
  consequence.

  NOT the artifact it first looked like. The audit proposed that energy's Hit@1 advantage on the
  cross-line task IS this asymmetry, since energy ranks a single-mode candidate first 0 times
  against mean cosine's 538 of 1,350. Tested on the controlled task, where `tasks.py:133` passes
  one `pseudo_control` to every candidate and no between-line offset exists: the pattern holds
  there too (0.890 against 0.270, single-mode first 33 against 219). The concentration is the
  paper's own thesis, not a preprocessing artifact. Recorded so the test is not redone.

**The partial-observation p values treat 765 non-independent queries as independent.** Recorded in
R74 as unfixed and still unfixed as an analysis; what changes here is that the manuscript now says
so. The Statistical analysis subsection now states
that those P values and intervals are anticonservative, and marks the arm as an explicit departure
from the principle its own first sentence asserts.

  The decomposition took two attempts and both failures were the same one, asserting a count that
  had been inferred rather than read. "144 held-out drugs" counts the literal placeholder `batch`,
  which covers the 45 partial-library queries that hold out no single drug, as a drug. The verified
  reading: of the 765 queries, **720 hold out one of 143 drugs and 45 pool the unmeasured drugs into
  a single batch query**; the 600 on which mechanism recovery is scored come from 130 of those
  drugs, selected by split type and not, as first written, by whether a mechanism annotation exists;
  and the 765 rest on **420 distinct drug-by-cell-line contexts**, re-scored across 15 library
  fractions and 5 seeds, which is a stronger multiplicity than the drug clustering alone.

**Two released Source Data tables had drifted from the files their panels read.**
`fig2a_hit1_ladder.csv` held eight rows where the caption says nine scores, missing `mean_l2`
(0.7877), the magnitude-aware mean the whole figure is built around, and carried three stale
values including `global_energy` 0.8369, the **pre-repair V-statistic** reading.
`fig2d_alpha_crossover.csv` disagreed in exactly one of fifteen cells, K562 at alpha 0.9, and it
is the cell the panel's crossover reading depends on (0.35 released against 0.30 live, turning a
tie into +0.05). Both were classified DERIVED in `sync_source_data.py`, meaning existence-checked
and never rewritten, which is how they drifted. Both are GENERATED now, computed from their
parents by a builder and drift-checked like every other generated view.

**Formalism left the Results.** A display equation and the symbols lambda, mu, beta and K sat in
the Results, duplicating Methods "Connection between mean and population retrieval" (which carries
the same derivation in more detail) and the coverage-score paragraph. The Results state the two
relationships in prose and point to Methods. No claim was dropped, but the Fig. 1 caption still
carries beta and lambda and their in-text gloss left with the equation, so the two symbols are now
defined only in the Methods; that is open, below.

**Also fixed:** the Fig. 3j caption named "query-magnitude matching", a row the panel does not
draw and a score that is separately named and strongly positive elsewhere in the same figure
(`\MAGMATCHFUNC` = +0.232, Fig. 3h); Fig. 3k was cited before Fig. 3j, their only two citations;
the abstract's one quantified positive result quoted the 5:1 ratio without naming its baseline,
where the paper's own honest comparator gives 4:1; and the Discussion said the beyond-magnitude
component "consistently reached the ranking", which Fig. 2e was drawn to contradict.

**R74's second item is stale.** It records that no sentence in either .tex discloses the exp08
mixture construction. Methods now disclose it in full: the alpha mixture, the held-out re-mixture
at the same weight as ground truth, the two single-mode candidates and the 43-candidate library.

**The adversarial pass over these repairs** returned 3 blocking problems, all of them in the two
edits that stated a decomposition rather than reading one, plus the Fig. 3 preamble sweeping panel
c's 239 raw task dots and panel i's 103 per-query markers into a claim that every non-exception
point is a median, a causal "because" that the first number it introduced contradicted (a 17.5% tie
atom does not force Q1's median to zero; its negative mass of 50.6% is what puts the median at
-0.0062), a caption that named three of panel j's four rows and dropped the one showing the
correctly specified mean baseline does NOT invert, and an SI implementation spec that does not
reproduce the two Tahoe numbers this pass published (200 projections and one library-fitted
bandwidth, against the SI's 128 projections and pooled multi-scale). All are fixed above.

**Still open from this audit,** not fixed here: the Fig. 1 caption gloss for beta and lambda; the
energy distance's V-statistic row on the Tahoe task (+0.0006, CI -0.0019 to +0.0028 over the
magnitude-aware mean), deliberately not added to the main text because it is the same score under
an estimator this paper has argued is biased, not a third score family, but it is a judgement call;
`figures/source_data/README.md` and `fig2d.py`'s docstring, both stale after the DERIVED to
GENERATED move; Supplementary Table 1's energy row, which still says "control-referenced"; and 27
further verified findings of Medium and Low severity,
including the number-duplication surface (19 caption/Results literal pairs in the main text and 34
main-text macro values hard-coded in the SI, all currently in agreement and nothing keeping them
so) and 48 of the 112 macros defined and never used.
