"""PopRetrieve Figure 3 panel 3j: what size of gap was within reach in the top divergence quartile?

WHAT THIS PANEL CLAIMS
----------------------
In the highest quartile of true response divergence, the stratum the pre-specified gate says the
population advantage should be largest in, the two Class-B evaluators reach opposite verdicts on
whether the gap each of them observed was resolvable at all.

Two achieved powers, computed at the gap each evaluator actually observed in that stratum:
minority-state coverage 0.9999 at n = 191, MoA-nDCG 0.0562 at n = 143. Only the first clears the
conventional 0.80. The claim the title makes is asserted in code before anything is drawn, so the
title cannot outlive the data, and both numbers are recomputed from the source columns rather
than read from the achieved_power column alone.

WHY THE TITLE NAMES THE QUARTILE, AND DOES NOT ONLY LEAVE IT TO THE X LABEL
---------------------------------------------------------------------------
Because the unscoped sentence is false of the study, and false in the direction that flatters the
paper least. MoA-nDCG is not a blunt instrument in this design. Over all 600 queries its mean gap
is -0.0371 at s.d. 0.1959, which is achieved power 0.996 and Wilcoxon p = 2.5e-4; in Q1 it is
-0.0822 at power 0.999, in Q2 0.702, in Q3 0.249. The evaluator resolves MoA-nDCG gaps when they
are large, and what it cannot resolve is a gap the size of Q4's +0.0032. So "only the coverage gap
is detectable", read as a statement about the mechanism-recovery comparison rather than about this
stratum, is not a cautious reading of the panel: it is a wrong one, because the whole-query
MoA-nDCG gap IS resolved and it runs the other way, toward mean retrieval. Q4 is not a flattering
subset picked after the fact, it is the stratum the gate pre-specified and the one panel k draws,
but a panel whose sentence needs it must say it. The stratum is therefore in the title as well as
on the x label, and _load asserts against divergence_stratified.csv both that Q4 really is the
highest-divergence quartile and that MoA-nDCG clears the rule over all queries, which is the fact
that makes the scoping load-bearing rather than decorative. Panel k does not need the prefix for
its own title: its noise claim holds in every stratum, and its docstring shows the check.

What this panel does NOT claim: that the Q4 MoA-nDCG null is therefore secure. Read alone it says
the opposite, that a gap of the size MoA-nDCG observed is out of this study's reach. What makes
the null informative is the size of the gap that WOULD be reachable, and that is panel k's
number, not this one's. This panel is a statistical diagnostic and is drawn at a diagnostic's
weight: one axis, two dots, one reference rule.

SOURCE
------
results/exp17_true_divergence_subset/power_analysis.csv        the two Q4 rows that are drawn
results/exp17_true_divergence_subset/divergence_stratified.csv never drawn, read only to
    ASSERT three things: that Q4 is the highest-divergence quartile, that its per-metric n agree
    with the power file, and that MoA-nDCG clears the rule on the ALL row. The first two check the
    words "highest response-divergence quartile" against the file that defines them; the third
    checks the title's "Top quartile:" prefix against the sentence it is there to prevent.
Both are written by src/experiments/exp17_true_divergence_subset.py, whose power_two_sided is a
two-sided one-sample normal approximation at alpha = 0.05 with the effect and s.d. estimated from
the same sample. _achieved_power below reimplements it and the loader asserts agreement.

JUDGEMENT CALLS A READER COULD REASONABLY DISAGREE WITH
-------------------------------------------------------
1. ACHIEVED (post-hoc, observed-effect) POWER IS A CRITICISED STATISTIC. Computed at the observed
   effect it is a monotone function of the p-value and adds no information to it, and it must
   never be read as evidence for the null. It is drawn because the reviewer's question is about
   the DESIGN rather than about this sample: at these n and these variances, what size of gap was
   within reach. The axis says "at the observed gap" so the reader can apply that discount. An
   alternative panel, the minimum detectable effect at 80% power, would carry the same content
   without the post-hoc framing; it is not drawn here because panel k already carries the
   sample-size form of exactly that quantity and two panels should not say one thing twice.
2. THE TWO DOTS ARE NOT COMPUTED ON THE SAME QUERIES. Both are the Q4 stratum, but MoA-nDCG is
   undefined for 48 of its 191 queries, so it is a 143-query subset. The n are on the panel for
   that reason; they also block the misreading that the low power is a sample-size difference,
   which 143 against 191 cannot produce.
3. BOTH DOTS ARE SHARED GREY. Neither is a retrieval method: both are evaluators judging the same
   rankings, so neither may take POP blue or MEAN orange. The retired Extended Data version
   (figures/edfigs/ed_panels.draw_ed2a) drew MoA-nDCG in mean-retrieval orange and minority
   coverage in population blue, which said these were two competing methods. They are not, and
   nothing here is a signed difference either, so no half-plane wash applies.
4. 0.80 IS A CONVENTION, NOT A PRE-REGISTERED CRITERION OF THIS STUDY. It is drawn as a dashed
   reference, named once beside it, and named again in the title. The title says "clears 80%"
   rather than "is detectable" for that reason: the convention is the whole content of the word,
   and a reader who rejects the convention can read the two numbers off the axis instead.
5. POWERS ARE PRINTED TO FOUR DECIMALS. 0.99992 printed as "1.00" would read as an exactness the
   estimate does not have, and 0.056191 needs the precision to be distinguishable from zero.
6. THE HAIRLINE LEAD FROM ZERO TO EACH DOT is a fifth element the brief for this panel did not
   ask for: axis, two dots, one rule. It is kept at 0.8 pt in FAINT because without it the two
   dots do not read as fractions of the same [0, 1] gauge, and it is a hairline rather than a bar
   because a bar would give a statistical diagnostic the ink of a result.
7. THE AXIS LABEL IS SET AT PT_TICK (6.8), not at PT_ANNOT. Both of its lines are load-bearing and
   at 7.2 the two-line label ends 0.011 in below the panel box, which the preview harness does not
   catch: ax.xaxis reports a zero-size window extent, so neither the tick labels nor the axis
   label are measured against the box. Measured by hand it now clears by 0.023 in.
8. THE PANEL DOES NOT DRAW THE VARIANCES that explain the two positions (s.d. 0.0135 against
   0.1632, a factor of 12). At 2.36 x 0.57 in a second quantity would crowd the gauge, and the
   ratio is panel k's title and this figure's caption.
9. "minority-state coverage" and "MoA-nDCG" are named without their metric class. Both are
   Class B, task-proximal biological, so a class label would separate nothing here.
10. THE WHOLE-QUERY MoA-nDCG ROW IS NOT DRAWN, only asserted. A third dot at power 0.996 on all
   600 queries would make the title's prefix visible instead of verbal, and would be the honest
   way to show that this evaluator is not blind. It is left out because the panel's brief is the
   Q4 gauge, three rows do not fit legibly in 0.57 in, and a whole-query dot would need its own
   sign annotation to avoid reading as a THIRD null rather than a resolved NEGATIVE gap. If the
   figure ever gains height, drawing it is the first thing to add here.

Run standalone: python fig3j.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig3_style import (FAINT, MS_DOT, PT_ANNOT, PT_SMALL, PT_TICK, REPO,  # noqa: E402
                        SHARED, SUBTLE, TEXT, bare_axes, title)

POWER_CSV = os.path.join(REPO, "results", "exp17_true_divergence_subset", "power_analysis.csv")
STRAT_CSV = os.path.join(REPO, "results", "exp17_true_divergence_subset",
                         "divergence_stratified.csv")

STRATUM = "Q4"          # the label exp17 gives the top quartile of true_divergence
ALPHA = 0.05            # exp16_common.power_two_sided default, two-sided
POWER_RULE = 0.80       # the conventional criterion, drawn as a reference and named once

# (column name in the source file, the name drawn on the panel). Order is top row first.
METRICS = (("minority_state_coverage", "minority-state coverage"),
           ("moa_ndcg", "MoA-nDCG"))

# Scoped to the stratum on purpose; see WHY THE TITLE NAMES THE QUARTILE above. The unscoped
# sentence is false of the whole query set, and _load asserts the fact that makes it false.
TITLE_3J = "Top quartile: only coverage clears 80%"


def _achieved_power(effect: float, sd: float, n: int, alpha: float = ALPHA) -> float:
    """Reimplementation of src/experiments/exp16_common.power_two_sided.

    Power of a two-sided one-sample (paired-difference) test at the OBSERVED effect and s.d.,
    normal approximation. Present so the loader can assert that the achieved_power column is
    this quantity and not some other one, which is what licenses the axis label.
    """
    from scipy.stats import norm
    if not (np.isfinite(effect) and np.isfinite(sd)) or sd <= 0 or n < 2:
        raise ValueError(f"power undefined for effect={effect}, sd={sd}, n={n}")
    z = abs(effect) / (sd / np.sqrt(n))
    zcrit = norm.ppf(1.0 - alpha / 2.0)
    return float(norm.cdf(z - zcrit) + norm.cdf(-z - zcrit))


def _load():
    """Return [(drawn name, n, achieved power), ...] for the Q4 rows, everything checked.

    Five assertions, one per statement the panel makes in words:
      * the file carries exactly one Q4 row for each of the two metrics;
      * Q4 really is the highest-divergence quartile, per divergence_stratified.csv;
      * the per-metric n agree between the two files;
      * achieved_power is the power of the OBSERVED gap, reproduced here from mean, s.d. and n;
      * MoA-nDCG clears the rule over ALL queries, which is what the title's stratum prefix is
        there to prevent a reader from denying.
    """
    pw_all = pd.read_csv(POWER_CSV)
    pw = pw_all[pw_all["stratum"] == STRATUM]
    assert len(pw), (f"{POWER_CSV} carries no {STRATUM} row; strata present: "
                     f"{sorted(set(pw_all['stratum']))}")
    assert set(pw["metric"]) == {m for m, _ in METRICS}, (
        f"{STRATUM} metrics are {sorted(set(pw['metric']))}, not the two this panel draws")
    assert len(pw) == len(METRICS), f"expected one {STRATUM} row per metric, got {len(pw)}"

    st_all = pd.read_csv(STRAT_CSV)
    st = st_all[st_all["stratum"] != "ALL"]

    out = []
    for metric, name in METRICS:
        row = pw[pw["metric"] == metric].iloc[0]
        n = int(row["n"])
        power = float(row["achieved_power"])

        sub = st[st["metric"] == metric]
        top = str(sub.loc[sub["divergence_median"].idxmax(), "stratum"])
        assert top == STRATUM, (
            f"{metric}: the highest-divergence stratum is {top}, not the {STRATUM} this panel "
            f"names 'highest response-divergence quartile'")
        n_strat = int(sub.loc[sub["stratum"] == STRATUM, "n"].iloc[0])
        assert n_strat == n, f"{metric}: n disagrees between the two exp17 files, {n_strat} vs {n}"

        recomputed = _achieved_power(float(row["observed_mean_gap"]), float(row["sd_gap"]), n)
        assert abs(recomputed - power) < 1e-9, (
            f"{metric}: achieved_power {power} is not the power of the observed gap "
            f"({recomputed}); the axis label 'at the observed gap' would be false")
        assert 0.0 <= power <= 1.0, f"{metric}: power {power} outside [0, 1]"
        out.append((name, n, power))

    # The title, half one. "only coverage clears 80%" is true exactly when the coverage row
    # clears the drawn rule inside this stratum and the MoA-nDCG row does not.
    (_, _, p_cov), (_, _, p_moa) = out
    assert p_cov >= POWER_RULE > p_moa, (
        f"the panel title says that in {STRATUM} only coverage clears {POWER_RULE:.0%}; the file "
        f"says coverage {p_cov:.4f}, MoA-nDCG {p_moa:.4f}")

    # The title, half two: "Top quartile:". The prefix is load-bearing, not a courtesy, because
    # the same MoA-nDCG evaluator DOES clear the rule over the whole query set, where its gap is
    # negative. Without this check the prefix could be dropped in a later edit and the sentence
    # would become a false statement about the study rather than a true one about the stratum.
    moa_key = METRICS[1][0]
    whole = st_all[(st_all["metric"] == moa_key) & (st_all["stratum"] == "ALL")]
    assert len(whole) == 1, f"{STRAT_CSV} carries {len(whole)} ALL rows for {moa_key}, expected 1"
    whole = whole.iloc[0]
    p_whole = _achieved_power(float(whole["mean_gap"]), float(whole["sd_gap"]), int(whole["n"]))
    assert p_whole >= POWER_RULE, (
        f"the title is prefixed 'Top quartile:' because {moa_key} clears {POWER_RULE:.0%} over "
        f"all {int(whole['n'])} queries and so the unscoped sentence would be false; it now "
        f"reaches only {p_whole:.4f}, so the prefix no longer carries the sentence and the title "
        f"must be re-derived rather than left standing")
    return out


def draw_3j(ax):
    """Achieved power at the observed gap, highest-divergence quartile: a two-dot gauge."""
    rows = _load()
    ys = [0.70, 0.12]                      # the two dot rows, top row first
    dy = 0.075                             # labels sit ABOVE their lead, never across it
    x_lo, x_hi = -0.025, 1.055             # room for a dot sitting at power 1.0

    # A hairline lead from zero to each dot: enough to say how much of [0, 1] the power fills,
    # thin enough not to become the two bars this diagnostic does not deserve.
    for y, (_, _, power) in zip(ys, rows):
        ax.plot([0.0, power], [y, y], color=FAINT, lw=0.8, solid_capstyle="butt", zorder=1)

    # The rule stops just under the upper row's label rather than running the full height: it
    # only has to say which side of 0.80 each dot is on, and at full height it crowds the 0.9999.
    ax.vlines(POWER_RULE, 0.0, max(ys) + dy, color=SHARED, lw=0.8, ls=(0, (2.6, 2.0)), zorder=2)
    ax.text(POWER_RULE - 0.022, 0.47, f"{POWER_RULE:.0%} power", ha="right", va="center",
            fontsize=PT_SMALL, color=SHARED)

    for y, (name, n, power) in zip(ys, rows):
        ax.scatter([power], [y], s=MS_DOT, color=SHARED, lw=0, zorder=4, clip_on=False)
        # The value goes on the side of the dot that has room, which differs by row: the
        # coverage dot sits at the right end of the axis, the MoA-nDCG dot at the left end.
        right_end = power > 0.5
        ax.text(power - 0.030 if right_end else power + 0.030, y + dy,
                f"{power:.4f}", ha="right" if right_end else "left", va="bottom",
                fontsize=PT_ANNOT, color=TEXT, zorder=5)
        # The name goes in that row's empty half, so nothing crosses the reference rule.
        ax.text(0.015 if right_end else 0.28, y + dy, f"{name}, n = {n}", ha="left", va="bottom",
                fontsize=PT_ANNOT, color=TEXT, zorder=5)

    bare_axes(ax, keep=("bottom",))
    ax.spines["bottom"].set_bounds(0.0, 1.0)
    ax.set_xlim(x_lo, x_hi)
    ax.set_ylim(0.0, 1.0)
    ax.set_yticks([])
    ax.set_xticks([0.0, 0.5, 1.0])
    ax.set_xticklabels(["0", "0.5", "1"], fontsize=PT_TICK)
    ax.tick_params(axis="x", length=1.8, pad=1.4)
    # Two lines because both are load-bearing: the numbers are power AT THE OBSERVED GAP, and
    # they are the top divergence quartile rather than the whole query set.
    ax.set_xlabel("achieved power at the observed gap\nhighest response-divergence quartile",
                  fontsize=PT_TICK, color=SUBTLE, labelpad=1.0, linespacing=1.18)
    title(ax, TITLE_3J)
    return ax


if __name__ == "__main__":
    # The house rcParams the composite sets, applied here too. Without them the standalone falls
    # back to DejaVu Sans, which is about 18% wider than the deck's Arial/Liberation stack, and
    # the title overruns the 3.20 in box in this preview while fitting in the real figure. A
    # preview that lies about fit is worse than no preview.
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from figstyle import apply_style
    from fig3_style import PT_TITLE
    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))

    # The printed geometry of panel j: a 3.20 x 0.95 in box holding a 2.36 x 0.57 in axes, plus
    # the assemble file's 0.24 in letter block, which is the band the drawn title sits in.
    box_w, box_h, block = 3.20, 0.95, 0.24
    fig = plt.figure(figsize=(box_w, box_h + block))
    draw_3j(fig.add_axes([0.74 / box_w, 0.38 / (box_h + block),
                          2.36 / box_w, 0.57 / (box_h + block)]))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "3j.png")
    # Pin the export to the authored canvas. The house rcParams set savefig.bbox = "tight",
    # which would crop this preview back to the ink and hide exactly what it exists to show:
    # whether the panel's title and axis label fit inside the printed 3.20 x 1.19 in box.
    fig.savefig(out, dpi=300, bbox_inches=fig.bbox_inches)
    print(f"wrote {out}")
