"""PopRetrieve Figure 3 panel 3c: the minority-coverage gain, by true-divergence quartile.

WHAT THIS PANEL CLAIMS
----------------------
Exactly two things, both of which need no chosen yardstick:

  * the population-minus-mean minority-coverage gain is POSITIVE in every divergence stratum
    (all four bootstrap 95 per cent intervals lie above zero), and
  * NO GROWTH with true divergence is detectable (Spearman rho = +0.050, p = 0.17 over all 765
    queries; the four intervals mutually overlap and Q4 sits below Q3).

The second is the point of the panel, and it is why this panel belongs with d, e and f: the
pre-specified gate assumes the gain is concentrated where the true response distribution diverges
from its mean, and no such concentration is detectable along exactly that axis.

Source data: results/exp16_gate_diagnosis/_merged_query_divergence.csv, 765 queries with both
true_divergence and minority_state_coverage_gap. Every number drawn or written here is computed
from that file at draw time; nothing is a literal. figures/source_data/fig3ef_gate_divergence.csv
is a hand-built column view of the same file and is deliberately not read.

WHAT THIS PANEL REFUSES TO CLAIM, AND WHY (2026-08-31 rebuild)
--------------------------------------------------------------
The previous version drew four bars with s.e.m. on an axis truncated at 0.012 and titled itself
"Minority-coverage gain is negligible". Both halves were wrong.

  * THE BARS SHOWED A TREND THAT IS NOT THERE. Q1 to Q3 rise, and a truncated bar axis turns that
    into a visible ramp, but Spearman rho with divergence is +0.050 at p = 0.165, Q4 is below Q3,
    and all four intervals overlap. The panel now draws point estimates with intervals, which
    makes the overlap the visible fact, and states the correlation once.
  * "NEGLIGIBLE" DEPENDED ON THE DENOMINATOR, and the denominators disagree hard. The largest
    quartile mean, +0.0062, is 0.6 per cent of the nominal [0, 1] metric range, 2.6 per cent of
    the metric's observed range, 5.1 per cent of its central 98 per cent, and 53 per cent of the
    metric's own interquartile range; the paired Cohen's d is 0.33. Choosing among those is
    precisely the error this paper exists to criticise, so the panel makes no size claim at all.
    It prints one scale reference for the metric itself, the median and interquartile range of the
    1,530 coverage values the gains are differences of, and lets the reader size the gain.

JUDGEMENT CALLS A READER COULD REASONABLY DISAGREE WITH
-------------------------------------------------------
  1. THE POINT ESTIMATE IS THE MEAN, not the median, because the brief for this panel fixes it and
     because a mean is what the quartile intervals and the Spearman test are about. The medians
     are three to four times smaller (+0.0009, +0.0015, +0.0017, +0.0018): this gain has a heavy
     right tail, so the mean is not the typical query. Drawing both needs a two-symbol key that
     does not fit in 1.87 x 0.70 in, so THE MEDIANS BELONG IN THE CAPTION and the docstring
     records them.
     A reader who wants the typical query rather than the average one should read them there.
  2. THE SCALE REFERENCE IS THE METRIC'S OWN MEDIAN AND IQR, pooled over both arms (population and
     mean), stated as text and NOT drawn as a bracket on the gain axis. A drawn bracket would make
     "the gain is half an IQR" the panel's visual argument, and that is the largest of the four
     available denominators, i.e. the one that most flatters the gain.
  3. THE VIEW STARTS AT A SMALL NEGATIVE VALUE so zero is a datum inside the frame rather than the
     left edge. The negative half-plane is therefore a thin wash, which is honest: no quartile
     interval reaches it.
  4. QUARTILES ARE pandas.qcut ON true_divergence, giving 192 / 191 / 191 / 191. The n are equal
     to one query and are not drawn; they are in the caption.
  5. Q1 IS AT THE BOTTOM so the y axis increases with divergence, the direction the "no growth
     with divergence" reading runs in. groupby is not trusted to return that order: it is
     asserted on the per-quartile median divergence before anything is drawn.
  6. THE PHRASE OVER THE PANEL SAYS "all four positive", NOT "positive everywhere". The latter
     would be read at the query level and is false there: 26.9 per cent of the 765 queries have a
     negative gain and the smallest is -0.130. What is positive is each of the four quartile means
     together with its whole interval, which is what the panel draws.
  7. THE PHRASE SAYS "no trend VISIBLE", not "no trend". rho = +0.050 at n = 765 has a normal
     approximate 95 per cent interval of about [-0.02, +0.12], so a weak positive trend is not
     excluded; what the panel can report is that none is detectable in it. Asserting the bare null
     from a non-significant test is the same overclaim, mirrored, that this paper exists to
     criticise, so the phrase is a statement about the panel and not about the population.

Run standalone: python3 fig3c.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig3_style import (LW_HAIR, LW_LINE, MS_DOT, PT_ANNOT, PT_SMALL,  # noqa: E402
                        PT_TICK, REPO, SHARED, TEXT, bare_axes, boot_ci, sign_field, title,
                        zero_rule)

SRC = os.path.join(REPO, "results", "exp16_gate_diagnosis", "_merged_query_divergence.csv")

GAIN = "minority_state_coverage_gap"
POP_ARM = "minority_state_coverage_dart"
MEAN_ARM = "minority_state_coverage_mean"

# The view. XLO is a hair below zero so the zero rule is a datum with room on both sides; XHI
# clears the widest interval. Both are asserted against the data below.
XLO, XHI = -0.0014, 0.0092
# Row 0 is Q1, row 3 is Q4. The bands below row 0 and above row 3 carry the two notes and hold
# no data ink; they are sized so a 7.2 pt and a 6.5 pt line clear the outer dots inside 0.70 in.
YLO, YHI = -1.50, 4.50


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
    """Four quartile means with bootstrap 95 per cent intervals, against zero."""
    d = _load()
    n_total = len(d)

    labels, means, los, his, divs = [], [], [], [], []
    for name, sub in d.groupby("divq", observed=True):
        m, lo, hi = boot_ci(sub[GAIN].values, stat=np.mean, seed=0)
        labels.append(str(name))
        means.append(m)
        los.append(lo)
        his.append(hi)
        divs.append(float(sub["true_divergence"].median()))
    means, los, his = np.asarray(means), np.asarray(los), np.asarray(his)
    ys = np.arange(len(labels), dtype=float)

    # Row 0 is drawn at the bottom, so the y axis increases with divergence only if the groups
    # come back in ascending order. The y label and the "no growth with divergence" reading both
    # depend on that, so it is checked rather than assumed of groupby.
    assert np.all(np.diff(divs) > 0), f"rows are not in ascending divergence order: {divs}"

    rho, p_rho = stats.spearmanr(d["true_divergence"].values, d[GAIN].values)

    # ---- the two claims the panel makes, asserted before they are drawn or written -----------
    assert (los > 0).all(), (
        f"a quartile interval reaches zero, so 'all four positive' is false: lower bounds {los}")
    for i in range(len(means)):
        for j in range(i + 1, len(means)):
            assert los[i] <= his[j] and los[j] <= his[i], (
                f"intervals {labels[i]} and {labels[j]} are disjoint; a trend IS visible and "
                f"'no trend visible' is false")
    assert p_rho > 0.05, (
        f"Spearman p = {p_rho:.3g} is significant; 'no trend visible' is no longer what the data "
        f"say and the phrase over the panel must change")

    # ---- the metric's own scale, pooled over both arms. One reference, no denominator picked ---
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
    # stops short of the two note bands. Left full height it printed straight through the words
    # "Spearman" and "metric", which no text-vs-text layout check can see. axvline blends x in
    # data coordinates with y in AXES coordinates, so the row band is converted here.
    ROW_OVERHANG = 0.45     # rows are one data unit apart, so this is 0.45 of a row past each end
    zr = zero_rule(ax, at=0.0, vertical=True, color=TEXT, lw=0.8)
    zr.set_ydata([(ys.min() - ROW_OVERHANG - YLO) / (YHI - YLO),
                  (ys.max() + ROW_OVERHANG - YLO) / (YHI - YLO)])

    ax.hlines(ys, los, his, color=SHARED, lw=LW_LINE, zorder=3)
    ax.scatter(means, ys, s=MS_DOT, color=SHARED, zorder=4, linewidths=0, clip_on=False)

    # ---- the one statistic, stated once, in the data-free band above the rows -----------------
    ax.text(XLO + 0.0004, YHI - 0.90,
            f"Spearman $\\rho$ = {rho:+.2f}, p = {p_rho:.2f}",
            fontsize=PT_ANNOT, color=TEXT, ha="left", va="bottom")
    # ---- one honest scale reference for the metric itself, in the band below the rows ---------
    ax.text(XLO + 0.0004, YLO + 0.04,
            f"metric itself: median {med_metric:.3f}, IQR {iqr_metric:.3f}",
            fontsize=PT_SMALL, color=TEXT, ha="left", va="bottom")

    ax.set_yticks(ys)
    ax.set_yticklabels(labels, fontsize=PT_TICK)
    # Labels are formatted FROM the tick positions, so a moved tick cannot keep an old number.
    xticks = [0.0, 0.004, 0.008]
    ax.set_xticks(xticks)
    ax.set_xticklabels([f"{t:g}" for t in xticks], fontsize=PT_TICK)
    ax.set_xlabel("minority-coverage gain,\npopulation $-$ mean", fontsize=PT_ANNOT, labelpad=1.5)
    ax.set_ylabel("true-divergence\nquartile", fontsize=PT_ANNOT, labelpad=1.5)

    bare_axes(ax, keep=("bottom",))
    ax.tick_params(axis="y", length=0)
    ax.spines["bottom"].set_linewidth(LW_HAIR)

    title(ax, "All four positive, no trend visible")
    return {"labels": labels, "mean": means, "lo": los, "hi": his,
            "rho": float(rho), "p": float(p_rho), "n": n_total,
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
    fig = plt.figure(figsize=(2.75, 1.34))
    ax = fig.add_axes([0.78 / 2.75, 0.40 / 1.34, 1.87 / 2.75, 0.70 / 1.34])
    stats_out = draw_3c(ax)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "3c.png")
    fig.savefig(out, dpi=300)
    print({k: (np.round(v, 5).tolist() if isinstance(v, np.ndarray) else v)
           for k, v in stats_out.items()})
    print(f"wrote {out}")
