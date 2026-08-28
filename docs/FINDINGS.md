# Findings

The detailed version of the results, moved out of `README.md` so that the README can stay
focused on installing and reproducing. Nothing here is abridged: this is the text that used to
sit on the front page, including the retraction notes.

The authoritative statement of all of this is the manuscript
(`manuscript/latex/PopRetrieve_manuscript.tex`). Every number below names the results file it
comes from, and [`../CORRECTIONS.md`](../CORRECTIONS.md) records every value this project has
revised or withdrawn.

---

**If you build or evaluate distribution-aware methods for single-cell perturbation data, this
repository is here to answer one question you probably cannot answer from your own benchmark:**

> ### Is my reported gain real, or does it only exist because I graded it with a metric that measures the same thing my method optimises?

We ran that check on ourselves, on three datasets and one synthetic benchmark, and the answer was
uncomfortable enough to reorganise the whole project around it.

## The finding, in one table

Same candidate rankings. Same scorer. Same queries. **Only the judge changes.**

| who is asked | what the distributional score does |
|---|---|
| its own distributional objective | **far ahead**: Hit@1 0.837 against 0.388 for the mean-signature incumbent |
| mechanism-of-action recovery | **gone**: MoA-nDCG gain of −0.037, and 41% of queries get *worse* |
| an external functional oracle (GDSC) | **wins**, ρ +0.276 against +0.083, but a scalar comparing no distributions reaches +0.232 |
| the same proteins, same cells, scored as a *mean* instead of a distribution | **loses**, +0.146 against +0.242 |

That last row is the one to take away: two external, blind, independent criteria built from
identical material hand victory to opposite methods, purely by their own statistical form.

## What you can take from here

