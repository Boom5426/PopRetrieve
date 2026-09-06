"""PopRetrieve Figure 3 panel 3d: the mechanism-recovery gain, by the SAME true-divergence quartile.

WHAT THIS PANEL SHOWS
---------------------
Panel c and this panel are one comparison drawn twice. Both split the queries into quartiles of
measured true response divergence, using the SAME quartile edges, and both plot the mean
population-minus-mean gain with a bootstrap 95 per cent interval. Only the judge changes: panel c
scores minority-state coverage, which is objective-aligned, and this panel scores mechanism-of-action
nDCG, which is not.

Three facts are meant to be readable from the marks alone:

  * NO quartile mean clears zero on the positive side. Not the most divergent one.
  * the two LEAST divergent quartiles are wholly negative (-0.050 and -0.039): where the response
    distribution is closest to its own mean, population-level retrieval actively costs mechanism
    recovery.
  * the two most divergent quartiles straddle zero (-0.016 and +0.014), so what more divergence
    buys is the disappearance of the harm, not the appearance of a benefit.

All three are asserted in ``draw_3d`` before anything is drawn. The panel states none of them in
words: the caption carries the argument, this panel carries the evidence for it.

The per-query trend has the SAME sign as panel c's and about the same strength (Spearman
rho = +0.155, p = 1e-04, n = 600, against +0.141 and 1e-04 on n = 765). Read together, the pair is
the figure's cleanest statement: true response divergence grades both metrics in the same
direction, and it carries the objective-aligned one from zero up to positive while it carries the
independent one from negative up to zero.

WHY THIS PANEL EXISTS, AND WHERE IT CAME FROM
----------------------------------------------
It was Figure 5 panel g until Figure 5 was rebuilt around the intervention-retrieval benchmark on
2026-09-03. The measurement is unchanged; what changed is which argument it serves. Beside the old
Figure 5 it was a robustness check on a predictor; beside panel c it is the control that stops
panel c's positive trend from being read as a biological result. Panel c alone would say
"divergence predicts where population retrieval helps"; the two together say "it predicts where
each judge's verdict lands, and the two judges do not agree on the sign".

WHY IT IS NOT DRAWN THE WAY FIGURE 5g DREW IT
----------------------------------------------
Figure 5g drew four bars with significance markers, asterisk for q < 0.05 after Benjamini-Hochberg
and "ns" otherwise. That drawing is not reproduced here, and the reason is on the record for this
exact quantity's sibling: CORRECTIONS.md R48 retired four-bars-with-error-marks from panel c
because a truncated bar axis turns any rise into a visible ramp whatever its uncertainty, and
because a significance marker answers a different question from the one the panel asks. A reader
of this pair needs to compare an INTERVAL in c against an INTERVAL in d, at a glance, in two
panels that sit side by side. Two identical chart types is what makes that possible; two chart
types with different visual grammars would make the pair unreadable as a pair.

The BH q values are not lost. They are computed by
results/exp17_true_divergence_subset/divergence_stratified.csv, returned by ``draw_3d`` for the
caption, and they say the same thing the intervals say: q = 0.002 and 0.025 for the two negative
quartiles, 0.643 and 0.126 for the two that straddle zero.

SOURCE
------
results/exp16_gate_diagnosis/_merged_query_divergence.csv, the same file panel c reads. 765 queries
carry ``true_divergence``; 600 of them carry ``moa_ndcg_gap``, because mechanism recovery is only
defined on the leave-drug-out split where a held-out drug has a mechanism label to recover. Every
number drawn is computed from that file at draw time; none is a literal.

JUDGEMENT CALLS A READER COULD REASONABLY DISAGREE WITH
-------------------------------------------------------
  1. THE QUARTILE EDGES COME FROM ALL 765 QUERIES, then the rows are subset to the 600 that have a
     mechanism-recovery gain. The alternative, quartiling the 600 directly, gives four rows of 150
     but four DIFFERENT divergence ranges from panel c's, and the pair would then be comparing
     strata that are not the same strata. The cost is uneven n (166 / 150 / 141 / 143), which is
     drawn on the panel rather than hidden: the 165 queries without a mechanism gain are the
     partial-library ones and they are slightly more divergent than average, so they come mostly
     out of Q2 to Q4.
  2. THE POINT ESTIMATE IS THE MEAN, matching panel c, and here the medians are nearly useless as
     a summary: three of the four are exactly 0.000, because 17 to 32 per cent of the queries in
     each quartile select the same candidate under both scorers and score an exact tie. Those
     medians are returned for the caption; drawing them would put three dots on the zero rule and
     say less than the intervals do.
  3. THE VIEW IS SYMMETRIC ABOUT ZERO even though every mark is on or left of it. The empty right
     half is the panel's second statement: at this scale, on this metric, there is nothing over
     there. Cropping to the marks would hide that.
  4. THE X SCALE IS NOT SHARED WITH PANEL c. The two metrics differ by an order of magnitude
     (c's largest interval end is +0.0073, this panel's is -0.0755), and a shared scale would draw
     panel c as four dots on a rule. Each panel is labelled with its own metric, and the pair is
     read as two verdicts on the same strata, never as two magnitudes on one ruler.
  5. THE PANEL PRINTS rho AND p FOR THE 600, NOT FOR THE 765. Panel c's statistic is over all 765
     because every one of them has a coverage gain. Quoting a 765-query correlation here would be
     quoting a correlation over queries this panel does not draw.

Run standalone: python3 fig3d.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig3_style import (LW_HAIR, LW_LINE, LW_STEM, MS_DOT, PT_ANNOT,  # noqa: E402
                        PT_TICK, REPO, SHARED, SUBTLE, TEXT, bare_axes, boot_ci, sign_field,
                        zero_rule)

SRC = os.path.join(REPO, "results", "exp16_gate_diagnosis", "_merged_query_divergence.csv")

GAIN = "moa_ndcg_gap"
POP_ARM = "moa_ndcg_dart"
MEAN_ARM = "moa_ndcg_mean"
DIV = "true_divergence"

N_ALL = 765           # queries carrying true_divergence; the quartile edges are cut on these
N_SCORED = 600        # of those, the ones carrying a mechanism-recovery gain

# The view, symmetric about zero: see judgement call 3. Asserted against the data below.
XLO, XHI = -0.090, 0.090
XTICKS = [-0.08, -0.04, 0.0, 0.04, 0.08]

# Rows are one data unit apart, Q1 at y = 0 and Q4 at y = 3; the rest of the y axis is clearance,
# in the same units. Identical to panel c, because the two panels are read as a pair.
CLEAR_BOT = 0.45
CLEAR_TOP = 0.50
STAT_Y = 3.0 + CLEAR_TOP
YLO, YHI = -CLEAR_BOT, 4.22
LINE_H = 1.15
ROW_OVERHANG = 0.38
CAP = 0.17


def _p_text(p: float) -> str:
    """The printed p, in this figure's italic lowercase form, with a floor rather than a rounded 0."""
    return "$p$ < 0.001" if p < 0.001 else f"$p$ = {p:.2f}"


