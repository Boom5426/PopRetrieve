"""PopRetrieve Figure 3 panel a: the headline reversal, drawn as ONE quantity judged twice.

WHAT THIS PANEL CLAIMS
----------------------
Both rows are the SAME signed quantity, the population-minus-mean retrieval advantage, on the
SAME 480 paired leave-drug-out queries. Nothing is retrained between the rows; only the metric
doing the judging changes. Judged by response matching, the advantage has median +0.129 and 73
per cent of queries favour population retrieval. Judged by mechanism recovery, the median is
exactly 0.000 and 35 per cent of queries favour population retrieval. That is the reversal the
whole figure exists to carry, and it is two of the figure's four skeleton numbers.

SOURCE
------
figures/source_data/fig3a_classA_vs_classB.csv, columns ``classA_regret_reduction`` (response
matching) and ``classB_moa_ndcg_gain`` (mechanism recovery), 480 rows, one per (cell line,
held-out drug, seed). Every number drawn is computed from that file at draw time; there are no
literals in any label, and the relationships the labels assert are checked in code below so a
label cannot outlive the data.

THE 480 ARE A SUBSET, AND THE FILE DOES NOT SAY SO (open defect, 2026-08-31)
---------------------------------------------------------------------------
The leave-drug-out paired query set is 600, not 480. Rebuilding the pair from
``results/exp12_partial_observed_retrieval/per_query_scores.csv`` (baseline ``mean_cosine``,
variant ``DART_coverage_worst``, ``split_type == leave_drug_out``) gives 600 paired queries; this
file is exactly the 480 of them with ``recommendation_mode == "DART_recommended"``, matching value
for value to 4e-16. The other 120 are the queries the information-condition gate did NOT recommend,
and they are dropped with no column, README line or generator recording the choice. The gate that
did the dropping is the one panels d, e and f of this same figure show does not work.

The selection is nearly inert, which is the only reason this panel still stands: on all 600 the
response-matching median is +0.1288 against the drawn +0.1292, its mean +0.2752 against the drawn
+0.2881, and mechanism recovery gives median 0.000, mean -0.0371, 34.2 per cent favouring
population against the drawn 35.0. The direction, the collapse and the reversal are unchanged.
But an unrecorded subset chosen by the paper's own gate is the analytic degree of freedom this
paper exists to criticise, and the manuscript's numerical contract quotes these same statistics on
600. The fix belongs in the source file, not here: regenerate
``figures/source_data/fig3a_classA_vs_classB.csv`` on all 600 leave-drug-out paired queries, or
carry ``recommendation_mode`` as a column so a panel can state what it is drawing. Panel b reads
the same file and inherits the same subset. Until then the exclusion is disclosed in the caption,
below.

THE COLOUR ERROR THIS VERSION FIXES (2026-08-31)
------------------------------------------------
The previous version drew the two distributions in FOCAL_SOFT blue and COMP_SOFT orange, the
deck's colours for population retrieval and mean retrieval. That said the right-hand distribution
WAS the mean method. It is not: it is the same population-minus-mean advantage, scored by a
different evaluator. Colour was encoding the wrong variable in the figure's most important panel.
Here both distributions are SHARED grey, and blue and orange appear only as the half-planes behind
them (fig3_style.sign_field), where they say which sign favours which representation.

JUDGEMENT CALLS A READER COULD REASONABLY DISAGREE WITH
-------------------------------------------------------
1. ORIENTATION. The advantage runs along x, and the two evaluators are stacked rows, so the sign
   semantics read left/right rather than up/down. The panel is 3.16 x 0.84 in. On a vertical value
   axis the whole claim, a median shift of +0.129 against 0.000, would print as about 3 pt of
   offset, and less once this panel's annotation is deducted from the height; along x it prints
   as 11.7 pt. The argument has to be visible in three seconds, so the long side of the axes
   carries the quantity that carries it.
2. THE VIEW STOPS AT +1.42 while Class A runs to +2.82. Opening the view to the maximum would
   compress the region where every median, quartile and tie actually lives into the left third.
   The truncation is stated on the panel (the fraction beyond the view and the true maximum) and
   marked with a chevron at the right end of the response-matching baseline; nothing is silently
   amputated. Nothing is truncated on the left, and mechanism recovery is fully inside the view;
   both facts are asserted below, because "tail to +2.82" would otherwise be a claim about which
   side is cut that the data could stop supporting.
3. COMMON DENSITY SCALE, NOT EQUAL VIOLIN WIDTHS. Both rows have the same n, so the two densities
   are drawn on one scale: mechanism recovery peaks about twice as high because it is genuinely
   more concentrated. Per-row normalisation to equal maximum width, matplotlib's violinplot
   default, would have made an artefact of that difference.
4. A KERNEL DENSITY CANNOT DRAW AN ATOM. 24 per cent of the mechanism-recovery queries are EXACT
   ties: the same candidate scores identically under both retrievers. The kernel smooths that
   spike into a finite peak, so the tie fraction is stated in text rather than left to the shape.
5. HALF-VIOLINS (density upward from a baseline) rather than symmetric violins. At 0.84 in the
   two-sided form spends half its height mirroring information it already showed, and the baseline
   is needed anyway to carry the interquartile bar, the median dot and the truncation chevron.
6. ALL ANNOTATION IS SET IN INK, with size as the only secondary channel. The half-plane washes
   run the full height of the axes, so every label sits on one; META grey on POP_WASH is about
   3.5:1, under any legibility threshold worth naming at 6.5 pt, while INK is about 14:1.

CUT INTO THE CAPTION (this panel is 3.16 x 0.84 in and nothing here is shrunk to fit)
-------------------------------------------------------------------------------------
The share of queries favouring MEAN retrieval (19 per cent under response matching, 41 per cent
under mechanism recovery; neither pair sums to 100 because both rows carry exact ties, 8 per cent
under response matching and 24 per cent under mechanism recovery), the per-cell-line composition
(A549 157, K562 146, MCF7 177), the paired Wilcoxon p = 1.1e-3 for the mechanism-recovery
distribution, and the sentence the section above requires until the source file is regenerated:
these 480 are the gate-recommended subset of the 600 leave-drug-out paired queries, and on all 600
the two medians are +0.129 and 0.000 with 34 per cent favouring population under mechanism
recovery. The Wilcoxon quoted here counts zeros and treats the 480 as independent; they are 336
distinct held-out drug and cell-line settings repeated across five seeds, so it is anticonservative
and the manuscript's 600-query, zeros-excluded p = 2.4e-4 is the one to print if both appear.

Run standalone: python fig3a.py
"""
from __future__ import annotations