| you want to | go to |
|---|---|
| **check whether your own gain is circular** | [`analysis/diagnostics/`](../analysis/diagnostics/): four probes, one command, each falsifying a specific objection |
| **decide if distribution-aware retrieval is worth it for your data** | [the three conditions](#when-does-distributional-retrieval-help-three-conditions), measurable before you build anything |
| **avoid the four mistakes we made** | the controls below, each of which caught an error of ours |
| **reproduce a number from the paper** | [Reproducing the paper](../README.md#reproducing-the-paper): one script per claim |
| **see what we got wrong** | [`CORRECTIONS.md`](../CORRECTIONS.md): 45 entries covering 39 distinct corrections, two of which retract mechanisms we had asserted |

### The four controls, if you read nothing else

1. **Match the oracle to the task.** A similarity retriever graded on absolute potency is being
   asked a question it was never posed, and it will fail in a way that looks like a finding. We
   drew a conclusion from exactly that, and had to withdraw it.
2. **Beat the magnitude scalar.** Rank candidates by how closely their response *size* matches the
   query's, comparing no distributions at all. If your method does not beat that, you have not
   shown the distribution is doing the work. Ours does not, significantly.
3. **Vary the *shape* of your external oracle, not just its identity.** External, independent and
   invisible to the method is not enough, as the table above shows. Compute your criterion in at
   least two statistical forms and report both.
4. **Do not let a benchmark you built decide a claim about biology**, and check that the two things
   you are comparing are the same question. Our own constructed mixtures distorted the biology in
   both directions at once, and both distortions happened to flatter the premise we were testing.

## What this repository is not

**It is not a proposal for a better drug-ranking method.** The population-to-population retrieval
scores here are the *instrument*: one family of scores whose rankings can be re-graded under
criteria of increasing independence without being recomputed. They ship as **PopRetrieve**; the name
refers to the implementation, not to a contribution, and to what the study finds: the rankings hold
still and the evaluation is what shifts.

The honest one-line summary of the whole thing:

> *Distributional information in this domain is real, and much smaller than objective-aligned
> evaluation makes it appear.*

---

## The one-paragraph idea

Given a query cell population `Q` and candidate response populations `{P_d}`, pick

```
d* = argmin_d  D(P_d, Q)      # distance in DISTRIBUTION space, not mean space
```

The incumbent, cosine of mean-delta signatures ("mean-out" retrieval, and,
provably, the CMap connectivity score), is the **degenerate zero-spread special
case** of this: it discards every within-population subpopulation. When drug
responses split a population into diverging subpopulations, the mean match is
majority-biased and can miss the drug that actually covers all subpopulations.
The object under audit is the **retrieval / ranking decision layer**, *not* another
perturbation predictor or generator.

> An earlier version of this paragraph also claimed a **divergence-gated boundary**
> as a contribution. That claim is withdrawn. Measured rather than assumed, all three
> datasets clear the ≲0.9 divergence criterion, including the negative control on
> which the mean incumbent wins, so the gate has no discriminative power on real data
> (Result 3, and [CORRECTIONS.md](../CORRECTIONS.md) R3).

---

## Key results (the honest version)

**1. Under an objective-aligned energy proxy, distributional retrieval looks far
ahead of the mean.** Hit@1, **unweighted macro-mean over the 7 (task × setting)
cells of three retrieval tasks** (controlled SciPlex3, cross-line, Frangieh;
`results/exp08_signature_baselines/summary.csv`):

| scorer | Hit@1 (macro) | Hit@1 (query-weighted) | what it is |
|---|---:|---:|---|
| **global energy** (distributional) | **0.837** | 0.887 | K=1 population-to-population distance |
| pca-dist (distributional) | 0.778 | 0.817 | distance in PCA latent |
| coverage-mean (distributional) | 0.773 | 0.802 | subpopulation-matched aggregate |
| coverage-worst (distributional) | 0.589 | 0.595 | worst-subpopulation aggregate |
| cmap-wtcs | 0.463 | 0.499 | rank-based connectivity |
| **mean-cosine** = **cmap-cosine** | **0.388** | 0.421 | the mean-signature incumbent |

The two aggregations differ because the cells carry 12-fold different query
counts (controlled n=30 each, cross-line n=360, Frangieh n=90). The direction of
the result is the same under both, but the macro-mean is the reported one and is
labelled as such.

**Report the counterexample too:** on Frangieh, the only *natural* real dataset,
**mean-cosine (0.600) beats global energy (0.578)**
(`summary_by_task.csv`). The macro-mean hides this; the gain above is carried by
the constructed and semi-constructed mixtures.

`mean_cosine` and `cmap_cosine` are **algebraically identical** (both 0.3885, and
numerically identical to within float32 rounding): both compute the cosine of
mean-delta signatures. That equivalence is itself one of the paper's points.

**2. Under an oracle-independent metric, the gain largely evaporates.** When the
same rankings are judged by criteria that do *not* share PopRetrieve's objective, a
mean-to-minority coverage proxy and MoA-annotation nDCG, the advantage is either
negligible or reversed. From the true-divergence stratification
(`results/exp17_true_divergence_subset/divergence_stratified.csv`; PopRetrieve method =
`coverage_worst` throughout):

| oracle-independent metric | n | lowest-divergence Q1 | highest-divergence Q4 | verdict |
|---|---:|---:|---:|---|
| minority-state coverage (median gap) | 765 | +0.0009 (q=6e-7) | +0.0018 (q=1e-14) | **real & divergence-monotone, but negligibly small** |
| MoA-nDCG@10 (median gap) | 600 | **−0.030** (q=6e-5) | 0.000 (q=0.57) | **no advantage anywhere; significantly WORSE at low divergence** |

MoA-nDCG has n=600, not 765: it is **undefined** for the `leave_MoA_out` and
`partial_library` splits (165 queries, 21.6%), where the whole MoA class is
removed from the library. Those rows are NaN and excluded. (Before 2026-07-12 they
carried a `-1` sentinel that was differenced as if it were a measurement,
`(-1) - (-1) = 0`, so 165 structural zeros were pinning every stratum's median at
exactly 0.000. See `exp16_common.mask_undefined`.)

Q1's gap is now significantly **negative** on both the median (−0.030) and the
mean (−0.082): at low divergence PopRetrieve actively *hurts* annotation recovery. The
coverage effect is real and mechanistically consistent (it grows monotonically
with true response divergence) but **far too small to be practically useful**; the
annotation-recovery effect is null at high divergence and severely underpowered
(Q4 would need n≈20,800 for 80% power).

**3. The advantage is gated, but the gate is not a gate.** The coverage gain grows
monotonically with true response divergence, yet it is **BH-significant even in Q1**,
the lowest-divergence stratum (q=6e-7), where the theory says it should not appear.
Q1's queries are not "below the gate": their state-response cosines already span
[−0.55, +0.62], i.e. all of them clear the ≲0.9 divergence criterion.

**The divergence axis cannot separate the positive anchor from the negative control.**
Measured rather than assumed (`results/exp02_divergence_gate/dataset_positions_on_gate.csv`):

| dataset | measured typical cross-cosine | clears the ≲0.9 gate? | who actually wins |
|---|---:|:---:|---|
| cross-line (SciPlex3) | 0.032 | yes | **PopRetrieve** |
| **CD34+ lineages** | **0.186** | **yes** | **mean-cosine** |
| Frangieh immune | 0.709 | yes | mean-cosine (0.600 vs 0.578) |

CD34+ is the paper's honest negative control, and it sits at cosine **0.186**, i.e.
strongly divergent and comfortably inside the gate. The gate therefore predicts that
PopRetrieve *should* win there. It does not. Two of the three datasets clear the gate and
still favour the mean incumbent, so the ≲0.9 divergence criterion has no
discriminative power on real data. This is an independent confirmation of the gate
failure that exp16 finds directly (the gate's reliability axis is *anti*-correlated
with true divergence, Spearman rho = −0.21, p = 3.8e-9).

> **Retraction.** This table used to be three typed-in literals in
> `exp02_divergence_gate.py` under a comment reading "from probes", and no probe ran.
> It placed CD34+ at cosine **0.95** ("below gate, no advantage"), which made the
> negative control look like a *confirmation* of the gate. The repository's own exp04
> measures 0.186 on the same cells. The table is now computed, and a missing input
> raises rather than being replaced by a plausible number.

The Phase-1 headline numbers pass a **35/35 consistency re-check**
(`results/all_existing_results_recomputed.csv`). This is a re-read of the cached
experiment CSVs against the constants in `src/experiments/common.py`, **not** an
end-to-end re-execution: `recompute_all.py` runs no experiment. Run
`scripts/run_all_core.sh` for that.

**Bottom line.** The value of this comparison is *diagnostic*: it makes the gap between
objective-aligned and oracle-independent evaluation measurable, and it shows that a
distributional signal exists while its independent utility is limited. Treat "the
distributional score beats the mean" as true *only* under the proxy that score optimizes.

---

## The four-probe diagnostic protocol

The reusable core of the PopRetrieve audit is a small, dependency-light module
([`analysis/diagnostics/dart_diagnostic.py`](../analysis/diagnostics/dart_diagnostic.py))
that answers one question for any distributional retrieval method: **is a null
result a REAL null, or an implementation artifact** (an unfair comparison, a
broken metric, low power, or a hidden confound)?

| probe | falsifies the objection | on PopRetrieve | source |
|-------|-------------------------|---------|--------|
| `translation_invariance_probe` | "raw-vs-delta is an unfair comparison" | energy is translation-invariant, rho = 1.0 | `upgrade/protocol_validation.json` |
| `subsampling_power_probe` | "the null is just low statistical power" | energy CV at n=120 is **3.8%** | `upgrade/protocol_validation.json` |
| `metric_blindspot_probe` | "the reported metric measures what it claims" | mean-based coverage is blind, rho = -0.19 vs cell-level | `upgrade/protocol_validation.json` |
| `magnitude_confound_probe` | "the apparent positive is real" | the positive is real but is **not distributional**: on the semantically matched functional oracle energy reaches **+0.276** against **+0.083** for the correct incumbent, yet a query-dependent scalar comparing no distributions reaches **+0.232**, and partialling that channel out leaves energy **+0.097** | `upgrade/class_c_functional_oracle.json` |

(The 6.3% figure previously quoted here is the CV of the *same-drug self-distance*
at n=120 in `upgrade/subsample_power_results.csv`, a different quantity from the
probe's own output. The probe reports 3.8%.)

```bash
PYTHONPATH=src python analysis/diagnostics/protocol_validation.py   # reproduces all four verdicts
```

Applied to PopRetrieve, all four probes point the same way: the oracle-independent null
is **real**, and the confirmed weaknesses had been *over*-crediting the method,
not under-crediting it.

---

## When does distributional retrieval help? Three conditions

Distributional retrieval can only beat the mean when **both** gates are open:

1. **Differential response (Gate 1).** The candidate populations must contain
   subpopulations that respond in **different directions**. Current predictors do
   not produce that. Crucially, **they do not fail by collapsing structure**, which
   is what an earlier version of this README claimed:

   | candidate population | subpop-variance ratio | induced response cosine `cos(d_maj, d_min)` |
   |---|---:|---:|
   | **real** (the population PopRetrieve actually ranks) | **0.138** | **0.014** |
   | predicted, average-effect | 0.142 | 0.186 |
   | predicted, latent (scGen-family) | 0.462 | 0.239 |
   | predicted, nearest-neighbor | 0.142 | 0.366 |

   (`results/exp09_structure_diagnostics/`, n=96 per row.) Predicted populations
   retain **as much** baseline structure as real ones. What they lack is
   *divergence*: real subpopulations respond near-orthogonally (cosine 0.014),
   predicted ones respond in largely aligned directions. This is not a tuning
   problem, it is **analytic**: average-effect, nearest-neighbor, scGen and CPA are
   all *additive* models that add **one** delta vector to **every** cell, so the two
   subpopulations' response deltas are identical by construction and the induced
   divergence is exactly zero (pinned by
   `tests/test_predictors_smoke.py::test_additive_predictors_induce_zero_response_divergence`).
   A distributional scorer has nothing differential to exploit no matter how much
   baseline structure survives.

   > **Retraction of the old number.** The previous claim, "predicted populations
   > have a ~5x lower subpopulation-variance ratio than real data (0.046 vs 0.009)",
   > was an artifact of our own code on **both** sides. Predicted populations were
   > synthesized as `control_mean + delta + iid Gaussian noise`, which is unimodal by
   > construction, so 0.009 is simply the **null value** of a k-means k=2
   > between/total ratio on an isotropic cloud (its isotropy index is 0.998). And the
   > "real" reference, 0.046, was a *single-context* population, not the alpha-blended
   > candidate the scorer actually ranks. Both are fixed; see
   > `src/baselines/population_synthesis.py`.

2. **Recoverability (Gate 2).** That structure must be resolvable by the decision
   layer. The question is not whether clustering succeeds but **why it fails**, and
   the two answers have opposite implications: if the information is absent from the
   representation no method can help, whereas if it is present and only the
   unsupervised step cannot reach it, the bottleneck is an algorithm and is solvable.
   Separating them needs a **supervised ceiling**, which is scored in the same unit
   (best-permutation accuracy, label matching free for every method).

   | setting | ceiling | best unsupervised | gap |
   |---|---:|---:|---:|
   | constructed K562 mixture, drug classes pooled | 0.692 | 0.674 | 0.018 |
   | constructed K562 mixture, one drug vs one drug | 0.879 | 0.837 | 0.042 |
   | **patient glioblastoma, one drug vs one drug** | **0.923** | **0.777** | **0.117** |
   | **Tahoe-100M plate 3, 960 drug pairs, 48 lines** | **0.853** | **0.611** | **0.157** |

   In a real tumour the information is **present** and off-the-shelf clustering does
   not reach it, so the limit is **algorithmic, not informational**. That reversed an
   earlier reading of this repository twice over; see `CORRECTIONS.md`. The Tahoe row
   replicates it at 26x the sample size with no method family rescuing the partition
   (k-means 0.592, Gaussian mixtures 0.582, Leiden 0.563, all near the 0.5 null).

   > **Superseded.** This section previously reported "no unsupervised clustering
   > method succeeds (best median ARI 0.106)". That number is a nine-column sweep of
   > only 6-7 distinct algorithms, all centroid- or Gaussian-based, with the best
   > median taken over the 4 of 20 seeds where its column won. Clustering failure
   > alone is consistent with the information being absent *and* with its being
   > present but unreachable, which is exactly the ambiguity the ceiling resolves.
   > The old sweep is kept as Extended Data Fig. 3a for completeness.

3. **Decision relevance (Gate 3), proposed rather than measured as the first two are.**
   The differential response must change **which candidate is preferred**, over and
   above what the mean already ranks. It is the condition that explains why opening
   the first two is not enough. Ranking one compartment's response similarity by
   another's, on **disjoint** cells:

   | material | partition | Spearman |
   |---|---|---:|
   | patient glioblastoma | myeloid -> malignant | **0.835** |
   | Tahoe-100M plate 3, 44 lines | G1 -> G2M | **0.841** |
   | Tahoe-100M plate 3, 45 lines | control-state k=2 | **0.778** |

   The bulk already ranks most of what the minority does. It is **not universal**:
   under the control-state partition 2 of 45 contexts fall below 0.5 (lowest 0.236),
   and those are the contexts where a distributional score should pay off. A
   condition that is usually met and sometimes not is a condition; one that is always
   met would have been a verdict.

Both gates are **open** in patient tissue and the advantage still does not appear, so
they are **necessary, not sufficient**. On the constructed mixtures both are closed,
which is why the observed-population advantage (Result 2) is an upper bound there
rather than an operating point.

**Class C (`analysis/class_c/`): the distributional gain is real, and a scalar reproduces it.**

Two independent external oracles, with disjoint failure modes. Neither is visible to any scorer.

**Oracle 1, GDSC functional similarity** (`class_c_functional_oracle.py`). Not absolute potency:
the rank correlation of two compounds' dose-response AUC profiles across the 966 GDSC2 cell lines
that remain once the three SciPlex3 lines are excluded, so it is measured out of context. 103
leave-one-drug-out queries at 10 uM. Median Spearman rho:

| ranking of candidates | performs retrieval? | rho |
|---|:---:|---:|
| potency match (needs the query's own AUC; diagnostic only) | no | **+0.399** |
| inverse-magnitude fixed ordering (query-INDEPENDENT) | no | +0.330 |
| **energy (distributional retrieval)** | yes | **+0.276** |
| mean cosine, no control subtraction | yes | +0.241 |
| **response-magnitude match (query-dependent SCALAR)** | no | **+0.232** |
| mean cosine, control-subtracted (correct incumbent) | yes | **+0.083** |

Energy beats the correctly specified incumbent threefold. But a query-dependent scalar that
compares **no distributions at all** reaches +0.232; energy beats it on only **62/103** queries
(Wilcoxon p = 0.073, itself anticonservative); and partialling that magnitude channel out leaves
energy with **+0.097**. The gain is real and almost none of it is distributional.

> **RETRACTED.** An earlier version graded these rankings against **absolute potency** and
> concluded that retrieval is anti-aligned with therapeutic utility (energy -0.520; a magnitude
> scalar +0.692 winning 103/103). That oracle is **semantically mismatched**: a similarity
> retriever handed a weak query *should* return other weak drugs, and potency is largely driven by
> response magnitude, so a magnitude scalar is near-guaranteed to win. The comparison survives only
> as a confounder audit (`class_c_magnitude_control_v2.py`), which is where the magnitude channel
> was found: energy *distance* tracks candidate magnitude at rho = +0.791. See `CORRECTIONS.md` R15.

**Oracle 2, surface protein** (`class_c_protein_oracle.py`). Frangieh Perturb-CITE-seq measures RNA
and 24 surface proteins in the **same cells**, barcode-for-barcode. The retrieval score sees only
RNA; the oracle is the cosine of CLR-normalized protein responses (isotype controls dropped). Same
controls, and the same question: does the distributional score beat the scalar? Energy reaches
**+0.529** against the mean's **+0.334** under a distribution-shaped protein oracle, and the
ordering **reverses** to +0.146 against +0.242 when the same proteins in the same cells are
collapsed to a mean before scoring. Two external, blind, independent criteria built from identical
material hand victory to opposite methods purely by their own statistical form
(`analysis/class_c/oracle_shape_test.py`).

That is the sharpest result here, and it is why the manuscript's third recommended control is
**vary the shape of your external oracle, not just its identity**: compute the criterion in at
least two statistical forms and report both, and if a method wins only under the form that matches
its own objective, say so.
