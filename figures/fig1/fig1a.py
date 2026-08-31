"""PopRetrieve Figure 1, panel a: the task, and the single fork the paper is about.

WHAT THIS PANEL HAS TO SAY
--------------------------
One query population, one candidate library, one ranking machine. The only thing that differs
between the two routes is whether the query's single-cell responses are collapsed to one vector
or kept as a population, and that one difference is allowed to change the ranked list. Panel a is
also where the figure's colour vocabulary is declared: MEAN orange for the collapsed route, POP
blue for the population route, SHARED grey for everything both routes have in common.

WHY THE LAYOUT IS THIS SHAPE
----------------------------
The axes is 1.514 x 3.00 in, portrait. Two consequences drive every position below.

  * The two routes are STACKED ROWS, not side-by-side columns. "$\\{x_1,\\ldots,x_n\\}\\to\\mu_Q$"
    measures about 1.06 in once its subscripts are set at a legible size, so a half-panel column
    (0.76 in) cannot hold it. Each route therefore gets a full-width row and the routes are
    separated top-from-bottom, which is also how the caption reads them.
  * The candidate library sits BESIDE the two rows rather than under them. Any arrow from the
    upper row to a library placed below would have to cross the lower row; put the library in the
    right margin and both routes reach it with a short horizontal arrow and nothing crosses.
    The two ranked lists then take the full width underneath, as a two-column table, so that
    rank 1 of one list sits directly beside rank 1 of the other and the swap is the thing the eye
    lands on. (The brief asked for the lists "to the right" of the library; at 1.514 in of total
    width the word "Population" alone is a fifth of the panel, so right became below.)

WHY SUBSCRIPTS ARE COMPOSED FROM TWO ARTISTS
--------------------------------------------
Matplotlib renders a mathtext sub/superscript at 0.7x nominal, so "$d_1$" set at PT_EQ (9.0) puts
its subscript on the page at 6.3 pt: below this figure's 6.5 pt floor, and fig1_assemble._assert_floor
measures exactly that product and refuses to build. Writing the base at PT_EQ and the subscript as
its own artist at PT_SMALL prints the subscript at 6.5 pt, the floor itself, which is LARGER than
the mathtext default rather than smaller. Nothing is shrunk to fit; the pair is measured and set
snug by _run().

Schematic, not data. No measured value appears anywhere in this panel.

Run standalone: python3 fig1a.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
from matplotlib.patches import Ellipse, Rectangle

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig1_style import (FAINT, LW_ARROW, LW_HAIR, MEAN, POP, PT_ANNOT, PT_EQ,  # noqa: E402
                        PT_SMALL, SHARED, SUBTLE, TEXT, arrow, blank, cells, centroid,
                        title)

# ------------------------------------------------------------------ layout, in axes units
# x. The width budget is the tight one: a route's equation measures 1.02 in, the library column
# needs 0.29 in for a population glyph plus its name, and the panel is 1.514 in wide. What is left
# pays for the grey spine on the left and for the arrow that carries each route into the library.
X_SPINE = 0.016             # the grey spine that carries the query down to both routes
X_ROW = 0.045               # left edge of a route's own content
X_ROWEND = 0.736            # right edge of a route's own content; its annotation right-aligns here
# 0.736, not 0.700. PT_EQ was corrected 9.0 -> 9.3 on 2026-08-31 (9.0 x 0.7 = 6.30 pt is under
# this figure's 6.5 pt floor, so the token could not carry real mathtext), and the 3.3% wider
# set notation left the collapse route 0.025 axes units of arrow against the 0.042 its own
# assertion demands. The width comes out of the run to the library, which was 0.106 units and
# is now 0.070: still unambiguously an arrow, and the shortest thing in the panel that had
# slack. Nothing was shrunk to fit.
X_TOLIB = 0.806             # where a route's arrow reaches the library, whatever the row's width
LIB_BOX = (0.812, 0.430, 0.188, 0.340)               # x, y, w, h
LIB_CELLS_X, LIB_LABEL_X = 0.855, 0.900
COL_RANK, COL_MEAN, COL_POP = 0.125, 0.470, 0.800    # the ranked-list table's three columns
X_RULE = (0.045, 0.990)     # the table's rule, starting where the routes above it start

# y, top to bottom
Y_TITLE = 0.996
Y_SUBTITLE = 0.950
Q_CY = 0.854                # centre of the query population
Y_LIBHEAD = 0.860           # library header, in the corner the query block leaves empty
Y_SPINE = (0.788, 0.765)    # where the trunk leaves the query, and where the spine proper starts
ROW_MEAN = (0.790, 0.700, 0.645)     # label (va top), equation baseline, annotation (va top)
ROW_POP = (0.593, 0.503, 0.448)
LIB_Y = (0.735, 0.645, 0.555, 0.465)
Y_TABLE_HEAD, Y_TABLE_RULE = 0.310, 0.282
TABLE_Y = (0.215, 0.140)
Y_TABLE_DOTS = 0.072

# ------------------------------------------------------------------ drawing constants
GAP = 0.010                 # horizontal breathing space between two parts of one expression
ARROW_MIN = 0.042           # shortest a transformation arrow may get and still read as flow
Y_MID = 0.012               # baseline to optical centre of a PT_EQ line, for marks set beside text
FORK_DROP = 0.020           # how far below a row's label the spine hands that row over
SUB_DROP_EM = 0.22          # subscript baseline drop, in ems of the base size, as mathtext sets it
N_QUERY = (54, 30)          # the query's two response states; 84 cells in total
CELL_S = 2.3                # marker area: small enough that 84 cells read as a population
DIAMOND_W = 0.052           # printed width of centroid()'s diamond at its default size

# The one candidate library, and the two rankings of it. Ranks 1 and 2 are swapped between the
# routes: that swap is the whole reason the panel exists, so it is data of the figure, not decoration.
CANDIDATES = ("1", "2", "3", "4")
RANKED = {"mean": ("3", "1"), "pop": ("1", "3")}


def _axes_in(ax):
    """The axes box in inches. Read from the figure so the panel is correct at any size."""
    w, h = ax.get_position().size * ax.figure.get_size_inches()
    return float(w), float(h)


def _rx(ax, ry):
    """The x radius that prints as round given a y radius, since x and y both span one unit."""
    w, h = _axes_in(ax)
    return ry * h / w


def _pt2y(ax, pt):
    """Points to axes-y units."""
    return pt / 72.0 / _axes_in(ax)[1]


def _renderer(ax):
    fig = ax.figure
    fig.canvas.draw()
    return fig.canvas.get_renderer()


def _run(ax, x, y, parts, rend, ha="left", zorder=8):
    """Set a run of fragments left to right on one baseline, spaced by MEASURED width.

    ``parts`` is ((text, pt, is_subscript, colour), ...). Subscript fragments are dropped by
    SUB_DROP_EM and carry their own size, which is how this panel gets a subscript that prints at
    the figure's floor instead of at 0.7x PT_EQ. Measuring rather than hard-coding an advance is
    what keeps the pair snug if the fallback font is not the one this was tuned on.

    Returns the run's width in axes units, so the caller can put an arrow after it.
    """
    drop = _pt2y(ax, PT_EQ * SUB_DROP_EM)
    inv = ax.transData.inverted()
    arts, cur = [], 0.0
    gid = "run-%d-%d" % (round(x * 1e4), round(y * 1e4))   # one expression, so QA can pair it up
    for txt, pt, is_sub, colour in parts:
        t = ax.text(cur, y - (drop if is_sub else 0.0), txt, ha="left", va="baseline",
                    fontsize=pt, color=colour, zorder=zorder, gid=gid)
        bb = t.get_window_extent(renderer=rend)
        cur += inv.transform((bb.x1, 0.0))[0] - inv.transform((bb.x0, 0.0))[0]
        arts.append(t)
    shift = {"left": x, "center": x - cur / 2.0, "right": x - cur}[ha]
    for t in arts:
        t.set_x(t.get_position()[0] + shift)
    return cur


def _set_parts():
    """{x_1, ..., x_n}: the query's cells, written the same way on both routes."""
    # The commas are braced so mathtext sets them as ordinary symbols. Its punctuation spacing
    # costs 0.05 in here, and the row's total width has no 0.05 in to give.
    return (("$\\{x$", PT_EQ, False, TEXT), ("$1$", PT_SMALL, True, TEXT),
            ("${,}\\ldots{,}x$", PT_EQ, False, TEXT), ("$n$", PT_SMALL, True, TEXT),
            ("$\\}$", PT_EQ, False, TEXT))


