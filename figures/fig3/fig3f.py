"""Figure 3 panel f: true response divergence, split by the gate's own verdict.

WHAT THIS PANEL SHOWS
---------------------
The pre-specified information-condition gate issues one verdict per query, and the point of that
verdict is to say when a query is divergent enough for population-level retrieval to be worth its
cost. Split the 765 stratified queries by that verdict and the gate is wrong in the direction it
cares about. The 133 queries it declined with ``mean_or_no_call`` are MORE divergent than the 621
it recommended, not less: medians 1.69 against 1.66, Mann-Whitney two-sided p = 0.001, and a
recommended query is the more divergent of a random pair only 41 per cent of the time (bootstrap
95 per cent interval 0.36 to 0.46, entirely below the 0.5 the gate's premise requires). The 11
queries it declined as ``mean_sufficient`` sit far below both other groups: every one of them is
under the fifth percentile of the recommended queries (1.03) and of the no-call queries (1.48),
and their median is 0.51. On those eleven the gate was right.

Both facts are DRAWN rather than stated. The 133 are the lower silhouette, whose bulk starts
further right than the upper one (first quartile 1.63 against 1.52, so its interquartile bar is
both shorter and further right) and whose median tick stands to the right of the upper median
tick. The 11 are eleven ticks far to the left of both. The reader takes the direction off the two
silhouettes and the two medians printed on them, and the eleven off their own marks.

This is supporting evidence for panels d and e, not a fifth headline. None of the figure's four
skeleton numbers (+0.129, 0.000, +0.276, +0.097) appears here. Panel e shows the gate's continuous
reliability axis running opposite to divergence; this panel shows that its thresholded verdict
inherits that inversion on the arm where it is actually used.

THE 2026-08-31 PASS: THE PANEL STATES NO CONCLUSION
---------------------------------------------------
This panel used to set the sentence "Inverted on 133, right on 11" over itself through the
now-deleted ``fig3_style.title``. Thirteen such sentences on one page is thirteen claims competing
for one reader, so every one of them has moved into the Fig. 3 caption, where it costs no space
and can be qualified properly. ``fig3_assemble._assert_no_titles`` now refuses to build a figure
in which any panel draws text above PT_ANNOT, so the sentence cannot come back at a smaller size.

Deleting it returned 0.42 in to the six rows and this panel's axes grew from 1.60 x 0.58 to
1.60 x 0.65 in. The height went into the MARKS, not into new text:

  * each silhouette is half again as tall (VH 0.34 -> 0.50 of the panel's unit, 0.15 -> 0.22 in),
    so the shape a reader is asked to compare is actually legible;
  * the middle strip shrank from 0.26 to 0.18 in, because it now holds one line rather
    than being the panel's text shelf;
  * the median tick no longer crosses into that strip. It runs from its own group's baseline into
    its own silhouette, which is where the number it marks belongs, and which leaves the strip to
    the only marks that belong in it, the eleven's own ticks at its lower left;
  * the fills dropped from FAINT to HAIRLINE. A taller silhouette at the old fill would have spent
    the returned height on grey area; the shape is carried by the SHARED outline, and the two
    summaries a reader actually reads off, the interquartile bar and the median tick, are darker
    than either.

What text remains is a group name, a statistic, or the eleven's three-word label:

  recommended / mean or no call   the two rows, in the margin
  n = 621, median 1.66            that row's size and centre, on that row
  n = 133, median 1.69            the same, on the other row
  P = 0.001                       the drawn two-group test, in the strip between the two rows
  11 mean sufficient              the eleven ticks, named where they stand
  true response divergence        the axis

THE POOLED READING IS A NULL, AND THAT NULL IS AN ARTEFACT OF THE POOLING
-------------------------------------------------------------------------
Pool the two decline verdicts into one group of 144 and the comparison collapses to Mann-Whitney
p = 0.09 with a common-language effect size of 0.455, interval 0.40 to 0.51, straddling 0.5. That
looks like an absence, and an earlier cut of this panel drew it as one under the phrase "two
verdicts, one distribution". It is not an absence. It is two opposite effects cancelling: 133
queries stochastically ABOVE the recommended group and 11 far BELOW it, in a group whose smaller
arm is 7.6 per cent of the pool and lies entirely under the fifth percentile of both other groups.
A Kolmogorov-Smirnov test rejects the equal-distribution reading the old phrase asserted
(D = 0.154, p = 0.007), and the old title's own guard, |CLES - 0.5| < 0.05, was never a test of
that phrase: two distributions can be arbitrarily different and still cross at one half.

Manufacturing a null by pooling a mixture is the error this paper exists to criticise, so the
pooled reading is not drawn. It is recomputed and asserted in ``draw_3f``, and the assertion fires
if pooling ever STOPS moving the answer, because at that point this docstring and the caption
would both need rewriting.

WHICH GROUPS ARE DRAWN, AND WHY THEY MATCH PANEL d
--------------------------------------------------
``recommendation_mode`` takes three values: DART_recommended (621), mean_or_no_call (133) and
mean_sufficient (11). The manuscript's two-way comparison, and the comparison panel d plots, is
621 against 133; panel d states the same three counts and asserts the same decomposition. This
panel draws the same split, so d and f do not disagree on what "not recommended" denotes. The
eleven mean-sufficient queries are neither dropped nor merged: they are drawn as eleven ticks on
the lower baseline with a three-word label, so a reader can see exactly which queries a pooled
reading would fold in without the panel making an announcement of them. The arithmetic
144 = 133 + 11 is asserted here and stated in the Fig. 3 caption, along with the pooled statistic
and the name of the test whose P is printed; there is no room for either on a 1.60 x 0.65 in axes,
and the rule for this figure is to cut into the caption rather than to shrink type.

SOURCE
------
results/exp16_gate_diagnosis/_merged_query_divergence.csv, columns ``recommendation_mode`` and
``true_divergence``, one row per query key (split_type, cell_line, heldout_drug,
observed_library_fraction, seed), n = 765. figures/source_data/fig3ef_gate_divergence.csv is a
hand-built column view of the same file and is deliberately NOT read here, so the panel cannot
drift from the analysis output. Every number drawn is computed at draw time; the counts, the
direction of the median difference, the effect size, the separation of the eleven and the fact
that pooling changes the answer are all asserted, so no label can outlive its data.

COLOUR
------
Both silhouettes are grey and identically styled, and the eleven ticks are TEXT ink like the
median ticks, because they are individual observations rather than a summary. Neither group is a
retrieval family: this is the gate's own verdict, which is grey in this figure's vocabulary
wherever it appears. There is no ``sign_field``, because the x axis carries a level (true response
divergence), not a signed population-minus-mean advantage; blue and orange would be a claim about
sign and no sign is plotted. The groups are separated by position and by their direct labels,
never by hue.

JUDGEMENT CALLS A READER COULD REASONABLY DISAGREE WITH
-------------------------------------------------------
1. n IS KEPT ON EACH ROW, though the caption also carries it. Each density is scaled to its own
   maximum (call 5), so nothing in the drawing says that one silhouette is 621 queries and the
   other 133; without the two n a reader can misjudge how much evidence each shape rests on. It is
   a statistic, not a sentence, and it shares the one line each row can hold.
2. THE ELEVEN ARE DRAWN AS RAW POINTS, NOT AS A THIRD DENSITY. Eleven observations do not support
   a kernel estimate at any bandwidth this panel could justify, and a third row does not fit in
   0.65 in without two-line labels colliding. Ticks show every one of the eleven at its own value,
   which is more information than a density would have carried. Three of them fall within 0.0042
   divergence units, about 1.3 dots at 300 dpi, and merge into one mark at this width, which is
   why the count is printed rather than left to be counted.
3. THE DRAWN TEST EXCLUDES THE ELEVEN. It is the manuscript's pre-specified two-way comparison and
   the one panel d plots, so this is not a subset chosen after seeing the answer. The excluded
   queries are nonetheless on the panel, and the pooled statistic is asserted in code and stated
   in the caption, which is the disclosure the exclusion requires.
4. THE PRINTED STATISTIC IS "P = 0.001" WITHOUT THE TEST'S NAME. The strip has 1.29 in to the
   right of the eleven ticks, and it has to hold their label as well; "Mann-Whitney P = 0.001"
   measures 1.15 in at PT_ANNOT on its own, so naming the test on the panel would have cost the
   eleven their label. The test is named in the caption and in this docstring, and a reader who
   needs to know which test it is is reading the caption anyway.
5. MIRRORED KERNEL DENSITIES RATHER THAN BOXES. A box at this size is five summary statistics per
   group; the shapes plus an interquartile bar and a median tick on each baseline carry the same
   information and let the reader see how far the two silhouettes overlap.
6. ONE ABSOLUTE BANDWIDTH FOR BOTH SILHOUETTES, Silverman's rule on all 765 queries, rather than
   each group's own rule. Per-group rules differ by (621/133) ** 0.2 = 1.36, so the smaller group
   would be drawn smoother and part of any apparent shape difference would be the estimator. The
   medians, the interquartile bars and the test, which carry the claim, do not depend on it.
7. EACH DENSITY IS SCALED TO ITS OWN MAXIMUM, so the two silhouettes are comparable in shape and
   NOT in area. See call 1 for what compensates.
8. THE X LIMITS ARE PADDED ASYMMETRICALLY, 1.5 per cent of the range below the minimum and 4.5
   per cent above the maximum. The left edge has only to clear the leftmost of the eleven ticks, a
   0.7 pt line; the right edge has to clear two density tails. The asymmetry buys 0.04 in of strip
   width, which is the difference between the eleven's label and the statistic reading as two
   items and reading as one run of text.
9. THE PANEL NO LONGER SAYS "inverted" OR "right", IN ANY WORDS. Both were the deleted sentence's,
   and both are claims: that the ordering the gate delivers is the reverse of the one it promises
   (the effect is small in divergence units, 0.029 of median, but its interval excludes 0.5 from
   below), and that declining eleven queries which all sit under the fifth percentile of both
   other groups is what the gate's premise says it should do. The panel now draws the evidence for
   both, two silhouettes whose medians and bulk sit the wrong way round and eleven ticks stranded
   at the low end, and leaves the two words to the caption. The direction is readable without
   them: the lower silhouette is the more divergent one, and the eleven are visibly not.
10. NOT DRAWN: the gate's 0.40 decision threshold and its reliability axis. Those are panel e.
   What is at issue here is the verdict, not the axis, and one panel should carry one of them.
   Also not drawn: whether the eleven lost anything in outcome, which is panel d's measurement,
   not this one's; panel d reports their median regret reduction as exactly 0.000.
11. MIRRORED HALVES, ON A FIGURE WHOSE VOCABULARY USES HALF-PLANES FOR SIGN. Up and down here are
   two groups, not two signs. Three things hold them apart: there is no wash behind either half,
   both halves are the same grey, and the x axis carries a level rather than a signed advantage,
   so there is no zero for a half-plane to be defined against.

Run standalone: python fig3f.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
from matplotlib.font_manager import FontProperties
from matplotlib.textpath import TextPath
from scipy.stats import gaussian_kde, mannwhitneyu

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig3_style import (HAIRLINE, LW_HAIR, PT_ANNOT, PT_SMALL, REPO,  # noqa: E402
                        SHARED, TEXT, bare_axes)

SRC = os.path.join(REPO, "results", "exp16_gate_diagnosis", "_merged_query_divergence.csv")

# One row per query. The merged file is already unique on this key; the de-duplication is a
# guarantee, not a repair, and it is asserted below rather than trusted.
QUERY_KEY = ["split_type", "cell_line", "heldout_drug", "observed_library_fraction", "seed"]

N_QUERIES = 765                     # the count this figure's README and the Fig. 3 caption quote
RECOMMENDED = "DART_recommended"    # the gate's positive verdict
NO_CALL = "mean_or_no_call"         # the manuscript's "not recommended" arm; panel d plots it too
SUFFICIENT = "mean_sufficient"      # the third verdict: also a decline, drawn as eleven ticks
N_RECOMMENDED = 621
N_NO_CALL = 133
N_SUFFICIENT = 11
N_DECLINED = N_NO_CALL + N_SUFFICIENT   # every non-recommended verdict, the caption's 144

# Panel geometry, in units where one unit is the height of a full-scale density.
BAND = 0.20      # half-height of the middle strip: the eleven's ticks, their label, the test
VH = 0.50        # drawn height of each density at its own maximum
ROW_Y = BAND + VH / 2.0   # centre of a group's row: its name outside, its n and median inside
MED_LEN = 0.36   # median tick, from the group's own baseline INTO its own silhouette
IQR_LW = 1.4     # the interquartile bar drawn along that baseline
RUG_H = 0.12     # height of one mean-sufficient tick, standing on the lower baseline
LABEL_X = 0.015         # axes fraction: where a row's own statistic starts
RUG_LABEL_X = 0.215     # axes fraction: clear of the rightmost tick, asserted in draw_3f
STAT_X = 0.995          # axes fraction: right edge of the two-group test statistic
PAD_LO, PAD_HI = 0.015, 0.045   # x padding, as a fraction of the data range (judgement call 8)
HEAD = 1.06      # head-room factor, so the tallest point of a density clears the frame
GRID_N = 400

# Minimum clear space between two text blocks that share the middle strip, in inches. At 6.5 pt a
# word space is about 0.018 in, so 0.030 in is the point at which two items stop reading as one.
MIN_GAP_IN = 0.030
# TextPath measures INK. The rendered box adds side bearings, measured at 6.7 per cent of the ink
# width for this figure's face at these sizes; 1.07 is that, rounded up.
W_SAFETY = 1.07


def _load():
    """Return the one-row-per-query view, split into (recommended, no_call, sufficient) arrays."""
    raw = pd.read_csv(SRC)
    u = raw.dropna(subset=["recommendation_mode", "true_divergence"])
    u = u.drop_duplicates(subset=QUERY_KEY)
    assert len(u) == len(raw), (
        f"{SRC} was expected to hold one complete row per query key; "
        f"{len(raw)} rows collapsed to {len(u)}.")
    assert len(u) == N_QUERIES, (
        f"panel f is drawn and captioned for n = {N_QUERIES} queries, found {len(u)}. "
        f"Update the caption and this constant together, or the panel is lying about its n.")

    modes = set(u["recommendation_mode"].unique())
    assert modes == {RECOMMENDED, NO_CALL, SUFFICIENT}, (
        f"panel f draws one group per gate verdict and knows of "
        f"{sorted([RECOMMENDED, NO_CALL, SUFFICIENT])}; the file now carries {sorted(modes)}. "
        f"A new verdict must be placed deliberately, not folded into an existing group.")

    out = {m: u.loc[u["recommendation_mode"] == m, "true_divergence"].to_numpy(float)
           for m in (RECOMMENDED, NO_CALL, SUFFICIENT)}
    counts = {m: len(v) for m, v in out.items()}
    expected = {RECOMMENDED: N_RECOMMENDED, NO_CALL: N_NO_CALL, SUFFICIENT: N_SUFFICIENT}
    assert counts == expected, (
        f"panel f, panel d and the Fig. 3 caption all quote {expected}; this file now has "
        f"{counts}. Re-check both panels and the caption before redrawing.")
    assert sum(counts.values()) == N_QUERIES
    assert counts[NO_CALL] + counts[SUFFICIENT] == N_DECLINED, (
        f"the caption states that {N_DECLINED} queries were not recommended and that this splits "
        f"as {N_NO_CALL} plus {N_SUFFICIENT}; the file now splits it "
        f"{counts[NO_CALL]} plus {counts[SUFFICIENT]}.")
    return out[RECOMMENDED], out[NO_CALL], out[SUFFICIENT]


def _cles(a, b):
    """P(a random draw from ``a`` exceeds one from ``b``), ties split, with the two-sided p.

    The gate's premise needs this above 0.5 for recommended against declined queries.
    """
    u_stat, pval = mannwhitneyu(a, b, alternative="two-sided")
    return float(u_stat) / (len(a) * len(b)), float(pval)


def _pooled_bandwidth(values):
    """Silverman's rule on all 765 queries: one absolute kernel width for both silhouettes.

    Returned in data units, so each group is handed ``h / sd`` as gaussian_kde's ``bw_method``
    and both silhouettes are smoothed identically (judgement call 6).
    """
    sd = float(np.std(values, ddof=1))
    q1, q3 = np.percentile(values, [25, 75])
    spread = min(sd, (q3 - q1) / 1.349)
    assert spread > 0.0, "true_divergence has no spread; a density estimate would be meaningless."
    return 0.9 * spread * len(values) ** (-0.2)


def _text_w_in(s, pt):
    """Width of ``s`` at ``pt``, in inches, WITHOUT a renderer.

    TextPath parses the string with the same font machinery the backends use, so this works
    identically under Agg, PDF and SVG; it measures ink, which W_SAFETY converts to a box.
    """
    ink = TextPath((0, 0), s, size=pt, prop=FontProperties()).get_extents().width
    return W_SAFETY * ink / 72.0


def _axes_size_in(ax):
    """(width, height) of the axes in inches on the printed page."""
    pos = ax.get_position()
    fig_w, fig_h = ax.figure.get_size_inches()
    return pos.width * float(fig_w), pos.height * float(fig_h)


def _half(ax, values, sign, h):
    """Draw one group: a density silhouette, its interquartile bar, its median tick, its statistic.

    The silhouette is evaluated only over the group's OWN observed range, so no density is drawn
    where that group has no query; the flat stretch each curve runs along its baseline is a real
    near-zero density, not a rule added for decoration. The drawn median, the label and the
    evaluated curve are returned so ``_assert_row_label_clears`` can check the text against the
    marks it was drawn over, rather than against an assumption about them.
    """
    grid = np.linspace(values.min(), values.max(), GRID_N)
    density = gaussian_kde(values, bw_method=h / float(np.std(values, ddof=1)))(grid)
    density = density / density.max()

    base = sign * BAND
    top = sign * (BAND + VH * density)
    ax.fill_between(grid, base, top, color=HAIRLINE, lw=0, zorder=1)
    ax.plot(grid, top, color=SHARED, lw=LW_HAIR, zorder=2, solid_capstyle="round")

    q1, med, q3 = (float(v) for v in np.percentile(values, [25, 50, 75]))
    ax.plot([q1, q3], [base, base], color=SHARED, lw=IQR_LW, zorder=3, solid_capstyle="butt")
    # The median tick stays inside its own group's silhouette: the strip between the two groups
    # carries text, and a tick crossing into it would have to share the width of that text.
    ax.plot([med, med], [base, sign * (BAND + MED_LEN)], color=TEXT, lw=1.0, zorder=4,
            solid_capstyle="butt")

    # The n and the median sit ON the group's own row, level with its name in the margin, in the
    # left part of the row where this group's density is flat against its baseline. How far right
    # that text reaches is measured, and the curve it would have to clear is checked against it.
    label = f"n = {len(values)}, median {med:.2f}"
    ax.text(LABEL_X, sign * ROW_Y, label, transform=ax.get_yaxis_transform(),
            ha="left", va="center", fontsize=PT_SMALL, color=TEXT)
    return med, label, grid, density


def _assert_row_label_clears(ax, label, grid, density, per_unit_in, w_in):
    """The row's statistic must not sit on its own density curve.

    Everything here is measured, not assumed: the label's width comes from the font, the panel's
    inches from the axes rect, and the curve from the same array that was drawn.
    """
    x0, x1 = ax.get_xlim()
    end_frac = LABEL_X + _text_w_in(label, PT_SMALL) / w_in
    assert end_frac < 1.0, f"the row statistic {label!r} is wider than the panel ({end_frac:.3f})."
    x_end = x0 + end_frac * (x1 - x0)
    covered = density[grid <= x_end]
    peak = float(covered.max()) if covered.size else 0.0
    # Half the text box, converted from points to the panel's y units.
    half = (0.6 * PT_SMALL / 72.0) / per_unit_in
    assert BAND + VH * peak < ROW_Y - half, (
        f"the row statistic {label!r} reaches axes fraction {end_frac:.3f}, where its own density "
        f"has risen to {BAND + VH * peak:.3f} and the text box starts at {ROW_Y - half:.3f}. "
        f"Shorten the label or move the row.")


def draw_3f(ax):
    """True response divergence by gate verdict: 621 recommended, 133 no-call, 11 sufficient."""
    rec, no_call, suff = _load()

    cles, pval = _cles(rec, no_call)
    med_rec, med_nc, med_suf = (float(np.median(v)) for v in (rec, no_call, suff))

    # The caption says the drawn comparison is INVERTED, so both its direction and its strength
    # are pinned here: the declined arm is the more divergent one, and the effect size is on the
    # wrong side of the half the gate's premise needs. The panel draws this; it does not say it.
    assert med_rec < med_nc, (
        f"the panel and the caption state that the queries the gate declined for no call are the "
        f"MORE divergent ones, but the recommended median {med_rec:.4f} is not below "
        f"{med_nc:.4f}. Rewrite the docstring and the caption before redrawing.")
    assert cles < 0.5 and pval < 0.01, (
        f"the caption calls the {N_NO_CALL}-query comparison inverted, which needs an effect size "
        f"below 0.5 at a p this panel is willing to print; found CLES = {cles:.4f}, "
        f"p = {pval:.3g}.")
    assert 0.0005 <= pval < 0.995, (
        f"P is printed to three decimals and p = {pval:.3g} would print uninformatively.")

    # The eleven are drawn apart from the lower silhouette, so the panel asserts that they really
    # are a separate low cluster rather than a slice of the same population.
    assert suff.max() < np.percentile(rec, 5) and suff.max() < np.percentile(no_call, 5), (
        f"the panel draws the {N_SUFFICIENT} mean-sufficient queries as a separate low cluster "
        f"and the caption calls the gate right about them; their maximum {suff.max():.4f} is no "
        f"longer below the fifth percentile of both other groups "
        f"({np.percentile(rec, 5):.4f}, {np.percentile(no_call, 5):.4f}).")
    assert med_suf < med_rec and med_suf < med_nc

    # The pooled reading is the one this panel refuses to draw, so the reason it refuses is a
    # test, not a sentence: pooling has to move the answer, and if it stops moving it the
    # docstring and the Fig. 3 caption are both wrong.
    declined = np.concatenate([no_call, suff])
    cles_pool, p_pool = _cles(rec, declined)
    assert len(declined) == N_DECLINED
    assert cles_pool > cles and p_pool > 0.05 > pval, (
        f"this panel does not draw the pooled {N_DECLINED}-query reading because pooling the "
        f"{N_SUFFICIENT} mean-sufficient queries cancels the effect: CLES {cles:.4f} -> "
        f"{cles_pool:.4f}, p {pval:.3g} -> {p_pool:.3g}. Pooling no longer does that, so the "
        f"docstring's argument and the caption's pooled statistic must be rewritten.")

    pooled = np.concatenate([rec, declined])
    lo, hi = float(pooled.min()), float(pooled.max())
    span = hi - lo
    h = _pooled_bandwidth(pooled)

    ax.set_xlim(lo - PAD_LO * span, hi + PAD_HI * span)
    ax.set_ylim(-(BAND + HEAD * VH), BAND + HEAD * VH)
    w_in, h_in = _axes_size_in(ax)
    per_unit_in = h_in / (2.0 * (BAND + HEAD * VH))

    drawn_rec, lab_rec, g_rec, d_rec = _half(ax, rec, +1, h)
    drawn_nc, lab_nc, g_nc, d_nc = _half(ax, no_call, -1, h)
    # The medians tested above and the medians labelled on the panel must be the same two numbers.
    assert abs(drawn_rec - med_rec) < 1e-12 and abs(drawn_nc - med_nc) < 1e-12, (
        f"the drawn medians ({drawn_rec:.6f}, {drawn_nc:.6f}) are not the tested medians "
        f"({med_rec:.6f}, {med_nc:.6f}).")
    _assert_row_label_clears(ax, lab_rec, g_rec, d_rec, per_unit_in, w_in)
    _assert_row_label_clears(ax, lab_nc, g_nc, d_nc, per_unit_in, w_in)

    # Every mean-sufficient query, one tick each, standing on the lower group's baseline. Raw
    # observations rather than a summary, so they take TEXT ink like the median ticks.
    ax.vlines(suff, -BAND, -BAND + RUG_H, color=TEXT, lw=0.7, zorder=4)

    # No SUMMARY mark crosses the strip between the two silhouettes: the only ink in it besides
    # text is the eleven's own ticks, standing at its lower left. It holds one line, the eleven's
    # label where the eleven are and the two-group test at the right, between the two medians it
    # compares. Both boxes are measured against the marks and against each other, so neither the
    # label nor the statistic can grow into the other.
    rug_label = f"{len(suff)} {SUFFICIENT.replace('_', ' ')}"
    stat_label = f"$P$ = {pval:.3f}"
    x0, x1 = ax.get_xlim()
    rug_end_in = (suff.max() - x0) / (x1 - x0) * w_in
    lab_start_in = RUG_LABEL_X * w_in
    lab_end_in = lab_start_in + _text_w_in(rug_label, PT_SMALL)
    stat_start_in = STAT_X * w_in - _text_w_in(stat_label, PT_ANNOT)
    assert lab_start_in - rug_end_in >= MIN_GAP_IN, (
        f"the {len(suff)} ticks reach {rug_end_in:.3f} in and their label starts at "
        f"{lab_start_in:.3f} in, closer than the {MIN_GAP_IN} in that keeps a label off the marks "
        f"it names.")
    assert stat_start_in - lab_end_in >= MIN_GAP_IN, (
        f"{rug_label!r} ends at {lab_end_in:.3f} in and {stat_label!r} starts at "
        f"{stat_start_in:.3f} in on a {w_in:.2f} in panel; closer than {MIN_GAP_IN} in and the "
        f"two read as one run of text. Shorten one of them or move it to the caption.")
    ax.text(RUG_LABEL_X, 0.0, rug_label, transform=ax.get_yaxis_transform(),
            ha="left", va="center", fontsize=PT_SMALL, color=TEXT)
    ax.text(STAT_X, 0.0, stat_label, transform=ax.get_yaxis_transform(),
            ha="right", va="center", fontsize=PT_ANNOT, color=TEXT)

    xticks = [0.5, 1.0, 1.5]
    assert all(x0 < t < x1 for t in xticks), f"an x tick lies outside the view: {xticks}"
    ax.set_xticks(xticks)
    ax.set_yticks([ROW_Y, -ROW_Y])
    ax.set_yticklabels(["recommended", "mean or\nno call"], linespacing=1.12)
    bare_axes(ax, keep=("bottom",))
    ax.spines["bottom"].set_bounds(lo, hi)
    ax.tick_params(axis="y", length=0, pad=2.0)

    ax.set_xlabel("true response divergence", fontsize=PT_ANNOT, labelpad=1.5)
    return ax


if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    sys.path.insert(0, os.path.join(REPO, "figures"))
    from figstyle import apply_style
    from fig3_style import PT_TICK, PT_TITLE

    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    # apply_style sets savefig.bbox = "tight", which crops this preview back to its ink and hands
    # back a PNG at a different scale from the printed panel. Keep the canvas, so 3f.png is a 1:1
    # reproduction of the box panel f occupies in fig3_assemble.
    plt.rcParams["savefig.bbox"] = None
    # 0.42 in of bottom pad plus 0.65 in of axes is the row's 1.07, and 0.17 is LETTER_BLOCK.
    fig = plt.figure(figsize=(2.40, 1.24))
    draw_3f(fig.add_axes([0.70 / 2.40, 0.42 / 1.24, 1.60 / 2.40, 0.65 / 1.24]))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "3f.png")
    fig.savefig(out, dpi=300)
    print(f"wrote {out}")
