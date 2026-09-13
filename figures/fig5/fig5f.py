"""Figure 5 panel f: the perturbation response is detectable at single-cell resolution.
Source data: results/phase2_transition/phase_c/gate2_observed.csv (via phase2_data.recoverability)
Run standalone: python fig5f.py

WHY THE GATE NEEDS ITS OWN PANEL
---------------------------------
Panel h reports that response detectability is the one quantity whose coefficient survives conditioning on the
mean route's own performance, at +0.0084 of reciprocal rank per standard deviation. A coefficient
on a quantity a reader has not seen is not evidence, so this panel is the quantity.

Two accuracies, on the same cells, for the same 3,992 queries. Given the state labels, the two
response arms are separable at a median of 0.80. Without them, the same separation is 0.555, on a
two-class balanced problem where 0.5 is chance. The supervised curve is therefore a CEILING, not a
method, and it is drawn in the deck's EXT green for exactly that reason: green in this figure means
a readout handed information the retrieval method does not have, so it can never be misread as a
competing score.

WHAT THE PANEL DOES NOT SAY
----------------------------
It does not say that unsupervised recovery is impossible; 30 per cent of queries clear 0.6. It says
that the median query does not, which is what makes the gate's positive coefficient in panel h a
statement about a quantity a deployed pipeline cannot read off its own data.
"""
import os as _os
import sys as _sys

import matplotlib.pyplot as plt
import numpy as np

_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from phase2_style import INK  # noqa: E402
from phase2_data import recoverability  # noqa: E402
from phase2_style import (EXT, LW_HAIR, POP, PT_ANNOT, PT_SMALL,  # noqa: E402
                          PT_TICK, SHARED, TEXT, axes_size_in, key_label)

BINS = np.linspace(0.50, 1.00, 26)      # 0.02 wide: fine enough to show the pile-up at chance
Y_MED = 0.150                           # one baseline for both median rules, clear of every bin
Y_TOP = 0.232

# The axes size is MEASURED at draw time (phase2_style.axes_size_in). It used to be declared
# here as a copy of fig5_assemble's ledger, and the copy went stale the first time a row height
# moved: the two series keys below are placed one 6.5 pt line down from a fraction computed
# against this number, so a stale value put the "labels given" key on top of the n annotation
# that sits above the axes.
SERIES = (("unsup", "without labels", POP), ("sup", "labels given", EXT))
CHANCE = 0.5


def draw_5f(ax):
    r = recoverability()
    for key, label, colour in SERIES:
        v = r[key]
        h, _ = np.histogram(v, bins=BINS)
        frac = h / len(v)
        # Step outline plus a light fill: two filled histograms at this overlap read as one shape,
        # and two bare outlines lose the one that sits lower.
        ax.stairs(frac, BINS, color=colour, lw=1.2, fill=False, zorder=4)
        ax.stairs(frac, BINS, color=colour, alpha=0.16, lw=0, fill=True, zorder=2)
        med = float(np.median(v))
        # Both median rules run to one height, and both value labels sit on one baseline above
        # every bin: drawn to a fraction of their own peak they land inside the histogram they
        # describe, and the two peaks differ threefold.
        ax.plot([med, med], [0, Y_MED], lw=1.0, color=colour, ls="--", zorder=5,
                dash_capstyle="butt")
        # Ink. The label sits on the head of its own coloured median rule, so the rule is already
        # carrying the hue; setting the digits in it too would spend a colour twice, so the
        # softened fills stay separate from the text.
        ax.text(med, Y_MED + 0.004, f"{med:.3f}", ha="center", va="bottom",
                fontsize=PT_SMALL, color=TEXT)

    ax.axvline(CHANCE, lw=LW_HAIR, color=SHARED, zorder=1)

    # Each series named over its OWN distribution and in its OWN colour: unsupervised recovery
    # piles up against chance on the left, supervised sits out to the right.
    # Not top-left: the unsupervised histogram's first bin reaches 0.21 there, which is the
    # tallest ink in the panel. The name sits to the right of its own median, over the empty
    # band both distributions leave between 0.6 and 0.7.
    # Each name takes a swatch rather than coloured letters. The unsupervised one needs it most:
    # the comment above places it in the band BOTH distributions leave empty, so it is the one
    # series name on this panel that is not sitting over its own ink and cannot rely on position.
    ax_h_in = axes_size_in(ax)[1]
    x_unsup = (0.615 - ax.get_xlim()[0]) / (ax.get_xlim()[1] - ax.get_xlim()[0])
    y_unsup = (Y_TOP - 0.012 - PT_SMALL / 72.0 / ax_h_in * Y_TOP) / Y_TOP
    key_label(ax, x_unsup, y_unsup, SERIES[0][1], SERIES[0][2], ha="left")
    key_label(ax, 0.98, 0.99 - PT_SMALL / 72.0 / ax_h_in, SERIES[1][1], SERIES[1][2],
              ha="right")

    ax.set_xlim(0.485, 1.005)
    ax.set_ylim(0.0, Y_TOP)
    ax.set_xticks([0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    # "chance" is set as part of its own tick rather than as a rotated label beside the rule:
    # rotated, it stood inside the tallest bin in the panel.
    ax.set_xticklabels(["0.5\nchance", "0.6", "0.7", "0.8", "0.9", "1.0"], fontsize=PT_TICK,
                       linespacing=1.12)
    ax.set_xlabel("response-detectability accuracy", fontsize=PT_ANNOT, labelpad=1.5)
    ax.set_ylabel("share of queries", fontsize=PT_ANNOT, labelpad=1.5)
    ax.tick_params(axis="y", labelsize=PT_TICK)
    ax.grid(axis="y", lw=LW_HAIR, color="#E5E7E7", zorder=0)
    ax.set_axisbelow(True)
    for sp in ("right", "top"):
        ax.spines[sp].set_visible(False)
    ax.text(1.0, 1.0, f"n = {r['n']:,} queries", transform=ax.transAxes, ha="right",
            va="bottom", fontsize=PT_SMALL, color=SHARED)
    return ax


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(2.40, 1.16))
    draw_5f(ax)
    fig.savefig(_os.path.join(_os.path.dirname(__file__), "5f.png"), dpi=200, bbox_inches="tight")
    print("wrote 5f.png")