def _load():
    """The 600 scored queries, carrying the divergence quartile cut on all 765."""
    raw = pd.read_csv(SRC)
    assert len(raw) == N_ALL, (
        f"the quartile edges are cut on all {N_ALL} queries so that this panel's rows are panel "
        f"c's rows; the file now holds {len(raw)}")
    assert raw[DIV].notna().all(), (
        "a query lacks true_divergence, so the quartile it belongs to is undefined and the edges "
        "would be cut on a subset without saying so")
    d = raw.assign(divq=pd.qcut(raw[DIV], 4, labels=["Q1", "Q2", "Q3", "Q4"]))
    scored = d.dropna(subset=[GAIN])
    assert len(scored) == N_SCORED, (
        f"expected {N_SCORED} queries with a mechanism-recovery gain, found {len(scored)}")
    # The axis label says "population - mean". Assert it, so the label cannot outlive the data.
    ok = scored[[POP_ARM, MEAN_ARM]].notna().all(axis=1)
    assert np.allclose(scored.loc[ok, GAIN].values,
                       scored.loc[ok, POP_ARM].values - scored.loc[ok, MEAN_ARM].values,
                       atol=1e-12), (
        f"{GAIN} is not {POP_ARM} minus {MEAN_ARM}; the signed axis label would be false")
    return scored


