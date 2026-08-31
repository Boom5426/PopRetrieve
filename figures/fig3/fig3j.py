"""PopRetrieve Figure 3 panel 3j: what size of gap was within reach in the top divergence quartile?

WHAT THIS PANEL SHOWS
---------------------
In the highest quartile of true response divergence, the stratum the pre-specified gate says the
population advantage should be largest in, two achieved powers computed at the gap each Class-B
evaluator actually observed there: minority-state coverage 0.9999 at n = 191, MoA-nDCG 0.0562 at
n = 143. One dot lands to the right of the conventional 0.80 rule and one to the left of it, and
that contrast is the whole panel. Both numbers are recomputed at draw time from the source columns
rather than read from the achieved_power column alone, and the relationship the caption states is
asserted in code before anything is drawn, so no label can outlive its data.

THE 2026-08-31 PASS: THE SENTENCE IS GONE
-----------------------------------------
This panel used to set the phrase "Top quartile: only coverage clears 80%" over itself through
fig3_style.title(). That helper is deleted (its former site in fig3_style carries the reasoning)
and fig3_assemble._assert_no_titles now refuses to build a figure in which any panel draws text
above PT_ANNOT. Thirteen conclusion sentences on one page is thirteen claims competing for the
reader, so the phrase moved into the caption, where it costs no page height and can be qualified.

Only four kinds of text remain here: the two metric names with their n, the two power values, the
reference rule's "80% power", and the axis name with its three tick labels. Removing the sentence
returned height to the row, and it was spent on the marks rather than on new text:

  * the two dot rows moved apart, from 0.331 in of separation to 0.353 in, which is the gap the
    two 7.2 pt row labels needed and did not have;
  * the lower lead lifted from 0.068 in above the x axis to 0.107 in, so its dot no longer reads
    as sitting on the spine, and the rule both dots are judged against is 0.059 in longer
    (0.442 to 0.501 in);
  * nothing was enlarged. The dot is still MS_DOT, the lead is still a 0.8 pt hairline, and no
    type moved off the 7.2 / 6.8 / 6.5 ladder.

The claim the deleted phrase made is not restated anywhere on the panel. It is carried by the
drawing: two dots on one [0, 1] gauge, on opposite sides of a dashed rule that is named.

WHY THE AXIS LABEL NAMES THE QUARTILE, RATHER THAN LEAVING THE SCOPE TO THE CAPTION
-----------------------------------------------------------------------------------
Because the unscoped reading is false of the study, and false in the direction that flatters the
paper least. MoA-nDCG is not a blunt instrument in this design. Over all 600 queries its mean gap
is -0.0371 at s.d. 0.1959, which is achieved power 0.996 and Wilcoxon p = 2.5e-4; in Q1 it is
-0.0822 at power 0.999, in Q2 0.702, in Q3 0.249. The evaluator resolves MoA-nDCG gaps when they
are large, and what it cannot resolve is a gap the size of Q4's +0.0032. So "only the coverage gap
is detectable", read as a statement about the mechanism-recovery comparison rather than about this
stratum, is not a cautious reading of the panel: it is a wrong one, because the whole-query
MoA-nDCG gap IS resolved and it runs the other way, toward mean retrieval. Q4 is not a flattering
subset picked after the fact, it is the stratum the gate pre-specified and the one panel k draws,
but the panel must still say which queries these two dots are. The stratum is therefore the second
line of the x label, which is a scope statement and not a conclusion, and _load asserts against
divergence_stratified.csv both that Q4 really is the highest-divergence quartile and that
MoA-nDCG clears the rule over all queries, which is the fact that makes the scoping load-bearing
rather than decorative.

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
    checks that scoping line against the sentence it is there to prevent.
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
2. THE TWO ROW NAMES ARE NOT SET FROM A COMMON LEFT MARGIN. Each name goes in its row's empty
   half so that neither crosses the rule: the coverage name is left-aligned at x = 0.015, and the
   MoA-nDCG name is RIGHT-aligned at the rule less NAME_PAD, which is where it already sat. The
   alignment differs on purpose. A left edge fixed at 0.28 put the name clear of the rule only
   for the string "MoA-nDCG, n = 143"; right-aligning against the rule makes "nothing crosses the
   rule" true of any name, and moves the remaining failure mode, a collision with the value
   label, into something the preview harness measures. A reader could still want one label
   column, which would cost the panel a left margin it does not have at 2.36 in.
3. THE TWO DOTS ARE NOT COMPUTED ON THE SAME QUERIES. Both are the Q4 stratum, but MoA-nDCG is
   undefined for 48 of its 191 queries, so it is a 143-query subset. The n are on the panel for
   that reason; they also block the misreading that the low power is a sample-size difference,
   which 143 against 191 cannot produce.
4. BOTH DOTS ARE SHARED GREY. Neither is a retrieval method: both are evaluators judging the same
   rankings, so neither may take POP blue or MEAN orange. The retired Extended Data version
   (figures/edfigs/ed_panels.draw_ed2a) drew MoA-nDCG in mean-retrieval orange and minority
   coverage in population blue, which said these were two competing methods. They are not, and
   nothing here is a signed difference either, so no half-plane wash applies.
5. 0.80 IS A CONVENTION, NOT A PRE-REGISTERED CRITERION OF THIS STUDY. It is drawn as a dashed
   reference and named once beside it, in per-cent because that is how the convention is stated.
   A reader who rejects the convention can ignore the rule and read the two powers off the axis;
   nothing else on the panel depends on it, now that the panel states no verdict in words.
6. POWERS ARE PRINTED TO FOUR DECIMALS. 0.99992 printed as "1.00" would read as an exactness the
   estimate does not have, and 0.056191 needs the precision to be distinguishable from zero.
7. THE HAIRLINE LEAD FROM ZERO TO EACH DOT is a fifth element the brief for this panel did not
   ask for: axis, two dots, one rule. It is kept at 0.8 pt in FAINT because without it the two
   dots do not read as fractions of the same [0, 1] gauge, and it is a hairline rather than a bar
   because a bar would give a statistical diagnostic the ink of a result.
8. THE AXIS LABEL IS SET AT PT_TICK (6.8), not at PT_ANNOT. It is an axis name, which is what
   PT_TICK is for, and it is two lines because both are load-bearing. The preview harness cannot
   check it either way: ax.xaxis reports a zero-size window extent, so neither the tick labels nor
   the axis label are ever measured against the panel box. Measured by hand against the current
   ledger (row 1.01 in, bottom pad 0.38 in) the label's lower edge clears the box bottom by
   0.0226 in at 6.8 pt and by 0.0103 in at 7.2 pt. The previous version of this note claimed 7.2
   pt overflowed the box by 0.011 in; that does not reproduce under the row heights this pass
   left, so the note is corrected rather than repeated. 6.8 stands on the ladder argument and on
   the 0.012 in of clearance it buys, not on an overflow.
9. THE PANEL DOES NOT DRAW THE VARIANCES that explain the two positions (s.d. 0.0135 against
   0.1632, a factor of 12). At 2.36 x 0.63 in a second quantity would crowd the gauge, and the
   ratio belongs to panel k and to this figure's caption.
10. "minority-state coverage" and "MoA-nDCG" are named without their metric class. Both are
   Class B, task-proximal biological, so a class label would separate nothing here.
11. THE WHOLE-QUERY MoA-nDCG ROW IS NOT DRAWN, only asserted. A third dot at power 0.996 on all
   600 queries would make the scoping visible instead of verbal, and would be the honest way to
   show that this evaluator is not blind. The height this pass returned to the row is 0.06 in,
   which is a third of what a legible third row needs, and a whole-query dot would also need its
   own sign annotation to avoid reading as a THIRD null rather than a resolved NEGATIVE gap. It
   remains the first thing to add here if the row ever gains a real 0.2 in.

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
                        SHARED, SUBTLE, TEXT, bare_axes)

POWER_CSV = os.path.join(REPO, "results", "exp17_true_divergence_subset", "power_analysis.csv")
STRAT_CSV = os.path.join(REPO, "results", "exp17_true_divergence_subset",
                         "divergence_stratified.csv")

STRATUM = "Q4"          # the label exp17 gives the top quartile of true_divergence
ALPHA = 0.05            # exp16_common.power_two_sided default, two-sided
POWER_RULE = 0.80       # the conventional criterion, drawn as a reference and named once

# (column name in the source file, the name drawn on the panel). Order is top row first.
METRICS = (("minority_state_coverage", "minority-state coverage"),
           ("moa_ndcg", "MoA-nDCG"))


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

    Five assertions, one per statement the panel makes, in words or in marks:
      * the file carries exactly one Q4 row for each of the two metrics;
      * Q4 really is the highest-divergence quartile, per divergence_stratified.csv;
      * the per-metric n agree between the two files;
      * achieved_power is the power of the OBSERVED gap, reproduced here from mean, s.d. and n;
      * MoA-nDCG clears the rule over ALL queries, which is what the x label's stratum line is
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

    # The drawing, half one: the two dots straddle the drawn rule, coverage above and MoA-nDCG
    # below. The panel no longer says so in words, but the marks do, and the caption does.
    (_, _, p_cov), (_, _, p_moa) = out
    assert p_cov >= POWER_RULE > p_moa, (
        f"this panel draws the two {STRATUM} dots on opposite sides of the {POWER_RULE:.0%} rule; "
        f"the file now says coverage {p_cov:.4f}, MoA-nDCG {p_moa:.4f}, so the marks would no "
        f"longer carry that reading and the panel must be re-derived")

    # The marks, half one and a half: draw_3j branches on whether each dot sits above or below
    # the middle of the gauge, and puts that row's name in the other half. The straddle above
    # pins the coverage dot to the upper half but leaves the MoA-nDCG dot anywhere below 0.80,
    # and at 0.5 to 0.8 its value label would be written over its own name. Assert the branch
    # the drawing takes rather than letting a future value silently stack two labels.
    assert p_moa <= 0.5, (
        f"draw_3j places the {STRATUM} MoA-nDCG name in the RIGHT half because its dot is in the "
        f"left half; the file now says {p_moa:.4f}, so the name and the value would be set on "
        f"the same ink and the row layout must be re-derived")

    # The drawing, half two: the x label's "highest response-divergence quartile" line. That scope
    # is load-bearing, not a courtesy, because the same MoA-nDCG evaluator DOES clear the rule over
    # the whole query set, where its gap is negative. Without this check the line could be dropped
    # in a later edit and the panel would become a false statement about the study rather than a
    # true one about the stratum.
    moa_key = METRICS[1][0]
    whole = st_all[(st_all["metric"] == moa_key) & (st_all["stratum"] == "ALL")]
    assert len(whole) == 1, f"{STRAT_CSV} carries {len(whole)} ALL rows for {moa_key}, expected 1"
    whole = whole.iloc[0]
    p_whole = _achieved_power(float(whole["mean_gap"]), float(whole["sd_gap"]), int(whole["n"]))
    assert p_whole >= POWER_RULE, (
        f"the x label scopes this panel to {STRATUM} because {moa_key} clears {POWER_RULE:.0%} "
        f"over all {int(whole['n'])} queries and so the unscoped reading would be false; it now "
        f"reaches only {p_whole:.4f}, so the scoping no longer carries that work and the panel "
        f"must be re-derived rather than left standing")
    return out


def draw_3j(ax):
    """Achieved power at the observed gap, highest-divergence quartile: a two-dot gauge."""
    rows = _load()
    ys = [0.73, 0.17]                      # the two dot rows, top row first
    dy = 0.075                             # labels sit ABOVE their lead, never across it
    x_lo, x_hi = -0.025, 1.055             # room for a dot sitting at power 1.0
    val_pad = 0.030                        # gap between a dot and its own value
    name_pad = 0.090                       # gap between the rule and a name set against it
    rule_head = 0.010                      # gap between the rule's top and the label above it

    # A hairline lead from zero to each dot: enough to say how much of [0, 1] the power fills,
    # thin enough not to become the two bars this diagnostic does not deserve.
    for y, (_, _, power) in zip(ys, rows):
        ax.plot([0.0, power], [y, y], color=FAINT, lw=0.8, solid_capstyle="butt", zorder=1)

    # The rule runs from the axis to just under the top row's label, so it passes both dots and
    # reads as the one threshold they are judged against, without cutting through the row label
    # that spans it. Its name sits in the band between the two rows, left of the rule, which is
    # the only region no row's text reaches.
    ax.vlines(POWER_RULE, 0.0, max(ys) + dy - rule_head, color=SHARED, lw=0.8,
              ls=(0, (2.6, 2.0)), zorder=2)
    ax.text(POWER_RULE - 0.024, 0.49, f"{POWER_RULE:.0%} power", ha="right", va="bottom",
            fontsize=PT_SMALL, color=SHARED, zorder=3)

    for y, (name, n, power) in zip(ys, rows):
        ax.scatter([power], [y], s=MS_DOT, color=SHARED, lw=0, zorder=4, clip_on=False)
        # The value goes on the side of the dot that has room, which differs by row: the
        # coverage dot sits at the right end of the axis, the MoA-nDCG dot at the left end.
        right_end = power > 0.5
        ax.text(power - val_pad if right_end else power + val_pad, y + dy,
                f"{power:.4f}", ha="right" if right_end else "left", va="bottom",
                fontsize=PT_ANNOT, color=TEXT, zorder=5)
        # The name goes in that row's empty half, so nothing crosses the reference rule. A
        # right-end dot leaves the axis start as the row's only hard edge, so its name is set
        # from there; a left-end dot leaves the RULE as the only hard edge, so its name is set
        # against the rule rather than from a fixed left edge. Set from the left, that name
        # cleared the rule only because "MoA-nDCG, n = 143" happens to be short enough, and
        # nothing here could check it; set from the rule, it cannot cross the rule at any length.
        ax.text(0.015 if right_end else POWER_RULE - name_pad, y + dy, f"{name}, n = {n}",
                ha="left" if right_end else "right", va="bottom",
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
    return ax


if __name__ == "__main__":
    # The house rcParams the composite sets, applied here too. Without them the standalone falls
    # back to DejaVu Sans, which is about 18% wider than the deck's Arial/Liberation stack, and
    # the labels overrun the 3.20 in box in this preview while fitting in the real figure. A
    # preview that lies about fit is worse than no preview.
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from figstyle import apply_style
    from fig3_style import PT_TITLE
    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))

    # The printed geometry of panel j after the sentence was cut: a 3.20 x 1.01 in box holding a
    # 2.36 x 0.63 in axes, plus the assemble file's 0.17 in letter block, which now carries the
    # panel letter and nothing else.
    box_w, box_h, block = 3.20, 1.01, 0.17
    fig = plt.figure(figsize=(box_w, box_h + block))
    draw_3j(fig.add_axes([0.74 / box_w, 0.38 / (box_h + block),
                          2.36 / box_w, 0.63 / (box_h + block)]))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "3j.png")
    # Pin the export to the authored canvas. The house rcParams set savefig.bbox = "tight",
    # which would crop this preview back to the ink and hide exactly what it exists to show:
    # whether the panel's labels and axis label fit inside the printed 3.20 x 1.18 in box.
    fig.savefig(out, dpi=300, bbox_inches=fig.bbox_inches)
    print(f"wrote {out}")
