"""JUDGE Figure 1 panel 1d: what makes an evaluator independent of the score it grades.

Schematic (no external data). It states the manuscript's sharpest structural claim about
retrieval evaluation: the candidate is chosen by MAXIMIZING a score, and an objective-aligned
metric then measures that same score's ground truth on those same candidates, so the ranking
function and the evaluation function are one function evaluated once, with no estimation error
to expose and no way to lose. A more independent judge can overturn the ranking; a coupled one
cannot.

The panel was previously a node-and-arrow diagram like its two neighbours in this figure. It is
now built on a shape contrast instead: a CLOSED loop for the coupled case, an OPEN chain that
ends in a verdict for the independent case. The contrast, not the labels, carries the claim.

Run standalone: python fig1d.py
"""
import os

import matplotlib as mpl
import matplotlib.pyplot as plt

FOCAL, COMP, GREY, INK = "#5185C0", "#E99D4E", "#7A7A7A", "#1A1A1A"
FAINT = "#DCDCDC"


def _box(ax, x, y, w, h, txt, ec, fc="white", fs=6.0, tc=None, bold=False):
    ax.add_patch(mpl.patches.FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.004,rounding_size=0.025",
        fc=fc, ec=ec, lw=0.9, zorder=2))
    ax.text(x, y, txt, ha="center", va="center", fontsize=fs, color=tc or INK,
            zorder=3, linespacing=1.25, fontweight="bold" if bold else "normal")


def _arc(ax, p0, p1, color, rad, lw=1.2):
    ax.add_patch(mpl.patches.FancyArrowPatch(
        p0, p1, arrowstyle="-|>", mutation_scale=7, lw=lw, color=color, zorder=4,
        connectionstyle=f"arc3,rad={rad}"))


def draw_1d(ax):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # ============ coupled: a closed loop ============
    ax.text(0.0, 0.965, "coupled evaluation", ha="left", va="center",
            fontsize=6.4, color=COMP, fontweight="bold")
    ax.text(1.0, 0.965, "Class A", ha="right", va="center", fontsize=6.0, color=COMP)

    # Box widths are set by their longest line ("ranks the candidates", 6 pt): at the printed panel
    # width of ~2.6 in a 0.40 box left almost no inner padding, so both boxes are widened to 0.45
    # and pushed out to the panel edges, and the return arcs tightened to fit the 0.10 channel.
    _box(ax, 0.228, 0.760, 0.45, 0.185, "retrieval score\nranks the candidates",
         COMP, fc="#FBEFE2")
    _box(ax, 0.772, 0.760, 0.45, 0.185, "evaluation metric\ngrades that ranking",
         COMP, fc="#FBEFE2")
    _arc(ax, (0.460, 0.800), (0.540, 0.800), COMP, -0.60)
    _arc(ax, (0.540, 0.720), (0.460, 0.720), COMP, -0.60)
    ax.text(0.500, 0.596, "one function, evaluated once", ha="center", va="center",
            fontsize=5.8, color=COMP)
    ax.text(0.500, 0.520, "no way to lose", ha="center", va="center",
            fontsize=6.2, color=COMP, fontweight="bold")

    ax.plot([0.0, 1.0], [0.455, 0.455], lw=0.6, color=FAINT, zorder=1)

    # ============ independent: an open chain that can end either way ============
    ax.text(0.0, 0.372, "independent evaluation", ha="left", va="center",
            fontsize=6.4, color=INK, fontweight="bold")
    ax.text(1.0, 0.372, "Class B / C", ha="right", va="center", fontsize=6.0, color=GREY)

    # "overturned" in bold 6 pt is ~0.19 of the printed panel width, so the chain is shifted left
    # to leave the verdict labels a full column rather than letting them run past the panel edge.
    _box(ax, 0.115, 0.190, 0.23, 0.170, "the same\nranking", GREY)
    _box(ax, 0.460, 0.190, 0.32, 0.170, "outside judge\nMoA, viability", FOCAL, fc="#EAF1F8",
         tc=FOCAL)
    _arc(ax, (0.238, 0.190), (0.292, 0.190), GREY, 0.0, lw=1.0)
    _arc(ax, (0.628, 0.216), (0.752, 0.262), FOCAL, -0.12, lw=1.0)
    _arc(ax, (0.628, 0.164), (0.752, 0.118), FOCAL, 0.12, lw=1.0)
    ax.text(0.766, 0.268, "confirmed", ha="left", va="center", fontsize=6.0, color=FOCAL)
    ax.text(0.766, 0.112, "overturned", ha="left", va="center", fontsize=6.0, color=INK,
            fontweight="bold")
    ax.text(0.460, 0.040, "the gain can fail", ha="center", va="center",
            fontsize=6.2, color=INK, fontweight="bold")


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.7, 2.9))
    draw_1d(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "1d.png"), dpi=200, bbox_inches="tight")
    print("wrote 1d.png")
