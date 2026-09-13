"""Figure 6 panel b: what deleting the observed candidate responses costs each route.
Source data: phase_a/summary.csv and phase_b/summary.csv (via phase2_data.route_loss)
Run standalone: python fig6c.py

WHAT THE PANEL HAS TO MAKE VISIBLE
-----------------------------------
Panel b reports the population route's deficit under a predictor as one number per predictor. That
number is a difference of differences and it hides which route moved. This panel shows the two
routes travelling from the oracle to the best predictor on the same axis: the mean route gives up
0.058 MRR, the population route 0.124, and the two lines cross. The crossing IS the result, and it
survives every label being removed.

WHY THE BEST PREDICTOR AND NOT ALL SEVEN
-----------------------------------------
average_effect is the strongest mean-route predictor in the panel above, so it is the one that
makes the comparison hardest to dismiss: the population route does not lose to a weak predictor,
it loses to the best one. The other predictors are in panel b with their intervals.
"""
import os as _os
import sys as _sys

import matplotlib.pyplot as plt

_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from phase2_style import INK  # noqa: E402
from phase2_data import route_loss  # noqa: E402
from phase2_style import (LW_HAIR, MEAN, POP, PT_ANNOT, PT_SMALL,  # noqa: E402
                          PT_TICK, SHARED, TEXT)

X_ORACLE, X_PRED = 0.0, 1.0
ROUTE_COLOUR = {"mean route": MEAN, "population route": POP}
LOSS_X = {"population route": 0.32, "mean route": 0.80}


def draw_6b(ax):
    d = route_loss()
    assert len(d) == 2, d
    for _, r in d.iterrows():
        c = ROUTE_COLOUR[r.route]
        ax.plot([X_ORACLE, X_PRED], [r.oracle, r.predicted], "-o", lw=1.4, ms=5.0, color=c,
                zorder=3, solid_capstyle="round")
        ax.plot([X_PRED, X_PRED], [r.predicted_lo, r.predicted_hi], lw=1.1, color=c, zorder=2,
                solid_capstyle="butt")
        # Ink from here down. Every label on this panel sits on or beside its own coloured line,
        # so the line carries the hue and the letters stay in dark ink. See phase2_style.key_label.
        ax.text(X_ORACLE - 0.06, r.oracle, f"{r.oracle:.4f}", ha="right", va="center",
                fontsize=PT_SMALL, color=TEXT)
        # The two lines cross at x = 0.46, so a label at either midpoint lands on the other
        # line. Each loss is set ABOVE its own line on the side of the crossing where that line
        # is the upper one: the population route before it, the mean route after it.
        lx = LOSS_X[r.route]
        ax.text(lx, r.oracle + lx * (r.predicted - r.oracle) + 0.007, f"−{r.loss:.3f}",
                ha="center", va="bottom", fontsize=PT_SMALL, color=TEXT)
    # Route names at the predicted end, one line each: the two endpoints are 0.036 MRR apart,
    # which is 0.22 in here, and a two-line name is 0.19 in tall.
    for _, r in d.iterrows():
        ax.text(X_PRED + 0.06, r.predicted, r.route.split()[0], ha="left", va="center",
                fontsize=PT_SMALL, color=TEXT)

    ax.set_xlim(-0.42, 1.62)
    ax.set_xticks([X_ORACLE, X_PRED])
    ax.set_xticklabels(["candidates\nobserved", "candidates\npredicted"], fontsize=PT_TICK,
                       linespacing=1.12)
    ax.tick_params(axis="x", length=0, pad=3)
    ax.set_ylim(0.795, 1.005)
    ax.set_yticks([0.80, 0.85, 0.90, 0.95, 1.00])
    ax.set_yticklabels(["0.80", "0.85", "0.90", "0.95", "1.00"], fontsize=PT_TICK)
    ax.set_ylabel("MRR", fontsize=PT_ANNOT, labelpad=1.5)
    ax.grid(axis="y", lw=LW_HAIR, color="#E5E7E7", zorder=0)
    ax.set_axisbelow(True)
    for sp in ("right", "top"):
        ax.spines[sp].set_visible(False)
    # Short: at 2.10 in the fuller form ran past both spines, and an artist outside its axes
    # widens the assembled page. The reference scorer is named in the caption.
    ax.text(0.5, 1.0, "predictor: average effect", transform=ax.transAxes, ha="center",
            va="bottom", fontsize=PT_SMALL, color=SHARED)
    return ax


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(2.10, 1.30))
    draw_6b(ax)
    fig.savefig(_os.path.join(_os.path.dirname(__file__), "6b.png"), dpi=200, bbox_inches="tight")
    print("wrote 6b.png")
