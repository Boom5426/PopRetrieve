"""Figure 5 panel h: the four things that have to hold, and what each one is worth.
Source data: the numbers annotated here are the same ones panels b, c, d and f measure; they are
             read from results/ through phase2_data so the panel cannot drift from them.
Run standalone: python fig5h.py

WHY THE TOP HALF IS TO SCALE AND THE BOTTOM HALF IS NOT
--------------------------------------------------------
The first two requirements are measured in the same unit, MRR at the oracle ceiling, so their bars
are drawn to scale against each other and the shrinkage from one to the next is the real number.
The last two are not in that unit: one is a rate of changed top-1 decisions, the other is a signed
gain after prediction. Drawing all four as one funnel would put a width on quantities that do not
share a scale, which is a visual claim the data cannot support. The last two are therefore drawn as
gates, outlined rather than filled, carrying their own numbers and no width.

This replaces the three-requirement chain the previous figure proposed. That chain read
differential response, then recoverability, then decision relevance; measured on this benchmark it
does not locate where population information pays (panel g), which is why the requirement that
took its place is about the forward model rather than about the biology.
"""
import os, sys as _sys, os as _os
import numpy as np, matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from figstyle import INK  # noqa: E402
from phase2_style import POP, MEAN, SHARED, PT_SMALL, PT_ANNOT, TEXT  # noqa: E402
from phase2_data import oracle_ladder, oracle_flips, gain_ladder  # noqa: E402

# The left labels are two short lines each, so the stub column is narrow and the bars get the
# width they need for their own value labels. The full wording of each requirement is in the
# legend; a panel label that has to be shortened to fit is a label, not a claim.
X0, XW = 0.180, 0.580      # left edge and full width of the to-scale bars


def draw_6h(ax):
    lad = oracle_ladder()
    total = float(lad.MRR.iloc[2] - lad.MRR.iloc[0])       # direction -> distribution
    beyond_mag = float(lad.MRR.iloc[2] - lad.MRR.iloc[1])  # magnitude -> distribution
    flips = oracle_flips().iloc[0]
    pred = gain_ladder().set_index("key").loc["average_effect", "dMRR"]

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # ---- the two requirements that share a unit ----
    for i, (name, val, w) in enumerate((
            ("beats the\nmean route", total, 1.0),
            ("beyond\nmagnitude", beyond_mag, beyond_mag / total))):
        y = 0.845 - i * 0.175
        ax.add_patch(FancyBboxPatch((X0, y - 0.055), XW * w, 0.105,
                                    boxstyle="round,pad=0.002,rounding_size=0.015",
                                    lw=0, fc=POP, zorder=2))
        ax.text(X0 - 0.018, y, name, ha="right", va="center", fontsize=PT_SMALL,
                color=INK, linespacing=1.1)
        ax.text(X0 + XW * w + 0.014, y, f"{val:+.4f} MRR", ha="left", va="center",
                fontsize=PT_SMALL, color=INK)

    ax.text(X0 + XW / 2, 0.955, "at the oracle ceiling, one unit",
            ha="center", va="center", fontsize=PT_SMALL, color=SHARED)

    # ---- the two that do not, drawn as gates rather than as widths ----
    gates = (("changes a\ndecision",
              f"{flips.corrected * 100:.1f}% corrected, {flips.reverse * 100:.1f}% broken", POP),
             ("survives\nprediction",
              f"{pred:+.4f} MRR".replace("-", "\u2212"), MEAN))
    for i, (name, val, col) in enumerate(gates):
        y = 0.335 - i * 0.175
        ax.add_patch(FancyBboxPatch((X0, y - 0.055), XW, 0.105,
                                    boxstyle="round,pad=0.002,rounding_size=0.015",
                                    lw=0.9, ec=col, fc="white", zorder=2))
        ax.text(X0 - 0.018, y, name, ha="right", va="center", fontsize=PT_SMALL,
                color=INK, linespacing=1.1)
        # Ink: the value sits INSIDE a box drawn in `col`, so the outline is already carrying it.
        ax.text(X0 + XW / 2, y, val, ha="center", va="center", fontsize=PT_SMALL, color=TEXT)

    ax.text(X0 + XW / 2, 0.465, "different units, no width drawn",
            ha="center", va="center", fontsize=PT_SMALL, color=SHARED)
    ax.plot([0.03, 0.99], [0.535, 0.535], lw=0.7, color="#DDDDDD", zorder=1)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.29, 1.45))
    draw_6h(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "6h.png"), dpi=200, bbox_inches="tight")
    print("wrote 6h.png")
