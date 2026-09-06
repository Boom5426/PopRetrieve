# Post-repair master results: the single source of truth for every reissued number

Phase 6A. Not an experiment. This is the ledger the manuscript is edited from: every number that
depends on a population scorer, recomputed under the correct estimator, sorted into the four
categories the plan fixes. After this point, a number that is not in this table and not in
`results/` is unsourced.

Backing tables: `results/estimator_audit/` (`arm_comparison_full.csv`, row-keyed;
`reissue_ledger.csv`; `manuscript_macros.csv`). Two complete arms of the legacy suite, identical in
code, data and seeds, differing only in `POPRETRIEVE_ESTIMATOR`.

**Scale: 129 files, 125,903 row-keyed comparisons.** One step failed identically in both arms
(`exp_nonadditive_gate1.py`, optional `scgen` absent), so it is uncovered rather than changed.

---

## Category D: blocked. **Now empty.**

The GDSC2 workbook was the only blocker. It was retrieved from the Sanger release archive
(`GDSC_release8.5/GDSC2_fitted_dose_response_27Oct23.xlsx`, 21,330,376 bytes, sha256
`f950a702...c07560`; GDSC1 also, 29,353,210 bytes, sha256 `837b0686...56dafd`) and
`class_c_functional_oracle.py` ran to completion in **both** arms. Fig. 3h to 3k are no longer of
unknown status. They are Category B, below.

---

## Category A: must be updated in the main text

Moves larger than the precision the manuscript quotes, or with per-row sign flips.

### A1. Coverage scorers, everywhere they appear

The V statistic penalised candidates whose subpopulations are small, and coverage aggregates over
subpopulations. This is the single largest class of change in the audit.

| Result | V | U | change |
|---|---:|---:|---:|
| exp04 CD34 `coverage_worst` Hit@1 | 0.2049 | **0.4132** | +102% |
| exp04 CD34 `coverage_mean` Hit@1 | 0.3507 | **0.4271** | +22% |
| exp04 CD34 `coverage_worst` MRR | 0.3232 | **0.5155** | +59% |
| exp03 cross-line `coverage_worst` Hit@1 | 0.6636 | **0.8693** | +31% |
| exp01 `coverage_worst` Hit@1 | 0.6533 | **0.7300** | +12% |
| exp01 `coverage_mean` Hit@1 | 0.8567 | **0.7733** | -10% |
| exp11 phase diagram `adv_coverage_vs_mean` | 0.2384 | **0.4005** | +68% |
| exp11 phase diagram `coverage_worst` | 0.3102 | **0.4722** | +52% |

### A2. exp12 decision regret, Class A (n = 98): the ordering among population scorers reverses

| Method | V regret | U regret |
|---|---:|---:|
| `DART_coverage_worst` | **0.1813** (best) | 0.2365 (worst of the family) |
| `DART_coverage_mean` | 0.2109 | 0.2294 |
| `DART_energy` | 0.2688 | **0.2155** (best) |
| `DART_mmd` | 0.2630 | 0.2169 |
| `mean_l2` | 0.2651 | 0.2244 |
| `mean_cosine` | 0.4077 | 0.3928 |

