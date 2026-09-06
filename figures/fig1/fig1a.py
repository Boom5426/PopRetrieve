"""PopRetrieve Figure 1, panel a: what a response is represented by, and what a score reads off it.

WHAT THIS PANEL HAS TO SAY
--------------------------
Two layers, and the whole panel exists to keep them apart:

    REPRESENTATION   what survives the summary of a single-cell response population
                     mean representation mu, or the population P itself
    SCORING RULE     what a score then reads off that representation

They are not the same layer, and conflating them is the error this cut of the panel was written
to remove. A mean representation is NOT direction-only: mu carries a direction and a magnitude.
It is the COSINE that discards the magnitude. So one representation, mu, supports two scoring
rules, and the figure's vocabulary is fixed here for the rest of the paper:

    directional mean score       cos(mu_Q, mu_d)          reads direction only
    magnitude-aware mean score   -||mu_Q - mu_d||         reads direction and magnitude
    population score             -D(P_Q, P_d)             reads the distribution as well

The information those three read is NESTED, not parallel, and the nesting is the drawing:

    direction  <  direction + magnitude  <  direction + magnitude + population structure

Each score's bar starts at the same origin and reaches one segment further along one shared
information axis. Three bars of increasing length on one axis is a containment statement; three
separate boxes would have been three rival methods, which is what the previous cut drew.

WHAT LEFT THIS PANEL, AND WHERE IT WENT
---------------------------------------
The 2026-08-31 cut ran a pipeline: query -> two representations -> a four-candidate library ->
two ranked stacks that disagreed at rank 1. Every part of it was correct and two parts belonged
elsewhere.

  * The two-route fork became a two-LAYER fork, because "mean route versus population route" is
    exactly the conflation above: it makes the mean route one thing when it is two.
  * The library and the two ranked stacks are gone. A ranking outcome is panel d's job, on a
    construction where the means are equal by design and the tie is therefore provable rather
    than arranged; e draws retrieval as a ranking handed to a judge. Panel a is now definitional,
    and a definition panel that also shows an outcome invites the outcome to be read as evidence.

Nothing here is measured and nothing here is a number: draw_1a asserts that no text it drew
contains a digit, so the panel cannot acquire one.

WHY THE MARKS ARE THE ONES THEY ARE
-----------------------------------
The two representation marks are the figure's own glyphs, taught here and reused unchanged:
fig1_style.centroid for "this population became one vector" and fig1_style.cells for "the
population is still here". The three score rows then carry those SAME two marks at key size,
which is the panel's second sentence made without a word: rows one and two carry the same orange
diamond, so a reader sees one representation feeding two scoring rules before reading either
name. Panel d's verdict rows use the identical grammar, mark then name then consequence.

Colour follows fig1_style. The three information segments take the deck's three RUNG colours,
MEAN orange, MAGNITUDE slate and POP blue, which are the colours Figures 2a and 5b already give
the same three rungs; a reader who learns the ladder here has to find it again there. The two
SCORE rows that read the mean representation are tied together by their MARK instead, the same
orange centroid diamond, which is the stronger statement and the one this panel exists to make.

LAYOUT, FOR A 3.15 x 1.58 IN AXES
---------------------------------
Two bands. The upper band is the representation fork, read left to right; the lower band is the
three scoring rules, read as rows against one shared axis at their foot. Positions are held in
INCHES on the printed page and converted at draw time, because every constraint in this panel is
a collision between a point size and a length. The bar block does not start at a typed x: it
starts past the MEASURED width of the widest score name, so renaming a score moves the bars
instead of printing them over the name.

Run standalone: python3 fig1a.py
"""
from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig1_style import (FAINT, LW_HAIR, MAGNITUDE, MEAN, POP, PT_ANNOT,  # noqa: E402
                        PT_SMALL, PT_TICK, SHARED, TEXT, arrow, blank, cells, centroid,
                        renderer as _renderer, text_w_in as _text_w_in)

# --------------------------------------------------------------------------------- the canvas
# The rect fig1_assemble gives panel a: half of the 6.90 in page less the 0.24 in letter gutter
# and the 0.06 in right margin, by the 1.58 in height of the a/b row. draw_1a asserts it, so a
# change to fig1_assemble.ROWS cannot silently rescale a layout that was tuned in inches.
PANEL_W_IN, PANEL_H_IN = 3.15, 1.58
SIZE_TOL_IN = 0.02


def _fx(x_in):
    return x_in / PANEL_W_IN


def _fy(y_in):
    """Inches from the BOTTOM of the axes to an axes fraction."""
    return y_in / PANEL_H_IN