def _sym_parts(base, sub):
    """One subscripted symbol, base at PT_EQ and subscript at the floor. See the module note."""
    return (("$%s$" % base, PT_EQ, False, TEXT), ("$%s$" % sub, PT_SMALL, True, TEXT))


def _query(ax, rend, rng):
    """The query: a real population, two response states in it, both in SHARED grey.

    The states are separated by position and fill, never by a fifth hue: the query belongs to both
    routes, so colouring one of its states POP or MEAN would hand the query to one of them. The
    faint ring names the second state without asking to be read.
    """
    title(ax, "Query response Q", y=Y_TITLE, va="top")
    ax.text(0.0, Y_SUBTITLE, "single-cell population", transform=ax.transAxes,
            fontsize=PT_ANNOT, ha="left", va="top", color=SUBTLE)

    ry_a, ry_b = 0.038, 0.028
    cx_a, cy_a = 0.085, Q_CY + 0.014
    cx_b, cy_b = 0.118, Q_CY - 0.014
    cells(ax, cx_a, cy_a, N_QUERY[0], _rx(ax, ry_a), ry_a, color=SHARED, rng=rng,
          s=CELL_S, alpha=0.60)
    cells(ax, cx_b, cy_b, N_QUERY[1], _rx(ax, ry_b), ry_b, color=SHARED, rng=rng,
          s=CELL_S * 1.35, alpha=0.95)
    ax.add_patch(Ellipse((cx_b, cy_b), 2 * _rx(ax, ry_b + 0.007), 2 * (ry_b + 0.007),
                         fill=False, ec=FAINT, lw=LW_HAIR, ls=(0, (1.7, 1.4)), zorder=2))
    return cx_a, cy_b - ry_b - 0.010


