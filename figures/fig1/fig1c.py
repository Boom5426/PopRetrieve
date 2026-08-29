"""PopRetrieve Figure 1 panel 1c: the same query-candidate pair, scored at two resolutions.

This panel answers exactly one question: what statistic of the same two response populations
enters the retrieval score? It does not draw a candidate library and it does not draw a ranking,
because panel a already carries the pipeline end to end. Panel c is the operator; panel d is the
consequence of the operator; drawing a ranking here would make c a second telling of a.

    (Q, P_d)  ->  s_mean(d, Q) = cos(mu_Q, mu_d)        one vector per population
              ->  s_pop(d, Q)  = -D(P_d, Q)             the empirical populations

Schematic (no external data). No measured score is shown: a number here would read as a result,
and Figure 1 reports none.

Design notes (presentation only, no data involved):
  * The two rows draw THE SAME point sets. Q and P_d are sampled once, at module scope, and each
    row plots those same coordinates; the rows differ only in what is done to them. Re-sampling
    per row would put the difference between the two scores in the data rather than in the
    operator, which is the one thing this panel exists to show.
  * The upper row's centroids are the actual means of the drawn points, not a nominal centre, so
    the collapse arrow lands where the arithmetic says it should.
  * No cards. The earlier version of this panel put each scoring rule in a filled, rounded,
    coloured box, which is what gave this figure its slide-deck look; the rows are now separated
    by whitespace and by a single grey grouping rule, and colour is carried by the row label and
    the connector alone.
  * Every mathtext label carrying a sub/superscript is set at 7.2 pt. Matplotlib renders a
    subscript at 0.7x nominal and figstyle.mathtext_offenders measures that product against the
    5 pt floor, so the 5.6-6.2 pt formulas this panel used to carry printed their subscripts at
    3.9-4.3 pt. 7.2 x 0.7 = 5.04 pt clears the floor, and the six mathtext warnings this figure
    used to emit were all from this panel.

Run standalone: python fig1c.py
"""
import os

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

# Palette comes from the house-style module; do NOT re-declare the hex values here. Every
# panel file used to carry its own copy, which made figstyle's "one edit here recolours the
# whole deck" untrue: a recolour meant editing 43 files and missing one was silent.
import sys as _sys, os as _os
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
from figstyle import FOCAL_SOFT, COMP_SOFT, GREY, INK  # noqa: E402
# the un-scored cells of the mean row: present, but no longer what is being compared
PALE = "#AFC0D2"

# panel width : panel height inside the composite; used only to keep round clouds round
ASPECT = 2.333
PT_MATH = 7.2

X_Q, X_D, X_MID = 0.335, 0.775, 0.555
Y_CLOUD_MEAN, Y_CENTROID, Y_CLOUD_POP = 0.860, 0.690, 0.300
R_CLOUD = 0.080


def _blob(rng, cx, cy, n, r, sy=1.0):
    """n points filling an ellipse of visual radius r, centred on (cx, cy)."""
    t = rng.uniform(0, 2 * np.pi, n)
    rad = r * np.sqrt(rng.uniform(0, 1, n))
    return cx + rad * np.cos(t) / ASPECT, cy + rad * np.sin(t) * sy


def _pair():
    """The one query population and the one candidate population, sampled once.

    Returned as offsets from the cloud centre so the same coordinates can be re-centred on either
    row. Both rows must plot identical shapes; that identity is the panel's argument.
    """
    rng = np.random.default_rng(19)
    qx, qy = _blob(rng, 0.0, 0.0, 34, R_CLOUD)
    # the candidate is drawn slightly wider and flatter than the query, so the two are visibly a
    # PAIR of different populations rather than one cloud copied twice
    dx, dy = _blob(rng, 0.0, 0.0, 34, R_CLOUD * 1.12, sy=0.82)
    return (qx, qy), (dx, dy)


Q_OFF, D_OFF = _pair()


def _cells(ax, off, cx, cy, colour, s, alpha, z=3):
    ax.scatter(off[0] + cx, off[1] + cy, s=s, c=colour, alpha=alpha, lw=0, zorder=z)
    return off[0].mean() + cx


