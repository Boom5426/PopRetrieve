"""PopRetrieve Figure 3 panel 3c: the minority-coverage gain, by true-divergence quartile.

WHAT THIS PANEL SHOWS
---------------------
Four quartile means of the population-minus-mean minority-coverage gain, each with its bootstrap
95 per cent interval, read against zero, with the rows ordered by increasing true divergence.
Two facts are meant to be readable from the marks alone:

  * every interval lies wholly to the right of the zero rule, in the population half-plane, and
  * every interval is longer than the whole spread of the four estimates, the shortest by a
    factor of 1.6 and the longest by 3.2, and all four mutually overlap, with Q4 below Q3, so
    the column does not march right as divergence increases.

Both are asserted in ``draw_3c`` before anything is drawn. The panel states neither in words: the
caption carries the argument, this panel carries the evidence for it.

That second fact is why this panel belongs with d, e and f. The pre-specified gate assumes the
gain is concentrated where the true response distribution diverges from its mean, and along
exactly that axis no concentration is detectable: Spearman rho = +0.050, p = 0.165 over all 765
queries, the one statistic the panel prints.

Source data: results/exp16_gate_diagnosis/_merged_query_divergence.csv, 765 queries with both
true_divergence and minority_state_coverage_gap. Every number drawn or written here is computed
from that file at draw time; nothing is a literal. figures/source_data/fig3ef_gate_divergence.csv
is a hand-built column view of the same file and is deliberately not read.

WHAT CHANGED IN THE 2026-08-31 RESTRAINT PASS
---------------------------------------------
The panel is unchanged in data, statistic and every asserted relationship. What went is text.

  * THE CONCLUSION PHRASE "All four positive, no trend visible" IS DELETED, with fig3_style.title
    itself. Thirteen panels each stating a conclusion over its own marks is thirteen claims
    competing on one page, which is not what a Nature-family main figure does. The phrase now
    opens this panel's caption entry, where it can be qualified properly and costs no height.
  * THE ON-PANEL SCALE REFERENCE "metric itself: median 0.985, IQR 0.012" IS DELETED FROM THE
    DRAWING, NOT FROM THE CODE. It reads as a sentence and it belongs in the caption. Both numbers
    are still computed here, still asserted to pool both arms of all 765 queries, and still
    returned by ``draw_3c`` and printed by ``python3 fig3c.py``, so the caption's copy of them
    cannot outlive the data either. Same for the four quartile medians and the four n.
  * THE 0.42 IN RETURNED TO THE SIX ROWS BY REMOVING THOSE PHRASES REACHES THE MARKS. The axes
    grew from 1.87 x 0.70 to 1.87 x 0.78 in, and deleting the note band under the rows frees the
    rest: row pitch goes from 0.117 to 0.167 in, and each interval gained end caps at its bounds,
    so "the lower bound clears zero" and "these two intervals overlap" are now read off drawn
    ends rather than off a fading line. The x view is untouched: the effect is small and the
    panel must keep showing that it is small.

WHAT THIS PANEL REFUSES TO CLAIM, AND WHY (CORRECTIONS.md R48, unchanged and still binding)
-------------------------------------------------------------------------------------------
An earlier version drew four bars with s.e.m. on an axis truncated at 0.012, titled "Minority-
coverage gain is negligible". Both halves were wrong.

  * THE BARS SHOWED A TREND THAT IS NOT THERE. Q1 to Q3 rise, and a truncated bar axis turns that
    into a visible ramp, but Spearman rho with divergence is +0.050 at p = 0.165, Q4 is below Q3,
    and all four intervals overlap. Point estimates with intervals make the overlap the visible
    fact instead.
  * "NEGLIGIBLE" DEPENDED ON THE DENOMINATOR, and the denominators disagree hard. The largest
    quartile mean, +0.0062, is 0.6 per cent of the nominal [0, 1] metric range, 2.6 per cent of
    the metric's observed range, 5.1 per cent of its central 98 per cent, and 53 per cent of the
    metric's own interquartile range; the paired Cohen's d is 0.33. Choosing among those is
    precisely the error this paper exists to criticise, so the panel makes no size claim at all
    and draws no ratio to any chosen denominator. The reader sizes the gain from the axis, and
    the caption supplies the metric's own median and IQR as the one scale reference.

JUDGEMENT CALLS A READER COULD REASONABLY DISAGREE WITH
-------------------------------------------------------
  1. THE POINT ESTIMATE IS THE MEAN, not the median, because the brief for this panel fixes it and
     because a mean is what the quartile intervals and the Spearman test are about. The medians
     are three to five times smaller (+0.0009, +0.0015, +0.0017, +0.0018, asserted below to be
     positive and below their means): this gain has a heavy right tail, so the mean is not the
     typical query. Drawing both needs a two-symbol key that does not fit in 1.87 x 0.78 in, so
     THE MEDIANS BELONG IN THE CAPTION, and ``draw_3c`` returns them for it.
  2. NO SCALE REFERENCE IS DRAWN ON THE GAIN AXIS. A bracket for the metric's own IQR would make
     "the gain is half an IQR" the panel's visual argument, and that is the largest of the four
     available denominators, i.e. the one that most flatters the gain. It is a caption number.
  3. THE VIEW STARTS AT A SMALL NEGATIVE VALUE so zero is a datum inside the frame rather than the
     left edge. The negative half-plane is therefore a thin wash, which is honest: no quartile
     interval reaches it.
  4. QUARTILES ARE pandas.qcut ON true_divergence, giving 192 / 191 / 191 / 191. The n are equal
     to one query and are not drawn; they are asserted to stay equal to one, and returned for the
     caption.
  5. Q1 IS AT THE BOTTOM so the y axis increases with divergence, the direction the "no growth
     with divergence" reading runs in. groupby is not trusted to return that order: it is
     asserted on the per-quartile median divergence before anything is drawn.
  6. THE ASSERTED CLAIM IS "ALL FOUR QUARTILE MEANS POSITIVE", NOT "positive everywhere". The
     latter would be read at the query level and is false there: 26.9 per cent of the 765 queries
     have a negative gain and the smallest is -0.130. What is positive is each of the four
     quartile means together with its whole interval, which is what the panel draws, and the
     caption must say it at that level too.
  7. THE ABSENCE OF A TREND IS A STATEMENT ABOUT THIS PANEL, NOT ABOUT THE POPULATION. rho = +0.050
     at n = 765 has a normal approximate 95 per cent interval of about [-0.02, +0.12], so a weak
     positive trend is not excluded; what can be reported is that none is detectable here. That is
     why the panel prints rho and P and leaves the reading to the caption: asserting the bare null
     from a non-significant test is the same overclaim, mirrored, that this paper criticises.
  8. THE ONE PRINTED STATISTIC KEEPS THE WORD "Spearman". It names which correlation was run,
     which is part of the statistic rather than a sentence about it, and rho alone would leave a
     reader to guess between rank and product-moment.
  9. THE P VALUE IS SET AS ITALIC LOWERCASE $p$, matching this panel's caption entry and the
     fifteen p values in the manuscript body. Nature's own house form is an italic capital, but a
     panel that disagrees with the caption printed under it is worse than one that disagrees with
     a style guide, and this panel exists to be checkable against that caption.

Run standalone: python3 fig3c.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig3_style import (LW_HAIR, LW_LINE, LW_STEM, MS_DOT, PT_ANNOT,  # noqa: E402
                        PT_TICK, REPO, SHARED, TEXT, bare_axes, boot_ci, sign_field, zero_rule)

SRC = os.path.join(REPO, "results", "exp16_gate_diagnosis", "_merged_query_divergence.csv")

GAIN = "minority_state_coverage_gap"
POP_ARM = "minority_state_coverage_dart"
MEAN_ARM = "minority_state_coverage_mean"

# The view. XLO is a hair below zero so the zero rule is a datum with room on both sides; XHI
# clears the widest interval. Both are asserted against the data below. This range is the true
# scale of the effect and is deliberately not expanded to separate the points.
XLO, XHI = -0.0014, 0.0092

# Rows are one data unit apart, Q1 at y = 0 and Q4 at y = 3. Everything else on the y axis is
# clearance, in the same units, and the axes are 0.78 in tall, so one row unit prints at 0.167 in.
CLEAR_BOT = 0.45        # below Q1: the dot's own radius plus air above the x spine
CLEAR_TOP = 0.50        # above Q4: separates the top interval from the statistic
STAT_Y = 3.0 + CLEAR_TOP
YLO, YHI = -CLEAR_BOT, 4.22     # the band from STAT_Y to YHI holds one printed PT_ANNOT line

# The statistic is set va="bottom" at STAT_Y, so it grows upward out of the frame if the band
# above STAT_Y is thinner than one printed line. In this deck's face a 7.2 pt line measures
# 7.92 pt from ascender to descender, 1.10x nominal; LINE_H carries a margin over that and is
# checked against the axes' real height in draw_3c, which differs between the standalone
# preview and fig3_assemble only if the ledger there changes.
LINE_H = 1.15

# The zero rule spans the rows only. Left full height it printed through the word "Spearman",
# which no text-versus-text layout check can see.
ROW_OVERHANG = 0.38     # rows are one unit apart, so this is 0.38 of a row past each end
CAP = 0.17              # half-height of the tick drawn at each interval bound, in row units


def _load():
    """The 765 queries with both columns, their divergence quartile, and the arm-level values."""
    cols = ["true_divergence", GAIN, POP_ARM, MEAN_ARM]
    raw = pd.read_csv(SRC)
    d = raw.dropna(subset=cols)
    # A dropna that quietly removed rows would shrink every number here AND the n the caption
    # quotes, with nothing on the panel to show it. The merge is complete today, so incompleteness
    # is a data problem to be fixed upstream, not something this panel may absorb in silence.
    assert len(d) == len(raw), (
        f"{len(raw) - len(d)} of {len(raw)} rows lack one of {cols}; the panel would silently be "
        f"drawn on {len(d)} queries while the caption still says {len(raw)}")
    # The axis label says "population - mean". Assert it, so the label cannot outlive the data.
    assert np.allclose(d[GAIN].values, d[POP_ARM].values - d[MEAN_ARM].values, atol=1e-12), (
        f"{GAIN} is not {POP_ARM} minus {MEAN_ARM}; the signed axis label would be false")
    d = d.assign(divq=pd.qcut(d["true_divergence"], 4, labels=["Q1", "Q2", "Q3", "Q4"]))
    return d


def draw_3c(ax):
    """Four quartile means with bootstrap 95 per cent intervals, against zero.

    Returns every number the caption for this panel quotes, so the caption is checkable against a
    run of this module rather than against a memory of one.
    """
    d = _load()
    n_total = len(d)

    labels, means, los, his, meds, ns, divs = [], [], [], [], [], [], []
    for name, sub in d.groupby("divq", observed=True):
        m, lo, hi = boot_ci(sub[GAIN].values, stat=np.mean, seed=0)
        labels.append(str(name))
        means.append(m)
        los.append(lo)
        his.append(hi)
        meds.append(float(np.median(sub[GAIN].values)))
        ns.append(int(len(sub)))
        divs.append(float(sub["true_divergence"].median()))
    means, los, his = np.asarray(means), np.asarray(los), np.asarray(his)
    meds = np.asarray(meds)
    ys = np.arange(len(labels), dtype=float)

    # Row 0 is drawn at the bottom, so the y axis increases with divergence only if the groups
    # come back in ascending order. The y label and the "no growth with divergence" reading both
    # depend on that, so it is checked rather than assumed of groupby.
    assert np.all(np.diff(divs) > 0), f"rows are not in ascending divergence order: {divs}"
    # qcut on 765 values gives 192 / 191 / 191 / 191. The caption quotes equal-to-one strata; if a
    # future merge makes them uneven, the caption is wrong and the quartile reading is weaker.
    assert max(ns) - min(ns) <= 1, f"divergence quartiles are not equal to one query: {ns}"
    assert sum(ns) == n_total, f"quartile sizes {ns} do not account for all {n_total} queries"

    rho, p_rho = stats.spearmanr(d["true_divergence"].values, d[GAIN].values)

    # ---- the two facts the marks must carry, asserted before they are drawn ------------------
    assert (los > 0).all(), (
        f"a quartile interval reaches zero, so the caption's 'all four positive' is false: lower "
        f"bounds {los}")
    for i in range(len(means)):
        for j in range(i + 1, len(means)):
            assert los[i] <= his[j] and los[j] <= his[i], (
                f"intervals {labels[i]} and {labels[j]} are disjoint; the four estimates are then "
                f"separated and the caption's 'no trend visible' is false")
    # The estimates must stay small against their own uncertainty, or "the intervals are longer
    # than the spread" stops being what the panel shows.
    assert means.max() - means.min() < (his - los).min(), (
        f"the spread of the four means, {means.max() - means.min():.5f}, exceeds the shortest "
        f"interval, {(his - los).min():.5f}; the overlap is no longer the visible fact")
    assert p_rho > 0.05, (
        f"Spearman p = {p_rho:.3g} is significant; 'no trend visible' is no longer what the data "
        f"say and the caption for this panel must change")
    # Docstring judgement call 1: the mean is drawn, and it is not the typical query.
    assert (meds > 0).all() and (meds < means).all(), (
        f"quartile medians {meds} are no longer positive-and-below-the-means; the docstring's "
        f"reason for drawing the mean, a heavy right tail, no longer holds")

    # ---- the metric's own scale, pooled over both arms. Computed for the CAPTION, not drawn ---
    metric = np.concatenate([d[POP_ARM].values, d[MEAN_ARM].values])
    assert metric.size == 2 * n_total, (
        f"the scale reference pools {metric.size} values, not both arms of all {n_total} queries")
    med_metric = float(np.median(metric))
    iqr_metric = float(np.percentile(metric, 75) - np.percentile(metric, 25))

    # ---- the view --------------------------------------------------------------------------
    assert XLO < 0.0 < XHI, "zero must be a datum inside the frame, not an edge of it"
    assert his.max() < XHI and los.min() > XLO and means.min() > XLO and means.max() < XHI, (
        f"the view clips a drawn mark: means [{means.min():.5f}, {means.max():.5f}], intervals "
        f"[{los.min():.5f}, {his.max():.5f}], outside [{XLO}, {XHI}]. The dots are drawn with "
        f"clip_on=False, so a clipped one would print outside the panel box rather than vanish")
    # The one printed statistic sits in a band that holds no data ink, above the rows and above
    # the end of the zero rule.
    assert STAT_Y > ys.max() + max(ROW_OVERHANG, CAP), (
        f"the statistic at y = {STAT_Y} would sit over row {ys.max()} or over the zero rule")
    assert YLO < ys.min() - max(CAP, ROW_OVERHANG), (
        f"the y view [{YLO}, {YHI}] clips a cap or the end of the zero rule")
    # YHI > STAT_Y is not enough: the statistic is drawn upward from STAT_Y, so what has to fit
    # is a printed line, measured in inches off the axes this panel was actually given.
    ax_h_in = ax.get_position().height * ax.figure.get_figheight()
    band_in = (YHI - STAT_Y) / (YHI - YLO) * ax_h_in
    assert band_in >= LINE_H * PT_ANNOT / 72.0, (
        f"the band above the rows is {band_in:.4f} in on a {ax_h_in:.3f} in axes, under the "
        f"{LINE_H * PT_ANNOT / 72.0:.4f} in one {PT_ANNOT} pt line prints at; the statistic "
        f"would overrun the top of the frame. Lower CLEAR_TOP or raise YHI")

    # Sign, not object: the distribution being plotted is a signed difference, so it is drawn in
    # SHARED grey and blue/orange live in the half-planes behind it.
    ax.set_xlim(XLO, XHI)
    ax.set_ylim(YLO, YHI)
    lo_wash, hi_wash = sign_field(ax, vertical=True, at=0.0, pop_side="right")
    # sign_field spans the plane to +/-1e9, which is invisible under the axes clip but makes the
    # patch's bbox unbounded, so a layout audit cannot tell a real overhang from the wash. Re-cut
    # both washes to the view; the drawn result is identical.
    # x is in data coordinates and y is in axes coordinates: axvspan blends the two.
    lo_wash.set_bounds(XLO, 0.0, -XLO, 1.0)
    hi_wash.set_bounds(0.0, 0.0, XHI, 1.0)
    # The zero rule is the datum the four estimates are read against, so it spans the rows and
    # stops short of the statistic. axvline blends x in data coordinates with y in AXES
    # coordinates, so the row band is converted here.
    zr = zero_rule(ax, at=0.0, vertical=True, color=TEXT, lw=0.8)
    zr.set_ydata([(ys.min() - ROW_OVERHANG - YLO) / (YHI - YLO),
                  (ys.max() + ROW_OVERHANG - YLO) / (YHI - YLO)])

    # The interval, then its two bounds, then the estimate. The caps are what make "this bound
    # clears zero" and "these two intervals overlap" readable off ends rather than off a line.
    ax.hlines(ys, los, his, color=SHARED, lw=LW_LINE, zorder=3)
    ax.vlines(np.concatenate([los, his]), np.concatenate([ys, ys]) - CAP,
              np.concatenate([ys, ys]) + CAP, color=SHARED, lw=LW_STEM, zorder=3)
    ax.scatter(means, ys, s=MS_DOT, color=SHARED, zorder=4, linewidths=0, clip_on=False)

    # ---- the one statistic, stated once, in the data-free band above the rows -----------------
    ax.text(XLO + 0.0004, STAT_Y,
            f"Spearman $\\rho$ = {rho:+.2f}, $p$ = {p_rho:.2f}",
            fontsize=PT_ANNOT, color=TEXT, ha="left", va="bottom")

    ax.set_yticks(ys)
    ax.set_yticklabels(labels, fontsize=PT_TICK)
    # Labels are formatted FROM the tick positions, so a moved tick cannot keep an old number.
    xticks = [0.0, 0.004, 0.008]
    assert all(XLO <= t <= XHI for t in xticks), f"a tick lies outside the view: {xticks}"
    ax.set_xticks(xticks)
    ax.set_xticklabels([f"{t:g}" for t in xticks], fontsize=PT_TICK)
    ax.set_xlabel("minority-coverage gain,\npopulation \u2212 mean", fontsize=PT_ANNOT,
                  labelpad=1.5)
    ax.set_ylabel("true-divergence\nquartile", fontsize=PT_ANNOT, labelpad=1.5)

    bare_axes(ax, keep=("bottom",))
    ax.tick_params(axis="y", length=0)
    ax.spines["bottom"].set_linewidth(LW_HAIR)

    return {"labels": labels, "n_per_quartile": ns, "mean": means, "lo": los, "hi": his,
            "median": meds, "rho": float(rho), "p": float(p_rho), "n": n_total,
            "metric_median": med_metric, "metric_iqr": iqr_metric}


if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from figstyle import apply_style
    from fig3_style import PT_TITLE

    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    # apply_style sets savefig.bbox = "tight", which would crop the preview back to its ink and
    # hand back a PNG at a different scale from the printed panel. The standalone preview is a
    # 1:1 reproduction of the panel BOX this panel occupies in fig3_assemble, so keep the canvas.
    plt.rcParams["savefig.bbox"] = None
    fig = plt.figure(figsize=(2.75, 1.35))
    ax = fig.add_axes([0.78 / 2.75, 0.40 / 1.35, 1.87 / 2.75, 0.78 / 1.35])
    stats_out = draw_3c(ax)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "3c.png")
    fig.savefig(out, dpi=300)
    print({k: (np.round(v, 5).tolist() if isinstance(v, np.ndarray) else v)
           for k, v in stats_out.items()})
    print(f"wrote {out}")
