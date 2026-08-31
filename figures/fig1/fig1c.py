"""PopRetrieve Figure 1 panel c: what mathematically changes between the two scores.

Panel b says WHY averaging can fail. Panel c says what is actually COMPUTED, on one pair of
populations, at two resolutions:

    same (Q, P_d)  ->  s_mean(d, Q) = cos(mu_Q, mu_d)     two vectors, one cosine
                   ->  s_pop(d, Q)  = -D(P_d, Q)          two populations, one divergence

Nothing here is measured, and no candidate library or ranking is drawn: panel a already carries
the pipeline end to end, and panel d carries the consequence. c is the operator alone.

WHY THE ROWS ARE BUILT THE WAY THEY ARE
---------------------------------------
The two rows plot THE SAME two point sets, at the same two column centres, at the same radius:
each cloud is sampled from a freshly seeded generator, so row 2's clouds are row 1's clouds to the
last cell. That identity is the panel's whole argument, so it is guaranteed by construction rather
than by two tuned constants that happen to agree. What differs between the rows is the ink laid on
top: row 1 collapses each cloud onto one MEAN centroid and links the two centroids; row 2 leaves
the cells in place and bridges the two clouds cell to cell.

The upper clouds are SHARED grey and the lower clouds are POP blue for the same reason. In the
mean route the cells are input that is thrown away, which is what SHARED means here; in the
population route the retained cells ARE the object being scored, which is what POP means.

SUBSCRIPTS ARE COMPOSED, NOT SET AS MATHTEXT
--------------------------------------------
Matplotlib renders a mathtext sub/superscript at 0.7x the surrounding size, so "$\\mu_Q$" set at
PT_EQ prints its Q at 6.3 pt. fig1_assemble._assert_floor measures exactly that product against
PT_FLOOR = 6.5 and refuses the build, so no label on this panel can carry a real "$..._x$":
PT_EQ would have to be 9.29 for one to clear the floor. fig1_style has no token for that and this
module may not add one, so ``_Grid.run`` sets the base at PT_EQ and each subscript as its own Text
at PT_SMALL, the figure's floor. That prints the subscript at 0.72x of the base rather than
matplotlib's 0.70x, a difference of two tenths of a point, and every glyph clears 6.5.

Run standalone: python fig1c.py
"""
from __future__ import annotations

import os
import sys

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.textpath import TextToPath

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fig1_style import (FAINT, LW_ARROW, LW_HAIR, LW_LINE, MEAN, MS_ARROW,  # noqa: E402
                        POP, PT_ANNOT, PT_EQ, PT_SMALL, PT_TITLE, SHARED, SUBTLE, TEXT,
                        arrow, blank, cells, centroid, title)

# The axes this panel is authored for, in inches. The layout below is written in POINTS measured
# from the top-left of that axes, because a schematic tuned in axes fractions silently restyles
# itself at any other aspect ratio, and this panel is the narrowest in the figure.
PANEL_W_IN, PANEL_H_IN = 1.238, 3.00

# ---------------------------------------------------------------------------------- geometry
COL_L, COL_R = 24.0, 65.0   # cloud centres, pt from the left edge of an 89.1 pt wide axes
R_CLOUD = 8.5               # cloud radius in pt; the two clouds leave a 23 pt gap to bridge
N_CELLS = 44                # a 17 pt cloud reads as a population at this density; 26 read as dots
# The candidate is a different population, not a copy of the query: it is drawn wider and flatter.
# What has to match is row against row, which is guaranteed by the seeds below, not column against
# column, and two identical clouds would say the query and the candidate are the same object.
CAND_RX, CAND_RY = 1.12, 0.85
# Seeds chosen so both clouds fill their disk evenly (no notch, no hollow centre) and their sample
# means land within 0.02 r of the centre, so the collapse arrow drops through the cloud it came
# from rather than off to one side. 7 is fig1_style.cells's own default.
SEED_Q, SEED_D = 7, 50

