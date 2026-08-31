# Figure 3: the population advantage weakens, and can change direction, once the judge changes

One-line message: the Class-A advantage established in Figure 2 does not survive a change to
criteria that do not share the retrieval objective. Four numbers are this figure's skeleton, and
every other panel supports or qualifies one of them:

| | |
|---|---|
| **+0.129** | response matching: population retrieval wins decisively (a) |
| **0.000** | mechanism recovery, the SAME rankings: the advantage is gone (a, b) |
| **+0.276** | external functional similarity: a real population signal (h) |
| **+0.097** | what survives once the response-magnitude channel is partialled out (h, m) |

Panel letters and every number below match the Fig. 3 caption in
`manuscript/latex/PopRetrieve_manuscript.tex`. If a number here and a number there ever disagree,
the manuscript is the authority and this file is the bug.

## Panels

| Row | Panel | What the reader sees | Reads |
|---|---|---|---|
| 1 | a | the advantage collapsing from +0.129 to 0 when only the judge changes | `results/exp12_partial_observed_retrieval/per_query_scores.csv` |
| 1 | b | three ECDFs stepping through zero, all three medians 0.000 | same |
| 2 | c | four quartile estimates, all positive, no trend | `results/exp16_gate_diagnosis/_merged_query_divergence.csv` |
| 2 | g | 239 tasks hugging zero, the largest mean on the smallest share | `results/exp13_real_data_projection/projection.csv` |
| 3 | d | two estimates with overlapping intervals | `results/exp12_partial_observed_retrieval/per_query_scores.csv` |
| 3 | e | a binned trend falling where it should rise | `results/exp16_gate_diagnosis/_merged_query_divergence.csv` |
| 3 | f | two divergence distributions, the declined one further right | same |
| 4 | h | energy above its incumbent, and an arc dropping it to +0.097 | `source_data/fig3hi_class_c_functional.csv` |
| 4 | i | a scatter split 62 / 41 by the diagonal | same |
| 5 | j | one dot past 0.8, one nowhere near it | `results/exp17_true_divergence_subset/power_analysis.csv` |
| 5 | k | two dumbbells of wildly different length on a log axis | same |
| 6 | l | two negative, one near zero, one strongly positive | `source_data/fig3hi_class_c_potency.csv` |
| 6 | m | a density piled up near +1 | same |

## No panel states a conclusion

Every panel used to carry one bold sentence over itself, thirteen in all. They are gone, and
`fig3_style.title()` is deleted rather than deprecated so none can come back. Only four kinds of
text may appear on a panel: axis and group names, statistics (median, rho, P, n, and the values
being compared), a two or three word direction hint, and nothing else. Every deleted phrase now
opens its panel's entry in the Fig. 3 caption, where it costs no space and can be qualified.

`fig3_assemble._assert_no_titles` enforces this mechanically: **no panel may draw text above
7.2 pt**, and the build fails if one does. It is a size gate rather than a wording gate, because no
code can tell a claim from a label, but a claim that has to fit at 7.2 pt beside the marks it
describes has already lost the argument for being on the panel. Removing the thirteen sentences
returned 0.42 in of height to the six rows, which is most of what had made rows 5 and 6 cramped.

## Verified numbers

- **a** n = **600** leave-one-drug-out queries, a balanced 200 per cell line. Class A regret
  reduction median +0.1288, mean +0.2752, 73.0% > 0, 19.7% < 0, 7.3% tied, max +2.823. Class B
  MoA-nDCG gain median +0.0000, mean -0.0371, 34.2% > 0, 41.3% < 0, 24.5% tied, paired Wilcoxon
  p = 2.46e-4. These reproduce the manuscript's Results sentence exactly; the 480-query version
  that used to be drawn did not. See CORRECTIONS.md R49.
- **b** Class B medians exactly 0.000 in all three lines; ties 20.0% (A549), 28.5% (K562), 25.0%
  (MCF7), n = 200 each.