# ------------------------------------------------------------------ band 1: the representations
# The source population, its two states drawn only so that "population structure" has something
# to refer to further down. It is SHARED grey: both representations are taken from these cells.
SRC_CXY = (0.300, 1.150)
SRC_RX, SRC_RY = 0.150, 0.150
SRC_STATES = ((0.074, +0.076, 3.0, 0.50, 11),   # (ry, dy, marker area, alpha, seed)
              (0.068, -0.076, 3.4, 0.92, 23))
SRC_N = 34                          # per state; enough dots to read as a population at 0.3 in
SRC_LABEL_TOP = 1.560               # va="top", so the two lines hang from a fixed edge

# The two representations, in one column so the fork is one horizontal step and the eye compares
# them without travelling. mu sits above P for no reason except reading order: the paper meets
# the mean representation first, in the literature it inherits.
MU_XY = (0.790, 1.395)
P_XY = (0.790, 0.985)
P_RX, P_RY = 0.088, 0.092
P_N = 26
MARK_LABEL_X = 0.905                # left edge of both representation names
FORK_X0 = 0.480                     # arrow tails, just clear of the source population's rim

# ------------------------------------------------------------------ band 2: the scoring rules
ROW_Y = (0.640, 0.455, 0.270)       # 0.185 in pitch: a 7.2 pt line is 0.10 in, so the rows read
                                    # as three rows and not as a block
HEADER_Y = 0.792                    # the two column names, on one baseline over the block
MARK_X = 0.055                      # the row's representation mark
NAME_X = 0.145                      # the score's name, flush left
NAME_GAP = 0.100                    # widest name -> the axis origin, MEASURED at draw time
BAR_X1 = 3.100                      # the axis ends where the panel's ink ends
BAR_H = 0.072
MARK_PT = 5.4                       # a row mark, a little under the 7.2 pt name beside it

# The information axis, and the one thing about it that is not free: the three segments are equal
# in WIDTH and that width carries no quantity. The axis is ordinal, and the caption says so; an
# unequal split would invite a reader to measure how much magnitude is worth, which is Fig. 2a.
SEG_LABELS = ("direction", "+ magnitude", "+ population\nstructure")
SEG_COLOURS = (MEAN, MAGNITUDE, POP)
TICK_DROP = 0.032                   # segment boundary ticks, below the bottom bar
SEG_LABEL_TOP = 0.198               # va="top" for the segment names
SEG_ALPHA = (0.95, 0.95, 0.95)      # one weight; the rungs are told apart by hue, which is the
                                    # hue Figures 2a and 5b give the same three rungs. That the
                                    # first two rungs come from ONE representation is carried by
                                    # the row MARK, the shared orange diamond, not by the fill.

_DIGITS = set("0123456789")


def _axes_in(ax):
    w, h = ax.get_position().size * ax.figure.get_size_inches()
    return float(w), float(h)


def _named(ax, x_in, y_in, words, sym, rend):
    """``words`` flush left at x, then its italic symbol after a measured word space.

    Two artists rather than one string because the symbol is a variable and a variable is italic.
    They share a gid so figures/check_overlaps.py compares the pair with everything except each
    other: set snug, as one label, their tight boxes touch.
    """
    gid = "sym-%d" % round(y_in * 1e4)
    ax.text(_fx(x_in), _fy(y_in), words, ha="left", va="center", fontsize=PT_ANNOT,
            color=TEXT, gid=gid, zorder=5)
    w = _text_w_in(ax, rend, words + " ", PT_ANNOT)
    ax.text(_fx(x_in + w), _fy(y_in), sym, ha="left", va="center", fontsize=PT_ANNOT,
            color=TEXT, style="italic", gid=gid, zorder=5)
    return x_in + w + _text_w_in(ax, rend, sym, PT_ANNOT, style="italic")


def _source(ax):
    """The single-cell response population both representations are taken from."""
    cx, cy = SRC_CXY
    for ry, dy, s, alpha, seed in SRC_STATES:
        cells(ax, _fx(cx), _fy(cy + dy), SRC_N, _fx(SRC_RX), _fy(ry), color=SHARED,
              rng=np.random.default_rng(seed), s=s, alpha=alpha, zorder=3)
    ax.text(_fx(cx), _fy(SRC_LABEL_TOP), "single-cell\nresponse", ha="center", va="top",
            fontsize=PT_ANNOT, color=TEXT, linespacing=1.15, zorder=5)