def draw_1c(ax):
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.axis("off")

    # ---------------- the pair, named once ----------------
    ax.text(X_Q, 0.968, "query $Q$", ha="center", va="center", fontsize=6.4, color=INK)
    ax.text(X_D, 0.968, "candidate $P_d$", ha="center", va="center", fontsize=PT_MATH, color=INK)

    # one grey rule holding the two rows together: same pair, two operators
    ax.plot([0.170, 0.170], [0.212, 0.936], lw=0.7, color="#D2D2D2",
            solid_capstyle="round", zorder=1)

    # ---------------- upper row: collapse each population, then compare two vectors ----------
    # Swatch, then the word. These two are the panel's key: each labels a whole row, and unlike
    # every other label in this figure it has no single adjacent mark to bind it to a family.
    ax.add_patch(Rectangle((0.148, Y_CLOUD_MEAN - 0.016), 0.016, 0.032, color=COMP_SOFT, lw=0,
                           clip_on=False, zorder=5))
    ax.text(0.138, Y_CLOUD_MEAN, "Mean", ha="right", va="center", fontsize=6.6,
            color=INK, fontweight="bold")
    mq = _cells(ax, Q_OFF, X_Q, Y_CLOUD_MEAN, PALE, s=3.4, alpha=0.85)
    md = _cells(ax, D_OFF, X_D, Y_CLOUD_MEAN, PALE, s=3.4, alpha=0.85)

    for xc in (mq, md):
        ax.add_patch(FancyArrowPatch((xc, 0.768), (xc, 0.714), arrowstyle="-|>",
                                     mutation_scale=5, lw=0.7, color=COMP_SOFT, zorder=4))
    ax.plot([mq, md], [Y_CENTROID, Y_CENTROID], lw=0.75, color=COMP_SOFT, zorder=3)
    ax.scatter([mq, md], [Y_CENTROID] * 2, s=17, c=COMP_SOFT, edgecolors="white", lw=0.5, zorder=5)
    ax.text(X_MID, 0.712, "cosine", ha="center", va="bottom", fontsize=6.0, color=INK)
    ax.text(mq - 0.048, Y_CENTROID, "$\\mu_Q$", ha="right", va="center", fontsize=PT_MATH,
            color=INK)
    ax.text(md + 0.048, Y_CENTROID, "$\\mu_d$", ha="left", va="center", fontsize=PT_MATH,
            color=INK)

    ax.text(X_MID, 0.545, "$s_{\\mathrm{mean}}(d,Q)=\\cos(\\mu_Q,\\,\\mu_d)$", ha="center",
            va="center", fontsize=PT_MATH, color=INK)
    # "uses one vector per population" / "uses the empirical response populations" are caption
    # sentences and are set there. The formulas above them already say which statistic each row
    # takes, so the two lines were a gloss on notation the caption has to define anyway.

    # ---------------- lower row: compare the populations themselves ----------------
    # Swatch, then the word. These two are the panel's key: each labels a whole row, and unlike
    # every other label in this figure it has no single adjacent mark to bind it to a family.
    ax.add_patch(Rectangle((0.148, Y_CLOUD_POP - 0.016), 0.016, 0.032, color=FOCAL_SOFT, lw=0,
                           clip_on=False, zorder=5))
    ax.text(0.138, Y_CLOUD_POP, "Population", ha="right", va="center", fontsize=6.6,
            color=INK, fontweight="bold")
    _cells(ax, Q_OFF, X_Q, Y_CLOUD_POP, FOCAL_SOFT, s=3.4, alpha=0.90)
    _cells(ax, D_OFF, X_D, Y_CLOUD_POP, FOCAL_SOFT, s=3.4, alpha=0.90)
    ax.add_patch(FancyArrowPatch((X_Q + 0.060, Y_CLOUD_POP), (X_D - 0.064, Y_CLOUD_POP),
                                 arrowstyle="<|-|>", mutation_scale=5, lw=0.8, color=FOCAL_SOFT,
                                 shrinkA=0, shrinkB=0, zorder=4))
    ax.text(X_MID, 0.352, "population distance", ha="center", va="bottom", fontsize=6.0,
            color=INK)

    ax.text(X_MID, 0.095, "$s_{\\mathrm{pop}}(d,Q)=-D(P_d,\\,Q)$", ha="center", va="center",
            fontsize=PT_MATH, color=INK)



if __name__ == "__main__":
    # Same axes geometry the composite gives this panel, so a position tuned here is correct there.
    fig, ax = plt.subplots(figsize=(3.724, 1.596))
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    draw_1c(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "1c.png"), dpi=300)
    print("wrote 1c.png")