- **c** quartile means +0.00415, +0.00495, +0.00619, +0.00561 with 95% bootstrap intervals
  [+0.0009, +0.0072], [+0.0035, +0.0067], [+0.0045, +0.0080], [+0.0039, +0.0076]; each Wilcoxon
  p < 1e-6. **Spearman(true_divergence, gain) = +0.0502, p = 0.165, n = 765: there is no trend.**
- **d** recommended median +0.11900 (n=621) against not recommended +0.12194 (n=133); difference
  -0.0029, 95% bootstrap CI -0.062 to +0.058, Mann-Whitney p = 0.967. Same measurement as
  Fig. 2d, and the two panels use the same split and the same direction of subtraction.
- **e** structure_reliability_score against true_divergence, Spearman rho = -0.2110,
  p = 3.79e-09, n = 765.
- **f** recommended n=621 median 1.660; mean_or_no_call n=133 median 1.689, Mann-Whitney
  p = 0.0011, common-language effect size 0.410 (95% CI 0.362 to 0.458); mean_sufficient n=11
  median 0.509, all eleven below the fifth percentile of both other groups. Pooled 621 against
  144 gives p = 0.0902 with a Kolmogorov-Smirnov D = 0.154, p = 0.0069. See the honesty note.
- **g** 239 tasks. Dataset means: cross-line +0.00426 (n=90, 18% > 0, median exactly 0.000),
  within-line +0.00038 (n=90, 56% > 0), Frangieh +0.00042 (n=23, 57% > 0), CD34+ +0.00027
  (n=12, 50% > 0), predicted candidates +0.00003 (n=24, 42% > 0). Overall mean +0.00181, median
  0.000; 102 of 239 tasks select the same candidate under both approaches.
- **h** 103 queries. Medians: energy +0.2761, mean cosine control-subtracted +0.0826, mean cosine
  raw +0.2413, magnitude match +0.2318, potency match +0.3987, energy partialled on magnitude
  match +0.0969. Per cell line the scalar-to-energy ratio is 0.95 (A549), 1.11 (K562), 0.49
  (MCF7), so "nearly matches" is a pooled statement.
- **i** energy better on 62 of 103; nominal paired Wilcoxon p = 0.0727, anticonservative.
- **j/k** Q4 stratum: minority_state_coverage n=191, gap +0.005608, s.d. 0.013496, power 0.99992,
  n for 80% power 45.5. moa_ndcg n=143, gap +0.003166, s.d. 0.163170, power 0.056191, n for 80%
  power 20,844.3 with `data_sufficient` False. The gaps differ by 1.8x, the standard deviations
  by 12x.
- **l/m** medians against the GDSC2 potency ranking: energy -0.5202, raw mean cosine -0.5334,
  control-subtracted mean cosine +0.1049, response magnitude alone +0.6918. Energy distance
  against candidate response magnitude, median +0.7910, IQR [+0.515, +0.961].

## Honesty notes

- **This is the load-bearing negative.** Every panel shows a different way the Class-A gain fails
  to transfer to oracle-independent evaluation. No panel is padding.
- **a and b measure the flip on the SAME queries**, so it is not a population difference; the
  metric changes the verdict.
- **a and b are on all 600 leave-one-drug-out queries, never on the gate's subset.** They read
  `results/` directly and assert n == 600, because until 2026-08-31 they plotted the 480 queries
  the diagnostic itself recommended while the Results text reported 600. That is the second time
  this deck drew a headline on a gate-selected subset; Fig. 2c was the first. CORRECTIONS.md R49.
- **Colour states a sign, not an object.** A distribution of population-minus-mean differences is
  grey with the sign carried by the half-planes behind it. The previous version drew panel a's two
  distributions blue and orange, which said the right-hand one was the mean method; both are the
  advantage, and only the judge differs. Panel l is the one place blue and orange are object
  colours, because it genuinely compares methods, and it draws no half-planes.
- **c makes no effect-size ratio claim, deliberately.** The largest quartile mean, +0.0062, is
  0.6% of the nominal [0, 1] metric range, 2.6% of the metric's observed range (0.756 to 0.996),
  5.1% of its central 98%, and **53% of the metric's own interquartile range**; the paired
  Cohen's d is 0.33. Those denominators disagree, so picking one would be the error this paper
  exists to criticise. What the data support without a choice is the absence of a trend with
  divergence, and that is what the panel claims. The earlier caption's "at most 0.0062 on a metric
  whose values run from 0.89 to 0.99" also mis-stated the range: 0.89 to 0.99 is the central 98%.