def _representations(ax, rend):
    """The fork: one population, two summaries of it, each named beside its own mark."""
    mx, my = MU_XY
    px, py = P_XY
    centroid(ax, _fx(mx), _fy(my), size=34)
    cells(ax, _fx(px), _fy(py), P_N, _fx(P_RX), _fy(P_RY), color=POP,
          rng=np.random.default_rng(41), s=3.2, alpha=0.85, zorder=3)

    # One tail, two heads: the two representations are alternatives taken from the same cells,
    # not two stages of one pipeline.
    for x1, y1 in ((mx - 0.055, my), (px - 0.052, py)):
        arrow(ax, (_fx(FORK_X0), _fy(SRC_CXY[1])), (_fx(x1), _fy(y1)), color=SHARED,
              connectionstyle="arc3,rad=0.0")

    _named(ax, MARK_LABEL_X, my, "mean representation", "μ", rend)
    _named(ax, MARK_LABEL_X, py, "population representation", "P", rend)


def _row_mark(ax, x_in, y_in, colour):
    """What the row's score reads: the collapsed one-vector diamond, or the cells themselves.

    The same two glyphs as the band above, at key size. Rows one and two get the SAME mark on
    purpose: one representation, two scoring rules, which is the panel's whole correction.
    """
    if colour is MEAN:
        centroid(ax, _fx(x_in), _fy(y_in), color=MEAN, size=MARK_PT ** 2)
    else:
        r = MARK_PT / 2.0 / 72.0
        cells(ax, _fx(x_in), _fy(y_in), 11, _fx(r), _fy(r), color=POP,
              rng=np.random.default_rng(5), s=2.6, alpha=0.95, zorder=5)


def _scores(ax, rend):
    """Three scoring rules as three reaches along one shared information axis."""
    # The three names carry no "score", because the column they sit in is headed with the word
    # once. Set in full they measure 1.37 in at 7.2 pt, which leaves the information axis 1.49 in
    # for three segments and puts "+ magnitude" (0.51 in) through its neighbours.
    names = ("directional mean", "magnitude-aware mean", "population")
    marks = (MEAN, MEAN, POP)

    widest = max(_text_w_in(ax, rend, s, PT_ANNOT) for s in names)
    bar_x0 = NAME_X + widest + NAME_GAP
    span = BAR_X1 - bar_x0
    assert span > 1.30, (
        f"the score names now leave only {span:.2f} in for the information axis, which cannot "
        f"carry three labelled segments; shorten a name rather than shrinking the axis.")
    seg = span / len(SEG_LABELS)
    edges = [bar_x0 + i * seg for i in range(len(SEG_LABELS) + 1)]

    # Two column names, on one baseline, at the size panel f gives its own columns. They are what
    # keeps the two layers apart in one reading: the left column is the SCORING RULE, the right
    # one is the information that rule retains, and neither is the representation drawn above.
    ax.text(_fx(NAME_X), _fy(HEADER_Y), "scoring rule", ha="left", va="baseline",
            fontsize=PT_TICK, color=TEXT, zorder=5)
    ax.text(_fx((bar_x0 + BAR_X1) / 2.0), _fy(HEADER_Y), "information retained", ha="center",
            va="baseline", fontsize=PT_TICK, color=TEXT, zorder=5)

    reach = []
    for y, name, mark, n_seg in zip(ROW_Y, names, marks, (1, 2, 3)):
        _row_mark(ax, MARK_X, y, mark)
        ax.text(_fx(NAME_X), _fy(y), name, ha="left", va="center", fontsize=PT_ANNOT,
                color=TEXT, zorder=5)
        for i in range(n_seg):
            ax.add_patch(plt_rect(_fx(edges[i]), _fy(y - BAR_H / 2), _fx(seg), _fy(BAR_H),
                                  SEG_COLOURS[i], SEG_ALPHA[i]))
        # A white hairline at every interior boundary, so the segments are countable rather than
        # inferred from two shades.
        for i in range(1, n_seg):
            ax.plot([_fx(edges[i])] * 2, [_fy(y - BAR_H / 2), _fy(y + BAR_H / 2)],
                    color="white", lw=0.7, zorder=5, solid_capstyle="butt")
        reach.append(edges[n_seg])
    # The nesting is the panel's claim, so it is asserted on the drawn geometry rather than left
    # to the three integers above: each score must reach strictly further than the one before it,
    # and the last must reach the end of the axis.
    assert reach[0] < reach[1] < reach[2], (
        f"the three scores no longer reach in increasing order ({reach}); the panel draws a "
        f"containment and this is what makes it one.")
    assert abs(reach[-1] - BAR_X1) < 1e-9

    # ---- the axis itself, under the bottom bar ----
    y0 = ROW_Y[-1] - BAR_H / 2
    for x in edges:
        ax.plot([_fx(x)] * 2, [_fy(y0), _fy(y0 - TICK_DROP)], color=FAINT, lw=LW_HAIR,
                zorder=2, solid_capstyle="butt")
    for i, label in enumerate(SEG_LABELS):
        ax.text(_fx((edges[i] + edges[i + 1]) / 2.0), _fy(SEG_LABEL_TOP), label,
                ha="center", va="top", fontsize=PT_SMALL, color=TEXT, linespacing=1.15,
                zorder=5)
    return edges