def _spine(ax, x_from, y_from):
    """One query, two treatments: SHARED grey down to the fork, route colour after it.

    The spine runs in the left margin because the two routes are stacked rows; an arrow from the
    query to the lower row drawn anywhere else would have to cross the upper row.
    """
    ax.plot([x_from, x_from, X_SPINE, X_SPINE],
            [y_from, Y_SPINE[0], Y_SPINE[1], ROW_POP[0] - FORK_DROP],
            color=SHARED, lw=LW_ARROW, solid_capstyle="round", solid_joinstyle="round", zorder=3)
    for row, colour in ((ROW_MEAN, MEAN), (ROW_POP, POP)):
        # Diagonal, not horizontal: the row starts 0.05 in from the spine, and an arrow that short
        # is all head. Dropping it onto the equation line buys a shaft the eye can follow.
        arrow(ax, (X_SPINE, row[0] - FORK_DROP), (X_ROW - 0.003, row[1] + Y_MID), color=colour)


def _route(ax, rend, rng, rows, label, colour, annot, keep):
    """One route: what it is called, what it does to the query, and what survives it.

    Both routes are drawn from the same three lines, so the only difference the reader can see is
    the one the paper is about: a diamond where the population was, or the population itself.
    """
    y_lab, y_eq, y_ann = rows
    mid = y_eq + Y_MID
    ax.text(X_ROW, y_lab, label, transform=ax.transAxes, fontsize=PT_ANNOT, ha="left",
            va="top", color=TEXT, fontweight="bold")

    # Both rows end at X_ROWEND, so the two arrows into the library are the same arrow drawn
    # twice. The transformation arrow takes up the slack, which is why the result block is set
    # from the right and the arrow is measured last rather than assumed first.
    x_set = X_ROW + _run(ax, X_ROW, y_eq, _set_parts(), rend)
    if keep:
        ry = 0.032
        x_res = X_ROWEND - 2 * _rx(ax, ry)
        cells(ax, X_ROWEND - _rx(ax, ry), mid, 30, _rx(ax, ry), ry, color=colour, rng=rng,
              s=CELL_S * 1.2)
    else:
        w_mu = _run(ax, X_ROWEND, y_eq, _sym_parts("\\mu", "Q"), rend, ha="right")
        x_res = X_ROWEND - w_mu - GAP - DIAMOND_W
        centroid(ax, x_res + DIAMOND_W / 2, mid, color=colour)
    assert x_res - x_set - 2 * GAP >= ARROW_MIN, (
        f"route {label!r} leaves {x_res - x_set - 2 * GAP:.3f} axes units for its arrow, less "
        f"than the {ARROW_MIN} it takes to read as flow")
    arrow(ax, (x_set + GAP, mid), (x_res - GAP, mid), color=colour)

    ax.text(X_ROWEND, y_ann, annot, transform=ax.transAxes, fontsize=PT_ANNOT, ha="right",
            va="top", color=TEXT)
    arrow(ax, (X_ROWEND + GAP, mid), (X_TOLIB, mid), color=colour)


