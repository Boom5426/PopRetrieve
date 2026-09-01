"""PopRetrieve Figure 1 panel c: what changes mathematically between the two scores.

Panel b says WHY averaging can fail. Panel c says what is actually COMPUTED, on one pair of
populations, at two resolutions. Panel d then says what that does to a ranking, and reuses this
panel's cloud vocabulary, because d is this panel's consequence.

THE DRAWING IS THE ARGUMENT
---------------------------
The panel is two rows over the SAME two populations, and the only thing that differs is the route
from one population to the other:

    mean route        each cloud collapses DOWN onto a centroid, and the comparison is one line
                      between the two centroids: the route detours below the data and back up
    population route  nothing collapses and nothing detours: the comparison is drawn between the
                      cells themselves, straight across, at the level they already sit at

One row detours through two points, the other goes straight across at the level of the cells. That
contrast is the whole panel and it survives every formula being deleted, which is the test this
panel is built to pass. The previous cut stated the same thing in a a collapse label, two
link labels, two display equations and a four-name family line, and the drawing underneath was
doing almost none of the work.

Three constructions carry the meaning, and each replaces a sentence:

  * BOTH POPULATIONS STAY WHOLE IN THE MEAN ROW. The centroid is produced BY the collapse; the
    cells are not deleted by it. Row 1 and row 2 are the same four clouds, at the same centres,
    from the same two generators, so a reader can see that the data is identical and only its
    representation differs. That identity is guaranteed by construction (one _row call per row,
    same seeds) rather than by two tuned constants that happen to agree.
  * THE LINK CARRIES ITS OWN RESOLUTION. One drawing routine draws both links, and each row hands
    it what its own comparison is made of: the mean route hands it ONE segment, between two
    centroids, because that is what a cosine of two vectors is; the population route hands it one
    segment per pair of facing cells, because a distributional distance consumes the whole
    population. One line against a sheaf of them is the two equations, made without letters.
  * THE COLLAPSE IS DRAWN, NOT NAMED. Two arrows leave the two clouds and land on two diamonds;
    fig1_style.centroid draws that diamond wherever in this figure a population has become one
    vector, so the glyph is taught before a reader arrives here. The word "collapse" is therefore
    gone, and the labels that remain, mu_Q and mu_d, name the two objects the equation at the
    foot of the panel compares.

WHY THE TYPE SITS WHERE IT DOES
-------------------------------
The two equations are a reference, not the subject, so they sit at the foot of the panel below
everything that is drawn, at PT_ANNOT, each behind the mark of the route it belongs to: the MEAN
diamond and a POP cell cluster, the same two marks panel d uses for its verdict rows. The marks
are what bind an equation to a row, which is why neither line needs a word of prose to say which
route it states. The score family is quieter still, at PT_SMALL in SUBTLE, introduced as examples
of D so that it reads as a gloss on the D above it rather than as a fifth claim.

Nothing on this panel is mathtext. fig1_style.PT_EQ exists because matplotlib renders a mathtext
sub/superscript at 0.7x nominal, so "$s_\\mathrm{mean}$" has to be set at 9.3 pt for its subscript
to clear this figure's 6.5 pt floor; a 9.3 pt equation would be the largest type on a panel whose
equations are deliberately the smallest thing on it. The runs below are composed instead: every
base glyph is an ordinary Text at PT_ANNOT and every subscript is its own Text at PT_SMALL, the
floor itself. No glyph was shrunk to fit, nothing prints below 6.5 pt, and Arial carries the
italic mu and the true minus sign, so the composed run needs no maths font at all.

Nothing here is measured, and no candidate library or ranking is drawn: panel a already carries
the pipeline end to end. c is the operator alone. The caption carries what the panel no longer
states: that both rows show the same query Q and the same candidate population P_d.

Run standalone: python3 fig1c.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.textpath import TextToPath

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig1_style import (LW_ARROW, LW_HAIR, LW_LINE, MEAN, MS_ARROW,  # noqa: E402
                        POP, PT_ANNOT, PT_SMALL, SHARED, SUBTLE, TEXT,
                        arrow, blank, cells, centroid)

# The axes this panel is authored for, in inches: fig1_assemble gives every schematic panel of the
# four-rows-of-two layout half the 6.90 in canvas less the letter gutter and the right margin, by
# the 1.60 in row height. The layout below is written in POINTS measured from the top-left corner
# of that axes, because a schematic tuned in axes fractions restyles itself at any other aspect
# ratio, and this panel went from 1.24 x 3.00 in portrait to 3.15 x 1.60 in landscape.
PANEL_W_IN, PANEL_H_IN = 3.15, 1.60

# ---------------------------------------------------------------------------------- geometry
# Columns are placed as centre +/- COL_OFF rather than as two absolute x, so the row is mirrored
# about the axes centre by construction and stays mirrored if the panel is ever re-sized.
COL_OFF = 64.0              # pt from the axes centre to each cloud centre. Wide, because the gap
                            # is where the two routes differ: a link label and its padding take
                            # 41 pt out of the 105 pt between the rims, and what is left still has
                            # to read as a link made of many lines rather than as two fringes.
R_CLOUD = 11.0              # query cloud radius in pt, equal in x and y: the clouds print round
N_CELLS = 48                # matches panel d's cells-per-blob, so both panels read as one tissue
# The candidate is a different population, not a copy of the query, so it is drawn wider and
# flatter. What has to match is row against row, which the shared seeds below guarantee; two
# identical clouds would say the query and the candidate are the same object.
CAND_RX, CAND_RY = 1.12, 0.85
# Seeds chosen by search over 1..3000 on two criteria, both measured on the cells actually drawn:
# the sample mean lands within 0.04 pt of the cloud centre under BOTH shapes, so the collapse
# arrow drops through the middle of the cloud it came from and the two rows stay mirrored to well
# under a printed point; and the largest empty disk inside the cloud is the smallest available,
# which is what stops a schematic population reading as two clumps with a hole between them.
SEED_Q, SEED_D = 2187, 554
MEAN_TOL_PT = 0.10          # the mirror is asserted, not assumed; see draw_1c
# One cell glyph, panel d's, for all four clouds. Drawing the mean route's cells lighter, on the
# argument that the route is about to discard them, was tried and reverted: it makes the top row
# look like a faded copy of the bottom one, and the claim this panel rests on is that the two rows
# ARE the same cells. Identical glyph, identical coordinates, and colour alone carries the role.
CELL = dict(s=3.2, alpha=0.85)

# Baselines and centres, pt from the top of a 115.2 pt tall axes. The drawing owns 4 to 78 and the
# reference block 87 to 112, so two thirds of the panel is the thing that has to be seen.
CY_MEAN = 15.0              # row 1, the two populations of the mean route
ARR_TOP, ARR_BOT = 26.5, 36.3   # the collapse: cloud rim down onto the diamond, shaft visible
# The centroids sit 10.6 pt under the clouds they came from, joined to them by the collapse arrow,
# and 11.7 pt above the next row, so they group upward with their own populations rather than
# reading as a third row. Row 2 in turn sits 11.7 pt below row 1 and 9.3 pt above the reference
# block, which is what keeps it a row of the drawing rather than a heading for the equations.
CENT_CY = 39.5              # row 1, the two centroids the mean route actually compares
CY_POP = 67.0               # row 2, the same two populations, compared as populations
EQ_MEAN_B, EQ_POP_B = 92.5, 102.0   # one equation per row, in row order
FAM_B = 111.0               # the score family, a gloss on the D one line above it

MARK_HALF = 3.0             # half the diagonal of the centroid diamond, whose area is 34 pt^2
LABEL_GAP = 4.0             # diamond edge -> its mu label
LINK_PAD = 3.5              # link line -> the label it makes way for
LABEL_HALF = 0.36 * PT_ANNOT  # half the cap height of a link label, which is the height of the
                            # rectangle the link has to leave clear; "cosine" and "distance D"
                            # carry no descender, so the box is symmetric about the link
N_LEAD = 7                  # cells per rim that the population link leaves from; see _rim
LEAD_ALPHA = 0.55           # a link line is lighter than any cell it joins
CAP_MID = 0.28              # baseline offset, in units of nominal size, that centres a mixed run
                            # of caps and x-height glyphs on a line. A run of two type sizes has
                            # no single box, so it is placed by baseline and centred by metric.
SUB_DROP = 0.20             # subscript baseline drop, as a fraction of the base size
MARK_PT = 5.4               # width of a reference-block route mark, as in panel d's verdict rows
TEXT_X = 11.0               # left edge of the reference block's type, clear of its marks

# Fragment kinds for a composed run: a variable is italic, an operator or a function name is
# upright, and either can be a subscript. This is the ordinary typography of a formula, and it is
# the reason the runs are composed from fragments rather than set as one string.
VAR, OP, VSUB, TSUB = "var", "op", "vsub", "tsub"

EQ_MEAN = [("s", VAR), ("mean", TSUB), ("(", OP), ("d", VAR), (", ", OP), ("Q", VAR),
           (") = cos(", OP), ("μ", VAR), ("Q", VSUB), (", ", OP), ("μ", VAR),
           ("d", VSUB), (")", OP)]
EQ_POP = [("s", VAR), ("pop", TSUB), ("(", OP), ("d", VAR), (", ", OP), ("Q", VAR),
          (") = −", OP), ("D", VAR), ("(", OP), ("P", VAR), ("d", VSUB), (", ", OP),
          ("Q", VAR), (")", OP)]
FAMILY = [("examples of ", OP), ("D", VAR),
          (": energy, MMD, Wasserstein, coverage", OP)]
LINK_MEAN = [("cosine", OP)]
LINK_POP = [("distance ", OP), ("D", VAR)]

_T2P = TextToPath()


def _width(text, size, style):
    """Advance width of one fragment in points, measured without a renderer.

    TextToPath reads the font metrics directly, so a run can be laid out at draw time on any
    backend and before the first draw. Hard-coding fragment positions instead is correct for
    exactly one axes width and one font, and silently overlaps when either changes. The family is
    left as the deck's "sans-serif" alias so the measurement tracks figstyle's font stack.
    """
    prop = FontProperties(family=["sans-serif"], size=size, style=style)
    return _T2P.get_text_width_height_descent(text, prop, False)[0]


class _Grid:
    """Point addressing for one axes, plus the composed-subscript text run.

    Everything is placed on baselines rather than on box edges: a label positioned by its box top
    moves when its string gains or loses a descender.
    """

    def __init__(self, ax):
        w_in, h_in = ax.figure.get_size_inches()
        box = ax.get_position()
        self.ax = ax
        self.w = box.width * w_in * 72.0
        self.h = box.height * h_in * 72.0

    def x(self, pt):
        """A point measurement to an axes fraction across. Also scales an x radius: no offset."""
        return pt / self.w

    def y(self, pt):
        """A point measurement DOWN FROM THE TOP to an axes fraction up from the bottom."""
        return 1.0 - pt / self.h

    def run(self, x_pt, base_pt, frags, size=PT_ANNOT, sub=PT_SMALL, color=TEXT, ha="left"):
        """Draw ``frags`` left to right on the baseline ``base_pt``; return the width in points."""
        spec = {VAR: (size, "italic", 0.0), OP: (size, "normal", 0.0),
                VSUB: (sub, "italic", SUB_DROP * size), TSUB: (sub, "normal", SUB_DROP * size)}
        parts = [(t,) + spec[kind] for t, kind in frags]
        widths = [_width(t, s, st) for t, s, st, _ in parts]
        total = sum(widths)
        x = x_pt - total / 2.0 if ha == "center" else (x_pt - total if ha == "right" else x_pt)
        # One gid for the whole run, matching fig1a's convention: a composed subscript is TUCKED
        # against its base on purpose, exactly where mathtext would put it, and a QA sweep that
        # compares Text bboxes pairwise has to be able to tell that from a real collision.
        gid = "run-%d-%d" % (round(x_pt * 1e3), round(base_pt * 1e3))
        for (t, s, st, drop), w in zip(parts, widths):
            self.ax.text(self.x(x), self.y(base_pt + drop), t, fontsize=s, color=color,
                         ha="left", va="baseline", style=st, gid=gid)
            x += w
        return total

    def on_line(self, x_pt, y_pt, frags, size=PT_ANNOT, color=TEXT):
        """A label centred on a horizontal link at ``y_pt``. Returns its width in points."""
        return self.run(x_pt, y_pt + CAP_MID * size, frags, size=size, color=color, ha="center")


def _cloud(ax, g, cx_pt, cy_pt, seed, color, glyph, fx=1.0, fy=1.0):
    """One population, drawn identically in both rows: same seed, same n, same radii.

    Returns the cells in points from the top-left, like every other number in this module, so a
    caller can hang a collapse arrow on the sample mean or a link on the cells at the rim.
    """
    x, y = cells(ax, g.x(cx_pt), g.y(cy_pt), N_CELLS, g.x(R_CLOUD * fx), R_CLOUD * fy / g.h,
                 color=color, rng=np.random.default_rng(seed), **glyph)
    return x * g.w, (1.0 - y) * g.h


def _row(ax, g, cy_pt, color, glyph):
    """The two populations of one row. Both rows call this, which is what makes them one pair."""
    cx = g.w / 2.0
    return (_cloud(ax, g, cx - COL_OFF, cy_pt, SEED_Q, color, glyph),
            _cloud(ax, g, cx + COL_OFF, cy_pt, SEED_D, color, glyph, CAND_RX, CAND_RY))


def _rim(x, y, facing, k=N_LEAD):
    """The k cells a cloud presents to the other cloud: the outermost one of each height band.

    Picking the k cells with the most extreme x instead bunches every leader into one corner of
    the cloud, and the bundle then reads as a fan out of a point rather than as a link that the
    whole population takes part in.
    """
    return np.array([band[np.argmax(facing * x[band])]
                     for band in np.array_split(np.argsort(y), k)])


def _shadow(seg, box):
    """The x interval of ``seg`` that runs behind the label rectangle ``box``, or None.

    A segment is linear in x, so the set of x where it is inside the box's height band is one
    interval; intersecting that with the box's width gives the only part of the line that has to
    be left undrawn. Breaking every line at the label's full width instead, which is the obvious
    thing to do, takes the same 41 pt out of all nine of them at once, and a sheaf with 41 pt of a
    105 pt gap missing from every line stops reading as a link and starts reading as two fringes.
    """
    (x0, y0), (x1, y1) = seg
    bx0, bx1, by0, by1 = box
    if y0 == y1:
        return (bx0, bx1) if by0 <= y0 <= by1 else None
    t0, t1 = sorted(((b - y0) / (y1 - y0) for b in (by0, by1)))
    lo, hi = max(x0 + t0 * (x1 - x0), bx0), min(x0 + t1 * (x1 - x0), bx1)
    return (lo, hi) if lo < hi else None


def _link(ax, g, y_pt, segs, frags, color, lw, alpha=1.0, zorder=4):
    """What one row compares, drawn as line segments that make way for the row's own label.

    Both rows call this, and the ONLY thing that differs is what they hand it: the mean route
    hands it one segment between two centroids, the population route hands it one segment per
    pair of facing cells. One line against a sheaf of them is the same statement as the two
    equations at the foot of the panel, which is why the label sits IN its link rather than beside
    it. The room it needs is taken out of the lines it actually covers, and taken by leaving them
    undrawn rather than by printing the word on a white patch, which a vector export would carry
    as an opaque box over a line.
    """
    cx = g.w / 2.0
    w = g.on_line(cx, y_pt, frags)
    box = (cx - w / 2.0 - LINK_PAD, cx + w / 2.0 + LINK_PAD,
           y_pt - LABEL_HALF - LINK_PAD, y_pt + LABEL_HALF + LINK_PAD)
    for (x0, y0), (x1, y1) in segs:
        gap = _shadow(((x0, y0), (x1, y1)), box)
        spans = [(x0, x1)] if gap is None else [(x0, gap[0]), (gap[1], x1)]
        for xa, xb in spans:
            if xb - xa < 1.0:                     # a stub shorter than a cell reads as a speck
                continue
            ya, yb = (y0 + (x - x0) / (x1 - x0) * (y1 - y0) for x in (xa, xb))
            ax.plot([g.x(xa), g.x(xb)], [g.y(ya), g.y(yb)], lw=lw, color=color, alpha=alpha,
                    solid_capstyle="round", zorder=zorder)


def draw_1c(ax):
    blank(ax)
    g = _Grid(ax)
    cx = g.w / 2.0

    # ------------------------------------------------- row 1: the mean route, which detours
    (qx, _), (dx, _) = _row(ax, g, CY_MEAN, SHARED, CELL)
    # the collapse lands on the mean of the cells actually drawn, so the arrow drops where the
    # arithmetic says it does rather than on a nominal column centre
    mq, md = qx.mean(), dx.mean()

    # The collapse, drawn rather than named: each population sends one arrow to one diamond, and
    # the population it came from stays on the page above it.
    for mx in (mq, md):
        arrow(ax, (g.x(mx), g.y(ARR_TOP)), (g.x(mx), g.y(ARR_BOT)),
              color=MEAN, lw=LW_ARROW, ms=MS_ARROW)

    # One line between two points, because that is what a cosine of two vectors is.
    _link(ax, g, CENT_CY, [((mq, CENT_CY), (md, CENT_CY))], LINK_MEAN, MEAN, LW_LINE)
    for mx in (mq, md):
        centroid(ax, g.x(mx), g.y(CENT_CY), color=MEAN)

    # mu_Q and mu_d sit outside their diamonds, mirrored, and are the only labels the drawing
    # keeps: they name the two objects the equation at the foot of the panel compares.
    g.run(mq - MARK_HALF - LABEL_GAP, CENT_CY + CAP_MID * PT_ANNOT,
          [("μ", VAR), ("Q", VSUB)], ha="right")
    g.run(md + MARK_HALF + LABEL_GAP, CENT_CY + CAP_MID * PT_ANNOT,
          [("μ", VAR), ("d", VSUB)], ha="left")

    # --------------------------------------- row 2: the population route, straight across
    (qx2, qy2), (dx2, dy2) = _row(ax, g, CY_POP, POP, CELL)

    # The same construction as row 1 and none of its detour: the link leaves the cells themselves,
    # spans the gap at the level it started at, and is made of as many lines as the comparison
    # takes cells. Two of the pairs cross, which is what says many to many rather than a pairing
    # of one query cell with one candidate cell. Under the cells, so the populations stay the
    # object being drawn.
    qi, di = _rim(qx2, qy2, +1), _rim(dx2, dy2, -1)
    pairs = list(zip(qi, di)) + [(qi[1], di[5]), (qi[5], di[1])]
    segs = [((qx2[a], qy2[a]), (dx2[b], dy2[b])) for a, b in pairs]
    _link(ax, g, CY_POP, segs, LINK_POP, POP, LW_HAIR, alpha=LEAD_ALPHA, zorder=2)

    # ------------------------------------------------- the reference block, below the drawing
    # One equation per row, in row order, each behind the mark of the route it states: the MEAN
    # diamond and a POP cell cluster, which are panel d's verdict marks and this panel's two rows
    # in miniature. The marks are what bind an equation to a row, so neither line needs prose.
    for base, frags, color in ((EQ_MEAN_B, EQ_MEAN, MEAN), (EQ_POP_B, EQ_POP, POP)):
        y = g.y(base - CAP_MID * PT_ANNOT)
        if color is MEAN:
            # scatter sizes are areas, so a mark MARK_PT across is MARK_PT squared
            centroid(ax, g.x(MARK_PT / 2.0), y, color=MEAN, size=MARK_PT ** 2)
        else:
            cells(ax, g.x(MARK_PT / 2.0), y, 11, g.x(MARK_PT / 2.0), MARK_PT / 2.0 / g.h,
                  color=POP, rng=np.random.default_rng(5), s=2.6, alpha=0.95, zorder=5)
        g.run(TEXT_X, base, frags)

    # D is a FAMILY of scores, not one mysterious index, and the sentence that says so is a gloss
    # on the line above it: PT_SMALL and SUBTLE, which is this figure's register for material that
    # is not itself a claim.
    g.run(TEXT_X, FAM_B, FAMILY, size=PT_SMALL, sub=PT_SMALL, color=SUBTLE)

    # The mirror is the panel's argument, so it is asserted rather than trusted: row 1's collapse
    # lands on the cloud's own sample mean, and that mean has to sit on the column the row 2 cloud
    # is drawn on, or the two rows are no longer the same two populations.
    for mx, off in ((mq, -COL_OFF), (md, +COL_OFF)):
        assert abs(mx - (cx + off)) < MEAN_TOL_PT, (
            f"collapse lands {mx - (cx + off):+.3f} pt off its column; re-run the seed search")


# --------------------------------------------------------------------------------- preview
def _min_effective_pt(fig):
    """Smallest size any Text on the panel actually prints at, mathtext sub/superscripts at the
    0.7x matplotlib renders them at. fig1_assemble._assert_floor measures exactly this."""
    import re

    import matplotlib.text as mtext
    subsup = re.compile(r"\$[^$]*[\^_][^$]*\$")
    sizes = []
    for t in fig.findobj(mtext.Text):
        s = str(t.get_text())
        if not s.strip() or not t.get_visible():
            continue
        sizes.append((t.get_fontsize() * (0.7 if subsup.search(s) else 1.0), s.replace("\n", "/")))
    return sorted(sizes)


def _overhangs(fig, ax, tol_pt=0.25):
    """Every artist that leaves the axes, and by how much. Text and clip_on=False artists do not
    clip, so anything hanging out here would widen the composite page (figstyle.pin_canvas)."""
    import matplotlib.text as mtext
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    box, out = ax.bbox, []
    # blank() has switched the axis furniture off, so XAxis/YAxis render no ink; the extent they
    # still report is a phantom of tick machinery that is never drawn.
    skip = set(ax.spines.values()) | {ax.patch, ax.xaxis, ax.yaxis}
    assert not ax.axison, "panel c draws no axis furniture; if that changes, measure it here"
    for a in ax.get_children():
        if not a.get_visible() or a in skip:
            continue
        if isinstance(a, mtext.Text) and not str(a.get_text()).strip():
            continue
        bb = a.get_tightbbox(r)
        if bb is None or bb.width <= 0:
            continue
        over = [(box.x0 - bb.x0), (bb.x1 - box.x1), (box.y0 - bb.y0), (bb.y1 - box.y1)]
        over = [o * 72.0 / fig.dpi for o in over]
        if max(over) > tol_pt:
            label = getattr(a, "get_text", lambda: type(a).__name__)() or type(a).__name__
            out.append((str(label).replace("\n", "/")[:34], [round(o, 2) for o in over]))
    return out


def _collisions(fig, ax, tol_pt=0.4):
    """Pairs of labels whose tight bboxes overlap. The floor keeps type legible one label at a
    time; the other way to lose a word is to print it under another one. Fragments of one composed
    run share a gid and are meant to touch, so they are not compared against each other."""
    import matplotlib.text as mtext
    r = fig.canvas.get_renderer()
    boxes = [(str(t.get_text()), t.get_gid(), t.get_window_extent(r))
             for t in ax.findobj(mtext.Text) if str(t.get_text()).strip() and t.get_visible()]
    pad = tol_pt * fig.dpi / 72.0
    hits = []
    for i, (li, gi, bi) in enumerate(boxes):
        for lj, gj, bj in boxes[i + 1:]:
            if gi is not None and gi == gj:
                continue
            if (bi.x0 < bj.x1 - pad and bj.x0 < bi.x1 - pad
                    and bi.y0 < bj.y1 - pad and bj.y0 < bi.y1 - pad):
                hits.append((li, lj))
    return hits


if __name__ == "__main__":
    from matplotlib.patches import Rectangle    # preview only: the axes boundary drawn below

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from figstyle import apply_style  # noqa: E402
    from fig1_style import PT_FLOOR, PT_TICK, PT_TITLE  # noqa: E402

    # The composite's own ladder, so the preview measures what the figure ships.
    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))

    # The axes is EXACTLY the size fig1_assemble gives this panel; the margin exists only so the
    # preview can show what, if anything, crosses the axes boundary.
    PAD = 0.10
    fig = plt.figure(figsize=(PANEL_W_IN + 2 * PAD, PANEL_H_IN + 2 * PAD))
    ax = fig.add_axes([PAD / (PANEL_W_IN + 2 * PAD), PAD / (PANEL_H_IN + 2 * PAD),
                       PANEL_W_IN / (PANEL_W_IN + 2 * PAD), PANEL_H_IN / (PANEL_H_IN + 2 * PAD)])
    draw_1c(ax)
    box = ax.get_position()
    assert abs(box.width * fig.get_size_inches()[0] - PANEL_W_IN) < 1e-6
    assert abs(box.height * fig.get_size_inches()[1] - PANEL_H_IN) < 1e-6

    sizes = _min_effective_pt(fig)
    assert sizes[0][0] >= PT_FLOOR - 1e-6, f"below the {PT_FLOOR} pt floor: {sizes[:4]}"
    print(f"smallest effective type: {sizes[0][0]:.2f} pt  ({sizes[0][1]!r})")

    hang = _overhangs(fig, ax)
    for label, over in hang:
        print(f"  hangs out [left, right, bottom, top] pt: {over}  {label}")
    assert not hang, "artists leave the axes; see above"

    hits = _collisions(fig, ax)
    for a, b in hits:
        print(f"  labels overlap: {a!r} / {b!r}")
    assert not hits, "labels overlap; see above"
    print("every artist inside the axes, and no two labels overlap")

    # the preview-only axes boundary, drawn after the checks so it cannot pass them itself
    fig.add_artist(Rectangle((box.x0, box.y0), box.width, box.height, transform=fig.transFigure,
                             fill=False, ec="#CC3333", lw=0.4, zorder=20))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "1c.png")
    fig.savefig(out, dpi=400, bbox_inches=None)
    print(f"wrote {out}")