def plt_rect(x, y, w, h, colour, alpha):
    from matplotlib.patches import Rectangle
    return Rectangle((x, y), w, h, fc=colour, ec="none", alpha=alpha, zorder=4)


def draw_1a(ax):
    """Draw panel a into ``ax``. The axes is 3.15 x 1.58 in in the composite."""
    w_in, h_in = _axes_in(ax)
    assert abs(w_in - PANEL_W_IN) < SIZE_TOL_IN and abs(h_in - PANEL_H_IN) < SIZE_TOL_IN, (
        f"panel a is laid out in inches for a {PANEL_W_IN} x {PANEL_H_IN} in axes and was handed "
        f"{w_in:.2f} x {h_in:.2f} in; retune the constants or restore the rect.")
    blank(ax)
    rend = _renderer(ax)

    _source(ax)
    _representations(ax, rend)
    _scores(ax, rend)

    # A definition panel states no quantity. This is the mechanical form of that rule: the panel
    # cannot acquire a number without the build failing, which is what stops a later edit from
    # printing a Hit@1 or a gain here where it could not be qualified.
    numeric = [str(t.get_text()) for t in ax.texts
               if set(str(t.get_text())) & _DIGITS]
    assert not numeric, (
        f"panel a is definitional and prints no number; found {numeric}. A measured value "
        f"belongs in Figure 2, where it can be given its n and its interval.")
    return ax


if __name__ == "__main__":
    import re

    import matplotlib
    matplotlib.use("agg")
    import matplotlib.pyplot as plt
    import matplotlib.text as mtext

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from figstyle import apply_style  # noqa: E402
    from fig1_style import PT_FLOOR, PT_TITLE  # noqa: E402

    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))
    fig = plt.figure(figsize=(PANEL_W_IN, PANEL_H_IN))
    ax = fig.add_axes([0.0, 0.0, 1.0, 1.0])
    draw_1a(ax)
    fig.canvas.draw()
    r = fig.canvas.get_renderer()

    subsup = re.compile(r"\$[^$]*[\^_][^$]*\$")
    sizes = sorted((t.get_fontsize() * (0.7 if subsup.search(str(t.get_text())) else 1.0),
                    str(t.get_text()).replace("\n", "/"))
                   for t in fig.findobj(mtext.Text)
                   if str(t.get_text()).strip() and t.get_visible())
    assert sizes[0][0] >= PT_FLOOR - 1e-6, f"below the {PT_FLOOR} pt floor: {sizes[:4]}"
    print(f"smallest effective size: {sizes[0][0]:.2f} pt  ({sizes[0][1]})")

    # Nothing may leave the axes: text and clip_on=False artists do not clip, so an overhang
    # here would widen the assembled page (figstyle.pin_canvas).
    box, hang = ax.bbox, []
    skip = set(ax.spines.values()) | {ax.patch, ax.xaxis, ax.yaxis}
    for a in ax.get_children():
        if not a.get_visible() or a in skip:
            continue
        bb = a.get_tightbbox(r)
        if bb is None:
            continue
        over = [(box.x0 - bb.x0), (bb.x1 - box.x1), (box.y0 - bb.y0), (bb.y1 - box.y1)]
        over = [o * 72.0 / fig.dpi for o in over]
        if max(over) > 0.25:
            label = getattr(a, "get_text", lambda: type(a).__name__)() or type(a).__name__
            hang.append((str(label).replace("\n", "/")[:34], [round(o, 2) for o in over]))
    for label, over in hang:
        print(f"  hangs out [left, right, bottom, top] pt: {over}  {label}")
    assert not hang, "artists leave the axes; see above"

    boxes = [(str(t.get_text()).replace("\n", "/")[:24], t.get_window_extent(r), t.get_gid())
             for t in ax.findobj(mtext.Text) if str(t.get_text()).strip() and t.get_visible()]
    pad = 0.4 * fig.dpi / 72.0
    hits = []
    for i, (li, bi, gi) in enumerate(boxes):
        for lj, bj, gj in boxes[i + 1:]:
            if gi is not None and gi == gj:
                continue
            if (bi.x0 < bj.x1 - pad and bj.x0 < bi.x1 - pad
                    and bi.y0 < bj.y1 - pad and bj.y0 < bi.y1 - pad):
                hits.append((li, lj))
    for a, b in hits:
        print(f"  labels overlap: {a!r} / {b!r}")
    assert not hits, "labels overlap; see above"
    print("every artist inside the axes, and no two labels overlap")

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "1a.png")
    fig.savefig(out, dpi=400)
    print(f"wrote {out}")