import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.backends.backend_agg import RendererAgg
from matplotlib.colors import to_hex
from scipy.stats import gaussian_kde

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig3_style import (HAIRLINE, MEAN_WASH, POP_WASH, PT_ANNOT, PT_SMALL,  # noqa: E402
                        REPO, SHARED, TEXT, bare_axes, sign_field, title, zero_rule)

SRC = os.path.join(REPO, "figures", "source_data", "fig3a_classA_vs_classB.csv")

# The view. XMAX is also the truncation cut: it is where the drawn density of the response-matching
# row stops and where its chevron sits.
XMIN, XMAX = -1.10, 1.42

# The vertical ledger, in POINTS measured down from the top of the axes. Written out because at
# 0.84 in of height every one of these is spent against the others, and a reader of this file
# should be able to add them up.
T_NOTE = 0.5        # the truncation note, right-aligned over the response-matching tail
T_BASE_A = 16.8     # response-matching baseline; its density grows upward from here
T_STAT_A = 20.4     # response-matching summary line (top of the text)
T_LINK = 34.5       # the "same rankings" label, mid-connector. The connector itself starts
                    # below the measured response-matching summary line, not at a baseline.
T_BASE_B = 46.0     # mechanism-recovery baseline
T_STAT_B = 49.6     # mechanism-recovery summary line
RIDGE_MAX = 15.0    # points of height given to the LARGER of the two density peaks
# Below the axes, measured downward from it: tick labels, then the two half-plane labels flanking
# zero, then the quantity. fig3_assemble.PADS["a"] owns that depth (0.42 in); the harness is what
# proves this ledger stays inside it.
T_SIGN = 12.8
T_XLAB = 21.0
ROW_LABELS = ("Response\nmatching", "Mechanism\nrecovery")


def _signed(v, nd=3):
    """A signed mathtext number whose sign is computed, never typed."""
    if abs(v) < 0.5 * 10 ** (-nd):
        return f"{0.0:.{nd}f}"
    return ("$+$" if v > 0 else "$-$") + f"{abs(v):.{nd}f}"