# Baselines and centres, pt from the top of a 216 pt tall axes. Row 1 runs 30-108 and row 2 runs
# 126-206, so the two rows carry the same weight and the grouping rule sits in clear space.
TITLE_B1, TITLE_B2 = 8.0, 18.5
CLOUD1_CY = 39.0
ARROW_TOP, ARROW_BOT = 50.0, 61.0
COLLAPSE_B = 58.5           # sits between the two collapse arrows, so one word labels both
CENT_CY = 66.0
COS_B = 79.0
EQ1_B1, EQ1_B2 = 93.0, 106.0
RULE_Y = 117.0
CLOUD2_CY = 135.0
POPD_B = 155.0
EQ2_B1, EQ2_B2 = 170.0, 183.0
FAM_B1, FAM_B2 = 196.0, 204.5

MARK_HALF = 3.0             # half the diagonal of the centroid diamond, whose area is 34 pt^2
LABEL_GAP = 5.0             # centroid marker edge -> its mu label
SUB_DROP = 0.20             # subscript baseline drop, as a fraction of the base size

_T2P = TextToPath()


def _width(text, size, weight):
    """Advance width of one fragment in points, measured without a renderer.

    TextToPath reads the font metrics directly, so a run can be laid out at draw time on any
    backend and before the first draw. Hard-coding fragment positions instead is correct for
    exactly one axes width and one font, and silently overlaps when either changes.
    """
    prop = FontProperties(family=["sans-serif"], size=size, weight=weight)
    return _T2P.get_text_width_height_descent(text, prop, text.startswith("$"))[0]


class _Grid:
    """Point addressing for one axes, plus the composed-subscript text run.

    Everything is placed on baselines rather than on box edges: a label positioned by its box top
    moves when its string gains or loses a descender, and this panel stacks a dozen of them.
    """

    def __init__(self, ax):
        w_in, h_in = ax.figure.get_size_inches()
        box = ax.get_position()
        self.ax = ax
        self.w = box.width * w_in * 72.0
        self.h = box.height * h_in * 72.0

    def x(self, pt):
        return pt / self.w

    def y(self, pt):
        return 1.0 - pt / self.h

    def text(self, x_pt, y_pt, s, size=PT_ANNOT, color=TEXT, ha="center", **kw):
        return self.ax.text(self.x(x_pt), self.y(y_pt), s, fontsize=size, color=color,
                            ha=ha, va="baseline", **kw)

    def run(self, x_pt, y_pt, frags, size=PT_EQ, sub=PT_SMALL, weight="normal",
            color=TEXT, ha="center"):
        """Draw ``frags`` left to right; a frag flagged True is set as a subscript.

        Returns the run's total width in points, so the caller can check it against the axes.
        """
        sizes = [sub if is_sub else size for _, is_sub in frags]
        widths = [_width(t, s, weight) for (t, _), s in zip(frags, sizes)]
        total = sum(widths)
        x = x_pt - total / 2.0 if ha == "center" else (x_pt - total if ha == "right" else x_pt)
        # One gid for the whole run, matching fig1a's convention: a composed subscript is TUCKED
        # against its base on purpose, exactly where mathtext would put it, and a QA sweep that
        # compares Text bboxes pairwise has to be able to tell that from a real collision.
        gid = "run-%d-%d" % (round(x_pt * 1e3), round(y_pt * 1e3))
        for (t, is_sub), s, w in zip(frags, sizes, widths):
            y = y_pt + SUB_DROP * size if is_sub else y_pt
            self.ax.text(self.x(x), self.y(y), t, fontsize=s, color=color, ha="left", gid=gid,
                         va="baseline", fontweight=weight)
            x += w
        return total


def _cloud(ax, g, cx_pt, cy_pt, seed, color, fx=1.0, fy=1.0):
    """One population, drawn identically in both rows: same seed, same n, same radius."""
    return cells(ax, g.x(cx_pt), g.y(cy_pt), N_CELLS, g.x(R_CLOUD * fx), R_CLOUD * fy / g.h,
                 color=color, rng=np.random.default_rng(seed))


def _rim(x, y, facing, k=5):
    """The k cells a cloud presents to the other cloud: the outermost one of each height band.

    Picking the k cells with the most extreme x instead bunches every leader into one corner of
    the cloud, and the bundle then reads as a fan out of a point rather than as a bridge.
    """
    return np.array([band[np.argmax(facing * x[band])]
                     for band in np.array_split(np.argsort(y), k)])


