"""PopRetrieve Figure 1 panel 1f: the three evidence classes, and who reports them.

Schematic (no external data). Two defects in an earlier version are corrected here and must not
come back.

1. The ladder was INVERTED. It placed Class A at the top of an arrow labelled "evidence
   strength". Class A is objective-aligned: per the manuscript it "tests objective fidelity, not
   independent utility", while Class C carries the external functional grounding "required for
   therapeutic-utility claims". Drawing Class A as the strongest evidence contradicted the paper
   in its own opening figure. Class C is at the top and the axis is named for what actually
   increases: independence from the retrieval objective.

2. The status column read "this study: none" for Class C. The manuscript says "We report
   PopRetrieve under all three classes", with the Class-C oracle imported from GDSC2 dose-response
   data and labelled semi-real for that reason. "none" was false. The column reports all three and
   the Class-C qualification is stated rather than hidden.

The panel also carries the field-level audit result, which is the comparison that gives the ladder
its point: across six published method families every headline metric is Class A and none reports
a Class-C readout as primary evidence (Supplementary Table 2).

Design notes (presentation only, no data involved):
  * No fills and no rounded boxes. Each tier used to sit in a rounded rectangle flooded at 10%
    alpha with a coloured left bar; three such blocks made a slide, not a journal panel. The tiers
    are separated by hairline rules and whitespace, and the only per-tier mark is a short vertical
    tick in a grey ramp, which encodes the ORDINAL axis the ladder is built on. An ordinal
    quantity is what a value ramp is for; three unrelated hues were the wrong encoding for it.
  * No hue. Per figstyle the deck's two hues mean distributional (FOCAL_SOFT) and mean/collapse (COMP_SOFT).
    Evidence-class independence is neither, so colouring the tiers gave both hues a second
    meaning inside the same figure. Panels a-d use colour where it means what the palette says;
    e and f are ink and grey. See the same note in fig1e.py.

Run standalone: python fig1f.py
"""
import os
import sys

import matplotlib as mpl
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from figstyle import text_run  # noqa: E402

GREY, INK = "#7A7A7A", "#1A1A1A"
HAIRLINE, HAIRLINE_FAINT = "#CFCFCF", "#E6E6E6"

X_AXIS, X_TICK, X_TEXT = 0.052, 0.095, 0.118
X_FIELD, X_OURS = 0.760, 0.940
Y = (0.195, 0.455, 0.715)               # Class A at the bottom, Class C at the top
SEP = (0.321, 0.581)                    # hairlines between adjacent tiers
TICK_H = 0.086

# name, definition, examples, gloss, ordinal tick shade, headline metric in the field?
TIERS = [
    ("Response matching", "objective-aligned", "energy regret, connectivity score",
     "closely aligned with the retrieval objective", "#BFBFBF", True),
    ("Mechanism recovery", "task-proximal", "MoA-nDCG, minority coverage",
     "more independent, same upstream data", "#8A8A8A", False),
    ("External functional", "evaluator-independent", "dose-response viability",
     "required for a therapeutic claim", INK, False),
]


def _dot(ax, x, y, filled, size=40):
    """Round status marker, sized in point units so it stays circular at any panel aspect."""
    ax.scatter([x], [y], s=size, marker="o", zorder=4, linewidths=0.8,
               facecolors=INK if filled else "white", edgecolors=INK)


def draw_1f(ax):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # ---- column headers ----
    ax.text(X_FIELD, 0.995, "published\nmethod families", ha="center", va="top",
            fontsize=5.6, color=GREY, linespacing=1.25)
    ax.text(X_OURS, 0.995, "this\nstudy", ha="center", va="top",
            fontsize=5.6, color=INK, linespacing=1.25)
    ax.plot([X_TICK - 0.012, 0.998], [0.855, 0.855], lw=0.6, color=HAIRLINE, zorder=1)

    for y in SEP:
        ax.plot([X_TICK - 0.012, 0.998], [y, y], lw=0.5, color=HAIRLINE_FAINT, zorder=1)

    # ---- the ladder ----
    for (name, defn, ex, gloss, shade, field), y in zip(TIERS, Y):
        ax.plot([X_TICK, X_TICK], [y - TICK_H, y + TICK_H], lw=1.6, color=shade,
                solid_capstyle="butt", zorder=2)
        text_run(ax, X_TEXT, y + 0.062,
                 [(name, INK, {"fontweight": "bold"}), (defn, GREY)], fontsize=6.2)
        ax.text(X_TEXT, y - 0.004, ex, ha="left", va="center", fontsize=5.6, color=INK)
        # The per-tier gloss ("required for a therapeutic claim", and its two siblings) is in
        # the caption. It was a sentence of interpretation under every row, i.e. three of the
        # panel's nine text lines spent on what the caption has to say anyway.

        _dot(ax, X_FIELD, y + 0.048, field)
        _dot(ax, X_OURS, y + 0.048, True)

    # The Class-C qualification sits under its own marker. It has to clear the hairline between
    # the top two tiers, which is why the markers ride on the tier-name line rather than mid-block.
    ax.text(X_OURS, Y[2] - 0.005, "imported\nevaluator", ha="center", va="top",
            fontsize=5.4, color=GREY, linespacing=1.2)

    # ---- the axis the ladder is ordered on ----
    ax.add_patch(mpl.patches.FancyArrowPatch(
        (X_AXIS, Y[0] - TICK_H), (X_AXIS, Y[2] + TICK_H), arrowstyle="-|>",
        mutation_scale=6, lw=0.7, color=INK, zorder=3))
    # Two lines, not one: set on a single line at 5.6 pt this label is 1.40 in tall against a
    # 1.64 in panel and its first character was clipped by the axes edge.
    ax.text(0.022, (Y[0] + Y[2]) / 2, "independence from\nretrieval objective",
            rotation=90, ha="center", va="center", fontsize=5.6, color=INK, linespacing=1.2)

    # The marker key is in the caption. Defining an encoding is exactly what a Nature figure
    # legend is for, and this one was the longest single line of text in the figure.


if __name__ == "__main__":
    # Same axes geometry the composite gives this panel, so a position tuned here is correct there.
    fig, ax = plt.subplots(figsize=(3.724, 1.639))
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    draw_1f(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "1f.png"), dpi=300)
    print("wrote 1f.png")
