"""Figure 5 panel c: the oracle's SHAPE picks the winner.

Source: results/upgrade/oracle_shape_test.json (analysis/class_c/oracle_shape_test.py)

THE PANEL IN ONE SENTENCE
------------------------
Same 218,331 cells, same 20 surface proteins, same two RNA rankings, byte-identical across the two
columns; the only thing that changes is whether the protein oracle is computed as a MEAN (cosine of
mean protein deltas) or as a DISTRIBUTION (energy distance between protein-response cell clouds).
The winner swaps.

This is the sharpest result in the paper because no scorer can see either oracle. Class-A
circularity is a method grading its own objective; this is something else and worse: two EXTERNAL,
independent, blind criteria, built from the same measurements, handing victory to opposite methods
purely because of their own statistical form.

The magnitude scalar is drawn as a third bar and it is not decoration. Both distributional objects
here are energy distances, and an energy distance tracks a candidate's own response magnitude
(rho = +0.791), so a magnitude-to-magnitude channel could have produced the swap with no
distribution ever compared. It does not, quite: the scalar climbs steeply under the distributional
oracle (+0.125 -> +0.352, the confound behaving exactly as predicted), but energy still leads it by
+0.177 there against +0.022 under the mean-shaped oracle. Dropping the scalar would leave the
reader unable to see either fact.
"""
import json
import os

import numpy as np
import matplotlib.pyplot as plt

FOCAL, COMP, GREY, INK = "#5185C0", "#E99D4E", "#7A7A7A", "#1A1A1A"
GREEN = "#55966B"
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = f"{REPO}/results/upgrade/oracle_shape_test.json"

# 2026-07-26: the legend labels were two lines each. Three two-line entries is 0.54 in of legend
# inside a 1.02 in tall axes at this figure's print size, which covered the left bar group. One line
# each fits in the empty upper-left corner and says the same thing.
ROWS = [("energy", "energy (distributional)", FOCAL),
        ("mean", "mean cosine (incumbent)", COMP),
        ("magmatch", "magnitude scalar (control)", GREY)]


def draw_shape(ax):
    if not os.path.exists(SRC):
        raise FileNotFoundError(
            f"{SRC} missing. Run analysis/class_c/oracle_shape_test.py.")
    d = json.load(open(SRC))

    x = np.arange(2)          # 0 = mean-shaped oracle, 1 = distribution-shaped oracle
    w = 0.26
    for i, (key, lab, col) in enumerate(ROWS):
        v = [d[f"{key}_vs_oracleMEAN"], d[f"{key}_vs_oracleDIST"]]
        off = (i - 1) * w
        hatch = "///" if key == "magmatch" else None
        ax.bar(x + off, v, w, color=col, alpha=0.88, label=lab, zorder=3,
               hatch=hatch, edgecolor="white", linewidth=0.6)
        for xx, vv in zip(x + off, v):
            # three decimals, because these are the six numbers the caption quotes verbatim
            ax.text(xx, vv + 0.012, f"{vv:+.3f}", ha="center", va="bottom",
                    fontsize=5.6, fontweight="bold", color=INK)

    # the swap is the finding: mark which bar wins in each column, and say so in words rather
    # than leaving a bare triangle for the reader to decode
    for xi, key in [(0, "mean"), (1, "energy")]:
        i = [r[0] for r in ROWS].index(key)
        v = d[f"{key}_vs_oracle{'MEAN' if xi == 0 else 'DIST'}"]
        # marker and word clear the printed value above the bar: at print size the 5.6 pt value
        # label is 0.06 of this axis's range, and the marker used to sit on top of it
        ax.plot(xi + (i - 1) * w, v + 0.108, marker="v", ms=4.0,
                color=ROWS[i][2], zorder=6, clip_on=False)
        ax.text(xi + (i - 1) * w, v + 0.134, "wins", ha="center", va="bottom", fontsize=5.8,
                fontweight="bold", color=ROWS[i][2], zorder=6)

    # above the bars: the bars carry a white edge, which was punching gaps in a baseline drawn
    # underneath them and leaving black only in the inter-bar gutters
    ax.axhline(0, lw=0.8, color=INK, zorder=5)
    ax.set_xticks(x)
    ax.set_xticklabels(["oracle built as a\nMEAN", "oracle built as a\nDISTRIBUTION"],
                       fontsize=6.2, fontweight="bold")
    # two lines: rotated, the one-line version is 1.4 in of text against a 1.02 in axes
    ax.set_ylabel("Spearman $\\rho$ with\nthe protein oracle", fontsize=6.2)
    ax.set_ylim(0, 0.76)
    ax.tick_params(axis="y", labelsize=6)
    for s in ("right", "top"):
        ax.spines[s].set_visible(False)
    ax.legend(fontsize=5.8, loc="upper left", frameon=False, handlelength=1.2,
              labelspacing=0.30, borderpad=0.2, handletextpad=0.5)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.7, 3.0))
    draw_shape(ax)
    ax.set_title("The oracle's shape picks the winner", loc="left", fontsize=8)
    fig.savefig(os.path.join(os.path.dirname(__file__), "6shape.png"), dpi=200,
                bbox_inches="tight")
    print("wrote 6shape.png")