def draw_1c(ax):
    blank(ax)
    g = _Grid(ax)

    # ---------------------------------------------------------------- the shared premise
    # Two lines because "Same query Q, same candidate P_d" is 134 pt wide at PT_TITLE and the
    # axes is 89 pt. The subscript is composed, so the phrase carries no mathtext and stays at
    # PT_TITLE rather than being promoted to PT_EQ.
    title(ax, "Same query Q,", x=0.0, y=g.y(TITLE_B1), va="baseline")
    g.run(0.0, TITLE_B2, [("same candidate P", False), ("d", True)],
          size=PT_TITLE, sub=PT_SMALL, weight="bold", ha="left")

    # ---------------------------------------------------------------- row 1: mean signature
    qx, qy = _cloud(ax, g, COL_L, CLOUD1_CY, SEED_Q, SHARED)
    dx, dy = _cloud(ax, g, COL_R, CLOUD1_CY, SEED_D, SHARED, CAND_RX, CAND_RY)
    # the centroid is the mean of the cells actually drawn, so the collapse lands where the
    # arithmetic says it does rather than on a nominal column centre
    mq_pt, md_pt = qx.mean() * g.w, dx.mean() * g.w

    for mx in (mq_pt, md_pt):
        arrow(ax, (g.x(mx), g.y(ARROW_TOP)), (g.x(mx), g.y(ARROW_BOT)),
              color=MEAN, lw=LW_ARROW, ms=MS_ARROW)
    g.text((mq_pt + md_pt) / 2.0, COLLAPSE_B, "collapse")

    ax.plot([g.x(mq_pt), g.x(md_pt)], [g.y(CENT_CY)] * 2, lw=LW_LINE, color=MEAN,
            solid_capstyle="round", zorder=5)
    for mx in (mq_pt, md_pt):
        centroid(ax, g.x(mx), g.y(CENT_CY), color=MEAN)
    # the mu labels are what bind the equation below to the two marks above it
    g.run(mq_pt - MARK_HALF - LABEL_GAP, CENT_CY + 0.32 * PT_EQ,
          [("$\\mu$", False), ("$Q$", True)], ha="right")
    g.run(md_pt + MARK_HALF + LABEL_GAP, CENT_CY + 0.32 * PT_EQ,
          [("$\\mu$", False), ("$d$", True)], ha="left")
    g.text((mq_pt + md_pt) / 2.0, COS_B, "cosine similarity")

    # The equation is the visual centre of its row. It breaks at the relation, which is where a
    # display equation is broken, because the one-line form is 108 pt wide in an 89 pt axes and
    # the alternative was to drop the (d, Q) arguments and make a scoring function look scalar.
    g.run(g.w / 2, EQ1_B1, [("$s$", False), ("$\\mathrm{mean}$", True), ("$(d,Q)$", False)])
    g.run(g.w / 2, EQ1_B2, [("$=\\cos($", False), ("$\\mu$", False), ("$Q$", True),
                            ("$,\\,$", False), ("$\\mu$", False), ("$d$", True), ("$)$", False)])

    # one hairline, not a box: the rows are a pair, not two exhibits
    ax.plot([g.x(3.0), g.x(g.w - 3.0)], [g.y(RULE_Y)] * 2, lw=LW_HAIR, color=FAINT, zorder=1)

    # ---------------------------------------------------------------- row 2: population
    qx2, qy2 = _cloud(ax, g, COL_L, CLOUD2_CY, SEED_Q, POP)
    dx2, dy2 = _cloud(ax, g, COL_R, CLOUD2_CY, SEED_D, POP, CAND_RX, CAND_RY)

    # A matching BRIDGE rather than one arrow: the score compares the cells, and a single arrow
    # between two clouds is the picture of a distance between two summaries. The leaders leave
    # from the rims that actually face each other and are spread over the height of each cloud,
    # so the bundle spans the gap; two of them cross, which is what says many-to-many rather
    # than a pairing. They sit under the cells, so the populations stay the object being drawn.
    qi, di = _rim(qx2, qy2, +1), _rim(dx2, dy2, -1)
    pairs = list(zip(qi, di)) + [(qi[1], di[3]), (qi[3], di[1])]
    for a, b in pairs:
        ax.plot([qx2[a], dx2[b]], [qy2[a], dy2[b]], lw=LW_HAIR, color=POP, alpha=0.45,
                zorder=2, solid_capstyle="round")
    g.text(g.w / 2, POPD_B, "population distance")

    g.run(g.w / 2, EQ2_B1, [("$s$", False), ("$\\mathrm{pop}$", True), ("$(d,Q)$", False)])
    g.run(g.w / 2, EQ2_B2, [("$=-D(P$", False), ("$d$", True), ("$,\\,Q)$", False)])

    # D is a FAMILY of scores, not one mysterious index. Two lines because the four names are
    # 114 pt wide at PT_SMALL, and PT_SMALL is the floor: the line breaks, the size does not.
    g.text(g.w / 2, FAM_B1, "energy / MMD /", size=PT_SMALL, color=SUBTLE)
    g.text(g.w / 2, FAM_B2, "Wasserstein / coverage", size=PT_SMALL, color=SUBTLE)


