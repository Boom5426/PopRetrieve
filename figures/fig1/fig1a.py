"""PopRetrieve Figure 1, panel a: what a response is represented by, and what a score reads off it.

WHAT THIS PANEL HAS TO SAY
--------------------------
Two layers, and the whole panel exists to keep them apart:

    REPRESENTATION   what survives the summary of a single-cell response population
                     mean representation mu, or the population P itself
    SCORING RULE     what a score then reads off that representation

They are not the same layer, and conflating them is the error this panel was written to remove.
A mean representation is NOT direction-only: mu carries a direction and a magnitude. It is the
COSINE that discards the magnitude. So one representation, mu, supports two scoring rules, and
the figure's vocabulary is fixed here for the rest of the paper:

    direction-only mean cosine     cos(mu_Q, mu_d)          reads direction
    magnitude-aware mean (L2)      -||mu_Q - mu_d||         reads direction and magnitude
    population distance            -D(P_Q, P_d)             reads the distribution as well

The information those three read is NESTED, not parallel, and the drawing has to say so.

THE 2026-09-06 CUT: A THREE-COLUMN READING, AND WHY THE MATRIX REPLACED THE BARS
--------------------------------------------------------------------------------
Until now the retained information was three bars of increasing length on one shared ordinal
axis. That drew the containment well and had one cost: the three THINGS being retained were
named only under the axis, as segment labels, so "direction", "magnitude" and "population
structure" read as parts of a quantity rather than as three separate properties a rule either
keeps or drops. Two readers took the segment widths for effect sizes, which is the one reading
the axis cannot support and the caption had to deny in a clause.

The panel now reads left to right in three columns, which is the order the sentence goes in:

    SOURCE       one single-cell response population, in SHARED grey, drawn with two visible
                 states so that "population structure" has something to point at
    RULE         the three scoring rules, each with the geometry it actually reads: a unit
                 arrow on a faint unit circle (orientation only), the same arrow at its true
                 length (orientation and size), and the cells with their centroid
    RETAINED     a three-column matrix, filled disc for retained and open ring for discarded

The matrix keeps the containment, because a filled cell is never followed by an open one to its
left, and it gains what the bars could not state: the three properties are NAMED as properties,
at the head of their own columns, and a discarded property is drawn rather than left absent.
The dot is the deck's rung colour, so a reader who learns the ladder here finds the same three
hues on Figure 2a and Figure 5b.

WHAT IS DELIBERATELY NOT DRAWN
------------------------------
No normalised mean vector mu-hat. A reference layout for this panel carried the three rows as a
"hierarchy of response REPRESENTATIONS", with mu/||mu|| as the first of them. The paper defines
no such representation: it has two, mu and P, and the normalisation lives inside the cosine.
Drawing it as a third would reintroduce exactly the conflation named above, and would contradict
the Results, which call these three the scoring rules of Fig. 1a.

No magnitude colour ramp on the source cells. A blue-to-orange ramp reads as response size in
isolation and as POP-to-MEAN inside this figure, where those two hues are frozen roles. Cell-to-
cell heterogeneity is carried by drawing two states in one grey instead, which is what the third
matrix column needs to refer to.

Nothing here is measured and nothing here is a number: draw_1a asserts that no text it drew
contains a digit, so the panel cannot acquire one.

LAYOUT, FOR A 3.15 x 1.58 IN AXES
---------------------------------
Positions are held in INCHES on the printed page and converted at draw time, because every
constraint in this panel is a collision between a point size and a length. Neither the rule
column nor the matrix starts at a typed x: the rule names are MEASURED and the matrix is placed
after the widest of them, so renaming a rule moves the columns instead of printing over them.

Run standalone: python3 fig1a.py
"""
from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from matplotlib.patches import FancyArrowPatch  # noqa: E402
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


# ---------------------------------------------------------------------- column 1: the source
SRC_CXY = (0.255, 0.735)
SRC_RX = 0.138
SRC_STATES = ((0.068, +0.088, 3.0, 0.34, 11),   # (ry, dy, marker area, alpha, seed)
              (0.064, -0.088, 3.6, 1.00, 23))
