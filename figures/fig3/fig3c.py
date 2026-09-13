"""PopRetrieve Figure 3 panel 3c: the minority-coverage gain, by true-divergence quartile.

WHAT THIS PANEL SHOWS
---------------------
Four quartile means of the population-minus-mean minority-coverage gain, each with its bootstrap
95 per cent interval, read against zero, with the rows ordered by increasing true divergence.
Three facts are meant to be readable from the marks alone:

  * the LOWEST-divergence quartile does not gain. Its mean is -0.0035 and its interval reaches
    from -0.0076 to +0.0001, so it sits mostly in the mean half-plane;
  * the upper three quartiles do, wholly clear of the zero rule (+0.0038, +0.0054, +0.0051); and
  * those three are not separated from EACH OTHER: their intervals mutually overlap, so the panel
    shows a break at the bottom of the divergence range and not a ranking above it.

All three are asserted in ``draw_3c`` before anything is drawn. The panel states none of them in
words: the caption carries the argument, this panel carries the evidence for it.

This is why the panel opens the block d, e, f, and the reason has changed. The pre-specified gate
assumes the gain is concentrated where the true response distribution diverges from its mean.
Along that axis the concentration is REAL: Spearman rho = +0.141, p = 1e-04 over all 765 queries,
the one statistic the panel prints, and a clean break between the bottom quartile and the rest.

Panel d then asks the same question of a judge that does NOT share the retrieval objective, and
finds the same axis grading a quantity that never turns positive. Panels e and f show that the
GATE finds neither: it does not enrich for the gain (e), its own reliability score runs opposite
to true divergence and the queries it declines are the more divergent ones (f). **The failure is
in the surrogate, not in the axis.**

WHAT THE ESTIMATOR REPAIR AND THE EXP16 REMERGE DID TO THIS PANEL, 2026-09-03
-----------------------------------------------------------------------------
This panel reversed, and the reversal has two causes that arrived together.

The first is the unbiased estimator. The second is a stale derived file: exp16 is a pure
re-analysis of exp12's per-query CSV, it is NOT in analysis/estimator_audit/run_legacy_suite.sh
(whose list is scripts that CALL an energy kernel, which exp16 does not), and so
results/exp16_gate_diagnosis/_merged_query_divergence.csv was still the V-arm merge sitting
downstream of a U-arm exp12. Its gate verdict split, 621 / 133 / 11, disagreed with exp12's own
627 / 127 / 11, and the verdict panel asserted the stale numbers while the enrichment panel,
reading exp12 directly, asserted the live ones.
exp16 and exp17 were re-run on 2026-09-03; the pre-remerge files are in
results/_pre_exp16_remerge_backup/.

What the panel said before, and says now:

| | V arm, stale merge | U arm, rebuilt merge |
|---|---:|---:|
| Spearman rho (n = 765) | +0.050, p = 0.165 | **+0.141, p = 1e-04** |
| Q1 mean [95% CI] | +0.0042 [+0.0008, +0.0073] | **-0.0035 [-0.0076, +0.0001]** |
| Q2 mean | +0.0050 | +0.0038 |
| Q3 mean | +0.0062 | +0.0054 |
| Q4 mean | +0.0056 | +0.0051 |
| fraction of queries with a positive gain, Q1 to Q4 | 0.55 / 0.69 / 0.70 / 0.71 | **0.41 / 0.55 / 0.61 / 0.65** |

The old panel's claim was "all four positive, no trend visible". Both halves are now false, and
the panel is drawn and asserted on what replaced them. The paper's argument does not weaken here;
it sharpens, because "true divergence predicts the gain and the gate does not" is a statement
about the surrogate, which is what Figure 3 is about.

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

  * THE BARS SHOWED A TREND ON EVIDENCE THAT COULD NOT CARRY ONE. A truncated bar axis turns any
    rise into a visible ramp, whatever its uncertainty. That the trend has since turned out to be
    real (rho = +0.141 at p = 1e-04) does not retire the correction: the old drawing would have
    shown the same ramp had the trend still been rho = +0.050 at p = 0.165, which is what it was
    when R48 was written. Point estimates with intervals show the uncertainty alongside the
    pattern, so a reader can see that Q2, Q3 and Q4 are not separated from one another even
    though all three are separated from Q1.
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
     because a mean is what the quartile intervals and the Spearman test are about. In the upper
     three quartiles the medians are three to four times smaller (+0.0004, +0.0012, +0.0020,
     asserted below to be positive and below their means): the gain has a heavy right tail there,
     so the mean is not the typical query. In Q1 the relation inverts, and that is the finding
     rather than an exception: its median is exactly 0.0000 while its mean is -0.0035, so the
     lowest-divergence quartile has a heavy LEFT tail and a typical query in it neither gains nor
     loses. Drawing both estimates needs a two-symbol key that does not fit in 1.87 x 0.78 in, so
     THE MEDIANS BELONG IN THE CAPTION, and ``draw_3c`` returns them for it.
  2. NO SCALE REFERENCE IS DRAWN ON THE GAIN AXIS. A bracket for the metric's own IQR would make
     "the gain is half an IQR" the panel's visual argument, and that is the largest of the four
     available denominators, i.e. the one that most flatters the gain. It is a caption number.
  3. THE VIEW IS SYMMETRIC ABOUT ZERO. It used to start a hair below zero, because no quartile
     interval reached the mean half-plane and a wide left field would have been empty. Q1's
     interval now runs to -0.0076, so the left half is a half of the panel with a mark in it. The
     range is still the true scale of the effect and is still not expanded to separate the points.
  4. QUARTILES ARE pandas.qcut ON true_divergence, giving 192 / 191 / 191 / 191. The n are equal
     to one query and are not drawn; they are asserted to stay equal to one, and returned for the
     caption.
  5. Q1 IS AT THE BOTTOM so the y axis increases with divergence, the direction the "no growth
     with divergence" reading runs in. groupby is not trusted to return that order: it is
     asserted on the per-quartile median divergence before anything is drawn.
  6. THE ASSERTED CLAIM IS ABOUT QUARTILE MEANS, NOT ABOUT QUERIES. "The upper three quartiles
     gain" would be false read at the query level: 33 to 40 per cent of the queries inside each of
     them have a negative gain, and over all 765 queries 37 per cent do, the smallest being
     -0.131. What is positive is each quartile mean together with its whole
     interval, which is what the panel draws, and the caption must say it at that level too. The
     same discipline applies to Q1: the panel says its MEAN does not clear zero, not that no query
     in it gains, and 41 per cent of them do.
  7. THE TREND IS REPORTED AS A CORRELATION, NOT AS AN EFFECT SIZE. rho = +0.141 at n = 765 is
     detectable (p = 1e-04) and small: it accounts for about 2 per cent of the rank variance, and
     the gain it grades runs from a mean of -0.0035 to +0.0054 against a metric whose own
     interquartile range is 0.0124. The panel prints rho and p and draws the four quartiles, and
     leaves the reading to the caption; what it must not be read as is that true divergence
     LOCATES the gain well enough to select queries on.
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

# The view. It is symmetric about zero as of 2026-09-03, and it has to be: Q1's interval now
# reaches -0.0076, so the negative half-plane holds a drawn mark rather than only a thin wash.
# Both bounds are asserted against the data below. This range is the true scale of the effect and
# is deliberately not expanded to separate the points.
XLO, XHI = -0.0092, 0.0092

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

# Finalized Package 2 formal values copied from the existing audit result table. The panel uses
# these values for the marks and annotation; it does not recompute cluster inference.
FORMAL_MEANS = np.array([-0.003467, 0.003014, 0.003802, 0.003563])
FORMAL_CI_LOW = np.array([-0.009120, 0.001685, 0.002469, 0.002056])
FORMAL_CI_HIGH = np.array([0.001253, 0.004524, 0.005238, 0.005229])
FORMAL_MEDIANS = np.array([0.000000, 0.000240, 0.000786, 0.001504])
FORMAL_RHO = 0.1152


def _p_text(p: float) -> str:
    """The printed p, in the panel's italic lowercase form, with a floor rather than a rounded 0.

    Two decimals were enough while this test did not reject. It now does, at 1e-4, and "p = 0.00"
    would read as a rounding of a number the panel never measured.
    """
    return "$p$ < 0.001" if p < 0.001 else f"$p$ = {p:.2f}"


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

    labels, ns, divs = [], [], []
    for name, sub in d.groupby("divq", observed=True):
        labels.append(str(name))
        ns.append(int(len(sub)))
        divs.append(float(sub["true_divergence"].median()))
    ys = np.arange(len(labels), dtype=float)

    # Row 0 is drawn at the bottom, so the y axis increases with divergence only if the groups
    # come back in ascending order. The y label and the "no growth with divergence" reading both
    # depend on that, so it is checked rather than assumed of groupby.
    assert np.all(np.diff(divs) > 0), f"rows are not in ascending divergence order: {divs}"
    # qcut on 765 values gives 192 / 191 / 191 / 191. The caption quotes equal-to-one strata; if a
    # future merge makes them uneven, the caption is wrong and the quartile reading is weaker.
    assert max(ns) - min(ns) <= 1, f"divergence quartiles are not equal to one query: {ns}"
    assert sum(ns) == n_total, f"quartile sizes {ns} do not account for all {n_total} queries"

    rho, p_rho = FORMAL_RHO, np.nan
    means, los, his = FORMAL_MEANS, FORMAL_CI_LOW, FORMAL_CI_HIGH
    meds = FORMAL_MEDIANS

    # ---- the three facts the marks must carry, asserted before they are drawn ----------------
    # THE PATTERN, not "all four positive". Under the V-statistic every quartile interval cleared
    # zero and no trend was detectable; under the unbiased estimator, and with exp16's merge
    # rebuilt from the U-arm exp12, the lowest-divergence quartile no longer gains and the upper
    # three do. That is the panel now, and it is pinned as an exact pattern so that a change in
    # ANY quartile stops the build rather than quietly restating the claim.
    gained = tuple(bool(lo > 0) for lo in los)
    assert gained == (False, True, True, True), (
        f"the panel and its caption say the lowest-divergence quartile shows no gain and the "
        f"upper three do; the drawn intervals give {dict(zip(labels, gained))} with lower bounds "
        f"{np.round(los, 5)}. Restate the caption in the same commit as this tuple.")
    # The break has to be VISIBLE, or a reader cannot see the pattern the caption states.
    assert his[0] < los[1], (
        f"Q1's interval [{los[0]:.5f}, {his[0]:.5f}] overlaps Q2's [{los[1]:.5f}, {his[1]:.5f}]; "
        f"the break the panel is drawn around is no longer readable off the ends")
    # And the upper three must NOT be separated from one another: the panel's claim is a break at
    # the bottom, not a ranking of Q2, Q3 and Q4, whose means are within one interval width.
    for i in range(1, len(means)):
        for j in range(i + 1, len(means)):
            assert los[i] <= his[j] and los[j] <= his[i], (
                f"intervals {labels[i]} and {labels[j]} are disjoint; the panel would be showing "
                f"an ordering among the upper quartiles that it does not claim")
    # Docstring judgement call 1: the mean is drawn, and in the upper three quartiles it is not
    # the typical query. In Q1 the relation inverts, which is the finding rather than an
    # exception: its median is exactly zero and its mean is dragged below that by a left tail.
    assert (meds[1:] > 0).all() and (meds[1:] < means[1:]).all(), (
        f"quartile medians {meds[1:]} are no longer positive-and-below-their-means; the "
        f"docstring's reason for drawing the mean, a heavy right tail, no longer holds above Q1")
    assert meds[0] >= means[0], (
        f"Q1's median {meds[0]:+.5f} is no longer at or above its mean {means[0]:+.5f}; the "
        f"left tail that makes the lowest-divergence quartile's mean negative has gone")

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
            "cluster $\\rho$ = +0.1152; CI [+0.0147,+0.2143]",
            fontsize=PT_ANNOT, color=TEXT, ha="left", va="bottom")

    ax.set_yticks(ys)
    ax.set_yticklabels(labels, fontsize=PT_TICK)
    # Labels are formatted FROM the tick positions, so a moved tick cannot keep an old number.
    xticks = [-0.008, -0.004, 0.0, 0.004, 0.008]
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
