"""PopRetrieve Figure 2 panel 2c: per-query regret reduction, ECDF over ALL 765 queries.

WHAT THE PANEL CLAIMS
---------------------
On a query-by-query basis, retrieval scored on the retained cell POPULATION reaches a lower
decision regret than retrieval scored on the COLLAPSED mean signature: 72% of queries improve,
21% get worse, 7% tie exactly, median +0.118, paired Wilcoxon p = 1.6e-66. Every one of those
numbers is computed at draw time from the source file, and the relationships the panel's marks
state are asserted below so a mark cannot outlive the data.

This is a Class-A (objective-aligned) statement about response matching only. `decision_regret` is
the regret of the decision taken from the retrieved candidate under the retrieval objective; the
panel says nothing about whether the retrieved perturbation is biologically preferable, which is
Figure 3's question.

SOURCE
------
results/exp12_partial_observed_retrieval/per_query_scores.csv, paired per query on the SIX-column
key that `src/experiments/exp12_partial_observed_retrieval.py` documents as identifying a query
(split_type, cell_line, heldout_drug, heldout_MoA, observed_library_fraction, seed), as
(mean_cosine decision_regret) minus (DART_coverage_worst decision_regret). `decision_regret` is
defined there as U[library-oracle] minus U[selected] and is therefore non-negative, with lower
better; that is asserted below, because it is what makes a POSITIVE difference mean the
population-level scorer left LESS regret, i.e. that population retrieval was better. A shorter key
mispairs rows (the partial_library queries repeat one drug at three library fractions), and the
experiment records that a short key once put a wrong median into this figure.

Scope note, and the reason this panel reads the raw per-query file: it previously plotted
figures/source_data/fig2c_regret_reduction.csv, which then held only the 621 gate-recommended
queries (annotated "n=621, p=4e-56"). The manuscript caption and Results text both report panel c
on ALL 765 partial-observed queries, precisely so the headline is not taken on a gate-selected
subset. The panel now computes the full 765-query set from the authoritative results file and
asserts n == 765 so a subset cannot silently return. That mirror has since been regenerated to
all 765 rows and its median agrees to six decimals, but the panel keeps reading the results file:
the mirror's key omits heldout_MoA and carries a recommendation_mode column, so it is one gate
filter away from the 621-row subset again and cannot be pinned by an assertion here.

THE RESTRAINT PASS (2026-08-31)
-------------------------------
One piece of text is gone, and nothing on the panel replaces it: "The gain survives partial
observation", set in ink over the axes at PT_TITLE. Seven such sentences on one page are seven
claims competing for one reader, which is not what a Nature-family main figure does; the figure
carries visual evidence and the legend carries the argument. fig2_style.title() was deleted, and
fig2_assemble._assert_no_titles now refuses to build a figure in which a panel draws text above
PT_ANNOT, so the sentence cannot come back a size smaller. It opens this panel's caption entry
instead, where it costs no space and can be qualified.

Nothing else moved, and nothing needed re-tuning. The axes box is unchanged at 2.63 x 1.08 in, and
no constant here was measured against the retired phrase: it was drawn at transAxes y = 1.0, in
the band above the axes that belongs to the panel letter, so removing it freed no height inside
the axes. That band is now empty apart from the letter, and it is left that way on purpose. The
reason the sentence went is that the top of the panel was competing with the marks; filling the
gap with a different annotation would lose the same argument twice.

What the sentence said is now said by MARKS, and three things it used to carry in words are
asserted of those marks instead, because a position can be wrong exactly as a phrase can:

  * the 21 / 72 split is stated by the two half-plane blocks, each sitting inside the half-plane
    it names with its family colour on the bar. The ECDF must clear both blocks by
    CURVE_CLEAR_PT printed points, measured against their RENDERED extents rather than an
    em-width estimate, so a longer label or a shifted curve cannot run the evidence through the
    mark that reports it.
  * the shift is stated by the median rule, which must stand MED_CLEAR_PT printed points clear of
    the zero rule on the resolved x scale. Below that the two verticals merge, and the panel then
    shows a distribution centred on zero while its label claims a shift.
  * the 7 per cent tie note names the vertical step at the origin, so that step has to exist. If
    no query ties, the note points at nothing and must be deleted with the tie.

Pairwise text collision and the panel-box overhang are NOT asserted here. They are properties of
the assembled page rather than of the data, and they are checked at the printed size by the layout
harness that fig2_assemble is verified with; duplicating them here with estimated text widths
would add a fudge factor and catch nothing the harness does not.

JUDGEMENT CALLS A READER COULD DISAGREE WITH
--------------------------------------------
1. The curve is INK, not POP blue. The plotted quantity is a signed DIFFERENCE between the two
   families, so it belongs to neither; and the two half-plane washes already spend both family
   colours here. A blue curve would fuse with the blue wash on the right and contrast with the
   orange on the left, which would say the curve is a population-level score, which it is not.
   The washes carry the families; the curve carries the data and is the strongest ink in the box.
2. The half-planes are named in family language ("mean retrieval" / "population retrieval") while
   the axis definition line names the two exact scorers ("mean-cosine regret - coverage-worst
   regret"). The panel compares one population-level scorer, not the whole family; panel f is what
   generalises the result across the five. Naming the family in the wash and the scorer on the axis
   keeps the fast read plain and the precise read available in the same 2.63 in.
3. The mean (+0.258) is NOT drawn. At this x scale it lands 0.09 in from the median rule, so two
   central-tendency rules would read as one thick rule, and the reason the mean exceeds the median
   (a long right tail out to +2.82) is already the most conspicuous feature of the ECDF's upper
   arm. The caption carries the mean; the panel shows the tail that explains it.
4. The ECDF is drawn as a true step function over the full data range rather than as an
   interpolated line, and both tails are kept in view (xlim spans the observed min and max). That
   costs horizontal room in the crowded region near zero, and buys an honest picture of how far the
   right tail runs.
5. The ties are labelled at 7% next to the vertical step at the origin rather than left implicit,
   so that "72% better" and "21% worse" are not read as a pair that should sum to 100.
6. The curve POOLS all 765 queries. Six hundred of them are leave_drug_out, where the library is
   fully observed (observed_library_fraction == 1.0) and only the optimal drug is hidden, which is
   this project's information condition; only 165 have a genuinely incomplete library. A pooled
   ECDF can therefore hide a gain that exists only where the library is complete, so the direction
   is asserted TWICE: over all 765, and over the 165 with fraction < 1 (median +0.087, 68%
   improved). The panel draws one curve and says nothing about partial observation in words; the
   second assertion is what keeps the caption entitled to say the gain survives it.

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
                        TEXT, bare_axes, zero_rule)

QUERY_KEY = ["split_type", "cell_line", "heldout_drug", "heldout_MoA",
             "observed_library_fraction", "seed"]
N_QUERIES = 765          # all partial-observed queries; see module docstring
N_INCOMPLETE = 165       # of those, the ones whose library is genuinely incomplete
SRC = "results/exp12_partial_observed_retrieval/per_query_scores.csv"

XLIM = (-1.35, 2.95)     # must contain both tails; asserted against the data in draw_2c
YLIM = (-0.03, 1.05)
WASH_ALPHA = 0.6        # the half-plane tint; see draw_2c

# Two geometric guards, in PRINTED POINTS on the resolved scale, standing where the deleted
# sentence used to stand: see the restraint-pass note in the module docstring. Both are well
# inside the current margins: median-to-zero measures 5.2 pt, and the tighter of the two block
# clearances 4.8 pt (47.2 pt at the mean block). They are regression guards, not fitted limits.
MED_CLEAR_PT = 2.5       # the median rule must be separable from the zero rule
CURVE_CLEAR_PT = 1.5     # air between the ECDF and each half-plane block


def regret_reduction():
    """Paired per-query regret reduction, mean-cosine minus coverage-worst, all 765 queries.

    Returns a Series indexed by QUERY_KEY, so the observed_library_fraction of every query stays
    attached to its value and the partial-library subset can be checked without a second read.
    """
    d = pd.read_csv(os.path.join(REPO, SRC))
    assert d["decision_regret"].notna().all() and (d["decision_regret"] >= 0).all(), (
        "decision_regret is documented as a non-negative regret (lower is better); if that "
        "changes, the sign of every difference plotted here inverts and both half-plane labels "
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


def _stroked_extent(artist, renderer, dpi) -> Bbox:
    """One block artist's PRINTED extent in pixels, with a stroked line's width included.

    ``Line2D.get_window_extent`` returns the bbox of the vertices and ignores linewidth, so the
    2.2 pt colour bar that caps each block would measure 1.1 pt thinner at the top than it prints.
    The guard below is a 1.5 pt threshold, so a systematic 1.1 pt is the difference between
    reporting air that exists and air that does not; the half-width is added back here.
    """
    bb = artist.get_window_extent(renderer=renderer)
    if isinstance(artist, Line2D):
        pad = 0.5 * artist.get_linewidth() / 72.0 * dpi
        bb = Bbox.from_extents(bb.x0 - pad, bb.y0 - pad, bb.x1 + pad, bb.y1 + pad)
    return bb


def _block_clearance_pt(ax, artists, ecdf, curve_below: bool) -> float:
    """Least vertical air, in printed points, between the ECDF and one half-plane block.

    The block is MEASURED rather than estimated: its width is set by the printed width of its two
    text lines, so a longer label, a larger type size or a shifted curve would otherwise close the
    gap silently and run the evidence through its own legend. The renderer is built here, as fig3d
    does it, so the measurement neither forces a draw of a half-assembled figure nor assumes which
    backend fig2_assemble is building under. The ECDF is non-decreasing, so over the block's x span
    the curve is nearest the block at one known end: its right end when the curve runs below the
    block, its left end when the curve runs above.
    """
    fig = ax.figure
    r = RendererAgg(int(fig.get_figwidth() * fig.dpi), int(fig.get_figheight() * fig.dpi), fig.dpi)
    bb = Bbox.union([_stroked_extent(a, r, fig.dpi) for a in artists])
    inv = ax.transData.inverted()
    x_near = inv.transform((bb.x1 if curve_below else bb.x0, bb.y0))[0]
    y_px = ax.transData.transform((x_near, ecdf(x_near)))[1]
    gap_px = (bb.y0 - y_px) if curve_below else (y_px - bb.y1)
    return 72.0 * gap_px / fig.dpi


def draw_2c(ax):
    """ECDF of the Class-A per-query regret reduction over all 765 partial-observed queries."""
    rr_s = regret_reduction()
    rr = rr_s.to_numpy(dtype=float)
    n = rr.size

    med = float(np.median(rr))
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
        f"the marks say the population half-plane holds the larger block and the median rule "
        f"stands right of zero; median {med:.4f}, up {f_up:.3f}, down {f_dn:.3f}, "
        f"p {p:.2e} do not support that reading.")
    assert f_ti > 0, (
        "no query ties exactly, so there is no vertical step at the origin for the tie note to "
        "name; drop the note before drawing, and check that the two percentages still cannot be "
        "read as a pair that should sum to 100.")
    frac_obs = rr_s.index.get_level_values("observed_library_fraction").to_numpy(dtype=float)
    part = rr[frac_obs < 1.0]
    assert part.size == N_INCOMPLETE, f"expected {N_INCOMPLETE} incomplete-library queries"
    assert (float(np.median(part)) > 0 and float((part > 0).mean()) > 0.5
            and float(wilcoxon(part).pvalue) < 1e-6), (
        "the gain does not hold on the queries whose library is genuinely incomplete, so the "
        "pooled curve drawn here would be carried by the fully observed ones alone and the "
        "caption must not say the gain survives partial observation.")
    assert XLIM[0] < rr.min() and rr.max() < XLIM[1], "the x range clips a tail"

    # The scale is resolved first, so every geometric check below measures the PRINTED panel
    # rather than a default view that the last line of this function would have replaced.
    ax.set_xlim(*XLIM)
    ax.set_ylim(*YLIM)

    # ---- the two half-planes: zero is the centre of the reading, and each side is named
    # WASH_ALPHA keeps the frozen wash hues but takes them down to a tint that names the
    # half-plane without competing with the curve; at full strength they read as two filled bars.
    ax.axvspan(XLIM[0], 0.0, color=MEAN_WASH, alpha=WASH_ALPHA, lw=0, zorder=0)
    ax.axvspan(0.0, XLIM[1], color=POP_WASH, alpha=WASH_ALPHA, lw=0, zorder=0)
    zero_rule(ax, 0.0, color=SUBTLE, lw=0.8, zorder=3)

    # ---- the ECDF itself, a true step over the full observed range
    xs = np.sort(rr)
    ys = np.arange(1, n + 1) / n
    ax.plot(np.concatenate([[XLIM[0]], xs, [XLIM[1]]]), np.concatenate([[0.0], ys, [1.0]]),
            drawstyle="steps-post", color=TEXT, lw=LW_LINE, zorder=6,
            solid_joinstyle="round", solid_capstyle="butt")

    # ---- the median, as a primary annotation: a rule, the 50% crossing, and a direct label
    ax.plot([med, med], [YLIM[0], 0.5], ls=(0, (1.6, 1.6)), lw=0.8, color=SHARED, zorder=4)
    ax.plot([XLIM[0], med], [0.5, 0.5], ls=(0, (1.6, 1.6)), lw=LW_HAIR, color=FAINT, zorder=4)
    ax.scatter([med], [0.5], s=MS_DOT, color=TEXT, zorder=7, linewidths=0)
    ax.text(med + 0.06, 0.36, f"median +{med:.3f}", fontsize=PT_ANNOT, color=TEXT,
            ha="left", va="center", zorder=7)

    # ---- the ties: the flat step at the origin, named at the MIDDLE of the step it explains,
    # so the leader lands on the riser rather than on the corner where the curve turns
    y_tie = f_dn + f_ti / 2.0
    ax.plot([-0.42, -0.015], [y_tie, y_tie], lw=LW_HAIR, color=SHARED, zorder=4)
    ax.text(-0.46, y_tie, f"{pct['ti']} tied", fontsize=PT_SMALL, color=SUBTLE,
            ha="right", va="center", zorder=7)

    # ---- the two half-plane blocks. The bar is the mark that carries the family colour; every
    # letter stays ink or grey. Each block sits inside the half-plane it names, so position and
    # colour say the same thing twice.
    mean_block = [
        ax.plot([0.030, 0.115], [0.975, 0.975], transform=ax.transAxes, lw=2.2, color=MEAN,
                solid_capstyle="butt", zorder=5, clip_on=False)[0],
        ax.text(0.030, 0.955, pct["dn"], transform=ax.transAxes, fontsize=PT_ANNOT, color=TEXT,
                fontweight="bold", ha="left", va="top", zorder=7),
        ax.text(0.030, 0.845, "mean retrieval\nbetter", transform=ax.transAxes,
                fontsize=PT_SMALL, color=TEXT, ha="left", va="top", linespacing=1.25, zorder=7)]

    pop_block = [
        ax.plot([0.885, 0.970], [0.845, 0.845], transform=ax.transAxes, lw=2.2, color=POP,
                solid_capstyle="butt", zorder=5, clip_on=False)[0],
        ax.text(0.970, 0.825, pct["up"], transform=ax.transAxes, fontsize=PT_ANNOT, color=TEXT,
                fontweight="bold", ha="right", va="top", zorder=7),
        ax.text(0.970, 0.715, "population retrieval\nbetter", transform=ax.transAxes,
                fontsize=PT_SMALL, color=TEXT, ha="right", va="top", linespacing=1.25, zorder=7)]

    ax.text(0.970, 0.030, f"n = {n} queries", transform=ax.transAxes, fontsize=PT_SMALL,
            color=SUBTLE, ha="right", va="bottom", zorder=7)

    # ---- axes (the limits are already set, above the geometric checks)
    ax.set_xticks([-1, 0, 1, 2])
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_yticklabels(["0", "0.25", "0.50", "0.75", "1.00"])
    ax.set_ylabel("cumulative fraction", fontsize=PT_ANNOT)
    bare_axes(ax)

    # The plain-language reading leads; the definition follows a size down, so two method names
    # never have to share the axis title. Neither line carries a sub/superscript, so neither is
    # printed at 0.7x and both stand at their nominal size.
    #
    # Both drops are INCHES, converted here, not axes fractions. They were -0.19 and -0.30 of the
    # axes height, which printed as 0.205 and 0.324 in at the 1.08 in axes this panel had until
    # 2026-09-01; those printed values are what is preserved. As fractions they moved with the box:
    # when the row grew to give this panel 1.55 in, the second line dropped 0.465 in against a
    # 0.50 in pad and its descenders left the panel. fig2a lost this defect on 2026-08-31 and
    # fig2b on 2026-09-01; this is the last of the three.
    ax_h_in = ax.get_position().height * ax.figure.get_figheight()
    def _below(inches):
        return -inches / ax_h_in
    ax.text(0.5, _below(0.205), "Regret reduction vs mean retrieval", transform=ax.transAxes,
            fontsize=PT_ANNOT, color=TEXT, ha="center", va="top")
    ax.text(0.5, _below(0.324), "mean-cosine regret $-$ coverage-worst regret",
            transform=ax.transAxes, fontsize=PT_SMALL, color=SUBTLE, ha="center", va="top")

    # ---- what the deleted sentence used to assert, now asserted of the MARKS that replaced it
    # (module docstring, restraint pass). Both are measured on the printed scale: this panel is
    # authored at the width it prints at, so a point here is a point on paper.
    ax_w_pt = ax.get_position().width * ax.figure.get_figwidth() * 72.0
    med_pt = med / (XLIM[1] - XLIM[0]) * ax_w_pt
    assert med_pt >= MED_CLEAR_PT, (
        f"the median rule prints {med_pt:.2f} pt from the zero rule and {MED_CLEAR_PT} pt is the "
        f"least that reads as two rules; below it the panel shows a distribution centred on zero "
        f"while its label claims a shift.")

    def _ecdf(x):
        return float((rr <= x).mean())

    for artists, below, name in ((mean_block, True, "mean"), (pop_block, False, "population")):
        gap_pt = _block_clearance_pt(ax, artists, _ecdf, below)
        assert gap_pt >= CURVE_CLEAR_PT, (
            f"the ECDF passes within {gap_pt:.2f} pt of the {name}-retrieval block and "
            f"{CURVE_CLEAR_PT} pt is the least air that keeps them separable; the curve would "
            f"run through the mark that states the {name} share.")


if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    from figstyle import apply_style
    from fig2_style import PT_TICK, PT_TITLE

    # The real printed box: a half-width column of Figure 2, drawn at 1:1. BOX_H is
    # fig2_assemble's LETTER_BLOCK (0.17) plus its row-2 height (1.58); it was 1.84 while the
    # letter band was 0.26 in and had to hold a panel phrase as well as the letter. The AXES are
    # unchanged at AX_W x AX_H, which is why nothing inside this panel was re-tuned.
    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    BOX_W, BOX_H, PAD_L, PAD_B, AX_W, AX_H = 3.45, 1.75, 0.72, 0.50, 2.63, 1.08
    fig = plt.figure(figsize=(BOX_W, BOX_H))
    ax = fig.add_axes([PAD_L / BOX_W, PAD_B / BOX_H, AX_W / BOX_W, AX_H / BOX_H])
    draw_2c(ax)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "2c.png")
    fig.savefig(out, dpi=300)
    print(f"wrote {out}")