if __name__ == "__main__":
    import re

    import matplotlib.text as mtext
    from matplotlib.axis import Axis
    from matplotlib.patches import Rectangle
    from matplotlib.spines import Spine

    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from figstyle import apply_style
    from fig1_style import PT_FLOOR, PT_TICK, PT_TITLE

    # The composite's own ladder, so the preview measures what the figure ships.
    apply_style(sizes=(PT_TITLE, PT_ANNOT, PT_TICK))

    # The axes is EXACTLY the size fig1_assemble gives this panel; the margin exists only so the
    # preview shows what, if anything, crosses the axes boundary.
    PAD = 0.10
    fig = plt.figure(figsize=(PANEL_W_IN + 2 * PAD, PANEL_H_IN + 2 * PAD))
    ax = fig.add_axes([PAD / (PANEL_W_IN + 2 * PAD), PAD / (PANEL_H_IN + 2 * PAD),
                       PANEL_W_IN / (PANEL_W_IN + 2 * PAD), PANEL_H_IN / (PANEL_H_IN + 2 * PAD)])
    draw_1c(ax)
    box = ax.get_position()
    assert abs(box.width * fig.get_size_inches()[0] - PANEL_W_IN) < 1e-6
    assert abs(box.height * fig.get_size_inches()[1] - PANEL_H_IN) < 1e-6

    # ---- 2. type floor, measured the way fig1_assemble._assert_floor measures it ----
    subsup = re.compile(r"\$[^$]*[\^_][^$]*\$")
    smallest = min((t.get_fontsize() * (0.7 if subsup.search(str(t.get_text())) else 1.0), 
                    str(t.get_text()))
                   for t in fig.findobj(mtext.Text)
                   if str(t.get_text()).strip() and t.get_visible())
    assert smallest[0] >= PT_FLOOR - 1e-6, f"below the {PT_FLOOR} pt floor: {smallest}"
    print(f"smallest effective type: {smallest[0]:.2f} pt  ({smallest[1]!r})")

    # ---- 3. nothing may hang outside the axes: an overhang widens the composite ----
    fig.canvas.draw()
    rend = fig.canvas.get_renderer()
    ab = ax.get_window_extent(rend)
    dpi = fig.dpi
    out = []
    for art in ax.get_children():
        if not art.get_visible() or art is ax.patch:
            continue
        # A switched-off axes draws neither spines nor tick labels, so the extent those artists
        # still report is not ink and cannot widen the composite.
        if not ax.axison and isinstance(art, (Spine, Axis)):
            continue
        if isinstance(art, mtext.Text) and not str(art.get_text()).strip():
            continue
        bb = art.get_tightbbox(rend)
        if bb is None or bb.width <= 0:
            continue
        over = max(ab.x0 - bb.x0, bb.x1 - ab.x1, ab.y0 - bb.y0, bb.y1 - ab.y1)
        if over > 0.75:                      # sub-pixel slack: antialiasing, not layout
            name = str(art.get_text()) if isinstance(art, mtext.Text) else type(art).__name__
            out.append(f"  {name!r} hangs out by {over / dpi * 72:.2f} pt")
    if out:
        print("OUTSIDE THE AXES:")
        print("\n".join(out))
    else:
        print("all artists inside the axes")

    # the preview-only axes boundary, drawn after the checks so it cannot pass them itself
    fig.add_artist(Rectangle((box.x0, box.y0), box.width, box.height, transform=fig.transFigure,
                             fill=False, ec="#CC3333", lw=0.4, zorder=20))
    fig.savefig(os.path.join(os.path.dirname(__file__), "1c.png"), dpi=400,
                bbox_inches=None)
    print("wrote 1c.png")