Under V, worst-case coverage had the lowest regret and the manuscript features it on that basis
(`\REGRETALL`'s own source comment reads "Class A, worst-case coverage against mean cosine"). Under
U it is the **worst** of the DART family and plain energy is the best. **Any sentence that selects
`coverage_worst` as the representative population scorer has to be rewritten, not renumbered.**

Note that `mean_cosine`'s regret also moves, 0.4077 to 0.3928, although a cosine cannot depend on
the estimator. The reason is in Category C3.

### A3. Recommendation-mode regret reduction, per row

| Row | V | U |
|---|---:|---:|
| `DART_recommended` / `DART_energy` mean regret reduction | 0.1759 | **0.1954** |
| `DART_recommended` / `DART_coverage_worst` | 0.2677 | **0.1351** |
| `DART_recommended` / `DART_coverage_mean` | 0.2194 | **0.1277** |
| queries in `DART_recommended` mode | 621 | 627 |

### A4. Signature baselines

| Result | V | U |
|---|---:|---:|
| exp08 MRR | 0.7619 | 0.7744 |
| exp08 Hit@1 | 0.5920 | 0.6085 |
| exp08 nDCG@10 | 0.8153 | 0.8267 |
| exp08 median rank proxy | 2.046 | 1.899 |
| exp08 by-task Hit@1 | 0.5747 | 0.5868 |

### A5. Fig. 2c: the headline regret reduction is a quarter of its published size

Found 2026-09-03, when panel 2c's own geometry gate refused to draw: the median rule printed 0.86
printed points from the zero rule, against the 2.5 pt the panel requires for the two to read as two
rules. The gate was right; the claim had shrunk under it.

`coverage_worst` against `mean_cosine`, paired over all 765 queries:

| | V (published) | U (repaired) |
|---|---:|---:|
| median regret reduction | **+0.1183** | **+0.0311** |
| fraction of queries improved | **72.0%** | **56.2%** |
| Wilcoxon p | 1.6e-66 | 1.6e-12 |
| incomplete-library subset, median | +0.0872 | +0.0350 |
| incomplete subset, fraction improved | 68.5% | 60.0% |
| incomplete subset, p | 9.7e-14 | 6.0e-05 |
| range of the paired difference | [-1.09, +2.82] | [-2.22, +2.85] |

These are the macros `\REGRETALL` (+0.118), `\REGRETALLFRAC` (72%) and `\REGRETALLP` (1.6e-66),
each used in the main text. The direction of the claim survives and its size does not: 72% of
queries improved becomes 56%, which is close to a coin flip, and the median falls to a quarter.

The widened range is itself a consequence of the repair rather than of the data. The V-statistic's
O(1/m) bias is positive and roughly common to both scorers, so removing it widens the spread of
their difference; the left tail goes from -1.09 to -2.22.

**Two things must not be done here, and are recorded as not done.** The panel's 2.5 pt
median-clearance constant was not lowered to let the drawing pass, and the panel's protagonist was
not switched from `coverage_worst` to `energy`, whose median against mean cosine is +0.0566 and
would restore a drawable separation. Either would be choosing the setting that preserves the old
picture.

**Resolved 2026-09-03: the DRAWING changed, not the claim, the scorer or the gate.** `MED_CLEAR_PT`
stands at 2.5, `coverage_worst` stays the panel's protagonist, and the panel stays in the main
figure. What was retired is the composition that needed a median RULE standing clear of a zero
rule, which is a chart that can only work for a large effect. Panel 2c is now a paired-outcome
panel: the x axis is the query percentile, so the three outcome shares are read as x extents and
the bottom axis is drawn as three coloured segments of exactly those widths; the y axis is the
paired difference on a signed square root, which is monotone, applied identically to both signs,
and compresses the longer (positive) tail rather than the shorter one; and the median is a POINT
with its bootstrap interval and its value on a leader, so nothing depends on two rules resolving
from each other. `MED_CLEAR_PT` is still asserted, inverted: the panel checks that the retired
composition remains illegible, so that a change to the data or the estimator that would make it
legible again surfaces as a build failure instead of as a quietly worse figure.

The headline numbers are frozen at median +0.031 (95% bootstrap CI +0.017 to +0.049), 56.2% of
queries improved, Wilcoxon P = 1.6e-12, with the incomplete-library subset median +0.035 in the
caption. The caption calls this a modest advantage in response matching over directional mean
retrieval, and explicitly not a strong population-specific gain; what survives once magnitude is
controlled is panel 2e's subject, where three of five distributional scorers gain exactly zero and
two lose. Figure 2 builds CLEAN as of 2026-09-03.

### A5c. The reissue missed exp16 and exp17, and Fig. 3c reverses once they are rebuilt

Found 2026-09-03, while rebuilding Figure 3: panel f asserted a gate verdict split of
621 / 133 / 11 and passed, while panel d, reading exp12 directly, asserted 627 / 127 / 11 and also
passed. Two panels of one figure disagreed about the same gate on the same 765 queries.

**Cause.** `analysis/estimator_audit/run_legacy_suite.sh` lists only scripts that CALL an energy
kernel; its header says so, and says everything else is estimator-independent. That reasoning
confuses estimator-independent CODE with estimator-independent OUTPUT. `exp16_gate_diagnosis` is a
pure re-analysis of exp12's per-query CSV and calls no kernel, so it is not in the suite and was
never re-run; `results/exp16_gate_diagnosis/_merged_query_divergence.csv` was still the V-arm merge
sitting downstream of a U-arm exp12, byte-identical to the copy in `results/_pre_ustat_backup/`.
`exp17_true_divergence_subset` reuses that merge and inherited the same staleness.

**Fix.** Both were re-run on 2026-09-03 as pure re-analyses of the U-arm exp12
(`POPRETRIEVE_ESTIMATOR=u python3 -m src.experiments.exp16_gate_diagnosis`, then exp17). The
pre-remerge files are in `results/_pre_exp16_remerge_backup/`.

**Sweep.** Every results file any main-figure panel reads was checked for the same defect. The
other twenty-two are produced either by a suite step or by a script that reads raw data rather than
another experiment's output (`analysis/identifiability/gate2_supervised_upper_bound.py`,
`analysis/natural/gate2_*.py`), so exp16 and exp17 were the only two affected.

