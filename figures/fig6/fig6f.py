"""Figure 5 panel f: the constructive test. Repairing interaction fidelity does not close the gap.
Source data: results/phase2_transition/phase_b_p5/summary.csv (via phase2_data)
             plus the fidelity coefficient, read from the same tree by phase2_data
Run standalone: python fig5f.py

WHAT THE PANEL HAS TO SHOW AT ONCE
----------------------------------
Two things that are only interesting together: the state-conditioned predictor is the first in
this set to predict the drug-by-state interaction at all, and its population route is still behind
its own mean route. Either half alone invites the wrong reading. Drawn as two paired bars per
predictor, with the fidelity result stated as the panel's one annotation rather than as a second
axis, because a second axis at this width is what forced the previous deck's only right pad above
0.10 in.
"""
import os, sys as _sys, os as _os
import numpy as np, matplotlib.pyplot as plt
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from figstyle import INK  # noqa: E402
from phase2_style import POP, MEAN, SHARED, PT_SMALL, PT_TICK, PT_ANNOT, LW_HAIR  # noqa: E402
from phase2_data import state_conditioned_retrieval  # noqa: E402

W = 0.32
ROUTE = {"mean": MEAN, "population": POP}


def draw_6f(ax):
    d = state_conditioned_retrieval()
    preds = list(dict.fromkeys(d.predictor))
    xs = np.arange(len(preds))
    for x, p in zip(xs, preds):
        for off, route in ((-W / 2 - 0.02, "mean"), (W / 2 + 0.02, "population")):
            r = d[(d.predictor == p) & (d.route == route)].iloc[0]
            ax.bar(x + off, r.MRR, width=W, color=ROUTE[route], lw=0, zorder=2)
            ax.plot([x + off, x + off], [r.lo, r.hi], lw=0.9, color=INK, zorder=3)
            ax.text(x + off, r.hi + 0.004, f"{r.MRR:.4f}", ha="center", va="bottom",
                    fontsize=PT_SMALL, color=INK)

    ax.set_xticks(xs)
    ax.set_xticklabels([d[d.predictor == p].label.iloc[0] for p in preds],
                       fontsize=PT_TICK, linespacing=1.15)
    ax.set_xlim(-0.55, len(preds) - 0.45)
    ax.set_ylim(0.78, 0.975)
    ax.set_yticks([0.80, 0.85, 0.90])
    ax.set_ylabel("MRR, held-out line", fontsize=PT_ANNOT, labelpad=2.0)
    ax.tick_params(axis="y", labelsize=PT_TICK)
    ax.grid(axis="y", lw=LW_HAIR, color="#EDEDED", zorder=0)
    ax.set_axisbelow(True)
    for sp in ("right", "top"):
        ax.spines[sp].set_visible(False)
    # A two-swatch key across the top band. The band is free because the fidelity coefficient,
    # which is a number with an interval, belongs in the caption rather than on the panel face.
    from matplotlib.patches import Rectangle
    for i, (txt, col) in enumerate((("mean route", MEAN), ("population route", POP))):
        x0 = -0.50 + i * 0.95
        ax.add_patch(Rectangle((x0, 0.9585), 0.085, 0.011, color=col, lw=0, clip_on=False,
                               zorder=5))
        ax.text(x0 + 0.115, 0.9642, txt, ha="left", va="center", fontsize=PT_SMALL, color=INK)
    # The fidelity result, which is the reason this predictor is on the page at all. It is a
    # measured coefficient with its own interval, not a claim, so it is drawn at annotation size
    # in the deck's neutral colour.
    # The interaction-fidelity coefficient (rho = 0.606 [0.576, 0.639]) is the reason this
    # predictor is on the page; it is quoted in the caption, where an interval can sit beside it.


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(2.89, 1.29))
    draw_6f(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "6f.png"), dpi=200, bbox_inches="tight")
    print("wrote 6f.png")
