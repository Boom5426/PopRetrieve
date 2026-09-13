"""Figure 5 panel g: the interaction statistic the gate used to be built on measured effect size.
Source data: results/phase2_transition/gate1_interaction/checks.json (via phase2_data.interaction_audit)
Run standalone: python fig5g.py

WHY A STATISTIC GETS ITS OWN PANEL
-----------------------------------
Panel f asks whether drug-by-state interaction locates the population route's advantage, and
answers no. That answer is only worth reading if the statistic being conditioned on measures
interaction. The one earlier drafts used, D_old = 1 − cos(r_1, r_2), does not: it runs at −0.69
with the response norm and −0.43 with the number of cells per arm, so the weakest drugs and the
smallest arms score as the most state-dependent. A gate built on it selects for weak signal.

Its replacement is a cross-fitted inner product, S_int = <I_A, I_B>/p, which is exactly zero in
expectation under the additive null. On the same queries it runs at +0.66 with the response norm,
which is the sign a real interaction should have, since a larger response can carry a larger
interaction; and at +0.10 with cell count, which is the number that should be near zero.

TWO ROWS, TWO DIFFERENT TARGETS, AND THE CAPTION CARRIES THAT
---------------------------------------------------------------
The two rows are not read the same way. On response magnitude the disqualifying result is a
NEGATIVE correlation, because it inverts the quantity being measured; on cells per arm the target
is zero, because a statistic of biology must not track how many cells were sequenced. The panel
draws both and states neither target: a target line would be a threshold this study did not
pre-register for the magnitude row, and the caption is where the two readings can be given.
"""
import os as _os
import sys as _sys

import matplotlib.pyplot as plt
import numpy as np

_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from phase2_style import INK  # noqa: E402
from phase2_data import CONFOUND_LABEL, interaction_audit  # noqa: E402
from phase2_style import (FAINT, LW_HAIR, MEAN, POP, PT_ANNOT,  # noqa: E402
                          PT_SMALL, PT_TICK, SHARED, TEXT, key_label)

# The retired statistic takes the deck's mean-family orange, exactly as it does in panel f: it is
# the quantity the population route does not get to use. Its replacement takes POP.
STAT_COLOUR = {"D_old": MEAN, "S_int": POP}
STAT_KEY = {"D_old": "naive cosine", "S_int": "cross-fitted interaction"}
ROWS = ("response_norm", "n_treated")

# The axes fig5_assemble gives this panel, which phase2_style.key_label needs and cannot know.
# The axes size is measured at draw time; see phase2_style.axes_size_in.


def draw_5g(ax):
    a = interaction_audit()
    d = a["rows"]
    ys = np.arange(len(ROWS))[::-1]

    for y, conf in zip(ys, ROWS):
        sub = {r.stat: float(r.rho) for _, r in d[d.confound == conf].iterrows()}
        # The join first, under both markers: it is what makes the pair one comparison rather
        # than two readings that happen to share a row.
        ax.plot([sub["D_old"], sub["S_int"]], [y, y], lw=1.0, color=FAINT, zorder=2,
                solid_capstyle="butt")
        for stat, rho in sub.items():
            ax.plot([rho], [y], "o", ms=5.4, color=STAT_COLOUR[stat], zorder=4)
            below = stat == "D_old"
            # INK, not the marker's colour. The value sits directly against its own dot, so the
            # dot is already carrying the hue and the letters were spending it a second time at
            # 6.5 pt, so the softened method colours are intentionally not used as text. Panel h,
            # on this same row, labels the same kind of
            # value in ink beside a coloured marker and loses nothing by it.
            ax.text(rho, y + (-0.30 if below else 0.30), f"{rho:+.2f}".replace("-", "−"),
                    ha="center", va="top" if below else "bottom", fontsize=PT_SMALL, color=TEXT)
    ax.axvline(0, ls="--", lw=1.0, color=SHARED, zorder=1)

    ax.set_yticks(ys)
    ax.set_yticklabels([CONFOUND_LABEL[c] for c in ROWS], fontsize=PT_TICK, linespacing=1.12)
    ax.set_ylim(-0.72, len(ROWS) - 0.28)
    ax.set_xlim(-0.92, 0.92)
    ax.set_xticks([-0.5, 0.0, 0.5])
    ax.set_xticklabels(["−0.5", "0", "0.5"], fontsize=PT_TICK)
    ax.set_xlabel("Spearman ρ with the statistic", fontsize=PT_ANNOT, labelpad=1.5)
    ax.grid(axis="x", lw=LW_HAIR, color="#E5E7E7", zorder=0)
    ax.set_axisbelow(True)
    for sp in ("right", "top"):
        ax.spines[sp].set_visible(False)

    # The key on the top band, where nothing is plotted. A SWATCH carries the colour and the name
    # is ink, which is the deck's rule and is what the value labels above now follow. These two
    # names have no marker beside them to inherit a hue from, so they get one of their own.
    for x, stat in ((0.0, "D_old"), (1.0, "S_int")):
        w = key_label(ax, x, 1.02, STAT_KEY[stat], STAT_COLOUR[stat],
                      ha="left" if x == 0 else "right")
        assert w < 0.5, (
            f"the key {STAT_KEY[stat]!r} plus its swatch spans {w:.0%} of the panel; the two keys "
            f"sit at opposite ends of one band and would meet in the middle.")
    return ax


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(2.30, 1.02))
    draw_5g(ax)
    fig.savefig(_os.path.join(_os.path.dirname(__file__), "5g.png"), dpi=200, bbox_inches="tight")
    print("wrote 5g.png")
