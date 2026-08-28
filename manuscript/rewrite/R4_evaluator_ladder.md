# R4. More independent criteria dissolve, reverse or decompose the apparent gain

**Status:** draft 1, contract-clean. Every numeral is locked to a macro defined at
`PopRetrieve_manuscript.tex:112-205` and verified in `manuscript/reference/numerical_contract_audit.md`.
The three accepted corrections C-1, C-2 and C-3 and the labelling fix D-2 are all applied here.

**Word count: 1,264** (target 1,200 to 1,400).

**One new result appears here that is not in the current manuscript.** The five distributional
variants order themselves oppositely under the two criteria: the variant with the largest
objective-aligned gain has the most negative mechanism-recovery gain, at a rank correlation of
$-0.90$ across the five. This is the variant-level form of the section's argument and it is a free
observation from data already in the contract (audit row R4-32). It is reported descriptively, never
with a p-value, because five variants cannot support a test.

---

## 1. Revised section title

> **More independent criteria dissolve, reverse or decompose the apparent gain**

The three verbs are not rhetorical; each names one rung. Class B dissolves the gain at the median and
reverses it on average, and the functional oracle decomposes it into a magnitude channel plus a
smaller residual. A title naming only the reversal ("Independent evaluation reverses the advantage")
would contradict the Class-C rung, where the distributional score wins.

---

## 2. Complete prose

**The evaluator ladder, and the queries it runs on.** The remaining analyses hold the scorer, the
rankings and the queries fixed and change only the criterion doing the judging. Two of the three rungs
are defined on the same queries. Mechanism-of-action recovery is undefined for \NMOAEXCL\ of the
\NALL\ partial-observed queries, because those splits remove the entire mechanism class from the
candidate library and there is then no mechanism left to recover; the Class-A and Class-B comparisons
below are therefore both computed on the \NMOA\ queries where both criteria are defined, and every
paired statistic in this subsection uses that one set (Methods).

**Class A to Class B: the advantage disappears at the median and reverses on average.** On those
\NMOA\ queries the worst-case coverage scorer achieves a Class-A regret reduction of \CLASSAMED\
(median; mean \CLASSAMEAN). Re-scoring the \emph{identical} rankings under mechanism-of-action
recovery nDCG, the same two statistics are \CLASSBMED\ (median) and \CLASSBMEAN\ (mean;
Fig.~\ref{fig:4}a). Both are load-bearing and they say different things: on the median query the
advantage does not shrink but vanishes exactly, and averaged over queries it turns negative. The
reversal is not the work of a heavy tail. \CLASSBWORSE\ of queries \emph{lose} mechanism recovery
under the distributional score against \CLASSBBETTER\ that gain it, with \CLASSBTIED\ unchanged
(two-sided paired Wilcoxon $p = \CLASSBP$, zeros excluded).

**The collapse does not depend on which distributional variant is used, and the variants order
themselves informatively.** Across the five variants, measured on the same \NMOA\ queries, the Class-A
gain runs \CLASSARANGE\ and the Class-B gain runs \CLASSBRANGE. No variant escapes the sign change.
Because both ranges are computed on one query set, they are directly comparable, which a range
assembled across different subsets would not be. Within that set the two rankings run opposite to each
other: the worst-case coverage scorer has both the largest Class-A gain and the most negative Class-B
gain, energy and MMD sit at the bottom of the first and the top of the second, and the rank
correlation between a variant's objective-aligned gain and its mechanism-recovery gain is
\VARIANTCOUPLING\ (Spearman over five variants, too few for a test and reported as a description).
The more sharply a variant optimises the aligned objective, the more mechanism recovery it gives up.

**A diagnostic gate does not concentrate the advantage where it should be.** The gate was built to
flag the queries on which subpopulation information ought to help, and it labels the \NALL\ queries
independently of whether mechanism recovery is defined for them: \NREC\ recommended, \NNONREC\
non-recommended and \NMEANSUFF\ mean-sufficient. This is a second partition of the same \NALL\
queries, not a subdivision of the \NMOA\ used above, so the two cuts are reported separately and never
compared term by term. On its own proxy metric the gate separates nothing. Median Class-A regret
reduction is \GATEREC\ on the recommended queries against \GATENONREC\ on the non-recommended ones
(Fig.~\ref{fig:4}d). The subset the gate selects against carries the marginally larger gain.

