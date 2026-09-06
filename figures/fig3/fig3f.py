"""PopRetrieve Figure 3 panel 3f: the gate is mis-wired on one axis, and its verdict inherits it.

WHAT THIS PANEL SHOWS
---------------------
One x axis, true response divergence, and two readings of the same gate against it.

  * BELOW, the gate's continuous score. The pre-specified information-condition gate rates each
    query on a composite ``structure_reliability_score``, and
    ``src/experiments/exp16_17_verdict.py`` states the design assumption in one line:
    "structure_reliability should rise with divergence; if it falls, the gate is mis-wired on its
    reliability axis." It falls. Over all 765 stratified queries the rank association is Spearman
    rho = -0.19 (P = 1.5e-07), and the binned conditional medians drop from about 0.57 at the
    low-divergence end to about 0.46 at the high end.
  * ABOVE, the gate's thresholded verdict. The 127 queries it declines with ``mean_or_no_call``
    are MORE divergent than the 627 it recommends, not less: medians 1.68 against 1.66,
    Mann-Whitney two-sided P = 0.009, and a recommended query is the more divergent of a random
    pair only 43 per cent of the time. The 11 it declines as ``mean_sufficient`` stand at the far
    left, every one of them below the fifth percentile of both other groups; on those eleven the
    gate was right.

The two readings share one axis on purpose. A reader can drop a vertical from the declined
group's median tick into the cloud and land where the reliability score is already falling, which
is the whole argument in one movement: the verdict is not a second, independent failure, it is the
continuous failure crossed with a threshold.

WHY THIS IS ONE PANEL AND NOT TWO
----------------------------------
Until 2026-09-03 this was panels e and f. They read the same file, plotted the same 765 queries,
and drew the same quantity on their x axes; the figure paid for that axis twice, printed the same
n twice, and asked the reader to carry a divergence value from one panel to the other by eye.
Merging them costs nothing that was measured and returns a panel slot to the figure, which panel d
now uses for the mechanism-recovery quartiles that used to sit in Figure 5.

THE SILHOUETTES ARE GONE, AND WHAT REPLACES THEM IS NOT A SIMPLIFICATION FOR SPACE
----------------------------------------------------------------------------------
The old panel f drew each verdict group as a kernel density silhouette. In a merged panel that
would draw the same marginal twice: the cloud below IS the divergence distribution, at full
resolution and per query, so a smoothed copy of its x marginal sitting directly above it is
redundant ink competing with the measurement. The strip therefore carries only what the cloud
cannot show, which is the SPLIT: each group's interquartile bar, its median tick, its n, and the
eleven mean-sufficient queries as their own ticks.

The two-group test is unchanged and still asserted, including the reading the panel refuses to
draw: pooling the eleven mean-sufficient queries into the declined arm cancels the effect
(CLES 0.43 to 0.47, P 0.009 to 0.31), so the pooled 138-query reading is a null and the panel
plots the 127-query arm the manuscript defines. That is asserted rather than argued, because if
pooling ever stopped cancelling the effect this docstring would be wrong.

WHAT THE ESTIMATOR REPAIR AND THE EXP16 REMERGE DID
----------------------------------------------------
Both readings weakened and neither changed sign. The continuous association went from
rho = -0.21 (P = 3.8e-09) to rho = -0.19 (P = 1.5e-07); the verdict comparison from
CLES 0.41 at P = 0.001 to CLES 0.43 at P = 0.009. The counts moved with exp12's own gate verdict,
621 / 133 / 11 to 627 / 127 / 11, and the reason the old numbers survived as long as they did is
that exp16 is a pure re-analysis of exp12 and was not in the reissue suite; see
docs/phase2/POST_REPAIR_MASTER_RESULTS.md section A5c. The P < 0.01 gate below now clears by a
factor of about two rather than by ten, which is stated here rather than discovered later.

SOURCE
------
results/exp16_gate_diagnosis/_merged_query_divergence.csv, one row per query, 765 rows. Every
number drawn is computed from that file at draw time; none is a literal.

JUDGEMENT CALLS A READER COULD REASONABLY DISAGREE WITH
-------------------------------------------------------
  1. THE STRIP IS ON TOP AND THE CLOUD BELOW. The cloud is the evidence and gets the height; the
     strip is a summary of a split and gets 0.32 in. Reversing them would put the panel's weakest
     marks in its largest space.
  2. THE ELEVEN ARE DRAWN, not summarised. They are the one place the gate is right, and eleven
     ticks cost less than a sentence saying so.
  3. THE CONDITIONAL MEDIANS ARE A PATH THROUGH DRAWN MEDIANS, not a fitted line. The association
     is a level difference between the sparse low-divergence tail and the dense bulk rather than a
     gradient inside the bulk; a regression line would assert the gradient. The path lets a reader
     see where the fall actually happens, which makes the gate look worse rather than better.
  4. THE PANEL PRINTS TWO STATISTICS, one per reading, and no sentence joining them. The joining
     is the caption's job.
  5. THE SPINES ARE CUT BACK TO THE DATA on the main axes, so a tick that fell outside the drawn
     range would hang off the end of the scale it labels. Asserted, because the lower y tick
     clears the smallest drawn score by less than 0.001.

Run standalone: python3 fig3f.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
from matplotlib.backends.backend_agg import RendererAgg
from scipy.stats import mannwhitneyu, spearmanr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig3_style import (HAIRLINE, LW_HAIR, MS_DOT, PT_ANNOT, PT_SMALL,  # noqa: E402
                        PT_TICK, REPO, SHARED, SUBTLE, TEXT, bare_axes)

SRC = os.path.join(REPO, "results", "exp16_gate_diagnosis", "_merged_query_divergence.csv")

# "Assumed to rise" is not a property of the data; it is the design assumption the verdict script
# states in one line. The panel does not draw that phrase, but this docstring and the caption both
# make the claim, so the sentence stays pinned to its source.
VERDICT_SRC = os.path.join(REPO, "src", "experiments", "exp16_17_verdict.py")
DESIGN_ASSUMPTION = ("structure_reliability should rise with divergence; if it falls, the gate "
                     "is mis-wired on its reliability axis.")

QUERY_KEY = ["split_type", "cell_line", "heldout_drug", "observed_library_fraction", "seed"]

N_QUERIES = 765
RECOMMENDED = "DART_recommended"
NO_CALL = "mean_or_no_call"
SUFFICIENT = "mean_sufficient"
N_RECOMMENDED = 627
N_NO_CALL = 127
N_SUFFICIENT = 11
N_DECLINED = N_NO_CALL + N_SUFFICIENT

N_BINS = 10          # equal-width bins of true_divergence
MIN_PER_BIN = 5      # below this a median is not worth drawing

XLIM = (0.33, 1.88)          # shared by the strip and the cloud, and asserted to hold every query
YLIM = (0.262, 0.790)        # the reliability score, plus the block that holds the statistic
XTICKS = [0.5, 1.0, 1.5]
YTICKS = [0.3, 0.5, 0.7]

# Weight ladder on the cloud: texture, then context, then the measurement.
RAW_S, RAW_ALPHA = 1.3, 0.12
IQR_LW, IQR_ALPHA = 1.0, 0.38
PATH_ALPHA = 0.85

MINUS = "−"

STAT_X = 0.018
STAT_Y_RHO, STAT_Y_P = 0.210, 0.005
STAT_BOX = (0.000, 0.360, 0.000, 0.374)
STAT_MAX_COVERED = 4

# The strip, in its own axes with ylim (0, 1). Both groups' interquartile bars live in the right
# fifth of the divergence range and the eleven mean-sufficient queries in the left sixth, so the
# middle is empty and that is where the text goes. STRIP_TEXT_X is a DATA coordinate for exactly
# that reason: a fraction would move the text off the empty band the moment the view changed.
ROW_Y = {RECOMMENDED: 0.80, NO_CALL: 0.48}
STRIP_IQR_LW = 2.0
MED_H = 0.16                 # half-height of a median tick, in strip units
RUG_Y0, RUG_Y1 = 0.06, 0.20  # the eleven mean-sufficient ticks
RUG_Y = (RUG_Y0 + RUG_Y1) / 2.0
STRIP_TEXT_X = 0.35          # left edge of a group's statistic, in true-divergence units
STRIP_CLEAR = 0.06           # divergence units of air demanded between that text and the bar
STRIP_LABEL = {RECOMMENDED: "recommended", NO_CALL: "declined"}


def _load():
    """The one-row-per-query view, with both axes and the verdict."""
    raw = pd.read_csv(SRC)
    kept = raw.dropna(subset=["structure_reliability_score", "true_divergence",
                              "recommendation_mode"])
    assert len(kept) == len(raw), (
        f"{SRC} was expected to score every query on both axes and carry a verdict; "
        f"{len(raw) - len(kept)} of {len(raw)} rows do not. Decide what a missing value means "
        f"before this panel summarises the rest.")
    u = kept.drop_duplicates(subset=QUERY_KEY)
    assert len(u) == len(kept), (
        f"{SRC} was expected to hold one row per query key; {len(kept)} rows collapsed to {len(u)}.")
    assert len(u) == N_QUERIES, (
        f"panel f is drawn and captioned for n = {N_QUERIES} queries, found {len(u)}. Update the "
        f"caption and this constant together, or the panel is lying about its n.")
    modes = set(u["recommendation_mode"].unique())
    assert modes == {RECOMMENDED, NO_CALL, SUFFICIENT}, (
        f"panel f splits by gate verdict and knows of {sorted([RECOMMENDED, NO_CALL, SUFFICIENT])}; "
        f"the file now carries {sorted(modes)}.")
    counts = u["recommendation_mode"].value_counts().to_dict()
    expected = {RECOMMENDED: N_RECOMMENDED, NO_CALL: N_NO_CALL, SUFFICIENT: N_SUFFICIENT}
    assert counts == expected, (
        f"panel f, panel e and the Fig. 3 caption all quote {expected}; this file now has "
        f"{counts}. exp16 is a pure re-analysis of exp12, so a disagreement here usually means one "
        f"of the two is stale: check both before editing these constants.")
    return u


def _assert_design_assumption():
    """The 'assumed to rise' claim is quoted from the verdict script, so it is checked against it."""
    # The sentence is a COMMENT in the verdict script and is wrapped across two lines with a "#"
    # at the start of the continuation, so the hash characters are stripped before the whitespace
    # is collapsed. Reading the file rather than quoting it is the point: if the sentence ever
    # leaves the verdict script the claim has lost its source, and the panel refuses to draw
    # rather than standing behind a design that is gone.
    with open(VERDICT_SRC, encoding="utf-8") as fh:
        flat = " ".join(fh.read().replace("#", " ").split())
    assert DESIGN_ASSUMPTION in flat, (
        f"this panel's caption says the gate's reliability axis was ASSUMED to rise, on the "
        f"authority of one sentence in {VERDICT_SRC}, which no longer states it:\n"
        f"  {DESIGN_ASSUMPTION}\nRe-source that claim or rewrite it.")


def _binned_medians(x, y):
    """Conditional median and interquartile range of ``y`` in N_BINS equal-width bins of ``x``."""
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


def _cles(a, b):
    """P(a random draw from ``a`` exceeds one from ``b``), ties split, with the two-sided p."""
    u_stat, pval = mannwhitneyu(a, b, alternative="two-sided")
    return float(u_stat) / (len(a) * len(b)), float(pval)


def _signed(v, nd=2):
    """A signed number whose sign is computed, never typed, and set in the body face."""
    return f"{MINUS if v < 0 else '+'}{abs(v):.{nd}f}"


def _p_label(pval):
    """A p value with a floor rather than a rounded zero."""
    return "$P$ < 0.001" if pval < 0.001 else f"$P$ = {pval:.3f}"


def draw_3f(ax, ax_top):
    """The gate's continuous score against divergence, under its own thresholded verdict."""
    _assert_design_assumption()
    u = _load()
    x = u["true_divergence"].to_numpy(dtype=float)
    y = u["structure_reliability_score"].to_numpy(dtype=float)

    groups = {m: u.loc[u["recommendation_mode"] == m, "true_divergence"].to_numpy(dtype=float)
              for m in (RECOMMENDED, NO_CALL, SUFFICIENT)}
    med = {m: float(np.median(v)) for m, v in groups.items()}
    cles, pval_g = _cles(groups[RECOMMENDED], groups[NO_CALL])

    rho, pval = spearmanr(x, y)

    # ---- what the two readings claim, asserted before either is drawn ------------------------
    assert rho < 0.0 and pval < 0.05, (
        f"the lower reading draws a significant NEGATIVE rank association, found rho = {rho:+.4f}, "
        f"P = {pval:.3g}. Rewrite the caption and the label before redrawing.")
    xm, ym, q1, q3, _ = _binned_medians(x, y)
    assert ym[-1] < ym[0], (
        f"the caption reads the binned medians as falling across the divergence range, but the "
        f"top bin median {ym[-1]:.4f} is not below the bottom bin median {ym[0]:.4f}.")

    assert med[RECOMMENDED] < med[NO_CALL], (
        f"the upper reading states that the queries the gate declined for no call are the MORE "
        f"divergent ones, but the recommended median {med[RECOMMENDED]:.4f} is not below "
        f"{med[NO_CALL]:.4f}.")
    assert cles < 0.5 and pval_g < 0.01, (
        f"the caption calls the {N_NO_CALL}-query comparison inverted, which needs an effect size "
        f"below 0.5 at a p this panel is willing to print; found CLES = {cles:.4f}, "
        f"p = {pval_g:.3g}.")
    assert 0.0005 <= pval_g < 0.995, (
        f"P is printed to three decimals and p = {pval_g:.3g} would print uninformatively.")
    suff = groups[SUFFICIENT]
    assert (suff.max() < np.percentile(groups[RECOMMENDED], 5)
            and suff.max() < np.percentile(groups[NO_CALL], 5)), (
        f"the strip draws the {N_SUFFICIENT} mean-sufficient queries as a separate low cluster and "
        f"the caption calls the gate right about them; their maximum {suff.max():.4f} is no longer "
        f"below the fifth percentile of both other groups.")
    assert med[SUFFICIENT] < med[RECOMMENDED] and med[SUFFICIENT] < med[NO_CALL]

    # The reading this panel refuses to draw: pooling the eleven cancels the effect.
    declined = np.concatenate([groups[NO_CALL], suff])
    assert len(declined) == N_DECLINED
    cles_pool, p_pool = _cles(groups[RECOMMENDED], declined)
    assert cles_pool > cles and p_pool > 0.05 > pval_g, (
        f"this panel plots the {N_NO_CALL}-query arm because pooling the {N_SUFFICIENT} "
        f"mean-sufficient queries cancels the effect: CLES {cles:.4f} -> {cles_pool:.4f}, "
        f"p {pval_g:.3g} -> {p_pool:.3g}. Pooling no longer does that, so the docstring's argument "
        f"and the caption's pooled statistic must be rewritten.")

    # ---- the view, shared by both axes -------------------------------------------------------
    assert XLIM[0] < x.min() and x.max() < XLIM[1], (
        f"the x view {XLIM} clips divergences running {x.min():.3f} to {x.max():.3f}.")
    assert YLIM[0] < min(y.min(), q1.min()) and max(y.max(), q3.max()) < YLIM[1], (
        f"the y view {YLIM} clips the drawn data: scores run {y.min():.3f} to {y.max():.3f} and "
        f"the interquartile bars run {q1.min():.3f} to {q3.max():.3f}.")

    # ================================ the strip: the thresholded verdict ======================
    ax_top.set_xlim(*XLIM)
    ax_top.set_ylim(0.0, 1.0)
    strip_texts = []
    for mode in (RECOMMENDED, NO_CALL):
        v = groups[mode]
        yy = ROW_Y[mode]
        lo, mid, hi = (float(t) for t in np.percentile(v, [25, 50, 75]))
        ax_top.plot([lo, hi], [yy, yy], color=SHARED, lw=STRIP_IQR_LW, solid_capstyle="butt",
                    zorder=3)
        ax_top.plot([mid, mid], [yy - MED_H, yy + MED_H], color=TEXT, lw=1.0, zorder=4,
                    solid_capstyle="butt")
        # Left-aligned in the empty middle band, on the group's own row. The two medians differ by
        # 0.02 on a 1.55-wide axis, which is 1 per cent of the panel: the tick positions cannot be
        # told apart by eye and the numbers have to be printed.
        strip_texts.append((mode, lo, ax_top.text(
            STRIP_TEXT_X, yy, f"n = {len(v)}, median {mid:.2f}", fontsize=PT_SMALL,
            color=SUBTLE, ha="left", va="center", zorder=5)))
    # The eleven, as their own ticks, where they stand. They share the strip's bottom row with the
    # two-group test, and neither is on a group's row, so neither can reach a bar or a tick.
    ax_top.vlines(suff, RUG_Y0, RUG_Y1, color=SHARED, lw=LW_HAIR, zorder=3)
    ax_top.text(float(suff.max()) + 0.03, RUG_Y, f"{len(suff)} mean sufficient",
                fontsize=PT_SMALL, color=SUBTLE, ha="left", va="center", zorder=5)
    ax_top.text(XLIM[1], RUG_Y, _p_label(pval_g), fontsize=PT_SMALL, color=TEXT, ha="right",
                va="center", zorder=5)

    # Each group's statistic must stop short of its own interquartile bar. Measured on the
    # rendered text rather than estimated from a character count, because the two labels differ in
    # width and the bars start at different places.
    r = RendererAgg(int(ax_top.figure.get_figwidth() * ax_top.figure.dpi),
                    int(ax_top.figure.get_figheight() * ax_top.figure.dpi), ax_top.figure.dpi)
    inv = ax_top.transData.inverted()
    for mode, bar_lo, artist in strip_texts:
        x_end = float(inv.transform((artist.get_window_extent(renderer=r).x1, 0.0))[0])
        assert x_end + STRIP_CLEAR < bar_lo, (
            f"the {mode} row's statistic reaches divergence {x_end:.3f} and its interquartile bar "
            f"starts at {bar_lo:.3f}; the text would run into the mark it describes. Shorten the "
            f"label, do not move it right.")

    ax_top.set_yticks([ROW_Y[RECOMMENDED], ROW_Y[NO_CALL]])
    ax_top.set_yticklabels([STRIP_LABEL[RECOMMENDED], STRIP_LABEL[NO_CALL]], fontsize=PT_TICK,
                           color=TEXT)
    ax_top.set_xticks([])
    ax_top.tick_params(axis="y", length=0, pad=2)
    for side in ("top", "right", "bottom", "left"):
        ax_top.spines[side].set_visible(False)

    # ================================ the cloud: the continuous score =========================
    bx0, bx1, by0, by1 = STAT_BOX
    sx0, sx1 = (XLIM[0] + b * (XLIM[1] - XLIM[0]) for b in (bx0, bx1))
    sy0, sy1 = (YLIM[0] + b * (YLIM[1] - YLIM[0]) for b in (by0, by1))
    covered = int(((x >= sx0) & (x <= sx1) & (y >= sy0) & (y <= sy1)).sum())
    assert covered <= STAT_MAX_COVERED, (
        f"the statistic block now sits over {covered} queries, above the {STAT_MAX_COVERED} this "
        f"panel accounts for. Re-read the corner counts before leaving it there.")
    on_marks = [(float(a), float(b)) for a, b, lo, hi in zip(xm, ym, q1, q3)
                if sx0 <= a <= sx1 and lo <= sy1 and hi >= sy0]
    assert not on_marks, (
        f"the statistic block covers the conditional medians or interquartile bars at {on_marks}. "
        f"It may sit on the cloud; it may not sit on the measurement.")

    ax.scatter(x, y, s=RAW_S, color=SHARED, alpha=RAW_ALPHA, edgecolors="none", linewidths=0,
               zorder=1)
    ax.vlines(xm, q1, q3, color=SHARED, lw=IQR_LW, alpha=IQR_ALPHA, zorder=3)
    ax.plot(xm, ym, color=SHARED, lw=LW_HAIR, alpha=PATH_ALPHA, zorder=4, solid_capstyle="round")
    ax.scatter(xm, ym, s=MS_DOT, color=SHARED, edgecolors="white", linewidths=0.5, zorder=5)

    ax.set_xlim(*XLIM)
    ax.set_ylim(*YLIM)
    assert all(x.min() <= t <= x.max() for t in XTICKS), (
        f"an x tick in {XTICKS} lies outside the drawn divergences {x.min():.3f} to {x.max():.3f}.")
    assert all(y.min() <= t <= y.max() for t in YTICKS), (
        f"a y tick in {YTICKS} lies outside the drawn scores {y.min():.4f} to {y.max():.4f}.")
    ax.set_xticks(XTICKS)
    ax.set_yticks(YTICKS)
    bare_axes(ax)
    ax.spines["left"].set_bounds(y.min(), y.max())
    ax.spines["bottom"].set_bounds(x.min(), x.max())

    ax.set_xlabel("true response divergence", fontsize=PT_ANNOT, labelpad=1.5)
    ax.set_ylabel("gate structure\nreliability", fontsize=PT_ANNOT, labelpad=1.5, linespacing=1.15)

    ax.text(STAT_X, STAT_Y_RHO, f"$\\rho$ = {_signed(float(rho))}", transform=ax.transAxes,
            fontsize=PT_ANNOT, color=TEXT, ha="left", va="bottom")
    ax.text(STAT_X, STAT_Y_P, _p_label(float(pval)), transform=ax.transAxes,
            fontsize=PT_ANNOT, color=TEXT, ha="left", va="bottom")

    return {"rho": float(rho), "p_rho": float(pval), "cles": cles, "p_verdict": pval_g,
            "median": med, "n": {m: int(len(v)) for m, v in groups.items()},
            "cles_pooled": cles_pool, "p_pooled": p_pool,
            "bin_median_first": float(ym[0]), "bin_median_last": float(ym[-1])}