**Consequence, and it is a reversal.** Figure 3c asks whether the minority-coverage gain
concentrates where the true response distribution is more divergent. It used to answer no.

| | V arm, stale merge | U arm, rebuilt merge |
|---|---:|---:|
| Spearman rho, gain vs true divergence (n = 765) | +0.050, p = 0.165 | **+0.141, p = 1.0e-04** |
| Q1 (lowest divergence) mean [95% CI] | +0.0042 [+0.0008, +0.0073] | **-0.0035 [-0.0076, +0.0001]** |
| Q2 / Q3 / Q4 mean | +0.0050 / +0.0062 / +0.0056 | +0.0038 / +0.0054 / +0.0051 |
| fraction of queries gaining, Q1 to Q4 | 0.55 / 0.69 / 0.70 / 0.71 | **0.41 / 0.55 / 0.61 / 0.65** |

The old panel's claim, "all four quartile means positive, no trend visible", is false on both
halves. What replaces it: **the lowest-divergence quartile does not gain and the upper three do,
and the per-query trend is positive and detectable.**

This does not weaken Figure 3, it sharpens it. The figure's subject is the pre-specified GATE, not
the divergence axis, and the four panels now say one thing instead of two:

- **c** true divergence does grade the gain (rho = +0.141, a clean break below Q2);
- **d** the gate does not enrich for it (difference -0.008, 95% CI -0.032 to +0.056, p = 0.64);
- **e** the gate's own reliability score runs opposite to true divergence (rho = -0.19, p = 1.5e-07);
- **f** the queries the gate declines are the more divergent ones (medians 1.68 against 1.66,
  CLES 0.43, p = 0.009).

The failure is in the surrogate, not in the axis. Panel f's inversion survives with a thinner
margin than before (p 0.001 to 0.009 against its own p < 0.01 gate), and that margin is recorded
in `figures/fig3/fig3f.py` rather than left to be discovered.

### A5d. The `\CLASS*` macro block kept its V-arm values, and the Results prose kept a hand-typed copy

Found 2026-09-03, while sweeping Figure 1's representation-versus-scoring-rule terminology through
the Results. The Class-A sentence printed a median improvement of $+0.129$ where Figure 3a draws
$+0.028$ on the same 600 queries.

**Cause.** In the preamble, the comment `% REISSUED 2026-09-03 under the unbiased U-statistic`
sits above the `\REGRETALL` group. The `\CLASS*` group is the next ten lines, reads the same
source file over the same 600 queries, and was not reissued with it. Nothing compared the two,
because the Results paragraph carried hand-typed literals rather than the macros: the macros were
defined and never referenced, so LaTeX could not have flagged the divergence either.