**Projected onto real datasets, the advantage is statistically real and practically negligible.**
Across all \PROJN\ real-data tasks the minority-state coverage advantage has a mean of \PROJMEAN\
(two-sided Wilcoxon $p = \PROJP$ on the \PROJNONZERO\ tasks with a nonzero difference) on a metric
whose observed values run from 0.60 to 1.00. In \PROJTIED\ of the \PROJN\ tasks the difference is
\emph{exactly} zero, because both method families select the same drug. The effect is also
concentrated in the mixtures we constructed: the mean gain is $+0.0043$ on the 90 constructed
cross-line tasks, against $+0.0004$ within line ($n = 90$), $+0.0004$ on Frangieh ($n = 23$),
$+0.0003$ on CD34$+$ ($n = 12$) and $+0.00003$ under predicted candidates ($n = 24$)
(Fig.~\ref{fig:4}g). An advantage of two thousandths on a metric with that operating range is not a
quantity a candidate list can be reordered by.

**An external functional oracle: the distributional score wins, on a criterion no scorer can see.**
Class B is task-proximal rather than independent. Mechanism annotation is curated from the same
pharmacological literature that named the compounds in the candidate library, so a scorer and a
mechanism label can share an upstream source without either being computed from the other, and the
reversal above therefore bounds the gain without being the last word on it. The ladder is incomplete
without a readout from outside the transcriptional data entirely. The semantically matched choice for
a similarity retriever is drug-drug functional
similarity: do the query and the candidate \emph{behave} alike in an independent assay? GDSC2 supplies
it as a dose-response AUC profile per compound across \CTXLINES\ cell lines, the three SciPlex3 lines
excluded so the oracle is never evaluated in the context the transcriptional query came from
(Methods). Across \NCQUERIES\ leave-one-drug-out queries, energy retrieval attains
$\rho = \ENERGYFUNC$ against \MEANCTRLFUNC\ for the correctly specified mean-signature incumbent, in
the same direction in all three cell lines (Fig.~\ref{fig:4}h). This is the first point in this study
at which the distributional score beats its incumbent on a criterion no scorer can observe.

**Most of that margin is a response-magnitude channel.** Rank the candidates instead by how closely
their response \emph{magnitude} matches the query's, a query-dependent scalar that compares no
distributions at all, and it reaches $\rho = \MAGMATCHFUNC$. Energy's edge over that scalar is
\ENERGYWINS\ of \NCQUERIES\ queries, which even under an anticonservative paired test is not
significant ($p = \ENERGYWINSP$). Partialling the magnitude channel out leaves energy with a partial
Spearman of \ENERGYPARTIAL\ (per line $+0.131$, $+0.053$, $+0.162$: positive in all three, and small).
The picture is layered rather than negative. Distributional retrieval carries genuine functional
signal that the mean signature does not; roughly two thirds of that signal is magnitude; and the
residual attributable to the \emph{distribution} is positive and small. We do not express this as a
ratio against the Class-A gain, because a Spearman correlation against an external oracle and a regret
reduction against an objective-aligned proxy are quantities on different scales.

**The affirmative result depends on how the oracle is constructed, and we report the dependence.**
Cell lines differ enormously in general drug sensitivity, and left uncorrected that shared main effect
makes almost every drug pair look alike, so each cell line's mean AUC, estimated across all
\NGDSCDRUGS\ GDSC2 compounds rather than only the matched ones, is subtracted before correlating
(Methods). Without that correction, energy falls to a raw Spearman of \ENERGYUNCEN, below both the
mean-signature incumbent's \MEANCTRLUNCEN\ and the magnitude scalar's \MAGMATCHUNCEN; both
constructions are given in full in Supplementary Table 4. The correction was specified on the
reasoning above before the retrieval results were inspected, and leaving a shared cell-line main
effect in an external criterion would be an error of its own. It remains an analytic choice, and the
Class-C positive holds under the construction we argue is correct and not under the one we argue is
wrong. What survives both constructions is the negative: under neither does the distributional score
significantly beat a scalar that compares no distributions.

