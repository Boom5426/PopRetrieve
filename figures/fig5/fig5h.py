"""Figure 5 panel h: nothing biological locates the gain once the mean route's own result is known.
Source data: results/phase2_transition/bottleneck/regression.csv (via phase2_data.conditional_terms)
Run standalone: python fig5g.py

THE SPECIFICATION THIS PANEL DRAWS, AND WHY IT IS NOT THE OBVIOUS ONE
---------------------------------------------------------------------
The obvious analysis regresses the gain, RR_population minus RR_mean, on the candidate
explanators. It cannot be read: the gain and any headroom term share RR_mean with opposite signs,
and reciprocal rank is capped at 1, so a correlation between them is partly arithmetic. A null
that reshuffles the population route's reciprocal ranks within each context reproduces the
observed headroom correlation of +0.790 at +0.786 [+0.767, +0.805].

The specification drawn here therefore regresses the population route's OWN reciprocal rank on the
mean route's, plus the explanators. A coefficient answers: given how well the mean route did, does
this variable predict how well the population route does. The covariate is not drawn; it is the
control, not a finding.
"""
import os, sys as _sys, os as _os
import numpy as np, matplotlib.pyplot as plt
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from figstyle import INK  # noqa: E402
from phase2_style import POP, MEAN, EXT, SHARED, PT_SMALL, PT_TICK, PT_ANNOT, LW_HAIR  # noqa: E402
from phase2_data import conditional_terms  # noqa: E402

# Colour by what the term IS, not by its sign: the two interaction terms are the repaired Gate 1,
# response detectability is the term that survives, and the retired statistic is drawn in the mean family
# because that is the deck's colour for a quantity the population route does not get to use.
TERM_COLOUR = {"interaction_share": POP, "R_int": POP, "A_sup": EXT, "D_old": MEAN}


def draw_5h(ax):
    d = conditional_terms()
    ys = np.arange(len(d))[::-1]
    for y, (_, r) in zip(ys, d.iterrows()):
        c = TERM_COLOUR[r.term]
        crosses = (r.lo <= 0 <= r.hi)
        ax.plot([r.lo, r.hi], [y, y], lw=1.1, color=c,
                alpha=0.45 if crosses else 1.0, solid_capstyle="butt", zorder=2)
        ax.plot([r.beta], [y], "o", ms=5.6, color=c if not crosses else "white",
                mec=c, mew=1.1, zorder=3)
        # Outer side of the interval, away from zero: on the inner side the label sits on the
        # null line and the minus sign disappears into it.
        outer, ha = (r.hi + 0.0009, "left") if r.beta > 0 else (r.lo - 0.0009, "right")
        ax.text(outer, y, f"{r.beta:+.4f}".replace("-", "\u2212"),
                ha=ha, va="center", fontsize=PT_SMALL, color=INK)
    ax.axvline(0, ls="--", lw=1.0, color=SHARED, zorder=1)

    ax.set_yticks(ys)
    ax.set_yticklabels(d.label, fontsize=PT_TICK, linespacing=1.12)
    ax.set_ylim(-0.65, len(d) - 0.35)
    ax.set_xlim(-0.030, 0.026)
    ax.set_xticks([-0.015, 0.0, 0.015])
    ax.set_xticklabels(["−0.015", "0", "0.015"], fontsize=PT_TICK)
    ax.set_xlabel("standardised coefficient", fontsize=PT_ANNOT, labelpad=1.5)
    ax.grid(axis="x", lw=LW_HAIR, color="#EDEDED", zorder=0)
    ax.set_axisbelow(True)
    for sp in ("right", "top"):
        ax.spines[sp].set_visible(False)
    # Both notes on the top band, where nothing is plotted: the four rows fill the panel and any
    # annotation inside them lands on a value label. An open marker is an interval covering zero,
    # which has to be said on the panel, because a reader who misses it sees four findings where
    # there is one.
    # One note only. The query and cluster counts are in the caption; at this width a second
    # note on the same band overlaps the first.
    ax.text(0.5, 1.0, "open marker: interval covers 0", transform=ax.transAxes,
            ha="center", va="bottom", fontsize=PT_SMALL, color=SHARED)


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(2.30, 1.02))
    draw_5h(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "5h.png"), dpi=200, bbox_inches="tight")
    print("wrote 5h.png")
