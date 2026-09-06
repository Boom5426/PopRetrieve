"""PopRetrieve Figure 3 panel 3i: per query, the population-level score against the scalar it
must beat, read as a side of the equality line.

WHAT THIS PANEL SHOWS
---------------------
Panel h reports the Class-C aggregate: energy retrieval reaches a median rho of +0.265 against
the matched functional oracle, the query-dependent response-magnitude scalar reaches +0.232, and
partialling that channel out leaves energy +0.105. This panel shows the same 103 queries one at a
time. What a reader takes from it is a SPLIT: the cloud straddles y = x, and the two half-plane
counts, 62 against 41, are a 60/40 division rather than a sweep. That split is the reason the
paper does not read h as a clean win for distributional retrieval. A reader who takes "energy
beats the scalar" away from h without this panel has taken a stronger claim than the data carry.
Saying so is the caption's job; the panel draws the split and the two counts, nothing more.

Source data: figures/source_data/fig3hi_class_c_functional.csv, 103 leave-one-drug-out queries
(SciPlex3 x GDSC2, 10 uM, 34-35 drugs per cell line).
    x = energy_rho             energy retrieval, which compares whole populations
    y = magnitude_match_rho    a QUERY-DEPENDENT SCALAR that compares no distributions and merely
                               prefers candidates whose response is about as large as the query's
The oracle both are scored against is drug-drug functional similarity from GDSC2 dose-response
profiles, named in full on panel h and in the row banner; these axis labels name only the score.
Note the source table also carries magnitude_only_rho, a DIFFERENT and query-independent scalar,
which is why the y label keeps the word "match".

THE 2026-08-31 PASS: THE SENTENCE IS GONE, THE COUNT IS NOT
-----------------------------------------------------------
This panel used to set "Energy better on 62 of 103 queries" over itself through fig3_style.title,
which has been deleted; thirteen such phrases on one page were thirteen claims competing for the
reader. The count itself is the panel's evidence, not its conclusion, so it stays, rendered as a
bare statistic under the half-plane label it belongs to: "energy better / 62/103" on the side
where y < x, "scalar better / 41/103" on the side where y > x. Both numbers and the denominator
are computed from the table at draw time and are asserted to partition the queries, so no label
can outlive the data under it. Losing the sentence loses no information a reader was using: the
sentence named one side's count and left the reader to subtract for the other, whereas the two
counts sit in the two washes and read as a split without arithmetic.

Removing the phrase band returned height to the row, so the axes grew from 1.98 x 0.82 in to
1.98 x 0.90 in. The height went to the marks and not to new text: markers are 3.4 pt rather than
3.0, which is what makes circle, square and triangle separable in print at 183 mm, and the
equality line carries a little more weight than the rho = 0 guides than it did before.

Two things the trim left unguarded, both fixed on audit. The counts and the direction hints were
the only new text on the panel and nothing measured whether they fit: "energy" set at PT_ANNOT is
0.320 in wide and the strip was 0.32 in, so the label ran edge to edge, and a longer word or a
font change would have pushed it into the cloud or off the frame while still passing the
assembler's floor gate. The strip is now 0.35 in and the fit is asserted from measured extents.
And "41/103" sat within 0.02 in of the height of the "0.0" y tick label, close enough to read as
an annotation on the y scale rather than as the left half-plane's score; the left label block now
sits at 0.80 of the y range, on its own row between the 0.0 and 0.5 ticks.

PROVENANCE, AND THE CORRECTION THAT MUST NOT BE LOST
----------------------------------------------------
An earlier version of this panel graded the same rankings against ABSOLUTE POTENCY and reported
that the scalar won 103 of 103 queries. Both halves of that were wrong. Potency is an oracle no
similarity retriever was ever asked to optimise, and it is largely response magnitude, so a
magnitude scalar was near-guaranteed to win it; and a 103-of-103 sweep over queries that share a
candidate library within each cell line counts pseudo-replicates as independent evidence, which
this study refuses to do elsewhere. The potency comparison survives only as the endpoint audit in
panels j and k.

JUDGEMENT CALLS A READER COULD REASONABLY DISAGREE WITH
-------------------------------------------------------
1. GREEN, NOT ORANGE, WASHES THE OTHER HALF-PLANE. fig3_style fixes orange as "mean-signature
   retrieval is favoured" and green as "a control that performs no retrieval, or an external
   readout", naming the response-magnitude scalar as green by example. The competitor here is
   that scalar, not the mean-signature retriever, so orange would say something flatly false.
   Green is used as a half-plane rather than as an object colour, which extends fig3_style's
   blue/orange half-plane idiom to the third family; the tint is DERIVED from the frozen EXT hex
   by the same white blend that produces the frozen POP_WASH from the frozen POP hex, and the
   blend is asserted against POP_WASH below so the two washes cannot drift apart.
2. THE AXES ARE NOT EQUAL-ASPECT. The printed axes are 1.98 x 0.90 in, so an equal-aspect square
   would waste more than half the width or go portrait, and an earlier version's set_aspect plus
   set_anchor left the panel floating inside its box. Anisotropic scaling distorts DISTANCE from
   the equality line but preserves SIDE of it exactly, and the side is the whole claim, so the
   distortion costs the panel nothing it uses. The line is still y = x in data coordinates; it
   simply prints at about 36 degrees rather than 45.
3. THE TWO OUTER STRIPS HOLD NO DATA. Both half-planes need a label, and there is no data-free
   region inside a 103-point cloud that spans both, so the x limits reserve 0.35 in on each side
   and leave the cloud 1.28 of the 1.98 in. The equality line leaves the view through the top and
   the bottom of the frame before either strip begins, so every visible point in the left strip
   satisfies y > x and every point in the right strip y < x, and each label sits in the half-plane
   it names. Five assertions hold that up: no query falls in a strip, the line clears both strips,
   each label coordinate is on the side its own text names, the count under each label is that
   side's count, and every drawn label clears its own strip on all four edges by a MEASURED
   margin. Because the strips push the x limits out to about +/- 1.14, past the range a Spearman
   rho can take, the bottom spine is cut back to the data the way panels f, h and j cut theirs
   back, so the strips read as margin and not as a scale; the drawn ticks are asserted to lie
   inside that cut-back span.
4. THE WILCOXON P IS CUT INTO THE CAPTION, and the cut is now a choice rather than a space
   constraint. The paired Wilcoxon on energy minus magnitude-match gives p = 0.073, and it is
   ANTICONSERVATIVE: queries within a cell line share a candidate library, so they are not
   independent. It is computed here, returned and printed, never drawn. A p set beside the marks
   is read as the panel's result, and this one cannot bear that weight, whereas a caption can
   carry the word NOMINAL next to it in the same breath. The caption must do so. It must also
   carry the marker key (circle A549, square K562, triangle MCF7); shapes without an on-panel key
   still show that the three lines interleave, and fig3_style forbids spending hue on them.
5. THE PANEL SHOWS NO PER-CELL-LINE COUNT, though the honest unit of replication is the three
   lines and they do not agree: energy leads on 22 of 34 A549, 15 of 34 K562 (a loss) and 25 of
   35 MCF7 queries. Three more counts beside the two half-plane counts would turn the strips back
   into a text column. They are returned by draw_3i for the caption, and the shapes let a reader
   see that no line is separate.
6. BOTH COUNTS CARRY THE DENOMINATOR. "62/103" and "41/103" repeat n, which one "n = 103"
   elsewhere on the panel would not. The repetition buys each label the property of being true on
   its own, in a panel whose whole point is that the two numbers are close.

Run standalone: python3 fig3i.py

EVERY NUMBER IN THIS DOCSTRING IS THE U-ARM VALUE, reissued 2026-09-03 when the
Class-C source-data views were brought under figures/sync_source_data.py and resynced
from results/upgrade/. The V-arm values they replaced are in
docs/phase2/POST_REPAIR_MASTER_RESULTS.md, Category B and C1.
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
from matplotlib.backends.backend_agg import RendererAgg
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig3_style import (CELL_MARKER, EXT, FAINT, POP, POP_WASH, PT_ANNOT,  # noqa: E402
                        PT_SMALL, PT_TICK, REPO, SHARED, SUBTLE, TEXT, bare_axes)

SRC = os.path.join(REPO, "figures", "source_data", "fig3hi_class_c_functional.csv")

XCOL, YCOL = "energy_rho", "magnitude_match_rho"

# Inches of x reserved on each side for one half-plane label. The label is stacked, so this is a
# width, not a height, and the widest thing it has to hold is "energy" set on one line at
# PT_ANNOT, which measures 0.320 in; the count under it at PT_SMALL is 0.280 in. The strip was
# 0.32 in, which held that label with 0.000 in to spare on either side: the word ran from the
# padded edge of the data to the frame, and nothing checked it. 0.35 in buys 0.015 in of air on
# each side, which is what makes the measured fit assertion below a gate rather than a coin flip.
# It costs 0.06 in of the 1.98 in axes, taken from a cloud that is nowhere near density-limited.
STRIP_IN = 0.35
# Minimum clear space, in points, between a strip label and every edge of its own strip. Stated
# in points because it is space around type; asserted from measured extents, not estimated.
LABEL_AIR_PT = 0.8
# Data-unit air between the outermost query and the strip it must not enter, and between the
# outermost query and the top or bottom frame.
# PAD_X pads the INNER BAND, which is the union of the two columns' ranges, and PAD_Y the
# y view. PAD_X must exceed PAD_Y or the equality line still reaches a strip; asserted below.
PAD_X, PAD_Y = 0.065, 0.050
# Where each half-plane label sits inside its strip, as a fraction of the y range, and how far
# below it the count is set, in points. The offset is in points because it separates two pieces of
# type; the label heights that set it are in points too. The high fraction was 0.72, which put
# "41/103" within 0.02 in of the height of the "0.0" y tick label and 0.10 in to its right, so the
# count read as an annotation on the y scale at rho = 0 rather than as the left half-plane's
# score. 0.80 lifts it onto its own row, between the 0.0 and 0.5 tick rows.
LY_FRAC_LOW, LY_FRAC_HIGH = 0.30, 0.80
COUNT_DROP_PT = 13.0
# Where the exact-tie note sits in the left label strip, as a fraction of the y range. Low, so it
# clears the "scalar better" block at LY_FRAC_HIGH and is read as a panel note rather than as part
# of that half-plane's count.
TIE_Y_FRAC = 0.07

MS = 3.4          # marker diameter in points; 103 queries inside about 1.28 x 0.90 in
LW_DIAG = 1.0     # the equality line, the datum this panel is read against
LW_ZERO = 0.6     # rho = 0 guides, deliberately fainter than the equality line


def _wash(hex_colour: str, frac: float = 0.15) -> str:
    """Blend a frozen family hex with white, the way POP_WASH is a blend of POP.

    fig3_style freezes a wash for POP and for MEAN but not for EXT, because no earlier panel put
    the external readout on a half-plane. Deriving the green tint by the same recipe, and
    asserting the recipe reproduces the frozen POP_WASH, keeps this panel's two washes at one
    weight and keeps them tied to the frozen hues rather than to a hex typed here.
    """
    r, g, b = (int(hex_colour[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02X%02X%02X" % tuple(round(255 - (255 - c) * frac) for c in (r, g, b))


_POP_CHECK = _wash(POP)
assert all(abs(int(_POP_CHECK[i:i + 2], 16) - int(POP_WASH[i:i + 2], 16)) <= 2
           for i in (1, 3, 5)), (
    f"_wash(POP) = {_POP_CHECK} no longer reproduces fig3_style.POP_WASH = {POP_WASH}; the two "
    f"half-planes of panel i would print at different weights.")

POP_TINT = POP_WASH          # energy better: the frozen blue wash
EXT_TINT = _wash(EXT)        # the scalar better: the same blend of the frozen green


def _load() -> pd.DataFrame:
    if not os.path.exists(SRC):
        raise FileNotFoundError(
            f"{SRC} does not exist. Run analysis/class_c/class_c_functional_oracle.py first.")
    d = pd.read_csv(SRC)
    missing = [c for c in (XCOL, YCOL, "cell_line") if c not in d.columns]
    if missing:
        raise KeyError(f"{SRC} is missing {missing}; panel 3i cannot be drawn from it.")
    unknown = sorted(set(d.cell_line.unique()) - set(CELL_MARKER))
    if unknown:
        raise KeyError(f"{SRC} carries cell lines {unknown} with no shape in fig3_style.")
    return d


def _axes_width_in(ax) -> float:
    """The axes width in inches ON THE PRINTED PAGE, taken from the axes, not from a constant.

    The strip width is specified in inches because it holds type, which is specified in points;
    the x limits therefore have to be solved from the real geometry. Reading it back from the
    axes means this panel follows fig3_assemble's inch ledger instead of duplicating it.
    """
    return float(ax.get_position().width * ax.get_figure().get_figwidth())


def draw_3i(ax):
    d = _load()
    x = d[XCOL].to_numpy(dtype=float)
    y = d[YCOL].to_numpy(dtype=float)
    n = int(x.size)

    energy_wins = int((x > y).sum())
    scalar_wins = int((x < y).sum())
    ties = int((x == y).sum())
    # A TIE IS DRAWN, NOT REFUSED (2026-09-03). This used to raise if the two half-planes did not
    # partition the queries, on the reasoning that two counts under two labels must sum to n.
    # Under the unbiased estimator exactly one query, A549 / Fulvestrant, scores identically on
    # both rules (0.663436 each), so they no longer do. Raising would have made an exact tie
    # unpublishable; the panel names it instead, on the equality line where it happened, which is
    # the same thing panels a and 2c do with theirs.
    assert energy_wins + scalar_wins + ties == n, (
        f"{energy_wins} + {scalar_wins} + {ties} does not account for all {n} queries on {XCOL} "
        f"against {YCOL}; a NaN has entered one of the two columns.")
    p_wilcoxon = float(stats.wilcoxon(x, y).pvalue)

    # ---- the view. Solve the x limits so each label strip is STRIP_IN wide on the page.
    ax_w = _axes_width_in(ax)
    if ax_w <= 3.0 * STRIP_IN:
        raise ValueError(f"panel i is {ax_w:.2f} in wide; two {STRIP_IN} in label strips would "
                         f"leave the 103 queries under a third of the axes.")
    # The inner band has to contain the y range as well as the x range, or the equality line
    # leaves the frame through a label strip and that strip's single label is false over part of
    # itself. Deriving it from BOTH axes makes that structural rather than lucky: until
    # 2026-09-03 it was x alone, and it held only because the energy column happened to be the
    # wider of the two. Under the unbiased estimator the energy column narrowed and the
    # magnitude-match column did not, y ran 0.004 past it, and the assertion below fired. PAD_X is
    # still the pad; what changed is what it is a pad around.
    inner_lo = min(float(x.min()), float(y.min())) - PAD_X
    inner_hi = max(float(x.max()), float(y.max())) + PAD_X
    span = inner_hi - inner_lo
    x_range = span / (1.0 - 2.0 * STRIP_IN / ax_w)
    strip = 0.5 * (x_range - span)
    XLO, XHI = inner_lo - strip, inner_hi + strip
    YLO, YHI = y.min() - PAD_Y, y.max() + PAD_Y

    assert (x > XLO).all() and (x < XHI).all() and (y > YLO).all() and (y < YHI).all(), (
        "a query falls outside the drawn limits; the visible split would not be the counted one.")
    assert not ((x > inner_hi) | (x < inner_lo)).any(), "a query sits in a label strip."

    # The equality line must leave the frame through the top and the bottom, not through a label
    # strip, or the strip would hold both half-planes and its single label would be false over
    # part of itself. It is also what lets the count under a label be set anywhere in that strip:
    # once the line clears the strip, every y in view is on the named side.
    assert inner_lo < YLO and YHI < inner_hi, (
        f"the equality line enters a label strip: y runs [{YLO:.3f}, {YHI:.3f}] against an inner "
        f"x of [{inner_lo:.3f}, {inner_hi:.3f}]. One half-plane label would then sit over a strip "
        f"containing both half-planes. Widen STRIP_IN or move the labels inside the data.")

    # ---- the two half-planes, their direction hints and their counts, from ONE table, so the
    # wash, the two words over it and the number under those words cannot be swapped
    # independently. side is the sign of y - x: negative is where energy scores higher. Each label
    # sits in the strip on its own side, high on the left and low on the right so neither lands on
    # the line's visual path. Ink, not colour: fig3_style allows a label on a wash, not coloured
    # text on one. The wash is faint on purpose: the equality line, the two hints and the two
    # counts do the separating, and a wash is never the only thing that does.
    xs = np.linspace(XLO, XHI, 512)
    edge = np.clip(xs, YLO, YHI)
    drawn = []
    for side, wash, hint, wins, lx, ly_frac in (
            (-1, POP_TINT, "energy\nbetter", energy_wins,
             0.5 * (inner_hi + XHI), LY_FRAC_LOW),
            (+1, EXT_TINT, "scalar\nbetter", scalar_wins,
             0.5 * (XLO + inner_lo), LY_FRAC_HIGH)):
        lo_edge, hi_edge = (YLO, edge) if side < 0 else (edge, YHI)
        ax.fill_between(xs, lo_edge, hi_edge, color=wash, lw=0, zorder=0)
        ly = YLO + ly_frac * (YHI - YLO)
        assert np.sign(ly - lx) == side, (
            f"the {hint.replace(chr(10), ' ')!r} label sits at ({lx:.2f}, {ly:.2f}), which is on "
            f"the wrong side of y = x for the half-plane it names.")
        assert wins == int((np.sign(y - x) == side).sum()), (
            f"the count drawn under {hint.replace(chr(10), ' ')!r} is not the number of queries "
            f"on that side of y = x; the label would contradict the cloud above it.")
        t_hint = ax.text(lx, ly, hint, ha="center", va="center", fontsize=PT_ANNOT, color=TEXT,
                         linespacing=1.15, zorder=4)
        # The count is a bare statistic, not a sentence: the two words say which way, this says
        # how many out of how many. Offset in points so the gap under the hint is type-set rather
        # than data-set, and so it does not move when the y range does.
        t_count = ax.annotate(f"{wins}/{n}", xy=(lx, ly), xycoords="data",
                              xytext=(0.0, -COUNT_DROP_PT), textcoords="offset points",
                              ha="center", va="center", fontsize=PT_SMALL, color=TEXT, zorder=4)
        drawn.append((side, (t_hint, t_count)))

    # rho = 0 on either method. Drawn only across the data, so the strips stay legibly empty, and
    # fainter than the equality line because zero is context here and the equality line is the
    # datum. A quarter to a third of queries anticorrelate with the functional oracle: 29 of 103
    # under energy, 34 under the scalar, and 11 under both.
    ax.plot([inner_lo, inner_hi], [0.0, 0.0], color=FAINT, lw=LW_ZERO, zorder=1)
    ax.plot([0.0, 0.0], [YLO, YHI], color=FAINT, lw=LW_ZERO, zorder=1)

    # ---- the equality line, spanning the full height of the frame. It is the only thing on the
    # panel a point is read against, so it outweighs the zero guides.
    ax.plot([YLO, YHI], [YLO, YHI], color=SUBTLE, lw=LW_DIAG, zorder=2, solid_capstyle="butt")

    # ---- the queries. Cell line is a SHAPE in SHARED grey: both axes are methods, so blue here
    # would say "population-level" of a mark whose identity is a query, and three hues would
    # spend the figure's only two meaningful colours on a nuisance variable.
    for line, marker in CELL_MARKER.items():
        s = d[d.cell_line == line]
        ax.plot(s[XCOL], s[YCOL], ls="", marker=marker, ms=MS, mfc=SHARED, mec="white",
                mew=0.35, alpha=0.85, zorder=3)

    bare_axes(ax)
    ax.set_xlim(XLO, XHI)
    ax.set_ylim(YLO, YHI)
    # The strips push the x limits past |rho| = 1, which no Spearman rho can reach, so the scale
    # stops where the data stop and the strips read as margin.
    ax.spines["bottom"].set_bounds(inner_lo, inner_hi)
    ax.set_xticks([-0.5, 0.0, 0.5])
    ax.set_yticks([-0.5, 0.0, 0.5])
    # The tick positions are the only literals on this panel, and the bottom spine they sit on is
    # cut back to the data, so a narrower cloud would strand a tick past the end of its own scale.
    assert all(inner_lo <= t <= inner_hi for t in ax.get_xticks()), (
        f"an x tick falls outside the cut-back bottom spine [{inner_lo:.3f}, {inner_hi:.3f}]; it "
        f"would print past the end of the scale it belongs to.")
    assert all(YLO <= t <= YHI for t in ax.get_yticks()), (
        f"a y tick falls outside the drawn y range [{YLO:.3f}, {YHI:.3f}].")

    # The tie. It belongs to NEITHER half-plane, so it is not a third count under either label:
    # it goes low in the left strip, which is data-free by the assertion above, where it reads as
    # a note about the panel rather than as part of a count. Naming it is not optional now that
    # the two drawn counts no longer sum to n: a reader who adds 62 and 40 and finds 102 must be
    # able to see what the missing query did. It was drawn at the tied point first, and that point
    # sits in the densest part of the cloud at (0.663, 0.663), where the note was unreadable.
    if ties:
        ax.text(0.5 * (XLO + inner_lo), YLO + TIE_Y_FRAC * (YHI - YLO),
                f"{ties} exact tie" if ties == 1 else f"{ties} exact ties",
                ha="center", va="center", fontsize=PT_SMALL, color=SUBTLE, zorder=4)

    ax.set_xlabel(r"energy retrieval, $\rho$", fontsize=PT_ANNOT)
    ax.set_ylabel("response-magnitude\nmatch (a scalar), " r"$\rho$", fontsize=PT_ANNOT,
                  linespacing=1.15)

    # ---- the four strip labels, MEASURED. Each strip is sized in inches because it holds type,
    # so whether the type fits is a fact about the font rather than about the data, and nothing
    # else would catch an overflow: a label that outgrows its strip runs into the cloud on one
    # side or off the frame on the other, and both still pass the assembler's floor gate and the
    # preview's text-overlap gate. The renderer is built here, as in fig3a and fig3d, rather than
    # taken from fig.canvas, so the measurement neither forces a draw of a half-assembled figure
    # nor assumes which backend fig3_assemble is building under. It runs after the limits are set
    # because the extents are taken through transData.
    fig = ax.get_figure()
    rend = RendererAgg(int(fig.get_figwidth() * fig.dpi), int(fig.get_figheight() * fig.dpi),
                       fig.dpi)
    air_in = LABEL_AIR_PT / 72.0
    for side, artists in drawn:
        strip_lo, strip_hi = (XLO, inner_lo) if side > 0 else (inner_hi, XHI)
        (px0, py0), (px1, py1) = ax.transData.transform(
            [(strip_lo, YLO), (strip_hi, YHI)])
        for art in artists:
            e = art.get_window_extent(renderer=rend)
            slack = min(e.x0 - px0, px1 - e.x1, e.y0 - py0, py1 - e.y1) / fig.dpi
            assert slack >= air_in, (
                f"the drawn label {str(art.get_text()).replace(chr(10), ' ')!r} clears its "
                f"{STRIP_IN} in label strip by only {slack:.4f} in, under the {LABEL_AIR_PT} pt "
                f"({air_in:.4f} in) this panel requires. It would print against the cloud or "
                f"against the frame. Widen STRIP_IN, or move the label with LY_FRAC_LOW / "
                f"LY_FRAC_HIGH, or shorten the wording; do not lower the size.")

    per_line = {ln: (int((s[XCOL] > s[YCOL]).sum()), int(len(s)))
                for ln, s in d.groupby("cell_line")}
    assert (sum(w for w, _ in per_line.values()) == energy_wins
            and sum(k for _, k in per_line.values()) == n), (
        f"the per-cell-line counts {per_line} do not add up to the {energy_wins}/{n} drawn in the "
        f"blue half-plane; the caption would contradict the figure.")
    return {"energy_wins": energy_wins, "scalar_wins": scalar_wins, "ties": ties,
            "n_queries": n, "wilcoxon_p": p_wilcoxon, "per_cell_line": per_line}


if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from figstyle import apply_style
    from fig3_style import PT_TITLE

    # The printed rect of panel i, copied from fig3_assemble's ledger (row 4, box 2.80 in wide,
    # pads 0.72 / 0.10 / 0.38, row height 1.28, letter block 0.17). The preview duplicates it so
    # this module never imports the assembler, which pulls in every other panel.
    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    fig = plt.figure(figsize=(2.80, 1.45))
    ax = fig.add_axes([0.72 / 2.80, 0.38 / 1.45, 1.98 / 2.80, 0.90 / 1.45])
    st = draw_3i(ax)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "3i.png")
    fig.savefig(out, dpi=400)
    print(f"wrote {out}")
    print(f"energy better on {st['energy_wins']} of {st['n_queries']} queries "
          f"(scalar better on {st['scalar_wins']})")
    print(f"per cell line (energy wins / n): {st['per_cell_line']}")
    print(f"paired Wilcoxon p = {st['wilcoxon_p']:.4f}  NOMINAL: queries within a cell line "
          f"share a candidate library, so this p is anticonservative. Caption must say so.")