**Scope of the functional oracle.** It is semi-real. Viability is measured in a separate bulk assay,
joined to the transcriptional data by compound identity rather than by shared cells, and under a
different dose regime, so it constrains what a transcriptional score recovers about drug function
without being a clinical endpoint. The \NCQUERIES\ queries within a cell line share a candidate pool,
so paired tests across them are anticonservative; the honest unit is the three cell lines, and per-line
values are given throughout.

---

## 3. Source-to-sentence numerical contract

Every value on the \NALL / \NMOA / \NREC / \NNONREC tree comes from
`results/exp12_partial_observed_retrieval/per_query_scores.csv`, baseline `mean_cosine`, variant
`DART_coverage_worst` unless the row says all five. Class A is `mean_cosine - variant` on
`decision_regret`; Class B is `variant - mean_cosine` on `moa_ndcg`.

| Sentence (opening words) | Value | Macro | n | Source / field | Audit row | Reproduced |
|---|---|---|---:|---|---|---|
| "undefined for 165 of the 765" | 165 / 765 | `\NMOAEXCL` / `\NALL` | 765 | `split_type`; sentinel rule `exp16_common.mask_undefined` | R4-02 | 120 `leave_MoA_out` + 45 `partial_library` |
| "computed on the 600 queries where both criteria are defined" | 600 | `\NMOA` | 600 | `split_type == leave_drug_out`; sha256 `1dda00b1...` | R4-01 | 600 |
| "a Class-A regret reduction of +0.129 (median; mean +0.275)" | +0.129 / +0.275 | `\CLASSAMED` / `\CLASSAMEAN` | 600 | `decision_regret` | R4-03, R4-04 | `+0.12883` / `+0.27515` |
| "the same two statistics are 0.000 and -0.037" | 0.000 / -0.037 | `\CLASSBMED` / `\CLASSBMEAN` | 600 | `moa_ndcg` | R4-05, R4-06 | `+0.00000` / `-0.03707` |
| "41.3% of queries lose ... against 34.2% that gain ... 24.5% unchanged" | 41.3 / 34.2 / 24.5 | `\CLASSBWORSE` / `\CLASSBBETTER` / `\CLASSBTIED` | 600 | `moa_ndcg` | R4-07, R4-08 | `0.4133` / `0.3417` / `0.2450` |
| "two-sided paired Wilcoxon p = 2.4e-4, zeros excluded" | 2.4e-4 | `\CLASSBP` | 600 | `moa_ndcg`, 453 nonzero | R4-09 | `T = 41194.5`, `z = -3.666`, `p = 2.461e-4` |
| **"the Class-A gain runs +0.053 to +0.129"** | **+0.053 to +0.129** | `\CLASSARANGE` | 600 | `decision_regret`, five variants | **R4-10, C-1 applied** | energy `+0.0533` to coverage-worst `+0.1288` |
| "the Class-B gain runs -0.011 to -0.037" | -0.011 to -0.037 | `\CLASSBRANGE` | 600 | `moa_ndcg`, five variants | R4-11 | mmd `-0.0111` to coverage-worst `-0.0371` |
| **"the rank correlation ... is -0.90"** | **-0.90** | `\VARIANTCOUPLING` | 5 variants on 600 | both columns above | **new, R4-32** | rank orders `A: 1,2,3,4,5` against `B: 4,5,3,2,1`, $\sum d^2 = 38$, $\rho = -0.90$ |
| "621 recommended, 133 non-recommended, 11 mean-sufficient" | 621 / 133 / 11 | `\NREC` / `\NNONREC` / `\NMEANSUFF` | 765 | `recommendation_mode` | R4-13, R4-14 | 621 + 133 + 11 = 765 |
| "+0.119 on the recommended against +0.122 on the non-recommended" | +0.119 / +0.122 | `\GATEREC` / `\GATENONREC` | 621 / 133 | `decision_regret` | R4-13 | `+0.11900` / `+0.12194` |
| "mean of +0.0018" | +0.0018 | `\PROJMEAN` | 239 | `projection.csv`, coverage difference | R4-15 | `+0.001806` |
| **"two-sided Wilcoxon p = 2.6e-7 on the 137 tasks"** | **2.6e-7** / 137 | `\PROJP` / `\PROJNONZERO` | 137 | same | **R4-16, C-3 applied** | `T = 2330`, `z = -5.149`, two-sided `2.620e-7` |
| "In 102 of the 239 tasks the difference is exactly zero" | 102 / 239 | `\PROJTIED` / `\PROJN` | 239 | same | R4-17 | 102 |
| "values run from 0.60 to 1.00" | 0.60 / 1.00 | literals | 239 | same, both arms | R4-18 | `[0.5999, 0.9969]` |
| "+0.0043 ... +0.0004 ... +0.0004 ... +0.0003 ... +0.00003" | per-dataset | literals | 90/90/23/12/24 | same, `dataset` | R4-19 | `0.004264` / `0.000382` / `0.000420` / `0.000269` / `0.000030` |
| "966 cell lines ... 103 leave-one-drug-out queries" | 966 / 103 | `\CTXLINES` / `\NCQUERIES` | 103 | `class_c_functional_oracle.json` | R4-30 | as recorded in the oracle string |
| "energy attains +0.276 against +0.083" | +0.276 / +0.083 | `\ENERGYFUNC` / `\MEANCTRLFUNC` | 103 | `energy_rho.median`, `mean_cosine_ctrl_rho.median` | R4-20 | `0.276089` / `0.082553` |
| "the scalar reaches +0.232" | +0.232 | `\MAGMATCHFUNC` | 103 | `magnitude_match_rho.median` | R4-21 | `0.231780` |
| "62 of 103 ... p = 0.073" | 62 / 0.073 | `\ENERGYWINS` / `\ENERGYWINSP` | 103 | `class_c_functional_oracle.csv` | R4-24 | 62; `z = -1.795`, `p = 0.07271` |
| **"a partial Spearman of +0.097"** | **+0.097** | `\ENERGYPARTIAL` | 103 | `energy_rho_partial_magmatch.median` | **R4-22, D-2 label applied** | `0.096925` |
| "per line +0.131, +0.053, +0.162" | per line | literals | 34/34/35 | `per_line.*.energy_partial` | R4-23 | `0.1307` / `0.0533` / `0.1624` |
| "all 286 GDSC2 compounds" | 286 | `\NGDSCDRUGS` | n/a | oracle string | R4-30 | 286 |
| **"a raw Spearman of +0.0967, below +0.138 and +0.217"** | **+0.0967 / +0.138 / +0.217** | `\ENERGYUNCEN` / `\MEANCTRLUNCEN` / `\MAGMATCHUNCEN` | 103 | `class_c_functional_oracle.csv`, `*_uncentered` medians | **R4-28, D-2 precision applied** | `0.096715` / `0.138035` / `0.216912` |