SRC_N = 30                          # per state; enough dots to read as a population at 0.3 in
SRC_LABEL_TOP = 1.255               # va="top", so the two lines hang from a fixed edge
FORK_X0 = 0.415                     # arrow tails, just clear of the source population's rim
FORK_X1 = 0.548                     # arrow heads, at the left edge of the rule column

# ---------------------------------------------------------------------- column 2: the rules
ROW_Y = (1.070, 0.700, 0.330)       # 0.370 in pitch: two 7.2 pt lines are 0.21 in, so the rows
                                    # read as three rows and not as a block
NAME_X = 0.600                      # rule names, flush left
GLYPH_GAP = 0.075                   # widest name -> the geometry glyph, MEASURED at draw time
GLYPH_W = 0.260                     # the geometry each rule reads
GLYPH_GAP_R = 0.090                 # geometry glyph -> the first matrix column

# The unit circle behind the first rule's arrow. It is the one mark that says the cosine threw
# a length away, rather than never having had one, and it is FAINT because it is a construction
# line: the reader should see the arrow stop on it, not stop on the circle.
GLYPH_R = 0.104                     # the unit radius, and rule 1's whole arrow length
GLYPH_LONG = 1.62                   # rule 2's arrow, as a multiple of GLYPH_R
GLYPH_ANG = 38.0                    # degrees, the shared orientation of both arrows
TAIL_DX, TAIL_DY = -0.040, -0.032   # both arrows leave one tail, left of centre
GLYPH_MARK = 9                      # one diamond size across all three glyphs
GLYPH_CLOUD_R = 0.088               # rule 3's population, in place of an arrow

# ---------------------------------------------------------------------- column 3: what is kept
# The three properties, named as properties. Equal columns, and the columns carry no quantity:
# a filled disc means the rule retains that property and an open ring means it discards it.
PROPS = ("direction", "magnitude", "distribution")
PROP_COLOURS = (MEAN, MAGNITUDE, POP)
KEPT = ((True, False, False),       # direction-only mean cosine
        (True, True, False),        # magnitude-aware mean L2
        (True, True, True))         # population distance
MATRIX_X1 = 3.140                   # the matrix ends where the panel's ink ends
HEADER_TOP = 1.480                  # va="top" for the property names
RULE_Y = 1.320                      # the hairline under the property names
DISC_PT = 5.2                       # marker size for a retained property
RING_PT = 4.8                       # and for a discarded one, a shade smaller so the filled
                                    # discs carry the row without the rings competing
BAND_X0 = 0.560                     # the row bands start clear of the fork arrowheads
BAND_H = 0.290                      # under the 0.370 row pitch, so the rows stay three rows
BAND_ALPHA = 0.085                  # a tint, not a fill: the dots and glyphs carry the row
ARROW_Y = 0.150                     # the less-to-more information arrow, under the matrix
ARROW_LABEL_TOP = 0.112

_DIGITS = set("0123456789")


def _axes_in(ax):
    w, h = ax.get_position().size * ax.figure.get_size_inches()
    return float(w), float(h)


def _bands(ax):
    """One faint band per rule, in that rule's rung colour, from the name to the panel edge.

    The panel is 3.15 in wide and a reader has to carry a rule name across all of it to its own
    three dots. Without the band the matrix reads as a separate object that happens to have
    three rows. The tint is the rung the row REACHES, which is the colour Figures 2a and 5b give
    the same three rungs, and it is set low enough that it never competes with the marks.
    """
    from matplotlib.patches import Rectangle
    for y, colour in zip(ROW_Y, (MEAN, MAGNITUDE, POP)):
        ax.add_patch(Rectangle((_fx(BAND_X0), _fy(y - BAND_H / 2.0)),
                               _fx(MATRIX_X1 - BAND_X0), _fy(BAND_H),
                               fc=colour, ec="none", alpha=BAND_ALPHA, zorder=1))


def _source(ax):
    """The single-cell response population all three rules are computed from.

    SHARED grey, because every rule takes its input from these cells; the two states are what
    the third property, population structure, refers to.
    """
    cx, cy = SRC_CXY
    for ry, dy, s, alpha, seed in SRC_STATES:
        cells(ax, _fx(cx), _fy(cy + dy), SRC_N, _fx(SRC_RX), _fy(ry), color=SHARED,
              rng=np.random.default_rng(seed), s=s, alpha=alpha, zorder=3)
    ax.text(_fx(cx), _fy(SRC_LABEL_TOP), "single-cell\nresponse", ha="center", va="top",
            fontsize=PT_ANNOT, color=TEXT, linespacing=1.15, zorder=5)


