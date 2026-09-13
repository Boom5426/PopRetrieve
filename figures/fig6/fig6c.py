"""Figure 5 panel c: what forward prediction does to the population route's gain.
Source data: phase_a + phase_b + phase_b_p5 delta_vs_reference.csv (via phase2_data.gain_ladder)
Run standalone: python fig5d.py

THE PANEL'S ONE JOB
-------------------
The oracle gain is positive; every additive predictor's is negative. That sign change is the
result, so the panel is built around the zero line and nothing else competes with it. Intervals
are context-clustered bootstrap, because queries inside one cell line share a source population
and an entire candidate library.
"""
import os, sys as _sys, os as _os
import numpy as np, matplotlib.pyplot as plt
_sys.path.insert(0, _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__))))
_sys.path.insert(0, _os.path.dirname(_os.path.abspath(__file__)))
from phase2_style import INK  # noqa: E402
from phase2_style import (POP, MEAN, SHARED, PT_SMALL, PT_TICK, PT_ANNOT,  # noqa: E402
                          LW_HAIR, TEXT, key_label)
from phase2_data import gain_ladder  # noqa: E402


# The axes size is measured at draw time; see phase2_style.axes_size_in.


def draw_6c(ax):
    d = gain_ladder()
    ys = np.arange(len(d))[::-1]
    for y, (_, r) in zip(ys, d.iterrows()):
        c = POP if r.dMRR > 0 else MEAN
        ax.plot([r.lo, r.hi], [y, y], lw=1.1, color=c, solid_capstyle="butt", zorder=2)
        ax.plot([r.dMRR], [y], "o", ms=5.6, color=c, mec="white", mew=0.6, zorder=3)
        side = 1 if r.dMRR > 0 else -1
        ax.text(r.hi + 0.012 if side > 0 else r.lo - 0.012, y,
                f"{r.dMRR:+.4f}".replace("-", "−"),
                ha="left" if side > 0 else "right", va="center",
                fontsize=PT_SMALL, color=INK)
    ax.axvline(0, ls="--", lw=1.0, color=SHARED, zorder=1)
    # The oracle is not a predictor and must not read as one more row in the same series.
    ax.axhline(ys[0] - 0.5, lw=LW_HAIR, color="#D2D7E0", zorder=1)

    ax.set_yticks(ys)
    ax.set_yticklabels(d.label, fontsize=PT_TICK, linespacing=1.12)
    ax.set_ylim(-0.7, len(d) - 0.02)
    ax.set_xlim(-0.50, 0.15)
    ax.set_xticks([-0.4, -0.3, -0.2, -0.1, 0.0, 0.1])
    ax.set_xticklabels(["\u22120.4", "\u22120.3", "\u22120.2", "\u22120.1", "0", "0.1"],
                       fontsize=PT_TICK)
    ax.set_xlabel("ΔMRR, population route minus mean route", fontsize=PT_ANNOT, labelpad=1.5)
    ax.grid(axis="x", lw=LW_HAIR, color="#E5E7E7", zorder=0)
    ax.set_axisbelow(True)
    for sp in ("right", "top"):
        ax.spines[sp].set_visible(False)
    # Each half-plane named with a swatch of its own rather than in coloured letters: these two
    # head a region and have no marker beside them, which is the case phase2_style.key_label
    # exists for. The right-hand label stays anchored to the axis edge rather than to zero,
    # because at this width the zero-anchored form runs past the spine. The data anchors are
    # converted here because key_label works in axes coordinates.
    y_frac = ax.transLimits.transform((0.0, len(d) - 0.10))[1]
    for x_data, txt, col in ((-0.012, "mean route better", MEAN),
                             (0.148, "population better", POP)):
        x_frac = ax.transLimits.transform((x_data, 0.0))[0]
        key_label(ax, x_frac, y_frac, txt, col, ha="right")


if __name__ == "__main__":
    fig, ax = plt.subplots(figsize=(3.05, 1.16))
    draw_6c(ax)
    fig.savefig(os.path.join(os.path.dirname(__file__), "6c.png"), dpi=200, bbox_inches="tight")
    print("wrote 6c.png")
