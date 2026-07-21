"""DART Figure 1 panel 1a: the biological motivation, drawn rather than rendered.

This panel used to be a dashed placeholder box reading "[ AI schematic 1a ]" with the path of a
prompt file printed inside it, which is not a submittable figure. It is now an actual schematic.

The claim it has to carry, and the whole reason a distributional score could matter, is this:
two drugs can produce the SAME mean signature and OPPOSITE consequences for a resistant minority.
The mean is a sufficient statistic only if every cell responds the same way. Where a minority
responds differently, two candidates that tie on the mean can differ entirely in what happens to
the cells that determine relapse.

Schematic, not data. It states the hypothesis this paper then tests; it does not assert a result.

Run standalone: python fig1a.py
"""
import os

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Ellipse

FOCAL, COMP, GREY, INK = "#5185C0", "#E99D4E", "#7A7A7A", "#1A1A1A"
MAJ, MIN = "#9DBEDC", "#E99D4E"


def _cloud(ax, cx, cy, n, color, rng, sx=0.30, sy=0.22, alpha=0.55, s=5.5):
    pts = rng.normal([cx, cy], [sx, sy], size=(n, 2))
    ax.scatter(pts[:, 0], pts[:, 1], s=s, c=color, alpha=alpha, lw=0, zorder=2)
    return pts


def draw_1a(ax):
    rng = np.random.default_rng(0)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.15)
    ax.axis("off")

    # ---- untreated query population: a sensitive majority plus a resistant minority ----
    _cloud(ax, 1.15, 4.25, 110, MAJ, rng)
    _cloud(ax, 1.15, 2.35, 26, MIN, rng, sx=0.22, sy=0.16)
    ax.add_patch(Ellipse((1.15, 2.35), 0.95, 0.72, fill=False, ec=COMP, lw=1.0, ls="--", zorder=3))
    ax.text(1.15, 5.30, "untreated", ha="center", fontsize=6.4, color=INK, fontweight="bold")
    ax.text(1.15, 4.95, "majority", ha="center", fontsize=5.6, color=FOCAL)
    ax.text(1.15, 1.62, "resistant\nminority", ha="center", fontsize=5.6, color=COMP)

    # ---- two candidate drugs, identical mean shift, opposite minority fate ----
    # drug A, upper: both subpopulations move
    _cloud(ax, 5.55, 4.85, 110, MAJ, rng)
    _cloud(ax, 5.55, 3.55, 26, MIN, rng, sx=0.22, sy=0.16)
    ax.add_patch(Ellipse((5.55, 3.55), 0.95, 0.72, fill=False, ec=COMP, lw=1.0, ls="--", zorder=3))
    ax.text(5.55, 5.72, "drug A", ha="center", fontsize=6.4, color=INK, fontweight="bold")

    # drug B, lower: the majority moves the same way, the minority does not move at all
    _cloud(ax, 5.55, 1.95, 110, MAJ, rng)
    _cloud(ax, 5.55, 0.55, 26, MIN, rng, sx=0.22, sy=0.16)
    ax.add_patch(Ellipse((5.55, 0.55), 0.95, 0.72, fill=False, ec=COMP, lw=1.4, zorder=3))
    ax.text(5.55, 2.82, "drug B", ha="center", fontsize=6.4, color=INK, fontweight="bold")

    for y0, y1 in [(3.85, 4.70), (3.10, 2.10)]:
        ax.add_patch(FancyArrowPatch((2.05, y0), (4.75, y1), arrowstyle="-|>", mutation_scale=8,
                                     lw=0.9, color=GREY, alpha=0.8,
                                     connectionstyle="arc3,rad=0.10"))

    # ---- the two mean-delta arrows are the SAME. That is the whole point. ----
    for yy in (4.30, 1.40):
        ax.add_patch(FancyArrowPatch((7.05, yy), (8.35, yy), arrowstyle="-|>", mutation_scale=10,
                                     lw=2.0, color=INK, zorder=4))
    ax.text(8.62, 4.30, r"$\delta$", ha="left", va="center", fontsize=9, color=INK)
    ax.text(8.62, 1.40, r"$\delta$", ha="left", va="center", fontsize=9, color=INK)
    ax.text(9.30, 2.85, "identical\nmean\nsignature", ha="center", va="center", fontsize=5.9,
            color=INK, fontweight="bold")
    ax.annotate("", xy=(8.95, 4.05), xytext=(8.95, 1.65),
                arrowprops=dict(arrowstyle="-", lw=0.8, color=INK))

    # ---- the consequence the mean cannot see ----
    ax.text(6.75, 3.55, "minority\nresponds", ha="left", va="center", fontsize=5.6, color=FOCAL)
    ax.text(6.75, 0.55, "minority\nsurvives", ha="left", va="center", fontsize=5.6, color=COMP,
            fontweight="bold")

    ax.text(5.0, 0.02,
            "Same mean shift, opposite fate for the cells that drive relapse.\n"
            "The mean is a sufficient statistic only if every cell responds alike.",
            ha="center", va="bottom", fontsize=5.7, color=GREY, style="italic")


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(5.4, 3.2))
    draw_1a(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "1a.png"), dpi=200, bbox_inches="tight")
    print("wrote 1a.png")