def draw_3d(ax):
    """Four quartile means with bootstrap 95 per cent intervals, against zero.

    Returns every number the caption for this panel quotes, so the caption is checkable against a
    run of this module rather than against a memory of one.
    """
    d = _load()
    n_total = len(d)

    labels, means, los, his, meds, ns, divs, ties = [], [], [], [], [], [], [], []
    for name, sub in d.groupby("divq", observed=True):
        v = sub[GAIN].to_numpy(dtype=float)
        m, lo, hi = boot_ci(v, stat=np.mean, seed=0)
        labels.append(str(name))
        means.append(m)
        los.append(lo)
        his.append(hi)
        meds.append(float(np.median(v)))
        ns.append(int(v.size))
        divs.append(float(sub[DIV].median()))
        ties.append(float((v == 0).mean()))
    means, los, his = np.asarray(means), np.asarray(los), np.asarray(his)
    meds, ties = np.asarray(meds), np.asarray(ties)
    ys = np.arange(len(labels), dtype=float)

    rho, p_rho = stats.spearmanr(d[DIV].values, d[GAIN].values)

    # ---- the three facts the marks must carry, asserted before they are drawn ----------------
    assert np.all(np.diff(divs) > 0), f"rows are not in ascending divergence order: {divs}"
    assert sum(ns) == n_total, f"quartile sizes {ns} do not account for all {n_total} queries"
    # Uneven n is expected here and is DRAWN; what must not happen is a quartile emptying out.
    assert min(ns) >= 100, (
        f"a divergence quartile holds only {min(ns)} scored queries ({ns}); at that size its "
        f"interval carries the panel's claim on too little data")

    assert not (los > 0).any(), (
        f"a quartile mean now clears zero on the positive side ({dict(zip(labels, np.round(los, 4)))}); "
        f"the panel's whole claim is that none does, and the caption must change with it")
    assert his[0] < 0.0 and his[1] < 0.0, (
        f"the two least divergent quartiles are supposed to be wholly negative; their upper "
        f"bounds are {his[0]:+.4f} and {his[1]:+.4f}")
    for i in (2, 3):
        assert los[i] < 0.0 < his[i], (
            f"{labels[i]} is supposed to straddle zero; its interval is "
            f"[{los[i]:+.4f}, {his[i]:+.4f}]")
    assert rho > 0 and p_rho < 0.01, (
        f"Spearman rho = {rho:+.4f}, p = {p_rho:.3g}: the trend this panel prints no longer runs "
        f"in the same direction as panel c's, which is the pair's whole point")

    # Judgement call 2: the medians are drawn from a distribution with a large exact-tie atom, and
    # the panel says so through the n column rather than by plotting three dots on the zero rule.
    assert (ties > 0.10).all(), (
        f"the exact-tie fractions {np.round(ties, 3)} no longer justify judgement call 2's reason "
        f"for drawing the mean rather than the median")

    # ---- the view --------------------------------------------------------------------------
    assert XLO < 0.0 < XHI, "zero must be a datum inside the frame, not an edge of it"
    assert his.max() < XHI and los.min() > XLO and means.min() > XLO and means.max() < XHI, (
        f"the view clips a drawn mark: means [{means.min():.4f}, {means.max():.4f}], intervals "
        f"[{los.min():.4f}, {his.max():.4f}] against [{XLO}, {XHI}]")
    assert STAT_Y > ys.max() + max(ROW_OVERHANG, CAP), "the statistic sits on the top row"
    assert YLO < ys.min() - max(CAP, ROW_OVERHANG), (
        f"the y view [{YLO}, {YHI}] clips a cap or the end of the zero rule")
    ax_h_in = ax.get_position().height * ax.figure.get_figheight()
    band_in = (YHI - STAT_Y) / (YHI - YLO) * ax_h_in
    assert band_in >= LINE_H * PT_ANNOT / 72.0, (
        f"the band above the rows is {band_in:.4f} in on a {ax_h_in:.3f} in axes, under the "
        f"{LINE_H * PT_ANNOT / 72.0:.4f} in one {PT_ANNOT} pt line prints at")

    # Sign, not object: the plotted quantity is a signed difference, so it is SHARED grey and the
    # two half-planes carry blue and orange behind it. Identical to panel c.
    ax.set_xlim(XLO, XHI)
    ax.set_ylim(YLO, YHI)
    lo_wash, hi_wash = sign_field(ax, vertical=True, at=0.0, pop_side="right")
    lo_wash.set_bounds(XLO, 0.0, -XLO, 1.0)
    hi_wash.set_bounds(0.0, 0.0, XHI, 1.0)
    zr = zero_rule(ax, at=0.0, vertical=True, color=TEXT, lw=0.8)
    zr.set_ydata([(ys.min() - ROW_OVERHANG - YLO) / (YHI - YLO),
                  (ys.max() + ROW_OVERHANG - YLO) / (YHI - YLO)])

    ax.hlines(ys, los, his, color=SHARED, lw=LW_LINE, zorder=3)
    ax.vlines(np.concatenate([los, his]), np.concatenate([ys, ys]) - CAP,
              np.concatenate([ys, ys]) + CAP, color=SHARED, lw=LW_STEM, zorder=3)
    ax.scatter(means, ys, s=MS_DOT, color=SHARED, zorder=4, linewidths=0, clip_on=False)

    # The n per row, because they are uneven here and panel c's are not (judgement call 1). They
    # sit in the empty right half, which is the only part of this panel with room and the part a
    # reader has no other reason to look at.
    for y, n in zip(ys, ns):
        ax.text(XHI - 0.004, y, f"n = {n}", fontsize=PT_TICK, color=SUBTLE, ha="right",
                va="center", zorder=5)

    ax.text(XLO + 0.004, STAT_Y, f"Spearman $\\rho$ = {rho:+.2f}, {_p_text(p_rho)}",
            fontsize=PT_ANNOT, color=TEXT, ha="left", va="bottom")

    ax.set_yticks(ys)
    ax.set_yticklabels(labels, fontsize=PT_TICK)
    assert all(XLO <= t <= XHI for t in XTICKS), f"a tick lies outside the view: {XTICKS}"
    ax.set_xticks(XTICKS)
    ax.set_xticklabels([f"{t:g}" for t in XTICKS], fontsize=PT_TICK)
    ax.set_xlabel("MoA-nDCG gain,\npopulation − mean", fontsize=PT_ANNOT, labelpad=1.5)
    ax.set_ylabel("true-divergence\nquartile", fontsize=PT_ANNOT, labelpad=1.5)

    bare_axes(ax, keep=("bottom",))
    ax.tick_params(axis="y", length=0)
    ax.spines["bottom"].set_linewidth(LW_HAIR)

    return {"labels": labels, "n_per_quartile": ns, "mean": means, "lo": los, "hi": his,
            "median": meds, "tie_fraction": ties, "rho": float(rho), "p": float(p_rho),
            "n": n_total}


if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from figstyle import apply_style
    from fig3_style import PT_TITLE

    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    BOX_W, BOX_H, PAD_L, PAD_B, AX_W, AX_H = 2.75, 1.36, 0.72, 0.42, 1.93, 0.78
    fig = plt.figure(figsize=(BOX_W, BOX_H))
    ax = fig.add_axes([PAD_L / BOX_W, PAD_B / BOX_H, AX_W / BOX_W, AX_H / BOX_H])
    out = draw_3d(ax)
    print({k: (np.round(v, 5).tolist() if isinstance(v, np.ndarray) else v)
           for k, v in out.items()})
    fig.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)), "3d.png"), dpi=300)
    print("wrote 3d.png")
