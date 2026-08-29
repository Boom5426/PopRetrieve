"""PopRetrieve Figure 1 panel 1a: from a single-cell response to a ranked candidate list.

The pipeline the whole paper operates on, and the one place where the two scoring rules differ.
A query perturbation produces a population of single-cell responses. That population is turned
into a comparable object in one of two ways: it is collapsed to one mean differential-expression
vector, or it is kept as a population. Everything downstream is shared: the same candidate
library, the same comparison step, one ranking. The paper's question is what the choice at that
single fork is worth, which is why the fork is the only branching in the diagram.

Schematic, not data. No measured value appears here.

Design notes (presentation only, no data involved):
  * There is exactly ONE query cloud, and both branches leave it. Drawing a separate cloud per
    branch would put the difference between the two rules in their INPUT, when the whole claim is
    that they receive the same input and keep different amounts of it.
  * The collapse is drawn on the branch rather than at its end: the upper branch is a fan of thin
    leaders running from the query cells to a single orange dot, so the blue minority is visibly
    consumed. The lower branch carries the population across unchanged. The asymmetry between the
    two branches IS the panel's content.
  * The candidate library and the ranked list are one object, a library column carrying rank
    numbers, and both branches point into it. They were separate stages while this panel had the
    full-width row; at the 3.17 in it gets sharing row 1 with panel b, five horizontal stages
    leave about 0.6 in each, which is narrower than the stage labels. Merging them also states
    something the two-stage version only implied: both rules rank the same library.
  * The panel is authored as a wide box (3.167 x 1.538 in in the composite), so a cloud that is
    circular in axes coordinates prints as a flat smear. Every cloud is drawn with its x-spread
    divided by ASPECT, the panel's own width-to-height ratio, so blobs read round at print size.
    ASPECT is a drawing constant, not a claim.
  * Palette semantics: GREY context, FOCAL_SOFT blue the within-population structure only a
    distributional score can use, COMP_SOFT orange the mean and the collapse onto it.
  * Every mathtext label carrying a sub/superscript is set at 7.2 pt, not at the 5.6-6.4 pt of the
    plain annotations. Matplotlib renders a subscript at 0.7x the nominal size and
    figstyle.mathtext_offenders measures that product against the 5 pt production floor, so a
    6.4 pt "$d_1$" would print its subscript at 4.5 pt. 7.2 x 0.7 = 5.04 pt clears the floor.

Run standalone: python fig1a.py
"""
import os

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch

# Palette comes from the house-style module; do NOT re-declare the hex values here. Every
# panel file used to carry its own copy, which made figstyle's "one edit here recolours the
# whole deck" untrue: a recolour meant editing 43 files and missing one was silent.
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from figstyle import FOCAL_SOFT, COMP_SOFT, GREY, INK  # noqa: E402
FAINT = "#CFCFCF"

# panel width : panel height inside the composite; used only to keep round clouds round
ASPECT = 2.059
# nominal size for any label containing a mathtext sub/superscript (see the design note above)
PT_MATH = 7.2

X_Q = 0.120                       # the one query population
X_REP = 0.395                     # where each branch has finished its representation
X_RANK, X_LIB = 0.765, 0.900      # rank column, and the candidate clouds beside it
Y_TOP, Y_BOT, Y_MID = 0.775, 0.205, 0.470

# the library, already ranked; both branches point into this one column
RANKED = (("1", "$d_3$"), ("2", "$d_1$"), ("3", "$d_4$"), ("4", "$d_2$"))
LIB_Y = (0.880, 0.640, 0.400, 0.160)


def _blob(rng, cx, cy, n, r):
    """n points filling an ellipse of visual radius r, centred on (cx, cy).

    Bounded on purpose. A Gaussian cloud puts a few percent of its points beyond 2 sigma, and at
    this panel's size those stragglers read as separate cells sitting outside the population and
    push neighbouring clouds apart. Sampling uniformly inside a disk keeps every cell inside the
    blob the reader is meant to see, which is all a schematic glyph has to do.
    """
    t = rng.uniform(0, 2 * np.pi, n)
    rad = r * np.sqrt(rng.uniform(0, 1, n))
    return cx + rad * np.cos(t) / ASPECT, cy + rad * np.sin(t)


def _cloud(ax, rng, cx, cy, n_bulk, n_min, r, s=1.5):
    """A population glyph: GREY bulk with the FOCAL_SOFT minority a distributional score can see."""
    gx, gy = _blob(rng, cx, cy, n_bulk, r)
    bx, by = _blob(rng, cx, cy, n_min, r * 0.46)
    ax.scatter(gx, gy, s=s, c=GREY, alpha=0.55, lw=0, zorder=3)
    ax.scatter(bx, by, s=s * 1.35, c=FOCAL_SOFT, alpha=0.95, lw=0, zorder=3)
    return np.r_[gx, bx], np.r_[gy, by]