def _library(ax, rend, rng):
    """One library, shared. Both routes point into the same four candidate populations."""
    ax.text(LIB_BOX[0] + LIB_BOX[2], Y_LIBHEAD, "candidate\nlibrary", transform=ax.transAxes,
            fontsize=PT_ANNOT, ha="right", va="top", color=TEXT, linespacing=1.15)
    ax.add_patch(Rectangle(LIB_BOX[:2], LIB_BOX[2], LIB_BOX[3], fill=False, ec=FAINT,
                           lw=LW_HAIR, zorder=1))
    ry = 0.018
    for name, yy in zip(CANDIDATES, LIB_Y):
        cells(ax, LIB_CELLS_X, yy, 13, _rx(ax, ry), ry, color=SHARED, rng=rng, s=CELL_S)
        _run(ax, LIB_LABEL_X, yy - 0.013, _sym_parts("d", name), rend)


def _rankings(ax, rend):
    """The same four candidates, ranked twice. The lists disagree at the top; that is the panel."""
    # Both arrows leave the SAME point on the library, because what differs downstream is the
    # score, not the candidates: one library, ranked twice.
    # Each arrow stops beside its column's heading rather than on it, so the heading stays a word
    # rather than becoming a labelled target.
    src = (LIB_CELLS_X + 0.020, LIB_BOX[1] - 0.008)
    arrow(ax, src, (COL_MEAN + 0.055, Y_TABLE_HEAD + 0.028), color=MEAN)
    arrow(ax, src, (COL_POP + 0.010, Y_TABLE_HEAD + 0.028), color=POP)

    ax.text(COL_RANK, Y_TABLE_HEAD, "rank", transform=ax.transAxes, fontsize=PT_SMALL,
            ha="center", va="top", color=SUBTLE)
    for x, head in ((COL_MEAN, "Mean"), (COL_POP, "Population")):
        ax.text(x, Y_TABLE_HEAD, head, transform=ax.transAxes, fontsize=PT_ANNOT, ha="center",
                va="top", color=TEXT, fontweight="bold")
    ax.plot(X_RULE, [Y_TABLE_RULE, Y_TABLE_RULE], color=FAINT, lw=LW_HAIR, zorder=2)

    for i, yy in enumerate(TABLE_Y):
        ax.text(COL_RANK, yy, str(i + 1), transform=ax.transAxes, fontsize=PT_ANNOT,
                ha="center", va="center", color=SUBTLE)
        for x, route in ((COL_MEAN, "mean"), (COL_POP, "pop")):
            _run(ax, x, yy - 0.013, _sym_parts("d", RANKED[route][i]), rend, ha="center")
    for x in (COL_RANK, COL_MEAN, COL_POP):
        ax.text(x, Y_TABLE_DOTS, "$\\vdots$", transform=ax.transAxes, fontsize=PT_EQ,
                ha="center", va="center", color=SUBTLE)


def draw_1a(ax):
    """Draw panel a into ``ax``. The axes is expected to be 1.514 x 3.00 in in the composite."""
    blank(ax)
    rend = _renderer(ax)
    rng = np.random.default_rng(7)

    qx, qy = _query(ax, rend, rng)
    _spine(ax, qx, qy)
    _route(ax, rend, rng, ROW_MEAN, "collapse", MEAN, "1 vector", keep=False)
    _route(ax, rend, rng, ROW_POP, "retain cells", POP, "n cellular responses", keep=True)
    _library(ax, rend, rng)
    _rankings(ax, rend)
    return ax