| Macro | V (in print) | U (now) |
|---|---:|---:|
| `\CLASSAMED` | +0.129 | **+0.028** |
| `\CLASSAMEAN` | +0.275 | **+0.135** |
| `\CLASSBMEAN` | -0.037 | **-0.024** |
| `\CLASSBWORSE` / `\CLASSBBETTER` / `\CLASSBTIED` | 41.3 / 34.2 / 24.5% | **40.8 / 35.7 / 23.5%** |
| `\CLASSARANGE` (five-variant Class-A medians) | +0.053 to +0.129 | **+0.028 to +0.067** |
| `\CLASSBRANGE` (five-variant Class-B means) | -0.011 to -0.037 | **-0.011 to -0.033** |
| `\VARIANTCOUPLING` (Spearman over the five, n = 5) | -0.90 | **+0.60** |

`\CLASSBMED` is 0.000 under both arms.

**Category.** B, not C: the sentence stands. Response matching stays positive, mechanism recovery
stays at a median of exactly zero with a negative mean, and the paragraph's conclusion, that the
response-matching gain does not carry over to mechanism recovery, is unchanged. What changes is
the size of the gain that fails to carry over, 4.6-fold smaller, and the word "large" has been
dropped from the closing sentence because it is no longer the right word for +0.028.

`\VARIANTCOUPLING` flips sign, from -0.90 to +0.60. No sentence in the paper uses it. At n = 5 it
was never able to carry an argument, the macro comment said so, and it is now recorded as a
description with its arm and its instability stated.

**Prevention.** The eight values now reach the page only through their macros, so a future reissue
that misses them prints a number that disagrees with the panel in a place a reader will see, not
in a comment. `docs/phase2/FINAL_FIGURE_NUMBER_LEDGER.md` records the per-variant table.

### A5e. Figure 5's caption and its Results subsection described a figure that had not existed for days

Found 2026-09-03, while splitting the Phase-II page into Figures 5 and 6. The manuscript's Figure 5
caption ran `\textbf{a}` to `\textbf{k}`, eleven panels, and the Results subsection cited
`Fig.~\ref{fig:5}b,c,d,e,f` and `h--k`. The built figure had carried **eight** panels since the
Phase-II rebuild, with entirely different content: `fig5b` was the oracle MRR ladder where the
caption described predictor nDCG gaps, `fig5c` the decision-correction counts where the caption
described constructed-mixture variance ratios.

**Why nothing caught it.** LaTeX validates `\ref{fig:5}` and never the panel letter after it, so
every one of those citations compiled without a warning. `build_all.py` gates typography, and
`check_overlaps.py` gates collisions; neither reads the caption. There is no gate anywhere in this
repository that compares a caption's panel list against the figure's, which is the single largest
class of undetected error left in the deck.

**Category.** Not A, B or C: no number moved. What was in print was a description of a figure the
reader would be looking at and would not recognise, together with five numbers (the predictor
nDCG gaps, the mixture cosines, the structure ratios, the 0.674/0.692 recoverability pair, the four
Tahoe values) attributed to panels that no longer drew them. Those measurements are all still true
and still in `results/`; they had simply stopped being panels.

**What was done.** The caption was rewritten for the eight oracle panels, a Figure 6 caption was
written for the eight prediction panels, and the Results subsection was rewritten around the two.
The measurements that lost their panels are kept as prose with Supplementary Note pointers, which
is where the Phase-II rebuild had already moved their content.

**Prevention, and what is still open.** Two source-data views named for the removed panels
(`fig5b_predictor_gaps.csv`, `fig5cd_structure_diagnostics.csv`) were retired to
`figures/source_data/_stale/` in the same pass, and the eleven Phase-II files the new panels read
are now under `sync_source_data.py`, which they had never been. **A caption-to-panel gate is still
not written.** The next figure that loses a panel will fail the same way.