# NO LOCAL text_run HERE. This module carried a private copy of figstyle.text_run, orphaned
# when panel a's coloured footer moved into the caption: defined, never called, and a strictly
# poorer version of the shared one (no per-fragment kwargs, no va). figstyle.text_run is the
# single implementation; fig1f imports it.


def _arrow(ax, p0, p1, color=GREY, lw=0.8, z=4, ms=6):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=ms, lw=lw,
                                 color=color, zorder=z))


def draw_1a(ax):
    rng = np.random.default_rng(7)
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(-0.12, 1.16)
    ax.axis("off")

    # ---------------- the one query population ----------------
    ax.text(X_Q, 1.075, "query response", ha="center", va="center", fontsize=6.0, color=INK)
    qx, qy = _cloud(ax, rng, X_Q, Y_MID, n_bulk=74, n_min=21, r=0.185)
    ax.text(X_Q, 0.185, "$d_q$", ha="center", va="center", fontsize=PT_MATH, color=INK)

    # ---------------- upper branch: the population is consumed into one vector ----------------
    dot = (X_REP - 0.028, Y_TOP)
    # Eight leaders, not eighty: the fan has to say "every cell ends up in this one dot" without
    # becoming the heaviest ink in the panel or drawing a web across the query cloud itself.
    for x0, y0 in zip(qx[::12], qy[::12]):
        ax.plot([x0, dot[0]], [y0, dot[1]], lw=0.25, color=FAINT, zorder=2)
    ax.scatter([dot[0]], [dot[1]], s=16, c=COMP_SOFT, edgecolors="white", lw=0.5, zorder=5)
    ax.text(X_REP - 0.028, 1.075, "mean signature", ha="center", va="center", fontsize=6.4,
            color=INK, fontweight="bold")

    # ---------------- lower branch: the population is carried across ----------------
    _arrow(ax, (X_Q + 0.075, 0.330), (X_REP - 0.130, 0.240), color=FOCAL_SOFT, lw=0.8, ms=5)
    _cloud(ax, rng, X_REP - 0.020, Y_BOT, n_bulk=52, n_min=15, r=0.150)
    ax.text(X_REP - 0.020, -0.070, "response population", ha="center", va="center", fontsize=6.4,
            color=INK, fontweight="bold")

    # ---------------- scoring: two rules, one library ----------------
    _arrow(ax, (X_REP + 0.010, Y_TOP), (X_RANK - 0.100, Y_TOP), color=COMP_SOFT, lw=0.8)
    _arrow(ax, (X_REP + 0.075, Y_BOT), (X_RANK - 0.100, Y_BOT), color=FOCAL_SOFT, lw=0.8)
    ax.text((X_REP + X_RANK) / 2 - 0.045, Y_TOP + 0.135, "mean-signature\nsimilarity",
            ha="center", va="center", fontsize=5.6, color=INK, linespacing=1.15)
    ax.text((X_REP + X_RANK) / 2 - 0.045, Y_BOT - 0.135, "population\nsimilarity",
            ha="center", va="center", fontsize=5.6, color=INK, linespacing=1.15)

    # ---------------- the shared candidate library, ranked ----------------
    ax.text(0.855, 1.075, "candidate library,\nranked", ha="center", va="center", fontsize=6.0,
            color=INK, linespacing=1.15)
    for (num, cand), yy in zip(RANKED, LIB_Y):
        ax.text(X_RANK - 0.030, yy, num, ha="center", va="center", fontsize=PT_MATH, color=GREY)
        ax.text(X_RANK + 0.045, yy, cand, ha="center", va="center", fontsize=PT_MATH, color=INK)
        _cloud(ax, rng, X_LIB + 0.022, yy, n_bulk=24, n_min=7, r=0.078, s=1.2)

    # THE CONTINUUM FOOTER IS IN THE CAPTION. It read "information retained: mean signature ->
    # full population", which is the same sentence caption entry a ends on ("they differ only in
    # how much within-population information is retained"), and Extended Data Fig. 1d,e is where
    # the continuum is measured. Text on a panel that repeats its own caption is what production asks authors
    # to delete, so it is deleted here rather than shrunk.


if __name__ == "__main__":
    # The preview is drawn on the SAME axes geometry the composite gives this panel (3.167 x 1.538 in
    # of axes, no subplot margins). An x tuned against a preview of a different width is wrong in
    # the figure that ships, which is how an earlier draft of this panel overlapped its own footer.
    fig, ax = plt.subplots(figsize=(3.167, 1.538))
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    draw_1a(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "1a.png"), dpi=300)
    print("wrote 1a.png")
