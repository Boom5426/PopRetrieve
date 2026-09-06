"""Figure 5 panel e: what interaction each predictor generates, against the interaction that is there.
Source data: results/phase2_transition/phase_b_p5/gate1_predicted.csv.gz and
             results/phase2_transition/gate1_interaction/interaction_per_query.csv (via phase2_data)
Run standalone: python fig5e.py

WHY A LOG AXIS, AND WHY ONE BAR RUNS OFF IT
-------------------------------------------
The quantity spans four orders of magnitude and its floor is exactly zero, so a linear axis would
show one bar and three invisible ones. An additive predictor adds one vector to every cell, so both
cellular states receive the same response and its interaction is zero by algebra: measured across
19,044 predictor-drug-seed values the largest absolute value is 2.5e-07, which is float32
round-off. Zero has no place on a log axis, so that bar is drawn as an arrow leaving the panel with
its value stated, rather than clamped to the smallest tick, which would make it look small instead
of absent.
"""
import os, sys as _sys, os as _os
import numpy as np, matplotlib.pyplot as plt
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from figstyle import INK  # noqa: E402
from phase2_style import (POP, MEAN, SHARED, TISSUE, PT_SMALL, PT_TICK, PT_ANNOT,
                        LW_HAIR, TEXT)  # noqa: E402
from phase2_data import predicted_interaction  # noqa: E402

ORDER = ["average_effect", "ot_map", "state_conditioned_average_effect"]
LABEL = {"average_effect": "average effect", "ot_map": "OT map",
         "state_conditioned_average_effect": "state-cond.\naverage effect"}
# Everything is drawn in units of 1e-4, so the tick labels are plain numbers. A superscripted
# 10^-6 prints its exponent at 0.7x nominal and clears this figure's 6.5 pt floor only at 9.3 pt,
# which is above the same module's 7.2 pt cap on panel text; rescaling the unit removes the
# conflict instead of arguing with it.
SCALE = 1e-4
FLOOR = 1e-6            # left edge of the drawn range, in raw units
ZERO_CUT = 1e-7         # below this a predictor is reported as generating none


def draw_6e(ax):
    d = predicted_interaction().set_index("predictor")
    obs = predicted_interaction().attrs["observed_median"]
    ys = np.arange(len(ORDER))[::-1]
    for y, k in zip(ys, ORDER):
        v = float(d.loc[k, "S_int_pred"])
        if v < ZERO_CUT:
            # An arrow off the left edge, not a bar. The claim is absence, not smallness.
            ax.annotate("", xy=(FLOOR / SCALE * 1.05, y), xytext=(FLOOR / SCALE * 4.2, y),
                        arrowprops=dict(arrowstyle="-|>", lw=1.0, color=MEAN,
                                        shrinkA=0, shrinkB=0, mutation_scale=6))
            ax.text(FLOOR / SCALE * 4.8, y, "0, to float precision", ha="left", va="center",
                    fontsize=PT_SMALL, color=TEXT)   # ink: the arrow beside it carries MEAN
        else:
            ax.barh(y, v / SCALE, left=FLOOR / SCALE, height=0.45, color=POP, lw=0,
                    zorder=2)
            # Inside the bar, right-aligned at its end: outside, the longer bar's label runs
            # into the observed-value rule, which is the one line in the panel that must stay
            # unobstructed.
            ax.text(v / SCALE * 0.90, y, f"{v / SCALE:.2g}", ha="right", va="center",
                    fontsize=PT_SMALL, color="white")
    # The interaction that is actually in the data, cross-fitted so it is unbiased.
    ax.axvline(obs / SCALE, ls="--", lw=1.1, color=TISSUE, zorder=4)
    ax.text(obs / SCALE * 1.12, len(ORDER) - 0.42, "observed", ha="left", va="top",
            fontsize=PT_SMALL, color=TEXT)   # ink: the dashed rule beside it carries TISSUE

    ax.set_xscale("log")
    ax.set_xlim(FLOOR / SCALE, 4.2)
    ax.set_xticks([0.01, 0.1, 1.0])
    ax.set_xticklabels(["0.01", "0.1", "1"], fontsize=PT_TICK)
    ax.set_yticks(ys)
    ax.set_yticklabels([LABEL[k] for k in ORDER], fontsize=PT_TICK, linespacing=1.12)
    ax.set_ylim(-0.62, len(ORDER) - 0.30)
    ax.set_xlabel("predicted drug-by-state interaction (units of 0.0001)",
                  fontsize=PT_ANNOT, labelpad=1.5)
    ax.grid(axis="x", lw=LW_HAIR, color="#EDEDED", zorder=0)
    ax.set_axisbelow(True)
    for sp in ("right", "top"):
        ax.spines[sp].set_visible(False)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(2.62, 1.02))
    draw_6e(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "6e.png"), dpi=200, bbox_inches="tight")
    print("wrote 6e.png")