### A5f. The Results prose reported the Fig. 2a ladder as a two-rung comparison, on two V-arm numbers

Found 2026-09-04, during the Nature-style prose pass. Two separate faults in one paragraph.

**Fault 1: two stale values.** The Results sentence reporting exp08 read "Hit@1 of 0.837" and
"0.887 for energy". Both are V-statistic values: under the U arm the macro-mean is **0.836** and the
query-weighted mean **0.884**. The Fig. 2a caption had been reissued and said 0.836; the prose had
not, and the two sat four pages apart.

| Quantity | V (in print) | U (now) |
|---|---:|---:|
| `\HITENERGY`, macro-mean Hit@1 | 0.837 | **0.836** |
| `\HITENERGYW`, query-weighted Hit@1 | 0.887 | **0.884** |

The other seven `\HIT*` macros do not touch an energy distance and could not move.

**Fault 2, the larger one: the magnitude rung was missing from the Results entirely.** The paragraph
reported 0.388 for mean cosine and 0.836 for energy and stopped, so a reader took the whole +0.447
gap as what populations buy. `mean_l2` sits at **0.788** between them: restoring response magnitude
to a mean signature is worth **+0.399** of that gap and adding the distribution a further
**+0.048**, so magnitude is 89.3% of it. That is the finding the section is named for, the finding
the abstract now leads with, and it appeared nowhere outside the Fig. 2a caption.

**Cause.** The same one as A5d, third instance. Nine `\HIT*` macros were defined in the preamble and
**not one was referenced anywhere in the body**: the prose hand-typed every value. A reissue that
updates a macro therefore changes nothing a reader sees, and nothing compares the macro to the
literal.

**Category.** B for fault 1, the sentence stands with two corrected digits. Fault 2 is a claim-level
omission, not a numeric error: nothing in print was false, but the Results supported a reading the
paper's own Figure 2a had retired.

**Prevention.** The prose and the Fig. 2a caption now both read the macros, `\HITMAG` and the two
step macros `\HITSTEPMAG` / `\HITSTEPDIST` were added, and the Frangieh magnitude value
`\HITFRANGMAG` (0.611, which beats both other scores on the one natural dataset) was added with it.
Two of the new macros were first written as `\HITMAGL2` and `\HITFRANGMAGL2`; LaTeX macro names take
letters only, so those parsed as `\HITMAGL` plus a literal `2` and printed "at 2" with no error.
They are letters-only now. **The general gap remains open: nothing checks that a preamble macro is
actually referenced, so a defined-and-unused macro is still invisible.**

### A5b. The regime classifier

| Result | V | U |
|---|---:|---:|
| exp13 `prediction_correct` (no panel; Supplementary Note 1) | 0.4519 | **0.3975** |

25 of 239 per-query predictions flip. This one gets **worse** under the correct estimator and must
be reported as such.

---

## Category B: the number moves, the sentence stands

Substitute the value; leave the claim.

| Result | V | U | claim |
|---|---:|---:|---|
| GDSC2 functional oracle, `energy_rho` median | 0.2761 | 0.2650 | unchanged |
| GDSC2 `energy_rho` fraction positive | 0.718 | 0.738 | unchanged |
| GDSC2 `energy_rho_partial_magmatch` median | 0.0969 | 0.1053 | unchanged |
| GDSC2 Wilcoxon energy vs magnitude-match, p | 0.0727 | 0.0543 | still above 0.05 |
| GDSC2 `mean_cosine_raw` median | 0.2413 | 0.2413 | identical by construction |
| GDSC2 `magnitude_match` median | 0.2318 | 0.2318 | identical by construction |
| exp12 `target_mrr` | -0.3213 | -0.3181 | unchanged |
| exp05 Frangieh advantage | -0.040 | -0.035 | unchanged, still negative |
| exp01 `global_energy` Hit@1 | 0.8933 | 0.8900 | unchanged |
| exp04 CD34 `mean_cosine` Hit@1 | 0.5139 | 0.5139 | identical; the negative control stays negative |
| exp09 predict-then-rank pooled MRR | 0.82315 | 0.82315 | identical |

