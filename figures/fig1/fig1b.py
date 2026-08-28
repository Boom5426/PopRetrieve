"""PopRetrieve Figure 1 panel 1b: the inverse-retrieval task, and the two scoring rules that act on it.

Schematic (no external data). The panel states two things the manuscript asserts:
  * the task is population-to-population inverse retrieval: a query population Q and a candidate
    library {P_d} produce one ranking of candidates;
  * the two scoring rules differ only in how much of a population they keep. Mean-signature
    retrieval collapses each population to a single vector; distributional retrieval keeps the
    whole population. Both rank the same library for the same query.

Drawn with real point-cloud glyphs rather than empty boxes, so it is visually distinct from the
other two schematic panels of this figure.

Run standalone: python fig1b.py
"""
import os

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

FOCAL, COMP, GREY, INK = "#5185C0", "#E99D4E", "#7A7A7A", "#1A1A1A"
FAINT = "#CFCFCF"


def _rbox(ax, x, y, w, h, ec, fc="white", lw=0.8, z=2):
    ax.add_patch(mpl.patches.FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.004,rounding_size=0.02",
        fc=fc, ec=ec, lw=lw, zorder=z))


def _cloud(ax, rng, cx, cy, n=26, rx=0.030, ry=0.030, c=GREY, s=1.6, alpha=0.75, z=3):
    ax.scatter(rng.normal(cx, rx, n), rng.normal(cy, ry, n), s=s, c=c, alpha=alpha,
               lw=0, zorder=z)


def _arrow(ax, p0, p1, color=GREY, lw=0.8, rad=0.0, z=4):
    ax.add_patch(mpl.patches.FancyArrowPatch(
        p0, p1, arrowstyle="-|>", mutation_scale=6, lw=lw, color=color, zorder=z,
        connectionstyle=f"arc3,rad={rad}"))


