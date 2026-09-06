"""Figure 6 panel d: the population route's deficit under prediction is a magnitude error.
Source data: results/phase2_transition/phase_b/delta_vs_reference.csv
             (via phase2_data.predicted_reference_deltas)
Run standalone: python fig6d.py

WHAT THE THREE ROWS ARE FOR
----------------------------
Panel b reports that the population route loses 0.0356 MRR to direction-only mean matching once
candidates are predicted rather than observed, and a reader can take that as a failure of
distributional scoring. It is not. On the SAME predictions and the same 19,960 query-seed pairs,
the magnitude-aware mean loses 0.0335, almost all of the same deficit, although it reads no
distribution at all. What is left once magnitude is controlled is 0.0020.

So the deficit is inherited from the predictor rather than produced by the scorer. An additive
predictor's candidate population is the vehicle population rigidly translated by an effect
averaged over the other cell lines, so its magnitude is wrong and its shape carries nothing about
the drug; a scorer that reads magnitude pays for that error and a cosine does not.

WHY ALL THREE ROWS AND NOT THE THIRD ALONE
-------------------------------------------
The third row alone would be the claim without its evidence. It is the first two rows being the
same size that makes the third one mean anything: a reader has to see that the quantity blamed on
distributional scoring is carried almost entirely by a scorer that does no distributional scoring.
"""
import os as _os
import sys as _sys

import matplotlib.pyplot as plt
import numpy as np

_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from figstyle import INK  # noqa: E402
from phase2_data import predicted_reference_deltas  # noqa: E402
from phase2_style import (FAINT, LW_HAIR, MATERIAL, POP, PT_ANNOT,  # noqa: E402
                          PT_SMALL, PT_TICK, SHARED)

# Coloured by the scorer being EVALUATED, in the deck's rung colours: the population route is POP
# blue and the magnitude-aware mean is the slate of the middle rung on Figures 1a, 2a and 5b.
ROW_COLOUR = {"energy": POP, "mean_l2": MATERIAL}
RATIO_MIN = 5.0     # the first two rows must stay within this factor of each other; see below


def draw_6d(ax):
    d = predicted_reference_deltas()
    assert len(d) == 3, d
    # The panel's claim, asserted on the drawn values: the deficit against direction-only is
    # carried by the magnitude-aware mean too, and what survives controlling for magnitude is
    # smaller than either by a wide margin. If that ever stops holding, the caption is wrong and
    # the build must stop rather than draw it.
    a, b, c = (float(d.dMRR[i]) for i in range(3))
    assert abs(a) / abs(b) < 2.0 and abs(b) / abs(a) < 2.0, (
        f"the population deficit {a:+.4f} and the magnitude-aware deficit {b:+.4f} are no longer "
        f"the same size; this panel's whole reading is that they are.")
    assert abs(a) / abs(c) > RATIO_MIN, (
        f"the magnitude-controlled residue {c:+.4f} is no longer small against the raw deficit "
        f"{a:+.4f}; the caption calls it what is left, and it would not be.")

    ys = np.arange(len(d))[::-1]
    for y, (_, r) in zip(ys, d.iterrows()):
        colour = ROW_COLOUR[r.scorer]
        ax.plot([r.lo, r.hi], [y, y], lw=1.1, color=colour, solid_capstyle="butt", zorder=2)
        ax.plot([r.dMRR], [y], "o", ms=5.4, color=colour, zorder=3)
        # Above its own marker, not beside the interval: at this width a label set outside the
        # interval either runs into the y tick labels on the left or crosses the zero rule on
        # the right, and the three rows are 1.0 apart in y, which is room for one 6.5 pt line.
        ax.text(r.dMRR, y + 0.20, f"{r.dMRR:+.4f}".replace("-", "−"), ha="center", va="bottom",
                fontsize=PT_SMALL, color=INK)
    ax.axvline(0, ls="--", lw=1.0, color=SHARED, zorder=1)

    ax.set_yticks(ys)
    ax.set_yticklabels(d.label, fontsize=PT_TICK, linespacing=1.12)
    ax.set_ylim(-0.60, len(d) - 0.20)
    ax.set_xlim(-0.072, 0.010)
    ax.set_xticks([-0.06, -0.03, 0.0])
    ax.set_xticklabels(["−0.06", "−0.03", "0"], fontsize=PT_TICK)
    ax.set_xlabel("ΔMRR under the predictor", fontsize=PT_ANNOT, labelpad=1.5)
    ax.grid(axis="x", lw=LW_HAIR, color="#EDEDED", zorder=0)
    ax.set_axisbelow(True)
    for sp in ("right", "top"):
        ax.spines[sp].set_visible(False)
    ax.text(1.0, 1.0, f"n = {int(d.n[0]):,} query-seed pairs", transform=ax.transAxes,
            ha="right", va="bottom", fontsize=PT_SMALL, color=SHARED)
    return ax


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(2.30, 1.10))
    draw_6d(ax)
    fig.savefig(_os.path.join(_os.path.dirname(__file__), "6d.png"), dpi=200, bbox_inches="tight")
    print("wrote 6d.png")