The GDSC panels are the reassuring case: the two estimator-free columns are byte-identical across
arms, which is the internal check that the pipeline changed nothing it should not have, and the
energy column moves by 4% without touching the conclusion.

---

## Category C: the explanation has to change, not just the number

### C1. The protein oracle-shape reversal

| Quantity | V | U |
|---|---:|---:|
| `energy_vs_oracleMEAN` | 0.1463 | 0.2222 |
| `energy_vs_oracleDIST` | 0.5291 | 0.3930 |
| `mean_vs_oracleDIST` | 0.3340 | 0.2299 |
| energy minus magnitude-match, **distributional** oracle | 0.1768 | **0.1166** |
| energy minus magnitude-match, **mean** oracle | 0.0216 | **0.0976** |
| winner under the mean oracle | mean | mean |
| winner under the distributional oracle | energy | energy |

**The reversal survives; the reason given for it does not.** Under V the energy advantage over a
magnitude-matched scalar was eight times larger under the distributional oracle than under the mean
oracle (0.177 against 0.022), which reads as a distribution-specific compatibility. Under U the two
are 0.117 and 0.098, nearly equal.

The sentence to write is no longer "population evaluators reward population scorers". It is:

> the statistical form of an external evaluator still decides which method wins, but the energy
> distance's advantage is not specific to a population-shaped evaluator: response magnitude is a
> channel that is present under both evaluator forms.

### C2. The three-gate framework, and headroom

Superseded by [P4](P4_BOTTLENECK_DECOMPOSITION.md), which is itself a correction of
[08](08_THREE_GATE_ANALYSIS.md). Two statements must not survive into the manuscript:

- that differential response and recoverability **locate** where population scoring helps. The
  repaired interaction statistic does not predict gain (β = +0.0011, p = 0.33) and the retired one
  anti-predicts it (β = -0.0096, p = 0.009) once the mean route's own performance is conditioned on.
- that headroom explains the gain. Spearman +0.790 is reproduced at +0.786 [+0.767, +0.805] by a
  null that keeps both marginals and the `RR <= 1` ceiling. What survives is the ceiling fact: on
  3,110 of 3,992 oracle queries the mean route is already perfect at every seed.

### C3. exp12's regret yardstick is not estimator-neutral

`_welfare_proxy` (`src/experiments/exp12_partial_observed_retrieval.py:242`) defines welfare as the
worst-over-states negative **energy distance** from a candidate to the query's states, and the query
states have different cell counts. So the yardstick against which decision regret is measured is
itself an estimator-dependent quantity.

Consequences, both of which must be stated wherever exp12 regret is quoted:

1. Every regret number in exp12 moves under the estimator swap, **including those of scorers that
   are themselves estimator-free**. That is why `mean_cosine`'s regret changes at all (A2).
2. Regret comparisons across the two arms are not like-for-like in the way the retrieval metrics
   are: the metric and the measuring stick moved together. The direction of A2's reversal is
   therefore reported, and its magnitude should not be quoted as an effect size.

This is not the Class-A circularity already audited in `analysis/audit/diag_welfare_circularity.py`
and recorded in `CORRECTIONS.md`; it is a separate, previously unrecorded property of the same
construction.

---

## Rules from here

1. **No number enters the manuscript that is not in this ledger or in `results/`.** The
   `manuscript_macros.csv` table lists all 104 macros with the recomputed column each one matches,
   where a numeric match exists; a macro with no match is either a hand-entered constant or
   unsourced, and each has to be resolved individually before the rewrite.
2. **Category A numbers are reissued in the main text, not moved quietly to the SI.**
3. **Category C requires new sentences.** Three of them: the oracle-shape explanation, the framework
   replacement, and the exp12 regret caveat.
4. **The default estimator stays `'v'` in code** so the pre-repair numbers keep reproducing. The
   manuscript switches to the U numbers; the V numbers remain reachable and are what this ledger
   records as "before".
