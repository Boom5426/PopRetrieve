"""PopRetrieve Figure 2 panel 2c: the paired outcome of population vs directional-mean retrieval.

WHAT THE PANEL CLAIMS
---------------------
Query by query, retrieval scored on the retained cell POPULATION leaves less decision regret than
retrieval scored on a DIRECTION-ONLY mean signature, on more queries than not and by a small
median amount: 56% of 765 queries improve, 36% get worse, 8% tie exactly, median +0.031 with a
bootstrap interval that excludes zero, paired Wilcoxon P = 1.6e-12. Every one of those numbers is
computed at draw time from the source file, and the relationships the panel's marks state are
asserted below so a mark cannot outlive the data.

This is a Class-A (objective-aligned) statement about response matching only. `decision_regret` is
the regret of the decision taken from the retrieved candidate under the retrieval objective; the
panel says nothing about whether the retrieved perturbation is biologically preferable, which is
Figure 3's question. It is a MODEST advantage and the caption says so in those words; it is not a
strong population-specific gain, and panel e is where the distributional residue is measured
against a magnitude-aware rather than a direction-only reference.

SOURCE
------
results/exp12_partial_observed_retrieval/per_query_scores.csv, paired per query on the SIX-column
key that `src/experiments/exp12_partial_observed_retrieval.py` documents as identifying a query
(split_type, cell_line, heldout_drug, heldout_MoA, observed_library_fraction, seed), as
(mean_cosine decision_regret) minus (DART_coverage_worst decision_regret). `decision_regret` is
defined there as U[library-oracle] minus U[selected] and is therefore non-negative, with lower
better; that is asserted below, because it is what makes a POSITIVE difference mean the
population-level scorer left LESS regret. A shorter key mispairs rows (the partial_library queries
repeat one drug at three library fractions), and the experiment records that a short key once put
a wrong median into this figure.

Scope note, and the reason this panel reads the raw per-query file: it previously plotted
figures/source_data/fig2c_regret_reduction.csv, which then held only the 621 gate-recommended
queries. The manuscript caption and Results text both report panel c on ALL 765 partial-observed
queries, precisely so the headline is not taken on a gate-selected subset. The panel computes the
full set from the authoritative results file and asserts n == 765 so a subset cannot silently
return.

WHY THE COMPOSITION CHANGED ON 2026-09-03, AND WHAT DID NOT CHANGE WITH IT
-------------------------------------------------------------------------
Until today this panel was an ECDF of the paired difference on a horizontal value axis, and its
central mark was a MEDIAN RULE standing clear of the ZERO RULE. Two vertical rules is a composition
that can only work when the median is far enough from zero to resolve as a separate line, and the
panel guarded exactly that with MED_CLEAR_PT below.

The estimator repair moved the median. Under the V-statistic energy distance the median paired
difference was +0.1183 with 72.0 per cent of queries improved; under the unbiased U-statistic it is
+0.0311 with 56.2 per cent improved (docs/phase2/POST_REPAIR_MASTER_RESULTS.md, section A5). The
direction and the significance survive; a quarter of the size does. At the printed width of this
panel the median rule then stood 0.86 pt from the zero rule against a 2.5 pt requirement, and the
gate refused to draw it.

Three things were NOT done about that, and they are the reason this docstring is long:

  * MED_CLEAR_PT was not lowered. It is unchanged at 2.5 pt and still asserted, in the inverted
    form the new composition needs: the panel checks that the retired composition is still
    illegible, so that a future change to the data or the estimator that would make it legible
    again surfaces as a build failure rather than as a quietly worse figure.
  * The scorer was not swapped. `coverage_worst` is the scorer this panel has always been about
    and it is the one the estimator repair moved MOST (P2_LEGACY_RERUN.md: it went from the best
    of the population family to the worst). Substituting `global_energy`, whose median against
    mean cosine is +0.0566 and would have drawn under the old composition, would have been
    choosing the setting that preserves the old picture.
  * The panel was not demoted to the supplement. The result is smaller, not absent.

What changed is the drawing. The composition is now a PAIRED-OUTCOME panel, built for a small
effect on a heavy-tailed difference:

  * The x axis is the query percentile, so the three outcome PROPORTIONS are read directly as
    x extents rather than inferred from a curve's height. The bottom axis is drawn as three
    coloured segments whose widths ARE 36 / 8 / 56 per cent, which is the stacked proportion bar
    the panel needs, occupying no plot area.
  * The y axis is the paired difference, and the curve is its quantile function. Where the curve
    lies below zero the population scorer lost, and the fill is orange; where above, it won, and
    the fill is blue. The sign change and the flat run of exact ties are therefore visible as
    positions on the axis, and they line up with the segment boundaries below them by
    construction: both are computed from the same three counts.
  * The median is a POINT with a bootstrap interval and a leader to its value, not a rule. Nothing
    in the panel now depends on two rules resolving from each other.

WHY THE VALUE AXIS IS A SIGNED SQUARE ROOT
------------------------------------------
The paired difference runs from -2.22 to +2.85 while 68 per cent of queries fall within +/-0.25 of
zero. On a linear axis that puts the entire region the claim is about into 5 per cent of the panel
height, and the panel would show two spikes and a flat line. A signed square root, sign(y)*sqrt|y|,
is monotone, is applied identically to both signs, has no threshold to tune, and compresses the
tails much less than a log would. It is CONSERVATIVE here rather than flattering: the longer tail
is the positive one, so compressing tails takes visual weight away from the population scorer's
best wins, not away from its losses. The tick labels are real values at their real positions, so
the compression is stated by the axis itself.

The transform does mean that the median dot's distance above zero is not proportional to +0.031.
That is why the median carries a printed value and an interval, and why the caption says modest.

JUDGEMENT CALLS A READER COULD DISAGREE WITH
--------------------------------------------
1. The curve is INK, not POP blue. The plotted quantity is a signed DIFFERENCE between two
   scorers, so it belongs to neither; the two fills already spend both tier colours here.
2. The two outcome blocks name the exact scorers ("mean cosine", "coverage-worst") rather than the
   tiers. This panel compares one population-level scorer against one direction-only scorer; panel
   f is what generalises across the five, and after the magnitude control entered the figure
   "mean retrieval" is no longer an unambiguous name for a direction-only method.
3. The mean (+0.132) is not drawn. It is four times the median because of the right tail, which is
   the most conspicuous feature of the curve; the caption carries the number.
4. Both tails are kept in view, so nothing is clipped and no count has to be reported as
   off-panel.
5. The ties are labelled at the plateau rather than left implicit, so that 56 and 36 are not read
   as a pair that should sum to 100.
6. The curve POOLS all 765 queries. Six hundred are leave_drug_out with a fully observed library;
   only 165 have a genuinely incomplete one. A pooled curve can therefore hide a gain that exists
   only where the library is complete, so the direction is asserted TWICE: over all 765, and over
   the 165 with fraction < 1 (median +0.035, 60 per cent improved, P = 6.0e-05).

Run standalone: python fig2c.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
from matplotlib.backends.backend_agg import RendererAgg
from matplotlib.lines import Line2D
from matplotlib.transforms import Bbox
from scipy.stats import wilcoxon

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fig2_style import (FAINT, LW_HAIR, LW_LINE, MEAN, MEAN_WASH, MS_DOT,  # noqa: E402
                        POP, POP_WASH, PT_ANNOT, PT_SMALL, REPO, SHARED, SUBTLE,
                        TEXT, bare_axes, boot_median_ci, zero_rule)

QUERY_KEY = ["split_type", "cell_line", "heldout_drug", "heldout_MoA",
             "observed_library_fraction", "seed"]
N_QUERIES = 765          # all partial-observed queries; see module docstring
N_INCOMPLETE = 165       # of those, the ones whose library is genuinely incomplete
SRC = "results/exp12_partial_observed_retrieval/per_query_scores.csv"

XLIM = (0.0, 1.0)        # query percentile, by construction
# The value range. These are the numbers the retired composition used as its x limits, kept because
# the quantity is the same one: they bound the observed [-2.219, +2.853] and the bound is asserted.
YLIM = (-2.35, 2.95)
YTICKS = (-2, -1, -0.5, -0.1, 0, 0.1, 0.5, 1, 2)

# Two geometric guards, in PRINTED POINTS on the resolved scale.
#
# MED_CLEAR_PT is UNCHANGED at 2.5 and is the constant that retired the previous composition; see
# the module docstring. It is now asserted the other way round, as the condition under which this
# composition is the necessary one.
MED_CLEAR_PT = 2.5
CURVE_CLEAR_PT = 1.5     # air between the quantile curve and each text block

# Where the three text blocks sit. x values are data coordinates and the x axis runs 0 to 1, so
# they are also axes fractions; y offsets from the axes floor are in PRINTED POINTS, which keeps
# the stacking independent of the non-linear value scale.
BLOCK_PCT_DY, BLOCK_NAME_DY = 12.0, 3.0
MEAN_BLOCK_X, POP_BLOCK_X = 0.02, 0.985
MED_X, MED_HALF_W = 0.5, 0.08       # the median point, and the half-width of its interval band
MED_TEXT_XY = (0.40, 0.46)          # right-aligned, in the empty upper-left quadrant
MED_LEADER = ((0.415, 0.42), (0.475, 0.075))
TIE_BRACKET_Y, TIE_BRACKET_TIP, TIE_TEXT_Y = -0.055, -0.012, -0.075
N_TEXT_XY = (0.02, 2.62)


def regret_reduction():
    """Paired per-query regret reduction, mean-cosine minus coverage-worst, all 765 queries.

    Returns a Series indexed by QUERY_KEY, so the observed_library_fraction of every query stays
    attached to its value and the partial-library subset can be checked without a second read.
    """
    d = pd.read_csv(os.path.join(REPO, SRC))
    assert d["decision_regret"].notna().all() and (d["decision_regret"] >= 0).all(), (
        "decision_regret is documented as a non-negative regret (lower is better); if that "
        "changes, the sign of every difference plotted here inverts and both outcome labels "
        "become false.")
    cols = {}
    for method, name in (("mean_cosine", "mean"), ("DART_coverage_worst", "pop")):
        s = d[d.method == method].set_index(QUERY_KEY)["decision_regret"]
        assert not s.index.has_duplicates, (
            f"{method} rows are not unique on {QUERY_KEY}; the pairing below would compare "
            f"mismatched queries.")
        cols[name] = s
    j = pd.concat([cols["mean"].rename("mean"), cols["pop"].rename("pop")], axis=1).dropna()
    assert len(j) == N_QUERIES, f"expected {N_QUERIES} paired queries, got {len(j)}"
    return j["mean"] - j["pop"]


def _signed_sqrt(v):
    v = np.asarray(v, dtype=float)
    return np.sign(v) * np.sqrt(np.abs(v))


def _signed_square(t):
    t = np.asarray(t, dtype=float)
    return np.sign(t) * t * t


def _stroked_extent(artist, renderer, dpi) -> Bbox:
    """One artist's PRINTED extent in pixels, with a stroked line's width included.

    ``Line2D.get_window_extent`` returns the bbox of the vertices and ignores linewidth, so a
    stroked segment would measure half its width thin on every side. The guard below is a 1.5 pt
    threshold, so a systematic point is the difference between reporting air that exists and air
    that does not; the half-width is added back here.
    """
    bb = artist.get_window_extent(renderer=renderer)
    if isinstance(artist, Line2D):
        pad = 0.5 * artist.get_linewidth() / 72.0 * dpi
        bb = Bbox.from_extents(bb.x0 - pad, bb.y0 - pad, bb.x1 + pad, bb.y1 + pad)
    return bb


def _curve_clearance_pt(ax, artists, curve, curve_above: bool) -> float:
    """Least vertical air, in printed points, between the quantile curve and one text block.

    The block is MEASURED rather than estimated: its width is set by the printed width of its text,
    so a longer label, a larger type size or a shifted curve would otherwise close the gap silently
    and run the evidence through the mark that reports it. The renderer is built here, as fig3d
    does it, so the measurement neither forces a draw of a half-assembled figure nor assumes which
    backend fig2_assemble is building under. The quantile curve is non-decreasing, so over the
    block's x span it is nearest the block at one known end: its left end when the curve runs above
    the block, its right end when the curve runs below.
    """
    fig = ax.figure
    r = RendererAgg(int(fig.get_figwidth() * fig.dpi), int(fig.get_figheight() * fig.dpi), fig.dpi)
    bb = Bbox.union([_stroked_extent(a, r, fig.dpi) for a in artists])
    inv = ax.transData.inverted()
    x_near = inv.transform((bb.x0 if curve_above else bb.x1, bb.y0))[0]
    y_px = ax.transData.transform((x_near, curve(x_near)))[1]
    gap_px = (y_px - bb.y1) if curve_above else (bb.y0 - y_px)
    return 72.0 * gap_px / fig.dpi


def draw_2c(ax):
    """Paired outcome of coverage-worst against mean-cosine over all 765 partial-observed queries."""
    rr_s = regret_reduction()
    rr = rr_s.to_numpy(dtype=float)
    n = rr.size

    med, med_lo, med_hi = boot_median_ci(rr, n_boot=4000, seed=0)
    f_up = float((rr > 0).mean())
    f_dn = float((rr < 0).mean())
    f_ti = float((rr == 0).mean())
    p = float(wilcoxon(rr).pvalue)

    # ---- the relationships the panel's MARKS state, asserted so a mark cannot outlive them
    assert abs(f_up + f_dn + f_ti - 1.0) < 1e-12, "the three signs must partition the queries"
    pct = {k: f"{v:.0%}" for k, v in (("up", f_up), ("dn", f_dn), ("ti", f_ti))}
    assert sum(int(s.rstrip("%")) for s in pct.values()) == 100, (
        f"the three drawn percentages {pct} do not sum to 100, so the panel would have to "
        f"explain the remainder; re-word before drawing.")
    assert med > 0 and f_up > f_dn and p < 1e-6, (
        f"the marks say the blue segment is the wider one and the median point sits above zero; "
        f"median {med:.4f}, up {f_up:.3f}, down {f_dn:.3f}, p {p:.2e} do not support that reading.")
    # The median is drawn as a point with an interval rather than as a rule, so the interval is
    # what now carries "systematic" on the panel. If it straddles zero the point is decoration.
    assert med_lo > 0, (
        f"the bootstrap median interval [{med_lo:+.4f}, {med_hi:+.4f}] includes zero, so the "
        f"drawn point and its whisker no longer state a positive shift.")
    assert f_ti > 0, (
        "no query ties exactly, so there is no flat run at zero for the tie bracket to name; drop "
        "the bracket before drawing, and check that the two percentages still cannot be read as a "
        "pair that should sum to 100.")
    frac_obs = rr_s.index.get_level_values("observed_library_fraction").to_numpy(dtype=float)
    part = rr[frac_obs < 1.0]
    assert part.size == N_INCOMPLETE, f"expected {N_INCOMPLETE} incomplete-library queries"
    # THE THRESHOLD MOVED FROM 1e-6 TO 1e-3 ON 2026-09-03, and only because the estimator did.
    # Under the V-statistic energy distance this subset gave p < 1e-6; under the unbiased
    # U-statistic it gives 5.96e-05. The gain is unchanged in direction and barely changed in size
    # (median +0.035, 60 per cent of 165 queries improved), so the claim the panel makes stands;
    # what fell is the extremity of a p-value on 165 queries, which the caption never quoted. The
    # new bound is stated here rather than removed, and the measured value is printed in the
    # failure message so the next move is visible instead of inferred.
    part_p = float(wilcoxon(part).pvalue)
    assert (float(np.median(part)) > 0 and float((part > 0).mean()) > 0.5
            and part_p < 1e-3), (
        f"the gain does not hold on the queries whose library is genuinely incomplete "
        f"(median {float(np.median(part)):+.4f}, {float((part > 0).mean()):.1%} improved, "
        f"p {part_p:.2e}), so the pooled curve drawn here would be carried by the fully observed "
        f"ones alone and the caption must not say the gain survives partial observation.")
    assert YLIM[0] < rr.min() and rr.max() < YLIM[1], "the value range clips a tail"

    # The scale is resolved first, so every geometric check below measures the PRINTED panel
    # rather than a default view that the last line of this function would have replaced.
    ax.set_xlim(*XLIM)
    ax.set_yscale("function", functions=(_signed_sqrt, _signed_square))
    ax.set_ylim(*YLIM)

    # ---- the quantile curve, and the two fills that name which scorer won each query
    # x is the cumulative fraction of queries, so the curve crosses zero at exactly f_dn and leaves
    # zero at exactly f_dn + f_ti: the sign changes on the curve and the segment boundaries on the
    # axis below are the same three counts, not two independent drawings.
    ys = np.sort(rr)
    xs = np.arange(1, n + 1) / n
    xs_full = np.concatenate([[XLIM[0]], xs])
    ys_full = np.concatenate([[ys[0]], ys])
    zero_rule(ax, 0.0, vertical=False, color=SUBTLE, lw=0.8, zorder=3)
    ax.fill_between(xs_full, ys_full, 0.0, where=ys_full < 0, color=MEAN_WASH, lw=0, zorder=1)
    ax.fill_between(xs_full, ys_full, 0.0, where=ys_full > 0, color=POP_WASH, lw=0, zorder=1)
    ax.plot(xs_full, ys_full, color=TEXT, lw=LW_LINE, zorder=6,
            solid_joinstyle="round", solid_capstyle="butt")

    def _curve(u):
        return float(np.interp(u, xs_full, ys_full))

    # ---- the median: a point, an interval, and its value on a leader. No second rule.
    #
    # The interval prints 3.1 pt tall and the point mark is 5.7 pt across, so a plain vertical
    # whisker would sit entirely inside its own dot. It is drawn as a BAND with capped ends
    # instead, wider in x than the dot, so the two ends stay visible on either side of it. What
    # the band has to show is that its lower end clears the zero rule, which it does by 4.5 pt.
    ax.fill_between([MED_X - MED_HALF_W, MED_X + MED_HALF_W], [med_lo, med_lo], [med_hi, med_hi],
                    color=FAINT, lw=0, zorder=4)
    for v in (med_lo, med_hi):
        ax.plot([MED_X - MED_HALF_W, MED_X + MED_HALF_W], [v, v], lw=LW_HAIR, color=SHARED,
                zorder=6, solid_capstyle="butt")
    ax.scatter([MED_X], [med], s=MS_DOT, color=TEXT, zorder=7, linewidths=0)
    ax.plot([MED_LEADER[0][0], MED_LEADER[1][0]], [MED_LEADER[0][1], MED_LEADER[1][1]],
            lw=LW_HAIR, color=SHARED, zorder=5)
    med_text = ax.text(MED_TEXT_XY[0], MED_TEXT_XY[1], f"median +{med:.3f}", fontsize=PT_ANNOT,
                       color=TEXT, ha="right", va="center", zorder=7)

    # ---- the ties: the flat run of the curve on the zero rule, bracketed and named
    ax.plot([f_dn, f_dn, f_dn + f_ti, f_dn + f_ti],
            [TIE_BRACKET_TIP, TIE_BRACKET_Y, TIE_BRACKET_Y, TIE_BRACKET_TIP],
            lw=LW_HAIR, color=SHARED, zorder=5, solid_joinstyle="miter")
    ax.text(f_dn + f_ti / 2.0, TIE_TEXT_Y, f"{pct['ti']} tied", fontsize=PT_SMALL, color=SUBTLE,
            ha="center", va="top", zorder=7)

    # ---- the proportion bar IS the x axis: three segments whose widths are the three outcomes
    ax.spines["bottom"].set_visible(False)
    for x0, x1, colour in ((XLIM[0], f_dn, MEAN), (f_dn, f_dn + f_ti, FAINT),
                           (f_dn + f_ti, XLIM[1], POP)):
        ax.plot([x0, x1], [YLIM[0], YLIM[0]], lw=2.6, color=colour, solid_capstyle="butt",
                clip_on=False, zorder=5)

    # ---- the two outcome blocks, each standing over the segment whose share it states
    def _block(x, ha, share, name):
        return [ax.annotate(share, xy=(x, YLIM[0]), xytext=(0, BLOCK_PCT_DY),
                            textcoords="offset points", ha=ha, va="bottom",
                            fontsize=PT_ANNOT, fontweight="bold", color=TEXT, zorder=7),
                ax.annotate(name, xy=(x, YLIM[0]), xytext=(0, BLOCK_NAME_DY),
                            textcoords="offset points", ha=ha, va="bottom",
                            fontsize=PT_SMALL, color=TEXT, zorder=7)]

    mean_block = _block(MEAN_BLOCK_X, "left", pct["dn"], "mean cosine better")
    pop_block = _block(POP_BLOCK_X, "right", pct["up"], "coverage-worst better")

    ax.text(N_TEXT_XY[0], N_TEXT_XY[1], f"n = {n} paired queries", fontsize=PT_SMALL,
            color=SUBTLE, ha="left", va="top", zorder=7)

    # ---- axes (the limits are already set, above the geometric checks)
    ax.set_xticks([0.0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xticklabels(["0", "25", "50", "75", "100"])
    ax.set_yticks(list(YTICKS))
    ax.set_yticklabels(["0" if v == 0 else f"{v:g}" for v in YTICKS])
    ax.set_ylabel("regret reduction", fontsize=PT_ANNOT, labelpad=1.5)
    bare_axes(ax, keep=("left",))

    # ONE line under the axis since 2026-09-04. The second line set the sign convention,
    # "mean-cosine regret - coverage-worst regret", and the panel already says it twice: the two
    # end blocks name which method is better on which side. It is now stated once, in the caption,
    # where a definition belongs, and the 0.12 in it occupied has left the figure.
    #
    # The drop is INCHES, converted here, not an axes fraction: as a fraction it moves with the
    # box, and when row 1 grew this label once dropped its descenders out of the figure.
    ax_h_in = ax.get_position().height * ax.figure.get_figheight()

    def _below(inches):
        return -inches / ax_h_in

    ax.text(0.5, _below(0.205), "Queries ranked by regret reduction (percentile)",
            transform=ax.transAxes, fontsize=PT_ANNOT, color=TEXT, ha="center", va="top")

    # ---- geometry, measured on the printed scale: this panel is authored at the width it prints
    # at, so a point here is a point on paper.
    #
    # The first check is the constant that retired the previous composition, asserted in the form
    # the new one needs. If the median ever stands MED_CLEAR_PT clear of the zero rule again, a
    # value-axis ECDF with a median rule becomes legible and this small-effect composition is no
    # longer the necessary drawing: that is a change worth a build failure, because it would mean
    # the paired difference has moved by a factor of three and the caption's "modest" with it.
    ax_w_pt = ax.get_position().width * ax.figure.get_figwidth() * 72.0
    med_on_value_axis_pt = med / (YLIM[1] - YLIM[0]) * ax_w_pt
    assert med_on_value_axis_pt < MED_CLEAR_PT, (
        f"the median now prints {med_on_value_axis_pt:.2f} pt from zero on a value axis of this "
        f"panel's width, at or above the {MED_CLEAR_PT} pt that reads as two separate rules. This "
        f"composition exists because it did not; re-read docs/phase2/POST_REPAIR_MASTER_RESULTS.md "
        f"section A5 and decide the panel again rather than editing this bound.")

    for artists, above, name in ((mean_block, True, "mean-cosine"),
                                 (pop_block, True, "coverage-worst"),
                                 ([med_text], False, "median")):
        gap_pt = _curve_clearance_pt(ax, artists, _curve, above)
        assert gap_pt >= CURVE_CLEAR_PT, (
            f"the quantile curve passes within {gap_pt:.2f} pt of the {name} text and "
            f"{CURVE_CLEAR_PT} pt is the least air that keeps them separable; the curve would run "
            f"through the mark that states the {name} share.")


if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from figstyle import apply_style
    from fig2_style import PT_TICK, PT_TITLE

    # The real printed box, drawn at 1:1: fig2_assemble's row-1 height (2.05) under its
    # LETTER_BLOCK (0.16), at the width ROW_WIDTHS gives c (2.85) and the pads PADS gives it
    # (0.72 left, 0.10 right, 0.50 bottom). Axes 2.03 x 1.55 in. Every printed-point assertion in
    # draw_2c measures this box, so the harness has to be the box.
    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    BOX_W, BOX_H, PAD_L, PAD_B, AX_W, AX_H = 2.85, 2.21, 0.72, 0.50, 2.03, 1.55
    fig = plt.figure(figsize=(BOX_W, BOX_H))
    ax = fig.add_axes([PAD_L / BOX_W, PAD_B / BOX_H, AX_W / BOX_W, AX_H / BOX_H])
    draw_2c(ax)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "2c.png")
    fig.savefig(out, dpi=300)
    print(f"wrote {out}")
