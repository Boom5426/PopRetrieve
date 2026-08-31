"""PopRetrieve Figure 3 panel 3i: per query, the population-level score against the scalar it
must beat, read as a side of the equality line.

WHAT THIS PANEL CLAIMS
----------------------
Panel h reports the Class-C aggregate: energy retrieval reaches a median rho of +0.276 against
the matched functional oracle, the query-dependent response-magnitude scalar reaches +0.232, and
partialling that channel out leaves energy +0.097. This panel shows the same 103 queries one at a
time, and its claim is a COUNT, drawn in the phrase over the panel and computed at draw time:
energy scores higher than the scalar on 62 of 103 queries. That is a 60/40 split, not a sweep,
and the split is the reason the paper does not read h as a clean win for distributional
retrieval. A reader who takes "energy beats the scalar" away from h without this panel has taken
a stronger claim than the data carry.

Source data: figures/source_data/fig3hi_class_c_functional.csv, 103 leave-one-drug-out queries
(SciPlex3 x GDSC2, 10 uM, 34-35 drugs per cell line).
    x = energy_rho             energy retrieval, which compares whole populations
    y = magnitude_match_rho    a QUERY-DEPENDENT SCALAR that compares no distributions and merely
                               prefers candidates whose response is about as large as the query's
The oracle both are scored against is drug-drug functional similarity from GDSC2 dose-response
profiles, named in full on panel h and in the row banner; these axis labels name only the score.
Note the source table also carries magnitude_only_rho, a DIFFERENT and query-independent scalar,
which is why the y label keeps the word "match".

PROVENANCE, AND THE CORRECTION THAT MUST NOT BE LOST
----------------------------------------------------
An earlier version of this panel graded the same rankings against ABSOLUTE POTENCY and reported
that the scalar won 103 of 103 queries. Both halves of that were wrong. Potency is an oracle no
similarity retriever was ever asked to optimise, and it is largely response magnitude, so a
magnitude scalar was near-guaranteed to win it; and a 103-of-103 sweep over queries that share a
candidate library within each cell line counts pseudo-replicates as independent evidence, which
this study refuses to do elsewhere. The potency comparison survives only as the endpoint audit in
panels l and m.

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
2. THE AXES ARE NOT EQUAL-ASPECT. The printed axes are 1.98 x 0.82 in, so an equal-aspect square
   would waste more than half the width or go portrait, and the previous version's set_aspect
   plus set_anchor left the panel floating inside its box. Anisotropic scaling distorts DISTANCE
   from the equality line but preserves SIDE of it exactly, and the side is the whole claim, so
   the distortion costs the panel nothing it uses. The line is still y = x in data coordinates;
   it simply prints at about 32 degrees rather than 45.
3. THE TWO OUTER STRIPS HOLD NO DATA. Both half-planes need a label, and there is no data-free
   region inside a 103-point cloud that spans both, so the x limits reserve 0.32 in on each side.
   The equality line leaves the view through the top and the bottom of the frame before either
   strip begins, so every visible point in the left strip satisfies y > x and every point in the
   right strip y < x, and each label sits in the half-plane it names. Three assertions hold that
   up: no query falls in a strip, the line clears both strips, and each label coordinate is on
   the side its own text names. Because the strips push the x limits out to about +/- 1.09, past
   the range a Spearman rho can take, the bottom spine is cut back to the data the way panels e,
   h and l cut theirs back, so the strips read as margin and not as a scale.
4. THE WILCOXON P AND THE CELL-LINE KEY ARE CUT INTO THE CAPTION. The paired Wilcoxon on
   energy minus magnitude-match gives p = 0.073, and it is ANTICONSERVATIVE: queries within a
   cell line share a candidate library, so they are not independent. It is computed here and
   returned and printed, never drawn, because at 1.98 x 0.82 in it displaces the count, which is
   the panel's actual claim. The caption must call it NOMINAL. The caption must also carry the
   marker key (circle A549, square K562, triangle MCF7); shapes without an on-panel key still
   show that the three lines interleave, and fig3_style forbids spending hue on them.
5. THE PANEL SHOWS NO PER-CELL-LINE COUNT, though the honest unit of replication is the three
   lines and they do not agree: energy leads on 22 of 34 A549, 15 of 34 K562 (a loss) and 25 of
   35 MCF7 queries. Three more counts do not fit beside the two half-plane labels. They are
   returned by draw_3i for the caption, and the shapes let a reader see that no line is separate.

Run standalone: python3 fig3i.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig3_style import (CELL_MARKER, EXT, FAINT, POP, POP_WASH, PT_ANNOT,  # noqa: E402
                        PT_TICK, REPO, SHARED, SUBTLE, TEXT, bare_axes, title)

SRC = os.path.join(REPO, "figures", "source_data", "fig3hi_class_c_functional.csv")

XCOL, YCOL = "energy_rho", "magnitude_match_rho"

# Inches of x reserved on each side for one half-plane label. 0.32 in holds "energy" set on one
# line at PT_ANNOT with a hair of air; the label is two lines, so this is a width, not a height.
STRIP_IN = 0.32
# Data-unit air between the outermost query and the strip it must not enter, and between the
# outermost query and the top or bottom frame.
PAD_X, PAD_Y = 0.035, 0.050

MS = 3.0          # marker diameter in points; 103 queries inside about 1.28 x 0.75 in
LW_DIAG = 0.9     # the equality line, the datum this panel is read against
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
    if energy_wins + scalar_wins != n:
        raise ValueError(
            f"{n - energy_wins - scalar_wins} of {n} queries score EXACTLY equal on {XCOL} and "
            f"{YCOL}. The two half-plane labels no longer partition the queries and the count in "
            f"the panel phrase would be a third of a three-way split.")
    p_wilcoxon = float(stats.wilcoxon(x, y).pvalue)

    # ---- the view. Solve the x limits so each label strip is STRIP_IN wide on the page.
    ax_w = _axes_width_in(ax)
    if ax_w <= 3.0 * STRIP_IN:
        raise ValueError(f"panel i is {ax_w:.2f} in wide; two {STRIP_IN} in label strips would "
                         f"leave the 103 queries under a third of the axes.")
    inner_lo, inner_hi = x.min() - PAD_X, x.max() + PAD_X
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
    # part of itself.
    assert inner_lo < YLO and YHI < inner_hi, (
        f"the equality line enters a label strip: y runs [{YLO:.3f}, {YHI:.3f}] against an inner "
        f"x of [{inner_lo:.3f}, {inner_hi:.3f}]. One half-plane label would then sit over a strip "
        f"containing both half-planes. Widen STRIP_IN or move the labels inside the data.")

    # ---- the two half-planes and their labels, from ONE table, so the wash and the text over it
    # cannot be swapped independently. side is the sign of y - x: negative is where energy scores
    # higher, and it is the side the count in the phrase over the panel refers to. Each label sits
    # in the strip on its own side, set high on the left and low on the right so the pair leans
    # the way the line does. Ink, not colour: fig3_style allows a label on a wash, not coloured
    # text on one. The wash is faint on purpose: the equality line and the two labels do the
    # separating, and a wash is never the only thing that does.
    xs = np.linspace(XLO, XHI, 512)
    edge = np.clip(xs, YLO, YHI)
    for side, wash, label, lx, ly_frac in (
            (-1, POP_TINT, "energy\nbetter", 0.5 * (inner_hi + XHI), 0.26),
            (+1, EXT_TINT, "scalar\nbetter", 0.5 * (XLO + inner_lo), 0.74)):
        lo_edge, hi_edge = (YLO, edge) if side < 0 else (edge, YHI)
        ax.fill_between(xs, lo_edge, hi_edge, color=wash, lw=0, zorder=0)
        ly = YLO + ly_frac * (YHI - YLO)
        assert np.sign(ly - lx) == side, (
            f"the {label.replace(chr(10), ' ')!r} label sits at ({lx:.2f}, {ly:.2f}), which is on "
            f"the wrong side of y = x for the half-plane it names.")
        ax.text(lx, ly, label, ha="center", va="center", fontsize=PT_ANNOT, color=TEXT,
                linespacing=1.15, zorder=4)

    # rho = 0 on either method. Drawn only across the data, so the strips stay legibly empty, and
    # fainter than the equality line because zero is context here and the equality line is the
    # datum. A quarter to a third of queries anticorrelate with the functional oracle: 29 of 103
    # under energy, 34 under the scalar, and 11 under both.
    ax.plot([inner_lo, inner_hi], [0.0, 0.0], color=FAINT, lw=LW_ZERO, zorder=1)
    ax.plot([0.0, 0.0], [YLO, YHI], color=FAINT, lw=LW_ZERO, zorder=1)

    # ---- the equality line, spanning the full height of the frame.
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
    ax.set_xlabel(r"energy retrieval, $\rho$", fontsize=PT_ANNOT)
    ax.set_ylabel("response-magnitude\nmatch (a scalar), " r"$\rho$", fontsize=PT_ANNOT,
                  linespacing=1.15)

    # The count IS the panel. Computed here so the phrase cannot outlive the table under it.
    title(ax, f"Energy better on {energy_wins} of {n} queries")

    per_line = {ln: (int((s[XCOL] > s[YCOL]).sum()), int(len(s)))
                for ln, s in d.groupby("cell_line")}
    assert (sum(w for w, _ in per_line.values()) == energy_wins
            and sum(k for _, k in per_line.values()) == n), (
        f"the per-cell-line counts {per_line} do not add up to the {energy_wins} of {n} drawn in "
        f"the phrase over the panel; the caption would contradict the figure.")
    return {"energy_wins": energy_wins, "scalar_wins": scalar_wins, "n_queries": n,
            "wilcoxon_p": p_wilcoxon, "per_cell_line": per_line}


if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from figstyle import apply_style
    from fig3_style import PT_TITLE

    # The printed rect of panel i, copied from fig3_assemble's ledger (row 4, box 2.80 in wide,
    # pads 0.72 / 0.10 / 0.38, row height 1.20). The preview duplicates it so this module never
    # imports the assembler, which pulls in every other panel.
    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    fig = plt.figure(figsize=(2.80, 1.44))
    ax = fig.add_axes([0.72 / 2.80, 0.38 / 1.44, 1.98 / 2.80, 0.82 / 1.44])
    st = draw_3i(ax)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "3i.png")
    fig.savefig(out, dpi=400)
    print(f"wrote {out}")
    print(f"energy better on {st['energy_wins']} of {st['n_queries']} queries "
          f"(scalar better on {st['scalar_wins']})")
    print(f"per cell line (energy wins / n): {st['per_cell_line']}")
    print(f"paired Wilcoxon p = {st['wilcoxon_p']:.4f}  NOMINAL: queries within a cell line "
          f"share a candidate library, so this p is anticonservative. Caption must say so.")