def _fork(ax):
    """One tail, three heads: the rules are alternatives on one population, not three stages."""
    for y in ROW_Y:
        arrow(ax, (_fx(FORK_X0), _fy(SRC_CXY[1])), (_fx(FORK_X1), _fy(y)), color=SHARED,
              connectionstyle="arc3,rad=0.0")


def _vec(ax, p0, p1, colour):
    """A vector that ends exactly where it is told to, unlike fig1_style.arrow.

    FancyArrowPatch defaults to shrinkA = shrinkB = 2 points, and 2 points is 0.028 in: on the
    0.104 in unit vector below that removes 54% of the arrow and stops it well inside the circle
    it is drawn to touch. The flow arrows everywhere else in this figure are ten times longer and
    WANT the standoff, so the shared helper keeps it and this one vector type opts out.
    """
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=4.5, lw=1.0,
                                 color=colour, zorder=4, shrinkA=0, shrinkB=0))


def _glyph(ax, kind, cx_in, cy_in):
    """The geometry each rule actually reads, at 0.30 x 0.26 in.

    ``unit``   an arrow that stops on a faint unit circle: the orientation is read and the
               length is not, which is the cosine.
    ``vector`` the same orientation at its true length: direction and magnitude, the mean L2.
    ``cloud``  the cells with their centroid still on them: the population distance.
    """
    # Rows one and two draw the SAME orange centroid at the arrow's tail, which is the
    # correction this panel exists to make: one representation, two scoring rules. It used to be
    # a separate mark in its own column between the fork and the name; folded into the glyph it
    # says the same thing beside the geometry it belongs to, and gives the matrix 0.15 in it
    # could not otherwise have had for three named columns.
    ang = np.deg2rad(GLYPH_ANG)
    if kind == "cloud":
        cells(ax, _fx(cx_in), _fy(cy_in), 24, _fx(GLYPH_CLOUD_R), _fy(GLYPH_CLOUD_R * 0.80),
              color=POP, rng=np.random.default_rng(17), s=2.6, alpha=0.85, zorder=4)
        centroid(ax, _fx(cx_in), _fy(cy_in), color=MEAN, size=GLYPH_MARK)
        return
    # Both arrows leave the SAME tail, and the circle is centred on that tail rather than on
    # the box, so "the arrow stops on the unit circle" is literally what is drawn. The first cut
    # centred the circle on the box and started the arrow at its rim, which drew the arrow
    # running inward to the centre: the opposite of the statement.
    x0, y0 = cx_in + TAIL_DX, cy_in + TAIL_DY
    if kind == "unit":
        th = np.linspace(0, 2 * np.pi, 96)
        ax.plot(_fx(x0 + GLYPH_R * np.cos(th)), _fy(y0 + GLYPH_R * np.sin(th)),
                color=FAINT, lw=LW_HAIR, zorder=2)
        length, colour = GLYPH_R, MEAN
    else:
        length, colour = GLYPH_R * GLYPH_LONG, MAGNITUDE
    _vec(ax, (_fx(x0), _fy(y0)),
         (_fx(x0 + length * np.cos(ang)), _fy(y0 + length * np.sin(ang))), colour)
    # The tail diamond is deliberately small. At size 12 it covered the first third of the unit
    # arrow's shaft, so the row that is ABOUT length was the row whose length could not be seen.
    centroid(ax, _fx(x0), _fy(y0), color=MEAN, size=GLYPH_MARK)


