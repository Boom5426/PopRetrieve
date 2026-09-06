"""Figure 5 panel b: the oracle ceiling, decomposed into direction, magnitude and distribution.
Source data: results/phase2_transition/phase_a/summary.csv (via phase2_data.oracle_ladder)
Run standalone: python fig5b.py

WHY A DOT PLOT AND NOT BARS
---------------------------
The three values are 0.945, 0.965 and 0.976 and the whole content of the panel is the two
increments between them, 0.020 and 0.010. Bars from zero would make those increments 2 per cent
of the ink; bars from a truncated baseline would make them look like the whole quantity. A dot
carries no baseline claim, so the axis can start where the data are without implying that the
distance to the axis means anything, and the increments are drawn as what they are: two brackets
between three points.
"""
import os, sys as _sys, os as _os
import numpy as np, matplotlib.pyplot as plt
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from figstyle import INK  # noqa: E402
from phase2_style import (POP, MEAN, MATERIAL, SHARED, PT_SMALL, PT_TICK, PT_ANNOT,
                        LW_HAIR)  # noqa: E402
from phase2_data import oracle_ladder  # noqa: E402

# One colour per rung, and they are the deck's own: the mean route is MEAN, the magnitude
# diagnostic is a material-slate because it is a diagnostic rather than a competing method, and
# the population route is POP.
RUNG = [MEAN, MATERIAL, POP]


def draw_5b(ax):
    d = oracle_ladder()
    xs = np.arange(len(d))
    for x, (_, r), c in zip(xs, d.iterrows(), RUNG):
        ax.plot([x, x], [r.lo, r.hi], lw=1.2, color=c, solid_capstyle="butt", zorder=2)
        ax.plot([x], [r.MRR], "o", ms=6.5, color=c, mec="white", mew=0.7, zorder=3)
        ax.text(x, r.hi + 0.0022, f"{r.MRR:.3f}", ha="center", va="bottom",
                fontsize=PT_SMALL, color=INK)

    # The two increments, drawn between consecutive rungs. These are the panel's subject, so they
    # get the only annotation with a leader.
    for i in range(len(d) - 1):
        a, b = d.iloc[i], d.iloc[i + 1]
        y = min(a.MRR, b.MRR) - 0.0075
        ax.annotate("", xy=(i + 1, y), xytext=(i, y),
                    arrowprops=dict(arrowstyle="-|>", lw=0.9, color=SHARED,
                                    shrinkA=0, shrinkB=0, mutation_scale=6))
        ax.text(i + 0.5, y - 0.0016, f"+{b.MRR - a.MRR:.4f}", ha="center", va="top",
                fontsize=PT_SMALL, color=SHARED)

    ax.set_xticks(xs)
    ax.set_xticklabels(d.label, fontsize=PT_TICK, linespacing=1.15)
    ax.set_xlim(-0.55, len(d) - 0.45)
    ax.set_ylim(0.918, 0.9885)
    ax.set_yticks([0.92, 0.94, 0.96, 0.98])
    ax.set_ylabel("MRR, oracle ceiling", fontsize=PT_ANNOT, labelpad=2.0)
    ax.tick_params(axis="both", labelsize=PT_TICK)
    ax.grid(axis="y", lw=LW_HAIR, color="#EDEDED", zorder=0)
    ax.set_axisbelow(True)
    for sp in ("right", "top"):
        ax.spines[sp].set_visible(False)
    # The axis does not start at zero, and a reader must be able to see that without counting
    # ticks. n is the query count behind every rung.
    ax.text(0.99, 0.02, "3,992 queries, 44 lines", transform=ax.transAxes, ha="right",
            va="bottom", fontsize=PT_SMALL, color=SHARED)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(2.19, 1.29))
    draw_5b(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "5b.png"), dpi=200, bbox_inches="tight")
    print("wrote 5b.png")