- **f's split is three-way because the gate's verdict is.** Pooling `mean_or_no_call` (n=133,
  median 1.69) with `mean_sufficient` (n=11, median 0.51) manufactures a null out of two opposite
  effects: the panel therefore draws both arms and states the pooled statistic in the caption.
  This is stronger than the p = 0.090 the panel used to report, and CORRECTIONS.md R47 records it.
- **g's largest mean is its least interesting number.** The constructed cross-line mixtures have
  the largest dataset mean and the smallest share of tasks above zero, so that mean is a tail and
  not a shift. The panel shows both, because a diamond alone says the opposite of what the tasks
  say.
- **h's oracle is drug-drug FUNCTIONAL SIMILARITY** (GDSC2 dose-response AUC profile correlation,
  the three SciPlex3 lines held out), not measured potency. The absolute-potency comparison is the
  endpoint control in l, not a competing result.
- **l's axis is the potency ranking, not AUC.** GDSC2 AUC runs opposite to potency, so an axis
  labelled "absolute potency (GDSC AUC)" makes a GDSC-literate reader take every sign backwards.
  The retired `ed5.py` phrasing "every ranking's correlation with potency inverts" is also wrong:
  the control-subtracted mean cosine goes +0.083 to +0.105, a collapse toward zero, not a sign
  change. Only energy and the raw mean cosine change sign.
- **j and k are a power analysis in a main figure**, which normally signals a thin headline. Here
  the headline IS the null, so the power analysis is the evidence rather than an apology for it.
  k prints 20,844 in full: rounding it to "about 20,000" costs the panel its force.

## Print geometry, authored 1:1

The figure enters the manuscript as `\includegraphics[width=\textwidth]` into a 6.951 in text
block. The canvas is **6.90 x 9.20 in** and exports 6.92 x 9.22, so LaTeX scales it by 1.004 and
nominal point size is printed point size. The float budget is the 9.461 in text block less about
16/72 in of overhead, i.e. 9.238 in, leaving 0.018 in of margin: **do not grow the canvas without
re-checking `Float too large` in the build log.** The caption is on the following page and is
itself near the limit; it overflowed at 991 words and fits at about 945.

Layout is an explicit inch ledger in `fig3_assemble.py`: six rows, `a|b`, `c|g`, `d|e|f`, `h|i`,
`j|k`, `l|m`, with unequal widths inside a row because the panels are unequal. It was five rows of
up to four panels until 2026-08-31.

**Thirteen panels on one page is tight, and the ledger says so rather than pretending.** Rows 5 and
6 give their panels 0.57 to 0.64 in of axes height. The response to that is to cut annotation into
the caption; `fig3_assemble._assert_floor` enforces a **6.5 pt** floor, above the deck's 5 pt
production limit, and measures mathtext at its effective 0.7x size.

## Files

- `fig3_style.py` : the frozen vocabulary. The sign rule, the type ladder, `CELL_MARKER`,
  `sign_field`, and the seeded `boot_ci` that every interval in the figure comes from.
- `fig3a.py` ... `fig3m.py` : per-panel draw functions, each `draw_3X(ax)`, each runnable
  standalone for a preview. Panels j to m were drawn by `edfigs/ed_panels.py` and `ed5/ed5.py`
  until 2026-08-31; they are re-authored here because those modules set type under this figure's
  floor, and are no longer imported by any main figure.
- `fig3_assemble.py` : the inch ledger, 9.5 pt panel letters, and the 6.5 pt floor gate. Owns
  `STEM`, which `build_all.py` checks against its own `STEMS` dict.
- `fig3_collapse.{pdf,svg,png}` : the composite. `python figures/build_all.py --write` enforces
  the floor, writes these, and copies the PDF to `manuscript/latex/figures/fig3.pdf`.
- `3a.png` ... `3m.png` : standalone previews, not inputs to the composite, not guaranteed fresh.