def draw_1b(ax):
    rng = np.random.default_rng(4)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # ---------------- stage 1: the query and the candidate library ----------------
    ax.text(0.105, 0.945, "query phenotype $Q$", ha="center", va="center",
            fontsize=6.2, color=INK)
    _rbox(ax, 0.105, 0.800, 0.19, 0.20, GREY)
    _cloud(ax, rng, 0.105, 0.800, n=48, rx=0.030, ry=0.030, c=GREY, alpha=0.55)
    _cloud(ax, rng, 0.105, 0.800, n=12, rx=0.015, ry=0.015, c=FOCAL, s=2.2, alpha=0.95)

    _rbox(ax, 0.105, 0.360, 0.19, 0.42, GREY)
    for i, yy in enumerate((0.500, 0.395, 0.290)):
        _cloud(ax, rng, 0.072, yy, n=30, rx=0.022, ry=0.016, c=GREY, alpha=0.5)
        _cloud(ax, rng, 0.072, yy, n=8, rx=0.011, ry=0.008, c=FOCAL, s=1.9, alpha=0.95)
        ax.text(0.162, yy, f"$P_{{{i + 1}}}$", ha="center", va="center", fontsize=5.6, color=GREY)
    ax.text(0.105, 0.198, "$\\vdots$", ha="center", va="center", fontsize=6.4, color=GREY)
    ax.text(0.105, 0.088, "candidate library $\\{P_d\\}$", ha="center", va="center",
            fontsize=6.2, color=INK)

    # merge the two inputs into one scoring step
    ax.plot([0.232, 0.232], [0.360, 0.800], lw=0.7, color=FAINT, zorder=1)
    _arrow(ax, (0.208, 0.800), (0.235, 0.800), color=FAINT)
    _arrow(ax, (0.208, 0.440), (0.235, 0.440), color=FAINT)
    ax.scatter([0.232], [0.560], s=6, c=GREY, zorder=4)

    # ---------------- stage 2: the two scoring rules ----------------
    _rbox(ax, 0.500, 0.755, 0.34, 0.32, FOCAL, fc="#EAF1F8", lw=1.0)
    ax.text(0.500, 0.868, "distributional score", ha="center", va="center",
            fontsize=6.2, color=FOCAL, fontweight="bold")
    ax.text(0.500, 0.786, "keeps the whole population", ha="center", va="center",
            fontsize=5.8, color=INK)
    _cloud(ax, rng, 0.408, 0.665, n=26, rx=0.018, ry=0.016, c=GREY, alpha=0.5)
    _cloud(ax, rng, 0.408, 0.665, n=8, rx=0.009, ry=0.008, c=FOCAL, s=1.9, alpha=0.95)
    _cloud(ax, rng, 0.592, 0.665, n=26, rx=0.018, ry=0.016, c=GREY, alpha=0.5)
    _cloud(ax, rng, 0.592, 0.665, n=8, rx=0.009, ry=0.008, c=FOCAL, s=1.9, alpha=0.95)
    ax.annotate("", xy=(0.556, 0.665), xytext=(0.444, 0.665),
                arrowprops=dict(arrowstyle="<|-|>", lw=0.8, color=FOCAL,
                                mutation_scale=5, shrinkA=0, shrinkB=0))
    ax.text(0.500, 0.712, "$s(P_d,\\,Q)$", ha="center", va="center",
            fontsize=6.0, color=FOCAL)

    _rbox(ax, 0.500, 0.278, 0.34, 0.32, COMP, fc="#FBEFE2", lw=1.0)
    ax.text(0.500, 0.391, "mean-signature cosine", ha="center", va="center",
            fontsize=6.2, color=COMP, fontweight="bold")
    ax.text(0.500, 0.309, "collapses it to one vector", ha="center", va="center",
            fontsize=5.8, color=INK)
    # The glyph row used to be captioned "population -> one delta vector" at y = 0.235. At the
    # printed panel size that line and the head of the thick delta arrow occupy the same band, and
    # the line only restated the box subtitle one line above it ("collapses it to one vector"), so
    # it is deleted rather than shrunk; the caption carries the same sentence.
    _cloud(ax, rng, 0.408, 0.190, n=26, rx=0.018, ry=0.016, c=GREY, alpha=0.5)
    _cloud(ax, rng, 0.408, 0.190, n=8, rx=0.009, ry=0.008, c=FOCAL, s=1.9, alpha=0.95)
    _arrow(ax, (0.446, 0.190), (0.502, 0.190), color=COMP, lw=0.7)
    _arrow(ax, (0.532, 0.166), (0.600, 0.218), color=COMP, lw=1.8)

    _arrow(ax, (0.240, 0.560), (0.326, 0.668), color=FOCAL, rad=-0.16)
    _arrow(ax, (0.240, 0.560), (0.326, 0.392), color=COMP, rad=0.16)

    # ---------------- stage 3: one ranking ----------------
    _arrow(ax, (0.674, 0.735), (0.748, 0.645), color=FOCAL, rad=0.14)
    _arrow(ax, (0.674, 0.297), (0.748, 0.455), color=COMP, rad=-0.14)

    _rbox(ax, 0.872, 0.560, 0.235, 0.52, GREY)
    for i, (num, lab, hit) in enumerate([("1", "candidate $d^\\star$", True), ("2", "", False),
                                         ("3", "", False), ("4", "", False)]):
        yy = 0.750 - 0.103 * i
        if hit:
            ax.add_patch(mpl.patches.Rectangle((0.762, yy - 0.044), 0.220, 0.086,
                                               fc="#EAF1F8", ec="none", zorder=2))
        ax.text(0.784, yy, num, ha="center", va="center", fontsize=5.8,
                color=FOCAL if hit else GREY, fontweight="bold" if hit else "normal")
        ax.plot([0.808, 0.968], [yy - 0.028, yy - 0.028], lw=0.6,
                color=FOCAL if hit else FAINT, zorder=3)
        if lab:
            ax.text(0.814, yy + 0.010, lab, ha="left", va="center", fontsize=5.6, color=FOCAL)
    ax.text(0.872, 0.352, "ranked candidates", ha="center", va="center",
            fontsize=6.2, color=INK)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(4.4, 3.3))
    draw_1b(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "1b.png"), dpi=200, bbox_inches="tight")
    print("wrote 1b.png")