if __name__ == "__main__":
    import re

    import matplotlib
    matplotlib.use("agg")
    import matplotlib.pyplot as plt
    import matplotlib.text as mtext
    from matplotlib.collections import Collection
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    from matplotlib.transforms import Bbox

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from figstyle import apply_style
    from fig1_style import PT_FLOOR, PT_TICK, PT_TITLE

    # EXACTLY the axes the composite gives this panel: 1.514 x 3.00 in with no subplot margins.
    # A panel tuned at another size is wrong in the figure that ships.
    AXW, AXH = 1.514, 3.000
    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    fig, ax = plt.subplots(figsize=(AXW, AXH))
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    draw_1a(ax)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "1a.png")
    fig.savefig(out, dpi=400, bbox_inches=Bbox([[0.0, 0.0], [AXW, AXH]]), pad_inches=0.0)

    # ---- gate 1: nothing prints below this figure's 6.5 pt floor -------------------------
    subsup = re.compile(r"\$[^$]*[\^_][^$]*\$")
    sizes = []
    for t in fig.findobj(mtext.Text):
        s = str(t.get_text())
        if not s.strip() or not t.get_visible():
            continue
        sizes.append((t.get_fontsize() * (0.7 if subsup.search(s) else 1.0), s[:30]))
    worst = min(sizes)
    assert worst[0] >= PT_FLOOR - 1e-6, f"below the {PT_FLOOR} pt floor: {worst}"

    # ---- gate 2: nothing hangs outside the axes rect -------------------------------------
    rend = fig.canvas.get_renderer()
    axbb = ax.get_window_extent(renderer=rend)
    skip = {ax.patch, *ax.spines.values()}
    over = []
    for art in ax.get_children():
        if art in skip or not art.get_visible():
            continue
        if not isinstance(art, (mtext.Text, Line2D, Collection, Patch)):
            continue
        if isinstance(art, mtext.Text) and not str(art.get_text()).strip():
            continue
        bb = art.get_tightbbox(rend)
        if bb is None:
            continue
        d = max(axbb.x0 - bb.x0, bb.x1 - axbb.x1, axbb.y0 - bb.y0, bb.y1 - axbb.y1)
        if d > 0.5:                       # half a device pixel of tolerance on the rect itself
            label = str(art.get_text())[:28] if isinstance(art, mtext.Text) else type(art).__name__
            over.append((round(d / fig.dpi * 72, 2), label,
                         [round(axbb.x0 - bb.x0, 1), round(bb.x1 - axbb.x1, 1),
                          round(axbb.y0 - bb.y0, 1), round(bb.y1 - axbb.y1, 1)]))
    for row in sorted(over, reverse=True):
        print(f"  OUTSIDE by {row[0]} pt  {row[1]!r}  [L,R,B,T px] {row[2]}")
    assert not over, f"{len(over)} artist(s) leave the axes; they would widen the composite"

    # ---- gate 3: no two text artists overlap ---------------------------------------------
    labels = [t for t in ax.get_children()
              if isinstance(t, mtext.Text) and str(t.get_text()).strip()]
    clashes = []
    for i, a in enumerate(labels):
        for b in labels[i + 1:]:
            # Fragments of one expression are meant to touch: a subscript sits against its base.
            if a.get_gid() is not None and a.get_gid() == b.get_gid():
                continue
            ba, bb2 = a.get_tightbbox(rend), b.get_tightbbox(rend)
            if ba is None or bb2 is None:
                continue
            ov = min(ba.x1, bb2.x1) - max(ba.x0, bb2.x0), min(ba.y1, bb2.y1) - max(ba.y0, bb2.y0)
            if min(ov) > 0.5:
                clashes.append((round(min(ov), 1), str(a.get_text())[:18], str(b.get_text())[:18]))
    for c in sorted(clashes, reverse=True):
        print(f"  OVERLAP {c[0]} px: {c[1]!r} / {c[2]!r}")
    assert not clashes, f"{len(clashes)} overlapping label pair(s)"

    print(f"wrote {out}  ({AXW} x {AXH} in axes)")
    print(f"smallest effective text size: {worst[0]:.2f} pt  ({worst[1]!r})")
    print(f"text artists: {len(sizes)}   all inside the axes: True")