def _clamp_span(patch, x0, x1):
    """Redraw one sign_field half-plane on FINITE coordinates.

    fig3_style.sign_field builds its washes with axvspan(-1e9, 0) and axvspan(0, 1e9). They render
    correctly, being clipped to the axes, but their reported window extent is about 1e11 px wide,
    which any layout audit that measures artist extents reads as ink outside the panel. The patch
    is in the x-data / y-axes blended transform axvspan uses, so clamping it to the view changes
    nothing that is drawn. Called only after the limits are fixed.
    """
    patch.set_bounds(x0, 0.0, x1 - x0, 1.0)


def draw_3a(ax):
    """Same 480 paired queries, two evaluators, one signed advantage."""
    p = pd.read_csv(SRC)
    a = p["classA_regret_reduction"].to_numpy(dtype=float)
    b = p["classB_moa_ndcg_gain"].to_numpy(dtype=float)
    n = len(p)
    assert n == 480 and a.size == b.size == n, f"expected 480 paired queries, got {n}"
    # What the file is allowed to be. It is a subset of the 600 leave-drug-out paired queries (see
    # the header); these two assertions at least pin the split and the library condition, so the
    # word "leave-drug-out" and the single n cannot quietly start describing a mixture of regimes.
    assert (p["split_type"] == "leave_drug_out").all(), "the panel draws one split, not a mixture"
    assert (p["observed_library_fraction"] == 1.0).all(), "the panel draws the full-library regime"
    assert not p.duplicated(subset=["cell_line", "heldout_drug", "seed"]).any(), "queries repeat"

    med_a, med_b = float(np.median(a)), float(np.median(b))
    mean_a, mean_b = float(a.mean()), float(b.mean())
    pos_a, pos_b = float((a > 0).mean()), float((b > 0).mean())
    tie_b = float((b == 0).mean())
    # The panel's claim: the same advantage, judged by mechanism recovery, is centred on zero and
    # favours population retrieval far less often. If either of these ever stopped holding, the
    # labels below would still be computed but the panel would no longer be this figure's reversal.
    assert med_a > med_b, f"response matching no longer leads: {med_a} vs {med_b}"
    assert pos_a > pos_b, f"population is no longer favoured less often: {pos_a} vs {pos_b}"
    assert abs(med_b) < 5e-4, f"mechanism-recovery median is no longer 0.000: {med_b}"
    assert tie_b > 0, "the exact-tie statement needs exact ties"

    # Only the response-matching row leaves the view, and only on the right. The truncation note
    # says "run past the view, to <max>", which is a claim about WHICH side is cut.
    assert a.max() > XMAX > b.max(), "the truncation note assumes only row A exceeds the view"
    assert min(a.min(), b.min()) > XMIN, "nothing may leave the view on the left unannounced"
    beyond = float((a > XMAX).mean())

    fig = ax.get_figure()
    h_pt = ax.get_position().height * fig.get_figheight() * 72.0
    w_in = ax.get_position().width * fig.get_figwidth()

    def yat(t):
        """Axes-fraction y for a ledger position given in points below the axes top."""
        return 1.0 - t / h_pt

    def ybelow(t):
        """Axes-fraction y for a ledger position given in points BELOW the axes bottom."""
        return -t / h_pt

    def xfrac(x):
        return (x - XMIN) / (XMAX - XMIN)

    ax.set_xlim(XMIN, XMAX)
    ax.set_ylim(0.0, 1.0)
    ax.set_autoscale_on(False)
    # Before the ticks are configured, not after: bare_axes ends in a tick_params call that resets
    # label size and tick length on BOTH axes, so calling it later silently undoes the row labels'
    # size and puts the suppressed y ticks back.
    bare_axes(ax, keep=("bottom",))

    # ---------------------------------------------------------------- sign, not object
    # Blue and orange are half-planes here. The distributions themselves are grey, because a
    # signed difference is not a method.
    lo, hi = sign_field(ax, vertical=True, at=0.0, pop_side="right", zorder=0)
    assert to_hex(lo.get_facecolor()) == MEAN_WASH.lower(), "left wash is not the mean wash"
    assert to_hex(hi.get_facecolor()) == POP_WASH.lower(), "right wash is not the population wash"
    _clamp_span(lo, XMIN, 0.0)
    _clamp_span(hi, 0.0, XMAX)
    zero_rule(ax, at=0.0, vertical=True, zorder=2)

    # ---------------------------------------------------------------- the two densities
    kdes = [gaussian_kde(a), gaussian_kde(b)]
    grids = [np.linspace(max(XMIN, v.min()), min(XMAX, v.max()), 512) for v in (a, b)]
    dens = [k(g) for k, g in zip(kdes, grids)]
    peak = max(float(d.max()) for d in dens)          # ONE scale for both rows: same n, same units

    base_t = (T_BASE_A, T_BASE_B)
    for v, g, d, tb in zip((a, b), grids, dens, base_t):
        y0 = yat(tb)
        y1 = y0 + (d / peak) * (RIDGE_MAX / h_pt)
        ax.plot([g[0], g[-1]], [y0, y0], color=HAIRLINE, lw=0.6, zorder=2, solid_capstyle="butt")
        ax.fill_between(g, y0, y1, color=SHARED, alpha=0.50, lw=0, zorder=3)
        ax.plot(g, y1, color=SHARED, lw=0.7, zorder=4)
        q1, q3 = np.percentile(v, [25, 75])
        ax.hlines(y0, q1, q3, color=TEXT, lw=2.0, zorder=5, capstyle="butt")
        ax.plot(np.median(v), y0, "o", ms=3.2, mfc="white", mec=TEXT, mew=0.8, zorder=6,
                clip_on=False)
    # The response-matching row continues past the view; say so in ink as well as in words.
    ax.plot(XMAX, yat(T_BASE_A), marker=">", ms=3.0, color=SHARED, mec="none", zorder=5,
            clip_on=False)

    # ---------------------------------------------------------------- the evaluator switch
    ax.set_yticks([yat(T_BASE_A), yat(T_BASE_B)])
    ax.set_yticklabels(ROW_LABELS, fontsize=PT_ANNOT, linespacing=1.15)
    ax.tick_params(axis="y", length=0, pad=2)
    # Nothing was retrained between the rows. The arrow is the panel's construction: one set of
    # rankings, handed to a second judge. It runs down the far left of the view, where neither
    # density has mass, so it costs the distributions nothing and cannot be read as a data mark.
    # Its x is asserted against the mechanism-recovery support below, and it is DRAWN after the
    # words, because where it may start is measured off the response-matching summary line: at
    # 2.5 pt below that row's baseline, the previous version put the shaft through the letters of
    # "median" on a line that spans the full width of the axes.
    x_link = XMIN + 0.08
    link = ax.text(x_link + 0.05, yat(T_LINK), "same rankings", ha="left", va="center",
                   fontsize=PT_SMALL, color=TEXT, zorder=6)

    # ---------------------------------------------------------------- words
    # The half-plane key sits UNDER the axis, flanking zero, so each phrase is directly under the
    # wash it names and the 0.84 in of axes height is left to the distributions.
    ax.text(xfrac(0.0) - 0.022, ybelow(T_SIGN), r"$\leftarrow$ mean better", transform=ax.transAxes,
            ha="right", va="top", fontsize=PT_SMALL, color=TEXT)
    ax.text(xfrac(0.0) + 0.022, ybelow(T_SIGN), r"population better $\rightarrow$",
            transform=ax.transAxes, ha="left", va="top", fontsize=PT_SMALL, color=TEXT)
    # "of this row": only response matching is cut, and 5 per cent is 5 per cent OF IT. Read as a
    # panel-wide fraction the same number would be false, and the assertion above is what makes
    # "this row" the true one.
    note = ax.text(1.0, yat(T_NOTE),
                   f"{beyond:.0%} of this row runs past the view, to {_signed(a.max(), 2)}",
                   transform=ax.transAxes, ha="right", va="top", fontsize=PT_SMALL, color=TEXT)
    # Lead with the MEDIAN on both rows, in identical form. The mean is secondary because on both
    # rows it differs from the median for the same uninteresting reason, a tail.
    stat_al = ax.text(0.0, yat(T_STAT_A),
                      f"median {_signed(med_a)}, {pos_a:.0%} of queries favour population",
                      transform=ax.transAxes, ha="left", va="top", fontsize=PT_ANNOT, color=TEXT)
    stat_ar = ax.text(1.0, yat(T_STAT_A), f"mean {_signed(mean_a)}", transform=ax.transAxes,
                      ha="right", va="top", fontsize=PT_SMALL, color=TEXT)
    stat_bl = ax.text(0.0, yat(T_STAT_B),
                      f"median {_signed(med_b)}, {pos_b:.0%} favour population",
                      transform=ax.transAxes, ha="left", va="top", fontsize=PT_ANNOT, color=TEXT)
    stat_br = ax.text(1.0, yat(T_STAT_B),
                      f"mean {_signed(mean_b)}, {tie_b:.0%} exact ties", transform=ax.transAxes,
                      ha="right", va="top", fontsize=PT_SMALL, color=TEXT)

    ax.set_xticks([-1.0, -0.5, 0.0, 0.5, 1.0])
    ax.set_xticklabels(["$-$1.0", "$-$0.5", "0", "$+$0.5", "$+$1.0"])
    ax.tick_params(axis="x", pad=1.5)
    # Drawn rather than set_xlabel: the half-plane key already occupies the strip matplotlib would
    # measure the label pad from, and this row's depth is spent to 0.1 in.
    ax.text(0.5, ybelow(T_XLAB), f"population $-$ mean advantage, n = {n} paired queries",
            transform=ax.transAxes, ha="center", va="top", fontsize=PT_ANNOT, color=TEXT)
    title(ax, "Only the evaluator changes; the advantage disappears")

    # ---------------------------------------------------------------- geometry, asserted
    # Measured, not estimated. Two things have to hold at this width or the panel is lying about
    # its own layout: the two items on each summary line must not run into each other, and the
    # truncation note must clear the density it sits over.
    r = RendererAgg(int(fig.get_figwidth() * fig.dpi), int(fig.get_figheight() * fig.dpi), fig.dpi)

    # The connector, now that the line it has to start below has been measured. Two claims:
    # it carries no data, so it must miss the mechanism-recovery support entirely; and it must
    # start clear of the response-matching summary line rather than strike through it.
    assert x_link < float(b.min()), f"the connector at {x_link} sits inside row B's support"
    t_top = T_STAT_A + stat_al.get_window_extent(renderer=r).height / fig.dpi * 72.0 + 1.5
    t_bot = T_BASE_B - 2.5
    assert t_top < T_LINK < t_bot, f"'same rankings' is off the connector: {t_top:.1f}, {t_bot:.1f}"
    ax.annotate("", xy=(x_link, yat(t_bot)), xytext=(x_link, yat(t_top)),
                arrowprops=dict(arrowstyle="-|>", lw=0.7, color=SHARED, shrinkA=0, shrinkB=0,
                                mutation_scale=5), zorder=5)

    for left, right, row in ((stat_al, stat_ar, "A"), (stat_bl, stat_br, "B")):
        gap = (right.get_window_extent(renderer=r).x0
               - left.get_window_extent(renderer=r).x1) / fig.dpi
        assert gap > 0.02, (f"row {row} summary line overruns itself by "
                            f"{-gap:.3f} in at {w_in:.2f} in")

    def _data_span(bbox):
        """The x range a drawn label occupies, in data units on this axes."""
        x_ax = ax.get_position().x0 * fig.get_figwidth()
        return [XMIN + (XMAX - XMIN) * (px / fig.dpi - x_ax) / w_in for px in (bbox.x0, bbox.x1)]

    def _ridge_top_t(i, span):
        """Ledger position (points below the axes top) of row i's density over an x range."""
        d = dens[i][(grids[i] >= span[0]) & (grids[i] <= span[1])]
        h = 0.0 if d.size == 0 else RIDGE_MAX * float(d.max()) / peak
        return base_t[i] - h

    nb = note.get_window_extent(renderer=r)
    clear = _ridge_top_t(0, _data_span(nb)) - (T_NOTE + nb.height / fig.dpi * 72.0)
    assert clear > 0.5, f"truncation note sits {clear:.2f} pt into the density it annotates"
    lb = link.get_window_extent(renderer=r)
    clear = _ridge_top_t(1, _data_span(lb)) - (T_LINK + 0.5 * lb.height / fig.dpi * 72.0)
    assert clear > 0.5, f"'same rankings' sits {clear:.2f} pt into the density it crosses"


if __name__ == "__main__":
    from figstyle import apply_style
    from fig3_style import PT_TICK, PT_TITLE

    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    fig = plt.figure(figsize=(4.00, 1.50))
    # The printed rect: 3.16 x 0.84 in of axes, with fig3_assemble's pads around it.
    fig.add_axes([0.74 / 4.00, 0.42 / 1.50, 3.16 / 4.00, 0.84 / 1.50])
    draw_3a(fig.axes[0])
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "3a.png")
    fig.savefig(out, dpi=400)
    print(f"wrote {out}")