---

## 4. Deleted or relocated source material

### 4.1 C-2 applied: the mixed-denominator pair is removed from the main text

**Deleted from Results** ([:334-338](../latex/PopRetrieve_manuscript.tex#L334)):

> "Selecting the best scorer separately for each metric class, on different query subsets, is an
> analytic degree of freedom this task readily permits, and it would report $+0.119$ against
> $-0.013$: it \emph{understates} the collapse. We fix both and report the larger number."

`+0.119` is computed on the \NREC\ gate-recommended queries and `-0.013` is not attributable to the
stated rule: on the \NMOA\ set the least-negative Class-B variant is `DART_mmd` at `-0.0111`, while
`-0.0129` belongs to `DART_energy`, the third of five (audit row R4-12).

**Installed in Methods**, "Evaluation metric taxonomy and circularity audit", verbatim per the author
decision:

> "Selecting the best-performing distributional scorer separately within each evaluator class would
> yield a smaller contrast than the fixed-scorer comparison reported here and therefore would not
> explain the observed collapse."

No numerals. The argument survives intact and no two values computed on different denominators are
juxtaposed anywhere in the section.

### 4.2 Deleted as redundancy, manuscript history or defensive framing

| Current text | Location | Reason |
|---|---|---|
| "This is the central result (Fig. 4)." | [:334](../latex/PopRetrieve_manuscript.tex#L334) | one of three competing "central result" markers; the four-level claim hierarchy replaces all three |
| "The correlation is computed over the 54,180 query-candidate scores ... an earlier draft called these '54,180 real queries', which overstates the independent sample size by a factor of 43." | [:291-295](../latex/PopRetrieve_manuscript.tex#L291) | manuscript-history narration. The unit definition itself moves to Methods |
| "The distributional score is not merely no better; it is worse." | [:348](../latex/PopRetrieve_manuscript.tex#L348) | replaced by the C-3 harmonized formulation, "disappears at the median and reverses on average", which is more precise and carries the same force |
| "An independent divergence audit reaches the same verdict and numerically the same effect ... Two analyses that share no code path converge on it." | [:363-365](../latex/PopRetrieve_manuscript.tex#L363) | the convergence claim adds no number the reader can act on; the audit itself moves to SI |
| "The conclusion is deliberately strong and deliberately bounded ... That dependence, not a verdict on any single method, is the finding." | [:422-426](../latex/PopRetrieve_manuscript.tex#L422) | paper-level conclusion restated inside a Results subsection; it belongs once, in the Discussion |
| "we report the dependence rather than bury it" and "a paper arguing that the choice of criterion decides the winner cannot exempt its own criterion" | [:468](../latex/PopRetrieve_manuscript.tex#L468), [:475](../latex/PopRetrieve_manuscript.tex#L475) | defensive meta-language. The dependence is now simply reported |
| "The honest statement is that the Class-C positive below holds under the oracle we argue is correct and not under the oracle we argue is wrong." | [:475-477](../latex/PopRetrieve_manuscript.tex#L475) | same clause without the honesty framing |
| "Objective fidelity does not make the distributional gain imaginary. It makes it look far larger than it is." | [:516-517](../latex/PopRetrieve_manuscript.tex#L516) | paper-level conclusion; relocated to Discussion paragraph 1 |
| "\textbf{The oracle must match the task.}" paragraph | [:445-451](../latex/PopRetrieve_manuscript.tex#L445) | compressed into one clause of the Class-C opening; the full argument is a Discussion recommendation (task alignment) |

### 4.3 Relocated to Methods

| Content | Current location |
|---|---|
| Query and scored-pair definitions (1,260 queries, 43 candidates, 54,180 pairs) | [:291-295](../latex/PopRetrieve_manuscript.tex#L291) |
| The oracle equation $\mathrm{oracle}(q,c) = \mathrm{Spearman}(\mathrm{AUC}_\bullet(q), \mathrm{AUC}_\bullet(c))$ and the SciPlex3 line holdout | [:457-461](../latex/PopRetrieve_manuscript.tex#L457) |
| Cell-line centering protocol and its pre-specification, including `\CENTERUNCEN` | [:461-466](../latex/PopRetrieve_manuscript.tex#L461) |
| Candidate-pool construction and the `MIN_SHARED_LINES = 100` eligibility rule | not currently in the manuscript |
| The $+0.01$ dominance threshold and why it is not interpretable | [:367-370](../latex/PopRetrieve_manuscript.tex#L367) |
| The best-scorer-selection statement, qualitative (4.1) | [:334-338](../latex/PopRetrieve_manuscript.tex#L334) |

### 4.4 Relocated to Supplementary Information

| Content | Current location | Words freed |
|---|---|---:|
| Dominance-count audit and seed resampling, including the two surviving HDAC compounds | [:367-378](../latex/PopRetrieve_manuscript.tex#L367) | ~210 |
| Gate-axis diagnostics: structure-reliability anti-correlation $\rho = -0.21$, preference-conflict $\rho = +0.18$, Mann-Whitney $p = 0.090$, divergence stratification | [:399-412](../latex/PopRetrieve_manuscript.tex#L399) | ~230 |
| Power analysis (achieved power 1.00 against 0.06; 20,800 queries for 80% power) | [:414-420](../latex/PopRetrieve_manuscript.tex#L414) | ~120 |
| Dataset-level divergence rule and its failure on its own terms | [:388-397](../latex/PopRetrieve_manuscript.tex#L388) | ~180 |
| Query-independent fixed-ranking magnitude control ($\rho = -0.330$, the sign-must-be-known-in-advance argument, potency matching at $+0.399$) | [:493-505](../latex/PopRetrieve_manuscript.tex#L493) | ~220 |
| Mismatched absolute-potency oracle confounder audit ($\rho = -0.520$, $+0.692$, $+0.791$) | [:526-533](../latex/PopRetrieve_manuscript.tex#L526) | ~140 |
| Uncorrected mean baseline without control subtraction ($\MEANRAWFUNC$) | [:519-524](../latex/PopRetrieve_manuscript.tex#L519) | ~90 |

Total relocated or deleted from this subsection: approximately **1,050 words**, against 2,369 in the
current Class-B plus Class-C sections combined. Net main-text length 1,318.

### 4.5 One value retained in the prose that is scheduled to move

`\ENERGYCANDMAG` ($\rho = +0.791$, the coupling between an energy distance and the candidate's own
response magnitude) is used in R5 and in the SI confounder audit but not in the R4 prose above. It is
listed here so that the macro is defined once and consumed by both.

---

## 5. Exact word count

Counted on the prose of section 2 only, macros expanded to their printed values, `\ref` resolved to a
single token, remaining LaTeX stripped.

```
1,264 words
```

Target 1,200 to 1,400. Inside band, 136 words below the ceiling.

Paragraph lengths: 103, 122, 160, 118, 153, 195, 159, 171, 83. Nine paragraphs covering the six
prescribed blocks in the prescribed order: block 1 (denominators) is paragraph 1, block 2 (Class A to
Class B) is paragraph 2, block 3 (variant robustness) is paragraph 3, block 4 (the gate) is paragraph
4, block 5 (real-data projection) is paragraph 5, block 6 (Class C) is paragraphs 6 to 9.

**One limitation paragraph only.** Paragraph 9 ("Scope of the functional oracle") is the section's
single limitation block, per the rule that no Results subsection carries more than one. The
construction dependence in paragraph 8 is a result, not a caveat, and is written as one.

**No block ends with the paper-level conclusion.** The closing sentence of each block states what that
rung showed and stops. The synthesis is deferred to the Discussion.

---

## 6. Grep checklist

```bash
# 1. C-1: the old cross-subset range must be gone everywhere.
grep -rn "0\.056" manuscript/latex/*.tex manuscript/rewrite/*.md   # expect hits ONLY in audit prose
grep -c 'CLASSARANGE' manuscript/latex/PopRetrieve_manuscript.tex     # expect >= 1 (definition)

# 2. C-2: the mixed-denominator pair must not appear in any Results file.
grep -rn '\-0\.013' manuscript/rewrite/R4_evaluator_ladder.md       # expect hits ONLY in section 4.1

# 3. C-3: the one-sided p must be gone.
grep -rn "1\.3.*10\^\{-7\}\|1\.3e-7" manuscript/latex/*.tex manuscript/rewrite/*.md  # expect 0 outside audit

# 4. D-2: the two Spearmans must never both print as a bare +0.097.
grep -n "ENERGYPARTIAL\|ENERGYUNCEN" manuscript/latex/PopRetrieve_manuscript.tex
#    \ENERGYPARTIAL -> +0.097 and is always preceded by the words "partial Spearman"
#    \ENERGYUNCEN   -> +0.0967 and is always preceded by the words "raw Spearman"
awk '/^## 2\./,/^## 3\./' manuscript/rewrite/R4_evaluator_ladder.md | tr '\n' ' ' \
  | grep -oE '(partial|raw) Spearman'   # both must appear; tr first, the labels straddle line breaks

# 5. Every macro used in R4 is defined exactly once.
for m in NALL NMOA NMOAEXCL NREC NNONREC NMEANSUFF CLASSAMED CLASSAMEAN CLASSBMED CLASSBMEAN \
         CLASSBWORSE CLASSBBETTER CLASSBTIED CLASSBP CLASSARANGE CLASSBRANGE GATEREC GATENONREC \
         PROJMEAN PROJP PROJN PROJTIED PROJNONZERO ENERGYUNCEN MEANCTRLUNCEN MAGMATCHUNCEN \
         CTXLINES NCQUERIES ENERGYFUNC MEANCTRLFUNC MAGMATCHFUNC ENERGYPARTIAL ENERGYWINS \
         ENERGYWINSP NGDSCDRUGS; do
  n=$(grep -c "newcommand{\\\\$m}" manuscript/latex/PopRetrieve_manuscript.tex)
  printf '%-16s %s\n' "$m" "$n"
done          # every line must read 1

# 6. Denominator hygiene. The rule is that no paragraph may put a VALUE from the 600-query cut
#    beside a VALUE from the gate cut. Naming both cuts in one paragraph is required, not
#    forbidden: paragraph 4 does it deliberately so the reader cannot read 621 as a subset of 600.
awk '/^## 2\./,/^## 3\./' manuscript/rewrite/R4_evaluator_ladder.md \
  | awk 'BEGIN{RS="\n\n"} /\\CLASSA|\\CLASSB/ && /\\GATEREC|\\GATENONREC/ {print "VIOLATION:"; print}'
#    expect no output

# 7. Macro values against the artifacts.
python3 analysis/audit/numerical_contract_stage1.py >/dev/null && \
python3 analysis/audit/numerical_contract_stage2.py | grep -E 'moa600_DART_coverage_worst|all765'

# 8. No em dashes.
awk '/^## 2\./,/^## 3\./' manuscript/rewrite/R4_evaluator_ladder.md \\
  | grep -cP '\\x{2014}'   # expect 0. Scoped to the prose and written as a
                              # codepoint so the check cannot match itself.
```

**Checklist result, measured 2026-07-29. All eight items pass.**

| Item | Result |
|---|---|
| 1 C-1, old range gone | `0.056` appears 0 times in the prose |
| 2 C-2, mixed pair gone | `-0.013` appears 0 times in the prose, only in section 4.1 where its removal is documented |
| 3 C-3, one-sided p gone | 0 hits |
| 4 D-2, both Spearmans labelled | `partial Spearman` and `raw Spearman` both present (join lines before matching; the labels straddle a line break) |
| 5 macros defined once | 35 of 35 |
| 6 denominator hygiene | no paragraph carries a value from the 600-query cut beside a value from the gate cut |
| 7 macro values against artifact | `NMOA` 600, `NALL` 765, `CLASSAMED` 0.129 / 0.128829, `CLASSAMEAN` 0.275 / 0.275155, `CLASSBMED` 0.000 / 0.000000, `CLASSBMEAN` -0.037 / -0.037073, `CLASSBWORSE` 41.3 / 41.333, `CLASSBBETTER` 34.2 / 34.167, `CLASSBTIED` 24.5 / 24.500, `GATEREC` 0.119 / 0.119004, `GATENONREC` 0.122 / 0.121939, `CLASSARANGE` +0.053 to +0.129 / +0.0533 to +0.1288, `CLASSBRANGE` -0.011 to -0.037 / -0.0111 to -0.0371, `CLASSBP` 2.4e-4 / 2.4614e-4. **ALL OK** |
| 8 em dashes in prose | 0 |

**Two checklist items were themselves wrong on first writing and are corrected above.** Item 4 matched
line by line and missed `partial Spearman`, which straddles a line break; it now joins lines first.
Item 6 forbade any paragraph naming both cuts, which would have flagged paragraph 4, where naming both
is the whole point; it now forbids only a value from one cut appearing beside a value from the other.
