"""EvalShift Figure 1 panel 1e: the three evidence classes, and who reports them.

Schematic (no external data). Two defects in the previous version are corrected here.

1. The ladder was INVERTED. It placed Class A at the top of an arrow labelled "evidence
   strength". Class A is objective-aligned: per the manuscript it "tests objective fidelity, not
   independent utility", while Class C carries the external functional grounding "required for
   therapeutic-utility claims". Drawing Class A as the strongest evidence contradicted the paper
   in its own opening figure. Class C is now at the top and the axis is named for what actually
   increases: independence from the retrieval objective.

2. The status column read "this study: none" for Class C. The manuscript says "We report EvalShift
   under all three classes", with the Class-C oracle imported from GDSC2 dose-response data and
   labelled semi-real for that reason. "none" was false. The column now reports all three, and
   the Class-C qualification is stated rather than hidden.

The panel also now carries the field-level audit result, which is the comparison that gives the
ladder its point: across six published method families every headline metric is Class A and none
reports a Class-C readout as primary evidence (Supplementary Table 2).

Run standalone: python fig1e.py
"""
import os

import matplotlib as mpl
import matplotlib.pyplot as plt

FOCAL, COMP, GREY, INK = "#5185C0", "#E99D4E", "#7A7A7A", "#1A1A1A"
FAINT = "#E4E4E4"

X_TIER, W_TIER = 0.115, 0.545          # tier block
X_FIELD, X_OURS = 0.735, 0.945         # the two status columns

# name, one-line definition, examples, accent, field-headline?, this-study status
TIERS = [
    ("Class A", "objective-aligned", "energy regret, connectivity score", COMP,
     True, "full"),
    ("Class B", "task-proximal", "MoA-nDCG, minority coverage", GREY,
     False, "full"),
    ("Class C", "oracle-independent", "dose-response viability", INK,
     False, "imported"),
]
Y = (0.185, 0.455, 0.725)              # A at the bottom, C at the top
H = 0.215


def _dot(ax, x, y, filled, color, size=44):
    """Round status marker. Drawn in point units so it stays circular whatever the panel aspect."""
    ax.scatter([x], [y], s=size, marker="o", zorder=4, linewidths=0.9,
               facecolors=color if filled else "white", edgecolors=color)


def draw_1e(ax):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # ---- column headers ----
    # There were three stacked header lines here: a "headline metric" spanning label over a
    # two-line label per column. At the printed panel size that stack is taller than the space
    # above the ladder, and the spanning label overlapped "method families" both vertically and
    # horizontally. The spanning label is deleted and its word moved into the marker legend at the
    # foot of the panel, which had room for it; no information is lost.
    ax.text(X_FIELD, 0.992, "published\nmethod families", ha="center", va="top",
            fontsize=5.6, color=GREY, linespacing=1.25)
    ax.text(X_OURS, 0.992, "this\nstudy", ha="center", va="top",
            fontsize=5.6, color=INK, linespacing=1.25)
    ax.plot([X_TIER - 0.02, 0.998], [0.868, 0.868], lw=0.6, color=FAINT, zorder=1)

    # ---- the ladder ----
    for (name, defn, ex, col, field, ours), y in zip(TIERS, Y):
        ax.add_patch(mpl.patches.FancyBboxPatch(
            (X_TIER, y - H / 2), W_TIER, H,
            boxstyle="round,pad=0.003,rounding_size=0.02",
            fc=col, ec="none", alpha=0.10, zorder=1))
        ax.add_patch(mpl.patches.Rectangle((X_TIER, y - H / 2), 0.010, H,
                                           fc=col, ec="none", zorder=2))
        ax.text(X_TIER + 0.032, y + 0.062, f"{name}  ·  {defn}", ha="left", va="center",
                fontsize=6.2, color=col, fontweight="bold")
        ax.text(X_TIER + 0.032, y - 0.008, ex, ha="left", va="center",
                fontsize=5.6, color=INK)

        _dot(ax, X_FIELD, y + 0.028, field, GREY)
        _dot(ax, X_OURS, y + 0.028, True, col)
        if ours == "imported":
            ax.text(X_OURS, y - 0.048, "imported\noracle", ha="center", va="top",
                    fontsize=5.4, color=GREY, linespacing=1.2)

    ax.text(X_TIER + 0.032, Y[2] - 0.072, "required for a therapeutic claim",
            ha="left", va="center", fontsize=5.6, color=INK, style="italic")
    ax.text(X_TIER + 0.032, Y[1] - 0.072, "more independent, same upstream data",
            ha="left", va="center", fontsize=5.6, color=GREY, style="italic")
    ax.text(X_TIER + 0.032, Y[0] - 0.072, "the field default; it cannot fail",
            ha="left", va="center", fontsize=5.6, color=COMP, style="italic")

    # ---- the axis the ladder is ordered on ----
    ax.add_patch(mpl.patches.FancyArrowPatch(
        (0.045, Y[0] - H / 2), (0.045, Y[2] + H / 2), arrowstyle="-|>",
        mutation_scale=7, lw=1.0, color=INK, zorder=3))
    ax.text(0.014, (Y[0] + Y[2]) / 2, "independence from retrieval objective",
            rotation=90, ha="center", va="center", fontsize=5.6, color=INK)

    ax.text(X_TIER, 0.028, "headline metric:  filled, reported as primary evidence;  "
                           "open, not reported",
            ha="left", va="center", fontsize=5.4, color=GREY)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.7, 2.9))
    draw_1e(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "1e.png"), dpi=200, bbox_inches="tight")
    print("wrote 1e.png")
