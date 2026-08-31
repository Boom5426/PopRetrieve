"""Figure 3 panel e: the gate's own reliability axis runs opposite to true response divergence.

WHAT THIS PANEL SHOWS (the argument is the caption's; the panel states no sentence)
-----------------------------------------------------------------------------------
The pre-specified information-condition gate scores each query on a composite
``structure_reliability_score``, and ``src/experiments/exp16_17_verdict.py`` states the design
assumption in one line: "structure_reliability should rise with divergence; if it falls, the gate
is mis-wired on its reliability axis." It falls. Over all 765 stratified queries the rank
association between the diagnostic and the true response divergence it is meant to track is
Spearman rho = -0.21 (P = 3.8e-9), and the binned conditional medians drop from about 0.57 at the
low-divergence end to about 0.46 at the high-divergence end. A diagnostic anti-correlated with the
quantity it exists to detect cannot be a valid trust signal, which is why panels d and f find no
gain concentration and no verdict separation: this panel is the mechanism for both. That reading
is the caption's to make; the panel draws the cloud, the conditional medians and the statistic.

That association is a level difference between the sparse low-divergence tail and the dense bulk
rather than a gradient inside the bulk. Judgement call 3 gives the numbers; the distinction makes
the gate look worse, not better, so the drawn statistic is the pooled one and this docstring
carries the anatomy.

The panel supports the figure's skeleton rather than competing with it. None of the four headline
numbers (+0.129, 0.000, +0.276, +0.097) appears here; this is a diagnosis of the gate that was
supposed to tell a user when population-level retrieval is worth it.

THE 2026-08-31 CUT: THE PANEL LOST ITS SENTENCE AND SPENT IT ON THE MARKS
-------------------------------------------------------------------------
The previous version set the phrase "Assumed to rise, it falls" over the panel through the retired
``fig3_style.title`` helper. Thirteen such phrases on one page is thirteen claims competing for
attention, so the phrase now opens this panel's caption entry, where it can be qualified, and
``fig3_assemble._assert_no_titles`` stops another from coming back. What changed here:

  * ``title()`` and its import are gone; the panel draws no sentence and no bold phrase.
  * The axes grew from 0.58 to 0.65 in high, and the y view no longer reserves a head-room band
    above the highest query for a phrase. Both went to the marks: the drawn y range shrank from
    0.623 to 0.528 while the panel got taller, so the 0.104 fall between the end bin medians now
    spans 0.128 in of the printed page rather than 0.097 in, about a third more.
  * The raw cloud was made smaller and fainter (s 2.2 -> 1.3, alpha 0.20 -> 0.12) and the binned
    medians heavier (opaque markers, a connector at alpha 0.85 rather than 0.55). With no sentence
    to say which mark carries the claim, the drawing has to, so the conditional-median path is now
    the first thing the eye resolves and the cloud is the texture behind it. The cloud is still
    dark enough to show the bin-count imbalance that judgement call 2 depends on.
  * The statistic is bare: "rho = -0.21" over "P = 3.8e-9", set low-left where the fall leaves the
    panel empty. The word "Spearman" moved to the caption with the rest of the prose. Both lines
    are one statistic, so both are set at PT_ANNOT; the p value was at PT_SMALL, which is this
    deck's size for provenance and units, and it made one block print at two sizes.
  * The minus is the literal U+2212 and only the Greek letter is mathtext. The old label set the
    whole string in mathtext, so its minus printed 6.48 pt wide, and its digits printed in the
    math face while every other number in Figure 3 prints in the body face. See MINUS.

WHY THE P VALUE IS PRINTED IN e-NOTATION, WHICH IS NOT THE HOUSE FORM
---------------------------------------------------------------------
"3.8 x 10^-9" cannot be set on this panel. Arial, the figure's resolved face, has no U+207B or
U+2079, so the Unicode superscripts render as missing glyphs; a mathtext superscript prints at
0.7x nominal, which is 5.04 pt at PT_ANNOT and below the 6.5 pt floor, and the PT_EQ 9.3 that
would fix that is above the 7.2 pt cap ``fig3_assemble._assert_no_titles`` now applies to all
panel text. e-notation is the only form left that keeps the exponent honest at 6.5 pt. The
mantissa and the exponent are both computed from the p value and checked against it at draw time.

SOURCE
------
results/exp16_gate_diagnosis/_merged_query_divergence.csv, columns
``structure_reliability_score`` and ``true_divergence``, one row per query key
(split_type, cell_line, heldout_drug, observed_library_fraction, seed), n = 765.
figures/source_data/fig3ef_gate_divergence.csv is a hand-built column view of the same file and is
deliberately NOT read here, so the panel cannot drift from the analysis output.
Every number drawn is computed at draw time; the label sign, the printed p value, the direction of
the binned medians and the row count are asserted, so no label can outlive its data.

COLOUR (and the error this fixes)
---------------------------------
The gate is not a retrieval method and is neither family, so it takes no side of the blue/orange
sign vocabulary. An earlier version of this panel drew the cloud and its fit in COMP_SOFT, the
deck's colour for mean-signature retrieval, which said the gate was the mean method. Everything
here is SHARED grey, separated by weight and opacity rather than by hue. Nothing on this panel is
a signed difference either, so there is no ``sign_field``: both axes are levels, not advantages.

JUDGEMENT CALLS A READER COULD REASONABLY DISAGREE WITH
-------------------------------------------------------
1. BINNED MEDIANS, NOT A REGRESSION LINE. The claim is a rank association, and a least-squares
   line invites reading an inferential linear model that was never fitted or checked. The binned
   medians estimate the same conditional-centre function without that promise, and they show the
   wiggle a straight line hides.
2. EQUAL-WIDTH BINS, NOT EQUAL-COUNT BINS. true_divergence is strongly left-skewed: 78 per cent of
   queries sit above 1.5 and the whole lower tail is 22 per cent. Equal-count bins would put six
   of ten points inside the rightmost 15 per cent of a 1.6 in axis and nine of ten inside the
   rightmost 30 per cent, unreadable at this size, and would sample the conditional median almost
   nowhere else. Equal-width bins sample it evenly across the drawn range, at the cost of unequal
   precision: bin counts run from 7 (around divergence 0.9) to 308 (the top bin). The cloud behind
   the points shows that imbalance directly, and the caption carries the counts. A reader who
   prefers equal precision should read the quantile-binned version, where the ten medians fall
   from 0.548 to 0.460 and the decline is concentrated below divergence 1.55, with the dense bulk
   above it roughly flat; the global rho is the same statistic either way, and it is the statistic
   drawn.
3. WHERE THE ASSOCIATION LIVES. Reported here because it is the first thing an adversarial
   reader will test, and because quoting a pooled number while a subset says something else is the
   error this paper exists to criticise. The pooled rho is carried by the contrast between the
   sparse low-divergence tail and the dense bulk, not by a gradient inside either: above divergence
   1.5 (598 of the 765 queries) rho = +0.02, P = 0.58; at or below it (167 queries) rho = -0.15,
   P = 0.053. So what the panel actually shows is that the diagnostic sits systematically LOWER on
   the high-divergence bulk than on the sparse low-divergence tail, and carries no gradient at all
   inside the range where nearly every query lands. The end-to-end fall is what the pooled
   statistic and the drawn medians both support, and the flat right-hand end is drawn rather than
   hidden: the top two medians are level.
4. HETEROGENEITY BY SPLIT. The sign is stable across cell lines (A549 -0.29, K562 -0.25,
   MCF7 -0.37, each P < 1e-4) and across the two large split types (leave_drug_out -0.25,
   leave_MoA_out -0.26), but it REVERSES on partial_library (n = 45, rho = +0.34, P = 0.02). The
   panel plots the pooled gate because the gate is specified once for all queries, and cell line
   is a shape and never a hue in this figure, so no stratification is drawn. The reversal belongs
   in the caption if a reader challenges the pooled number.
5. EACH POINT SITS AT ITS BIN'S MEDIAN x, not at the bin centre, so no marker is drawn where the
   data are not.
6. THE INTERVAL IS THE BIN'S INTERQUARTILE RANGE, a spread, not a confidence interval. It says how
   wide the diagnostic's distribution is at that divergence, which is the honest counterweight to
   a summary line: the bins overlap heavily and the shift is a shift of a broad distribution. It
   is drawn lighter than the medians it belongs to, because a spread is context and the
   conditional centre is the measurement.
7. THE MEDIANS ARE CONNECTED. A connector at this panel size keeps ten dots from reading as a
   second cloud, and with the panel's sentence deleted it is what carries the direction. It is a
   path through drawn points, not a fit, and it stays thin and behind the markers for that reason.
8. THE DECLINE IS NOT MONOTONE and the panel does not pretend it is: counting bins from the low
   end, the median ticks up at bins 2, 5, 7 and 10. What is asserted, and what the drawn path
   shows, is that the axis falls end to end.
9. TWO FAINT QUERIES SIT BEHIND THE STATISTIC. The low-left corner is the emptiest region of a
   falling cloud, which is why the label sits there, but the block's ink does cover the queries at
   (0.478, 0.400) and (0.603, 0.426). Moving it costs more, counting the queries a block of the
   same size covers when it is inset 0.015 of the view from the edges it is pushed into: 10 in the
   top-left, 44 in the top-right, and 30 above divergence 1.5 for a single one-line band along the
   bottom. Nothing that carries the claim is hidden, and STAT_BOX asserts it: no conditional
   median and no interquartile bar may enter the block, at any padding.
   (These counts replace 17 / 18 / 28, which were measured against the taller pre-cut y view and
   did not survive it. A count that is not recomputed after the view moves is a stale number, so
   the part of the claim that has to hold is now an assertion rather than a sentence.)
10. THE GATE'S 0.40 DECISION THRESHOLD IS NOT DRAWN. It would need a label this panel has no room
   for, and the gate's verdict is panels d and f. What is at issue here is the axis, not the cut.
11. NOT SHOWN, because it is a component-level explanation rather than the claim: the negative sign
   comes from the bootstrap rank-stability term (weight 0.40, rho = -0.42 against divergence), not
   from the energy-disagreement term (weight 0.35, rho = +0.35), so it is not an artifact of the
   retrieval circularity that analysis/audit/audit_circularity.py tested for and did not confirm.

Run standalone: python fig3e.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig3_style import (LW_HAIR, MS_DOT, PT_ANNOT, REPO,  # noqa: E402
                        SHARED, TEXT, bare_axes)

SRC = os.path.join(REPO, "results", "exp16_gate_diagnosis", "_merged_query_divergence.csv")

# "Assumed to rise" is not a property of the data; it is the design assumption the verdict script
# states in one line. The panel no longer draws that phrase, but this docstring and the caption
# both still make the claim, so the sentence stays pinned to its source.
VERDICT_SRC = os.path.join(REPO, "src", "experiments", "exp16_17_verdict.py")
DESIGN_ASSUMPTION = ("structure_reliability should rise with divergence; if it falls, the gate "
                     "is mis-wired on its reliability axis.")

# One row per query. The merged file is already unique on this key; the de-duplication is a
# guarantee, not a repair, and it is asserted below rather than trusted.
QUERY_KEY = ["split_type", "cell_line", "heldout_drug", "observed_library_fraction", "seed"]

N_QUERIES = 765      # the count this figure's README and the Fig. 3 caption both quote
N_BINS = 10          # equal-width bins of true_divergence; see judgement call 2
MIN_PER_BIN = 5      # below this a median is not worth drawing, so the panel refuses to draw

# The view. The y range is set to the data plus the block that holds the statistic, and nothing
# else: with the panel's phrase deleted there is no head-room band left to reserve.
XLIM = (0.33, 1.88)
YLIM = (0.262, 0.790)
# The spines are cut back to the data, so a tick has to fall inside the data range and not merely
# inside the view, or it hangs off the end of the scale it labels. Asserted, because the lower y
# tick clears the smallest drawn score by 0.0008.
XTICKS = [0.5, 1.0, 1.5]
YTICKS = [0.3, 0.5, 0.7]

# Weight ladder. The cloud is texture, the interquartile bars are context, the conditional
# medians are the measurement, and each step is a step up in opacity and in size.
RAW_S, RAW_ALPHA = 1.3, 0.12
IQR_LW, IQR_ALPHA = 1.0, 0.38
PATH_ALPHA = 0.85

# The minus sign is the literal U+2212, never a mathtext "$-$". Measured in this deck's resolved
# face (Arial) at PT_ANNOT, a mathtext minus prints 6.48 pt wide against 4.32 pt for U+2212: it is
# 90 per cent of an em dash and reads as one. fig3d's audit found and fixed the same defect, and
# its docstring carries the same two measurements. Only the Greek letter stays mathtext, because a
# statistic's symbol is italic; the digits stay in the body face like every other number here.
MINUS = "\u2212"

# Where the statistic block sits, in axes fractions, and the box it occupies. STAT_X and the two
# baselines position the text; STAT_BOX is that text's rendered extent, measured once at PT_ANNOT
# on this panel's 1.60 x 0.65 in rect and padded outward, and it is what judgement call 9 is
# asserted against. Both lines are drawn from these constants, so the guard cannot describe a
# block that is no longer where the text is.
STAT_X = 0.018
# The two lines are separate artists so the rho keeps its mathtext and the P label can carry
# its own formatting. Their spacing is therefore a layout constant, not a linespacing, and it
# was set against a 0.65 in axes. The 2026-08-31 hierarchy pass took this panel to 0.58 in,
# which is a 0.07 in loss on a gap that was 0.145 axes units, and the two boxes then
# overlapped by 17 per cent of the smaller one. Reopened to 0.205 axes units, which is
# 0.119 in at the current height, the same PRINTED gap the pair had before the shrink.
STAT_Y_RHO, STAT_Y_P = 0.210, 0.005
STAT_BOX = (0.000, 0.336, 0.000, 0.374)
# What the block is allowed to cover: the ink itself sits over two raw queries, and the guard box
# is padded outward by 0.03 of the view, which admits a third at (0.68, 0.45). No conditional
# median and no interquartile bar may enter it at all, which is the part that matters: the block
# may sit on texture, never on the measurement. Every alternative corner covers more raw queries;
# judgement call 9 carries the counts.
STAT_MAX_COVERED = 3


def _load():
    """Return the one-row-per-query view of the gate diagnosis table."""
    raw = pd.read_csv(SRC)
    kept = raw.dropna(subset=["structure_reliability_score", "true_divergence"])
    assert len(kept) == len(raw), (
        f"{SRC} was expected to score every query on both axes; {len(raw) - len(kept)} of "
        f"{len(raw)} rows are missing structure_reliability_score or true_divergence. Decide what "
        f"a missing score means before this panel summarises the rest.")
    u = kept.drop_duplicates(subset=QUERY_KEY)
    assert len(u) == len(kept), (
        f"{SRC} was expected to hold one row per query key; "
        f"{len(kept)} rows collapsed to {len(u)}.")
    assert len(u) == N_QUERIES, (
        f"panel e is drawn and captioned for n = {N_QUERIES} queries, found {len(u)}. "
        f"Update the caption and this constant together, or the panel is lying about its n.")
    return u


def _assert_design_assumption():
    """Pin "assumed to rise" to the line of code that states it.

    The panel no longer draws the phrase, but this module's docstring and the figure caption both
    assert what the gate was DESIGNED to do, which no column of the data can confirm. If that
    sentence leaves the verdict script, the claim has lost its source, so the panel refuses to
    draw rather than standing behind a design that is gone.
    """
    with open(VERDICT_SRC, encoding="utf-8") as fh:
        flat = " ".join(fh.read().replace("#", " ").split())
    assert DESIGN_ASSUMPTION in flat, (
        f"panel e's caption says the gate's reliability axis was ASSUMED to rise, on the authority "
        f"of one sentence in {VERDICT_SRC}, which no longer states it. Re-source that claim or "
        f"rewrite it.")


def _signed(v, nd=2):
    """Format ``v`` with the deck's literal minus, and check the string against the number.

    The same discipline as ``_p_label``: the drawn digits are read back and compared to the value
    they claim to print, so a formatting change cannot quietly alter the statistic.
    """
    shown = f"{MINUS if v < 0 else ''}{abs(v):.{nd}f}"
    assert abs(float(shown.replace(MINUS, "-")) - v) <= 0.5 * 10.0 ** -nd, (
        f"the printed value {shown} does not round-trip to the computed {v:.6f}.")
    return shown


def _p_label(pval):
    """Format a p value as "P = <mantissa>e<exponent>", and check the string against the number.

    The exponent form, not the house "3.8 x 10^-9", for the reason in the module docstring: no
    superscript can be set on this panel at or above the 6.5 pt floor.
    """
    assert 0.0 < pval < 1e-3, (
        f"panel e prints its p value in e-notation, which is only the right form for a small "
        f"p; p = {pval:.3g}. Print a decimal instead.")
    exponent = int(np.floor(np.log10(pval)))
    mantissa = pval / 10.0 ** exponent
    shown = float(f"{mantissa:.1f}") * 10.0 ** exponent
    assert abs(shown - pval) <= 0.05 * pval, (
        f"the printed p value {shown:.3g} does not round-trip to the computed {pval:.3g}.")
    return f"$P$ = {mantissa:.1f}e{exponent}"


def _binned_medians(x, y):
    """Conditional median and interquartile range of ``y`` in N_BINS equal-width bins of ``x``.

    Returns (x at the bin median, y median, y first quartile, y third quartile, count).
    """
    edges = np.linspace(x.min(), x.max(), N_BINS + 1)
    which = np.clip(np.digitize(x, edges[1:-1]), 0, N_BINS - 1)
    xm, ym, lo, hi, n = [], [], [], [], []
    for b in range(N_BINS):
        m = which == b
        assert m.sum() >= MIN_PER_BIN, (
            f"bin {b} of true_divergence holds {int(m.sum())} queries, under the {MIN_PER_BIN} "
            f"this panel will summarise; re-choose N_BINS rather than drawing the median anyway.")
        xm.append(np.median(x[m]))
        ym.append(np.median(y[m]))
        q1, q3 = np.percentile(y[m], [25, 75])
        lo.append(q1)
        hi.append(q3)
        n.append(int(m.sum()))
    return (np.array(xm), np.array(ym), np.array(lo), np.array(hi), np.array(n))


def draw_3e(ax):
    """The gate's structure-reliability axis against the divergence it is meant to track."""
    _assert_design_assumption()
    u = _load()
    x = u["true_divergence"].to_numpy(dtype=float)
    y = u["structure_reliability_score"].to_numpy(dtype=float)

    rho, pval = spearmanr(x, y)
    # The drawn statistic states a significant negative rank association, and the caption reads it
    # as a fall. Both are pinned to the data here so neither can outlive it.
    assert rho < 0.0 and pval < 0.05, (
        f"panel e draws a significant NEGATIVE rank association, found rho = {rho:+.4f}, "
        f"P = {pval:.3g}. Rewrite the caption and the label before redrawing.")

    xm, ym, q1, q3, _ = _binned_medians(x, y)
    assert ym[-1] < ym[0], (
        f"the caption reads the binned medians as falling across the divergence range, but the "
        f"top bin median {ym[-1]:.4f} is not below the bottom bin median {ym[0]:.4f}.")

    # The view must hold every query and every interquartile bar, or the panel is cropping its
    # own evidence to fit a label.
    assert YLIM[0] < min(y.min(), q1.min()) and max(y.max(), q3.max()) < YLIM[1], (
        f"the y view {YLIM} clips the drawn data: scores run {y.min():.3f} to {y.max():.3f} and "
        f"the interquartile bars run {q1.min():.3f} to {q3.max():.3f}.")
    assert XLIM[0] < x.min() and x.max() < XLIM[1], (
        f"the x view {XLIM} clips divergences running {x.min():.3f} to {x.max():.3f}.")

    # Judgement call 9, asserted rather than asserted-in-prose: the corner the statistic sits in
    # must stay the empty one. The block may cover a few faint queries; it may never cover a
    # conditional median or any part of an interquartile bar, which are what the panel measures.
    bx0, bx1, by0, by1 = STAT_BOX
    sx0, sx1 = (XLIM[0] + b * (XLIM[1] - XLIM[0]) for b in (bx0, bx1))
    sy0, sy1 = (YLIM[0] + b * (YLIM[1] - YLIM[0]) for b in (by0, by1))
    covered = int(((x >= sx0) & (x <= sx1) & (y >= sy0) & (y <= sy1)).sum())
    assert covered <= STAT_MAX_COVERED, (
        f"the statistic block now sits over {covered} queries, above the {STAT_MAX_COVERED} "
        f"judgement call 9 accounts for. Re-read the corner counts before leaving it there.")
    on_marks = [(float(a), float(b)) for a, b, lo, hi in zip(xm, ym, q1, q3)
                if sx0 <= a <= sx1 and lo <= sy1 and hi >= sy0]
    assert not on_marks, (
        f"the statistic block covers the conditional medians or interquartile bars at {on_marks}. "
        f"It may sit on the cloud; it may not sit on the measurement.")

    # The raw cloud stays behind everything, small and faint: it is what makes the unequal bin
    # counts visible, and it must not compete with the medians drawn on top of it.
    ax.scatter(x, y, s=RAW_S, color=SHARED, alpha=RAW_ALPHA, edgecolors="none", linewidths=0,
               zorder=1)

    # Interquartile range of the diagnostic inside each divergence bin: a spread, not a CI.
    ax.vlines(xm, q1, q3, color=SHARED, lw=IQR_LW, alpha=IQR_ALPHA, zorder=3)
    # A path through the drawn medians, not a fitted line (judgement call 7).
    ax.plot(xm, ym, color=SHARED, lw=LW_HAIR, alpha=PATH_ALPHA, zorder=4, solid_capstyle="round")
    ax.scatter(xm, ym, s=MS_DOT, color=SHARED, edgecolors="white", linewidths=0.5, zorder=5)

    ax.set_xlim(*XLIM)
    ax.set_ylim(*YLIM)
    assert all(x.min() <= t <= x.max() for t in XTICKS), (
        f"an x tick in {XTICKS} lies outside the drawn divergences {x.min():.3f} to "
        f"{x.max():.3f}, where the bottom spine now stops; it would label nothing.")
    assert all(y.min() <= t <= y.max() for t in YTICKS), (
        f"a y tick in {YTICKS} lies outside the drawn scores {y.min():.4f} to {y.max():.4f}, "
        f"where the left spine now stops; it would label nothing.")
    ax.set_xticks(XTICKS)
    ax.set_yticks(YTICKS)
    bare_axes(ax)
    # The view carries the statistic block, so the spines stop where the data do.
    ax.spines["left"].set_bounds(y.min(), y.max())
    ax.spines["bottom"].set_bounds(x.min(), x.max())

    ax.set_xlabel("true response divergence", fontsize=PT_ANNOT, labelpad=1.5)
    ax.set_ylabel("gate structure\nreliability", fontsize=PT_ANNOT, labelpad=1.5, linespacing=1.15)

    # The statistic, bare, in the corner the falling cloud leaves empty. "Spearman" is the
    # caption's word. Both lines are one statistic, so both are set at one size.
    ax.text(STAT_X, STAT_Y_RHO, f"$\\rho$ = {_signed(float(rho))}", transform=ax.transAxes,
            fontsize=PT_ANNOT, color=TEXT, ha="left", va="bottom")
    ax.text(STAT_X, STAT_Y_P, _p_label(float(pval)), transform=ax.transAxes,
            fontsize=PT_ANNOT, color=TEXT, ha="left", va="bottom")
    return ax


if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    sys.path.insert(0, os.path.join(REPO, "figures"))
    from figstyle import apply_style
    from fig3_style import PT_TICK, PT_TITLE

    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    # apply_style sets savefig.bbox = "tight", which would crop this preview back to its ink and
    # hand back a PNG at a different scale from the printed panel. Keep the canvas, so 3e.png is
    # a 1:1 reproduction of the box panel e occupies in fig3_assemble.
    plt.rcParams["savefig.bbox"] = None
    # 0.42 in of bottom pad plus 0.65 in of axes is the row's 1.07, and 0.17 is LETTER_BLOCK. The
    # canvas was 1.31 while the panel drew a phrase above itself; that head room went with it.
    fig = plt.figure(figsize=(2.40, 1.24))
    draw_3e(fig.add_axes([0.70 / 2.40, 0.42 / 1.24, 1.60 / 2.40, 0.65 / 1.24]))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "3e.png")
    fig.savefig(out, dpi=300)
    print(f"wrote {out}")