if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    sys.path.insert(0, os.path.join(REPO, "figures"))
    from figstyle import apply_style
    from fig3_style import PT_TITLE

    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    plt.rcParams["savefig.bbox"] = None
    # The printed box: fig3_assemble gives f a 2.40 in box in a 1.55 in row under a 0.16 in
    # LETTER_BLOCK, with pads (0.74, 0.10, 0.42). The axes column is 1.56 in wide and 1.13 in
    # tall, split into a 0.32 in strip, a 0.06 in gap and a 0.75 in cloud.
    BOX_W, BOX_H = 2.40, 1.71
    AX_W, PAD_L, PAD_B = 1.56, 0.74, 0.42
    STRIP_H, GAP, MAIN_H = 0.32, 0.06, 0.75
    fig = plt.figure(figsize=(BOX_W, BOX_H))
    ax_top = fig.add_axes([PAD_L / BOX_W, (PAD_B + MAIN_H + GAP) / BOX_H, AX_W / BOX_W,
                           STRIP_H / BOX_H])
    ax_main = fig.add_axes([PAD_L / BOX_W, PAD_B / BOX_H, AX_W / BOX_W, MAIN_H / BOX_H])
    out = draw_3f(ax_main, ax_top)
    print(out)
    fig.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)), "3f.png"), dpi=300)
    print("wrote 3f.png")