def _rules(ax, rend):
    """The three scoring rules, each beside the geometry it reads."""
    # Set on two lines: at 7.2 pt "magnitude-aware mean" measures 0.83 in on one, which leaves
    # the matrix 1.3 in for three named columns and puts "population structure" through its
    # neighbour. The L2 suffix the Results use is dropped rather than set here, because draw_1a
    # forbids a digit on this panel and "mean L2" carries one; the caption names the norm.
    names = ("direction-only\nmean cosine", "magnitude-\naware mean",
             "population\ndistance")
    kinds = ("unit", "vector", "cloud")

    widest = max(_text_w_in(ax, rend, line, PT_ANNOT)
                 for s in names for line in s.split("\n"))
    glyph_x = NAME_X + widest + GLYPH_GAP
    for y, name, kind in zip(ROW_Y, names, kinds):
        ax.text(_fx(NAME_X), _fy(y), name, ha="left", va="center", fontsize=PT_ANNOT,
                color=TEXT, linespacing=1.16, zorder=5)
        _glyph(ax, kind, glyph_x + GLYPH_W / 2.0, y)
    return glyph_x + GLYPH_W + GLYPH_GAP_R


def _matrix(ax, x0_in):
    """Three properties as three columns, retained or discarded, one row per rule."""
    span = MATRIX_X1 - x0_in
    assert span > 1.10, (
        f"the rule names now leave only {span:.2f} in for the retained-information matrix, "
        f"which cannot carry three named columns; shorten a rule name rather than shrinking "
        f"the columns.")
    col_w = span / len(PROPS)
    centres = [x0_in + (i + 0.5) * col_w for i in range(len(PROPS))]

    for cx, prop in zip(centres, PROPS):
        ax.text(_fx(cx), _fy(HEADER_TOP), prop, ha="center", va="top", fontsize=PT_SMALL,
                color=TEXT, linespacing=1.15, zorder=5)
    ax.plot([_fx(x0_in), _fx(MATRIX_X1)], [_fy(RULE_Y)] * 2, color=FAINT, lw=LW_HAIR,
            zorder=2, solid_capstyle="butt")

    for y, row in zip(ROW_Y, KEPT):
        for cx, colour, kept in zip(centres, PROP_COLOURS, row):
            if kept:
                ax.scatter([_fx(cx)], [_fy(y)], s=DISC_PT ** 2, c=colour, lw=0, zorder=5)
            else:
                ax.scatter([_fx(cx)], [_fy(y)], s=RING_PT ** 2, facecolors="none",
                           edgecolors=FAINT, lw=0.8, zorder=5)

    # The containment is the panel's claim, so it is asserted on the drawn matrix rather than
    # left to the three tuples above: no rule may retain a property that a rule below it drops,
    # and each row must retain strictly more than the one before it.
    counts = [sum(r) for r in KEPT]
    assert counts[0] < counts[1] < counts[2] == len(PROPS), (
        f"the three rules no longer retain in increasing order ({counts}); the panel draws a "
        f"containment and this is what makes it one.")
    for upper, lower in zip(KEPT, KEPT[1:]):
        assert all(l or not u for u, l in zip(upper, lower)), (
            "a rule discards a property that a weaker rule retains; the ladder is not nested.")

    # ---- less to more, under the matrix ----
    arrow(ax, (_fx(x0_in + 0.16), _fy(ARROW_Y)), (_fx(MATRIX_X1 - 0.16), _fy(ARROW_Y)),
          color=FAINT, lw=LW_HAIR, ms=6)
    ax.text(_fx(x0_in), _fy(ARROW_LABEL_TOP), "less", ha="left", va="top",
            fontsize=PT_SMALL, color=TEXT, zorder=5)
    ax.text(_fx(MATRIX_X1), _fy(ARROW_LABEL_TOP), "more", ha="right", va="top",
            fontsize=PT_SMALL, color=TEXT, zorder=5)


def draw_1a(ax):
    """Draw panel a into ``ax``. The axes is 3.15 x 1.58 in in the composite."""
    w_in, h_in = _axes_in(ax)
    assert abs(w_in - PANEL_W_IN) < SIZE_TOL_IN and abs(h_in - PANEL_H_IN) < SIZE_TOL_IN, (
        f"panel a is laid out in inches for a {PANEL_W_IN} x {PANEL_H_IN} in axes and was handed "
        f"{w_in:.2f} x {h_in:.2f} in; retune the constants or restore the rect.")
    blank(ax)
    rend = _renderer(ax)

    _bands(ax)
    _source(ax)
    _fork(ax)
    _matrix(ax, _rules(ax, rend))

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
